"""
DAXDA Next-Gen Symplectic Pauli Operator Representation (pauli.py)
==================================================================
Models the n-qubit Pauli group P_n with exact symplectic phase tracking:
P = i^phase * X(x_vec) * Z(z_vec), where phase in {0, 1, 2, 3}.
Evaluates symplectic inner products and exact commutation relations.
"""

from __future__ import annotations
from typing import List, Tuple, Union


class PauliOperator:
    """
    An n-qubit Pauli operator represented as binary vectors (x, z) of length n,
    and a global phase index in {0, 1, 2, 3} (representing 1, i, -1, -i).
    """

    __slots__ = ("num_qubits", "x", "z", "phase")

    def __init__(self, x_bits: int, z_bits: int, num_qubits: int, phase: int = 0):
        self.num_qubits = num_qubits
        mask = (1 << num_qubits) - 1
        self.x = x_bits & mask
        self.z = z_bits & mask
        self.phase = phase % 4

    @classmethod
    def from_string(cls, pauli_str: str) -> PauliOperator:
        """Construct from string representation, e.g. 'IXYZ'."""
        n = len(pauli_str)
        x = 0
        z = 0
        for i, char in enumerate(pauli_str):
            c = char.upper()
            if c == 'X':
                x |= (1 << i)
            elif c == 'Z':
                z |= (1 << i)
            elif c == 'Y':
                x |= (1 << i)
                z |= (1 << i)
            elif c == 'I':
                pass
            else:
                raise ValueError(f"Invalid Pauli character '{char}'")
        return cls(x, z, n, phase=0)

    def to_string(self) -> str:
        """Returns standard string representation, e.g. 'IXYZ'."""
        chars = []
        for i in range(self.num_qubits):
            has_x = bool(self.x & (1 << i))
            has_z = bool(self.z & (1 << i))
            if has_x and has_z:
                chars.append('Y')
            elif has_x:
                chars.append('X')
            elif has_z:
                chars.append('Z')
            else:
                chars.append('I')
        prefix = ["", "+i*", "-", "-i*"][self.phase]
        return prefix + "".join(chars)

    def symplectic_inner_product(self, other: PauliOperator) -> int:
        """
        Symplectic inner product: <P1, P2> = (x1 . z2 ^ z1 . x2) mod 2.
        Equals 0 iff P1 and P2 commute, 1 iff they anticommute.
        """
        if self.num_qubits != other.num_qubits:
            raise ValueError("Qubit count mismatch")
        c1 = (self.x & other.z).bit_count()
        c2 = (self.z & other.x).bit_count()
        return (c1 ^ c2) % 2

    def commutes_with(self, other: PauliOperator) -> bool:
        """True if [P1, P2] = 0."""
        return self.symplectic_inner_product(other) == 0

    def __mul__(self, other: PauliOperator) -> PauliOperator:
        """
        Exact multiplication of two Pauli operators in P_n:
        P1 * P2 = i^(phase1 + phase2) * X(x1) Z(z1) X(x2) Z(z2)
        Using Z(z1) X(x2) = (-1)^(z1 . x2) X(x2) Z(z1).
        """
        if self.num_qubits != other.num_qubits:
            raise ValueError("Qubit count mismatch")

        new_x = self.x ^ other.x
        new_z = self.z ^ other.z

        # Additional phase from commutation and Y = i X Z
        # For each qubit, compute phase of single-qubit multiplication
        phase_accum = self.phase + other.phase
        for i in range(self.num_qubits):
            x1 = bool(self.x & (1 << i))
            z1 = bool(self.z & (1 << i))
            x2 = bool(other.x & (1 << i))
            z2 = bool(other.z & (1 << i))

            if x1 and z1:  # Y
                if x2 and not z2:   # Y * X = -i Z
                    phase_accum += 3
                elif not x2 and z2: # Y * Z = i X
                    phase_accum += 1
            elif x1 and not z1: # X
                if x2 and z2:       # X * Y = i Z
                    phase_accum += 1
                elif not x2 and z2: # X * Z = -i Y
                    phase_accum += 3
            elif not x1 and z1: # Z
                if x2 and not z2:   # Z * X = i Y
                    phase_accum += 1
                elif x2 and z2:     # Z * Y = -i X
                    phase_accum += 3

        return PauliOperator(new_x, new_z, self.num_qubits, phase=phase_accum % 4)

    def weight(self) -> int:
        """Number of non-identity physical qubits."""
        return (self.x | self.z).bit_count()

    def __repr__(self) -> str:
        return self.to_string()
