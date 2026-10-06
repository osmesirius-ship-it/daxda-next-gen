"""
Quantum Epistemic State & Density Operator Algebra
==================================================
Complex Hilbert space density matrices rho in S(H^d),
von Neumann entropy, purity, and spectral decompositions.
"""

from dataclasses import dataclass
from typing import Optional, Union
import numpy as np


@dataclass
class QuantumDensityState:
    """Represents a density operator rho on complex Hilbert space H^d."""
    matrix: np.ndarray

    def __post_init__(self):
        self.matrix = np.asarray(self.matrix, dtype=np.complex128)
        assert self.matrix.ndim == 2 and self.matrix.shape[0] == self.matrix.shape[1], "Must be square matrix"
        self._enforce_physicality()

    def _enforce_physicality(self, tol: float = 1e-12):
        """Enforces Hermiticity, unit trace, and positive semi-definiteness."""
        # 1. Hermiticity: rho = (rho + rho^dagger) / 2
        rho_h = (self.matrix + self.matrix.conj().T) * 0.5
        # 2. Positive eigenvalues: truncate negative eigenvalues
        vals, vecs = np.linalg.eigh(rho_h)
        vals_pos = np.maximum(vals, 0.0)
        tr = np.sum(vals_pos)
        if tr < tol:
            vals_pos = np.ones_like(vals_pos) / len(vals_pos)
        else:
            vals_pos /= tr
        self.matrix = vecs @ np.diag(vals_pos) @ vecs.conj().T

    @property
    def dim(self) -> int:
        return self.matrix.shape[0]

    def purity(self) -> float:
        """Purity gamma(rho) = Tr(rho^2) in [1/d, 1.0]."""
        rho_sq = self.matrix @ self.matrix
        return float(np.real(np.trace(rho_sq)))

    def von_neumann_entropy(self, base: float = np.e) -> float:
        """Von Neumann entropy S(rho) = -Tr(rho ln rho)."""
        vals = np.linalg.eigvalsh(self.matrix)
        vals = vals[vals > 1e-15]
        if len(vals) == 0:
            return 0.0
        entropy = -np.sum(vals * (np.log(vals) / np.log(base)))
        return float(max(entropy, 0.0))

    def is_pure(self, tol: float = 1e-6) -> bool:
        """True if state is a pure state (purity == 1.0)."""
        return abs(self.purity() - 1.0) < tol


def create_pure_state(psi: np.ndarray) -> QuantumDensityState:
    """Constructs pure density matrix rho = |psi><psi| from state vector psi."""
    psi = np.asarray(psi, dtype=np.complex128).flatten()
    norm = np.linalg.norm(psi)
    assert norm > 1e-12, "State vector cannot be zero"
    psi_norm = psi / norm
    rho = np.outer(psi_norm, psi_norm.conj())
    return QuantumDensityState(rho)


def create_maximally_mixed_state(dim: int) -> QuantumDensityState:
    """Constructs maximally mixed state rho = (1/d) * I_d with purity = 1/d."""
    assert dim >= 2, "Dimension must be at least 2"
    rho = np.eye(dim, dtype=np.complex128) / float(dim)
    return QuantumDensityState(rho)
