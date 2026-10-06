"""
Wigner-Yanase Skew Information & Quantum State Tomography (QST)
===============================================================
Information-theoretic non-classical uncertainty quantification
and density operator reconstruction from POVM frequency arrays.
"""

from typing import List, Optional, Tuple, Union
import numpy as np

from .state import QuantumDensityState


def _matrix_sqrt_hermitian(rho: np.ndarray, reg: float = 1e-14) -> np.ndarray:
    """Computes matrix square root sqrt(rho) of a positive semi-definite matrix."""
    vals, vecs = np.linalg.eigh(rho)
    vals_clamped = np.maximum(np.real(vals), reg)
    return vecs @ np.diag(np.sqrt(vals_clamped)) @ vecs.conj().T


class WignerYanaseSkewAnalyzer:
    """
    Computes the Wigner-Yanase skew information metric:
    I(rho, K) = -0.5 * Tr([sqrt(rho), K]^2) = Tr(rho K^2) - Tr(sqrt(rho) K sqrt(rho) K)
    
    Ref: Wigner, E. P., & Yanase, M. M. (1963), PNAS.
    Measures purely non-commutative quantum uncertainty / hidden cognitive coherence.
    """

    @staticmethod
    def compute_skew_information(rho_matrix: np.ndarray, K_matrix: np.ndarray) -> float:
        """
        Calculates I(rho, K). If rho commutes with K, skew information is identically 0.0.
        """
        rho = np.asarray(rho_matrix, dtype=np.complex128)
        K = np.asarray(K_matrix, dtype=np.complex128)
        assert np.allclose(K, K.conj().T, atol=1e-10), "Observable K must be Hermitian"
        
        sqrt_rho = _matrix_sqrt_hermitian(rho)
        # Term 1: Tr(rho @ K^2)
        term1 = np.trace(rho @ (K @ K))
        # Term 2: Tr(sqrt_rho @ K @ sqrt_rho @ K)
        term2 = np.trace(sqrt_rho @ K @ sqrt_rho @ K)
        
        skew_info = float(np.real(term1 - term2))
        return float(max(skew_info, 0.0))


class QuantumStateTomographyEngine:
    """
    Reconstructs an unknown d-dimensional density matrix rho_hat
    from expectation values over a complete operator basis.
    """

    def __init__(self, dim: int = 4):
        self.dim = dim
        self._build_operator_basis()

    def _build_operator_basis(self):
        """Constructs an orthonormal Hermitian basis for M_d(C) under Hilbert-Schmidt inner product."""
        d = self.dim
        self.basis_matrices: List[np.ndarray] = []
        
        # 1. Identity component
        self.basis_matrices.append(np.eye(d, dtype=np.complex128) / np.sqrt(d))
        
        # 2. Generalized Gell-Mann symmetric off-diagonal: (|j><k| + |k><j|) / sqrt(2)
        for j in range(d):
            for k in range(j + 1, d):
                M = np.zeros((d, d), dtype=np.complex128)
                M[j, k] = 1.0 / np.sqrt(2.0)
                M[k, j] = 1.0 / np.sqrt(2.0)
                self.basis_matrices.append(M)
                
        # 3. Generalized Gell-Mann anti-symmetric off-diagonal: -i(|j><k| - |k><j|) / sqrt(2)
        for j in range(d):
            for k in range(j + 1, d):
                M = np.zeros((d, d), dtype=np.complex128)
                M[j, k] = -1j / np.sqrt(2.0)
                M[k, j] = 1j / np.sqrt(2.0)
                self.basis_matrices.append(M)
                
        # 4. Generalized Gell-Mann diagonal generators
        for l in range(1, d):
            M = np.zeros((d, d), dtype=np.complex128)
            norm = np.sqrt(2.0 / (l * (l + 1)))
            for j in range(l):
                M[j, j] = 1.0 * norm
            M[l, l] = -l * norm
            self.basis_matrices.append(M / np.sqrt(2.0))

    def create_pure_state(self, amplitudes: List[Union[float, complex]]) -> QuantumDensityState:
        """Helper to create a pure state on H^d."""
        psi = np.asarray(amplitudes, dtype=np.complex128)
        norm = np.linalg.norm(psi)
        psi_norm = psi / max(norm, 1e-12)
        return QuantumDensityState(np.outer(psi_norm, psi_norm.conj()))

    def tomographic_reconstruction(self, true_state: QuantumDensityState) -> QuantumDensityState:
        """
        Reconstructs state rho_hat = sum_k <B_k> B_k where <B_k> = Tr(rho B_k).
        """
        rho_true = true_state.matrix
        d = self.dim
        rho_hat = np.zeros((d, d), dtype=np.complex128)
        
        for B in self.basis_matrices:
            expectation = np.trace(rho_true @ B)
            rho_hat += expectation * B
            
        return QuantumDensityState(rho_hat)
