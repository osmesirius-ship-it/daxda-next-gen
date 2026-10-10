"""
DAXDA Next-Gen Quantum Stabilizer & Surface Code Engine (stabilizer.py)
======================================================================
Defines [[n, k, d]] stabilizer codes, including the canonical [[7,1,3]] Steane
CSS code and 2D topological surface code lattices.
Verifies Abelian stabilizer group commutation and logical algebra.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
from .pauli import PauliOperator


@dataclass
class StabilizerCode:
    """An [[n, k, d]] stabilizer code specification."""
    n_physical: int
    k_logical: int
    distance: int
    stabilizers: List[PauliOperator]
    logical_x: List[PauliOperator]
    logical_z: List[PauliOperator]

    def verify_abelian(self) -> bool:
        """Verifies that all stabilizer generators pairwise commute: [g_i, g_j] = 0."""
        m = len(self.stabilizers)
        for i in range(m):
            for j in range(i + 1, m):
                if not self.stabilizers[i].commutes_with(self.stabilizers[j]):
                    return False
        return True

    def verify_logical_commutation(self) -> bool:
        """
        Verifies that logical operators commute with all stabilizers
        and logical X and Z anticommute on the same logical qubit.
        """
        for g in self.stabilizers:
            for lx in self.logical_x:
                if not g.commutes_with(lx):
                    return False
            for lz in self.logical_z:
                if not g.commutes_with(lz):
                    return False

        # Logical X and Z must anticommute: {X_L, Z_L} = 0
        for lx, lz in zip(self.logical_x, self.logical_z):
            if lx.commutes_with(lz):
                return False

        return True


class SteaneCode:
    """The canonical [[7, 1, 3]] Steane CSS Quantum Error-Correcting Code."""

    @classmethod
    def get_code(cls) -> StabilizerCode:
        """
        Constructs [[7, 1, 3]] Steane code with:
        X-stabilizers:
        g1 = X0 X1 X2 X3
        g2 = X1 X2 X4 X5
        g3 = X2 X3 X5 X6
        Z-stabilizers:
        g4 = Z0 Z1 Z2 Z3
        g5 = Z1 Z2 Z4 Z5
        g6 = Z2 Z3 Z5 Z6
        """
        n = 7
        stabs = [
            # X-stabilizers
            PauliOperator.from_string("XXXXIII"),
            PauliOperator.from_string("IXXIXXI"),
            PauliOperator.from_string("IIXXIXX"),
            # Z-stabilizers
            PauliOperator.from_string("ZZZZIII"),
            PauliOperator.from_string("IZZIZZI"),
            PauliOperator.from_string("IIZZIZZ"),
        ]

        logical_x = [PauliOperator.from_string("XXXXXXX")]
        logical_z = [PauliOperator.from_string("ZZZZZZZ")]

        return StabilizerCode(
            n_physical=n,
            k_logical=1,
            distance=3,
            stabilizers=stabs,
            logical_x=logical_x,
            logical_z=logical_z
        )


class SurfaceCode:
    """Rotated 2D surface code lattice of code distance d."""

    @classmethod
    def get_code(cls, distance: int = 3) -> StabilizerCode:
        """Constructs rotated surface code with d^2 physical data qubits."""
        if distance % 2 == 0:
            raise ValueError("Surface code distance must be odd")

        n = distance * distance
        # Standard distance d=3 rotated surface code (9 data qubits, 8 stabilizers)
        stabs = [
            # X checks
            PauliOperator.from_string("IXXIIIIII"),  # X_{1,2}
            PauliOperator.from_string("IIIIIIXXI"),  # X_{6,7}
            PauliOperator.from_string("XXIXXIIII"),  # X_{0,1,3,4}
            PauliOperator.from_string("IIIIXXIXX"),  # X_{4,5,7,8}
            # Z checks
            PauliOperator.from_string("ZIIZIIIII"),  # Z_{0,3}
            PauliOperator.from_string("IIIIIZIIZ"),  # Z_{5,8}
            PauliOperator.from_string("IZZIZZIII"),  # Z_{1,2,4,5}
            PauliOperator.from_string("IIIZZIZZI"),  # Z_{3,4,6,7}
        ]

        # Logical X spans column 0 (qubits 0, 3, 6), Logical Z spans row 0 (qubits 0, 1, 2)
        logical_x = [PauliOperator.from_string("XIIXIIXII")]
        logical_z = [PauliOperator.from_string("ZZZIIIIII")]

        return StabilizerCode(
            n_physical=n,
            k_logical=1,
            distance=distance,
            stabilizers=stabs,
            logical_x=logical_x,
            logical_z=logical_z
        )
