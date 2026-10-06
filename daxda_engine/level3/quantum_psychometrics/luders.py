"""
Non-Commutative Observables & Lüders-von Neumann Measurement
============================================================
Hermitian observable algebras, Lüders state update rules,
and the Wang-Busemeyer Quantum Question (QQ) equality solver.
"""

from typing import List, Tuple
import numpy as np

from .state import QuantumDensityState


class HermitianObservable:
    """
    Represents a psychometric diagnostic observable A = A^dagger on H^d.
    Decomposes into orthogonal projectors A = sum a_i P_i.
    """

    def __init__(self, matrix: np.ndarray, name: str = "Observable"):
        self.matrix = np.asarray(matrix, dtype=np.complex128)
        self.name = name
        assert np.allclose(self.matrix, self.matrix.conj().T, atol=1e-10), "Observable must be Hermitian"
        
        # Spectral decomposition: A = sum a_i P_i
        vals, vecs = np.linalg.eigh(self.matrix)
        self.eigenvalues = np.real(vals)
        self.eigenvectors = vecs
        
        # Construct orthogonal 1D projectors P_i = |v_i><v_i|
        self.projectors: List[np.ndarray] = []
        d = self.matrix.shape[0]
        for col in range(d):
            v = vecs[:, col]
            P = np.outer(v, v.conj())
            self.projectors.append(P)

    @property
    def dim(self) -> int:
        return self.matrix.shape[0]

    def commutes_with(self, other: "HermitianObservable", tol: float = 1e-10) -> bool:
        """Checks if commutator [A, B] = AB - BA == 0."""
        comm = self.matrix @ other.matrix - other.matrix @ self.matrix
        return bool(np.linalg.norm(comm) < tol)

    def commutator(self, other: "HermitianObservable") -> np.ndarray:
        """Returns the Lie bracket commutator [A, B] = AB - BA."""
        return self.matrix @ other.matrix - other.matrix @ self.matrix

    @classmethod
    def from_pauli(cls, pauli_str: str) -> "HermitianObservable":
        """
        Constructs canonical 2x2 or 4x4 Pauli observables:
        e.g., 'X', 'Y', 'Z', 'Z_tensor_I', 'X_tensor_Z'
        """
        I2 = np.eye(2, dtype=np.complex128)
        sx = np.array([[0, 1], [1, 0]], dtype=np.complex128)
        sy = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
        sz = np.array([[1, 0], [0, -1]], dtype=np.complex128)
        paulis = {"I": I2, "X": sx, "Y": sy, "Z": sz}
        
        if pauli_str in paulis:
            return cls(paulis[pauli_str], name=pauli_str)
        elif "_tensor_" in pauli_str:
            p1, p2 = pauli_str.split("_tensor_")
            M = np.kron(paulis[p1], paulis[p2])
            return cls(M, name=pauli_str)
        else:
            raise ValueError(f"Unknown Pauli string: {pauli_str}")


class LudersMeasurementSimulator:
    """
    Executes projective quantum measurements according to the Lüders rule:
    rho_{A=i} = (P_i rho P_i) / Tr(P_i rho)
    """

    @staticmethod
    def measure_single(
        state: QuantumDensityState,
        observable: HermitianObservable,
        outcome_idx: int,
    ) -> Tuple[float, QuantumDensityState]:
        """
        Computes outcome probability P(i) = Tr(P_i rho) and post-measurement collapsed state.
        """
        P = observable.projectors[outcome_idx]
        rho = state.matrix
        prob = float(np.real(np.trace(P @ rho)))
        prob = max(prob, 0.0)
        
        if prob < 1e-15:
            # Undefined collapse for zero-probability event; return identity projection
            return 0.0, state
            
        collapsed_matrix = (P @ rho @ P) / prob
        return prob, QuantumDensityState(collapsed_matrix)

    @classmethod
    def compute_sequential_prob(
        cls,
        state: QuantumDensityState,
        first_obs: HermitianObservable,
        first_idx: int,
        second_obs: HermitianObservable,
        second_idx: int,
    ) -> float:
        """
        Computes joint sequential probability:
        P(A=i, B=j) = Tr(Q_j P_i rho P_i Q_j)
        """
        P = first_obs.projectors[first_idx]
        Q = second_obs.projectors[second_idx]
        rho = state.matrix
        
        # P_i @ rho @ P_i
        collapsed = P @ rho @ P
        # Tr(Q_j @ collapsed @ Q_j) = Tr(Q_j @ P_i @ rho @ P_i)
        joint_p = np.real(np.trace(Q @ collapsed @ Q))
        return float(np.clip(joint_p, 0.0, 1.0))


class WangBusemeyerQQSolver:
    """
    Solves and verifies the Quantum Question (QQ) equality:
    q = P(A=1, B=1) + P(A=0, B=0) - [P(B=1, A=1) + P(B=0, A=0)] == 0
    Ref: Wang, Z., & Busemeyer, J. R. (2013), PNAS.
    """

    @classmethod
    def verify_qq_equality(
        cls,
        state: QuantumDensityState,
        obs_A: HermitianObservable,
        obs_B: HermitianObservable,
    ) -> float:
        """
        Returns the empirical QQ equality difference:
        q_diff = P(A_0, B_0) + P(A_1, B_1) - P(B_0, A_0) - P(B_1, A_1)
        Under pure projective Lüders measurement, q_diff is identically 0.0.
        """
        sim = LudersMeasurementSimulator()
        # Binary projections (index 0 and index 1)
        p_A0_B0 = sim.compute_sequential_prob(state, obs_A, 0, obs_B, 0)
        p_A1_B1 = sim.compute_sequential_prob(state, obs_A, 1, obs_B, 1)
        p_B0_A0 = sim.compute_sequential_prob(state, obs_B, 0, obs_A, 0)
        p_B1_A1 = sim.compute_sequential_prob(state, obs_B, 1, obs_A, 1)
        
        q_diff = (p_A0_B0 + p_A1_B1) - (p_B0_A0 + p_B1_A1)
        return float(q_diff)
