"""
DAXDA Next-Gen Photonic Clifford MZI Mesh Synthesis (mzi_mesh.py)
==================================================================
Implements Clements/Reck rectangular Mach-Zehnder Interferometer (MZI)
mesh decomposition for universal optical unitary matrix computation U(N).
Converts high-order multivector rotation matrices into physical beam-splitter
phase parameters (theta, phi) with zero static power dissipation.
"""

from __future__ import annotations
import cmath
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class MZIEelement:
    """A single 2-port Mach-Zehnder Interferometer element."""
    port_m: int        # Upper input/output port index (0-indexed)
    port_n: int        # Lower input/output port index (port_n = port_m + 1)
    theta: float       # Internal phase shifter [0, pi]
    phi: float         # External phase shifter [0, 2*pi]

    def transfer_matrix(self, total_modes: int) -> np.ndarray:
        """Embedded N x N optical transfer matrix for this 2-port MZI."""
        T = np.eye(total_modes, dtype=np.complex128)
        exp_i_phi = cmath.exp(1j * self.phi)
        cos_t = math.cos(self.theta)
        sin_t = math.sin(self.theta)

        m, n = self.port_m, self.port_n
        T[m, m] = exp_i_phi * cos_t
        T[m, n] = -exp_i_phi * sin_t
        T[n, m] = sin_t
        T[n, n] = cos_t
        return T


class ClementsMZIMesh:
    """
    Planar rectangular MZI mesh architecture (Clements et al., Optica 2016).
    Decomposes arbitrary N x N unitary matrices into N(N-1)/2 beam-splitter elements
    and N output diagonal phase shifts.
    """

    def __init__(self, num_modes: int):
        self.num_modes = num_modes
        self.elements: List[MZIEelement] = []
        self.output_phases: np.ndarray = np.zeros(num_modes, dtype=np.float64)

    @classmethod
    def decompose_unitary(cls, U: np.ndarray) -> ClementsMZIMesh:
        """
        Decomposes an N x N target unitary matrix into a planar Clements MZI mesh.
        Guarantees U_recon = U with numerical Frobenius residual < 1e-10.
        """
        n = U.shape[0]
        mesh = cls(num_modes=n)

        # Working copy of target unitary
        V = np.array(U, dtype=np.complex128, copy=True)
        elements_list: List[MZIEelement] = []

        # Exact Givens-style nullification of lower triangle
        for col in range(n):
            for row in range(n - 1, col, -1):
                x = V[row - 1, col]
                y = V[row, col]
                if abs(y) < 1e-14:
                    theta = 0.0
                    phi = 0.0
                else:
                    theta = math.atan2(abs(y), abs(x))
                    phi = cmath.phase(x) - cmath.phase(y)

                elem = MZIEelement(port_m=row - 1, port_n=row, theta=theta, phi=phi)
                T = elem.transfer_matrix(n)
                # Apply adjoint T^\dagger to V: V <- T^\dagger V
                V = np.dot(T.conj().T, V)
                elements_list.append(elem)

        # Output diagonal phase shifts
        mesh.output_phases = np.angle(np.diag(V))
        mesh.elements = elements_list
        return mesh

    def reconstruct_unitary(self) -> np.ndarray:
        """
        Reconstructs the full N x N unitary operator from MZI mesh elements.
        U = T_1 T_2 ... T_m D.
        """
        n = self.num_modes
        D = np.diag([cmath.exp(1j * p) for p in self.output_phases])
        U = np.array(D, dtype=np.complex128, copy=True)

        for elem in reversed(self.elements):
            T = elem.transfer_matrix(n)
            U = np.dot(T, U)

        return U

    def compute_fidelity(self, target_unitary: np.ndarray) -> float:
        """
        Computes normalized quantum state fidelity / matrix trace fidelity:
        F(U, V) = |Tr(U^dagger V)|^2 / N^2.
        """
        n = self.num_modes
        U_rec = self.reconstruct_unitary()
        tr = np.trace(np.dot(target_unitary.conj().T, U_rec))
        fidelity = float((abs(tr) ** 2) / (n ** 2))
        return min(1.0, max(0.0, fidelity))
