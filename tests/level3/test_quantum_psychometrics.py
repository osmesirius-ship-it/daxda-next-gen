"""
Tests for DAXDA Level 3: Quantum Psychometrics Engine (Sub-Bounty 5.3)
=====================================================================
Validates complex density operator algebra, Lüders projection rules,
Wang-Busemeyer Quantum Question (QQ) equality, Wigner-Yanase skew info,
and Hilbert-Schmidt quantum state tomography.
"""

import math
import numpy as np
import pytest

from daxda_engine.level3.quantum_psychometrics import (
    QuantumDensityState,
    create_pure_state,
    create_maximally_mixed_state,
    HermitianObservable,
    LudersMeasurementSimulator,
    WangBusemeyerQQSolver,
    WignerYanaseSkewAnalyzer,
    QuantumStateTomographyEngine,
)


class TestQuantumDensityState:
    """Tests density matrix physicality, purity, and von Neumann entropy."""

    def test_pure_state_properties(self):
        # Qubit state |psi> = 1/sqrt(2) (|0> + |1>)
        psi = np.array([1.0, 1.0]) / np.sqrt(2.0)
        state = create_pure_state(psi)
        
        assert state.dim == 2
        assert state.is_pure()
        assert pytest.approx(state.purity(), abs=1e-10) == 1.0
        assert pytest.approx(state.von_neumann_entropy(), abs=1e-10) == 0.0
        assert pytest.approx(np.trace(state.matrix).real, abs=1e-10) == 1.0

    def test_maximally_mixed_state_properties(self):
        dim = 4
        state = create_maximally_mixed_state(dim)
        
        assert state.dim == dim
        assert not state.is_pure()
        # Purity for maximally mixed state in H^d is 1/d
        assert pytest.approx(state.purity(), abs=1e-10) == 1.0 / dim
        # Von Neumann entropy is ln(d)
        assert pytest.approx(state.von_neumann_entropy(), abs=1e-10) == math.log(dim)
        assert pytest.approx(np.trace(state.matrix).real, abs=1e-10) == 1.0

    def test_enforce_physicality_on_noisy_matrix(self):
        # Non-Hermitian and unnormalized noisy matrix
        noisy = np.array([
            [1.5 + 0.1j, 0.5 - 0.2j],
            [0.2 + 0.1j, 0.8]
        ], dtype=np.complex128)
        
        state = QuantumDensityState(noisy)
        # Should be Hermitian
        assert np.allclose(state.matrix, state.matrix.conj().T, atol=1e-10)
        # Trace must be 1.0
        assert pytest.approx(np.trace(state.matrix).real, abs=1e-10) == 1.0
        # Eigenvalues must be non-negative
        eigvals = np.linalg.eigvalsh(state.matrix)
        assert np.all(eigvals >= -1e-12)


class TestHermitianObservable:
    """Tests observable construction, commutators, and Pauli algebras."""

    def test_pauli_algebra_and_commutators(self):
        X = HermitianObservable.from_pauli("X")
        Y = HermitianObservable.from_pauli("Y")
        Z = HermitianObservable.from_pauli("Z")

        # Pauli matrices do not commute
        assert not X.commutes_with(Y)
        assert not Y.commutes_with(Z)
        assert not Z.commutes_with(X)

        # Lie bracket: [X, Y] = 2j * Z
        comm_XY = X.commutator(Y)
        expected = 2j * Z.matrix
        assert np.allclose(comm_XY, expected, atol=1e-10)

        # Observable commutes with itself
        assert X.commutes_with(X)
        assert np.allclose(X.commutator(X), np.zeros((2, 2)), atol=1e-10)

    def test_spectral_projector_completeness(self):
        # For any observable A = sum a_i P_i, sum P_i = I
        X = HermitianObservable.from_pauli("X")
        I_recon = sum(X.projectors)
        assert np.allclose(I_recon, np.eye(2), atol=1e-10)

        # Projectors are orthogonal: P_i P_j = delta_{ij} P_i
        P0, P1 = X.projectors[0], X.projectors[1]
        assert np.allclose(P0 @ P1, np.zeros((2, 2)), atol=1e-10)
        assert np.allclose(P0 @ P0, P0, atol=1e-10)

    def test_tensor_pauli_observable(self):
        # 4D observable (2 qubits)
        obs = HermitianObservable.from_pauli("X_tensor_Z")
        assert obs.dim == 4
        assert len(obs.projectors) == 4
        assert np.allclose(sum(obs.projectors), np.eye(4), atol=1e-10)


class TestLudersMeasurementAndQQEquality:
    """Tests Lüders-von Neumann measurement postulate and Wang-Busemeyer theorem."""

    def test_luders_state_collapse(self):
        # Start in pure superposition |0>
        psi = np.array([1.0, 0.0])
        state = create_pure_state(psi)
        
        # Measure in X basis (eigenvectors are (|0>+|1>)/sqrt(2) and (|0>-|1>)/sqrt(2))
        X = HermitianObservable.from_pauli("X")
        sim = LudersMeasurementSimulator()
        
        # Probabilities should be 0.5 and 0.5
        p0, post0 = sim.measure_single(state, X, 0)
        p1, post1 = sim.measure_single(state, X, 1)
        
        assert pytest.approx(p0, abs=1e-10) == 0.5
        assert pytest.approx(p1, abs=1e-10) == 0.5
        assert post0.is_pure()
        assert post1.is_pure()

    def test_wang_busemeyer_qq_equality(self):
        """
        Wang-Busemeyer theorem: For any quantum state rho and any two
        binary projective observables A and B, the QQ equality holds identically:
        q = [P(A_0, B_0) + P(A_1, B_1)] - [P(B_0, A_0) + P(B_1, A_1)] == 0.0
        even when [A, B] != 0 and order effects exist.
        """
        # Test across pure states and mixed states
        test_states = [
            create_pure_state(np.array([0.8, 0.6])),
            create_pure_state(np.array([1.0 / np.sqrt(2), 1j / np.sqrt(2)])),
            create_maximally_mixed_state(2),
            QuantumDensityState(np.array([[0.7, 0.2 - 0.1j], [0.2 + 0.1j, 0.3]])),
        ]

        # Use non-commuting observables A = Z, B = (Z + X)/sqrt(2)
        Z = HermitianObservable.from_pauli("Z")
        H_mat = (np.array([[1, 0], [0, -1]]) + np.array([[0, 1], [1, 0]])) / np.sqrt(2.0)
        B = HermitianObservable(H_mat, name="Hadamard-like")

        assert not Z.commutes_with(B)

        for s in test_states:
            q_val = WangBusemeyerQQSolver.verify_qq_equality(s, Z, B)
            assert pytest.approx(q_val, abs=1e-10) == 0.0


class TestWignerYanaseSkewInformation:
    """Tests information-theoretic skew information on cognitive observables."""

    def test_skew_information_non_negativity(self):
        rho = np.array([[0.8, 0.2j], [-0.2j, 0.2]], dtype=np.complex128)
        K = np.array([[1.0, 0.5], [0.5, -1.0]], dtype=np.complex128)

        skew = WignerYanaseSkewAnalyzer.compute_skew_information(rho, K)
        assert skew >= 0.0

    def test_skew_information_vanishes_when_commuting(self):
        # When [rho, K] = 0, skew information must be identically 0
        rho = np.diag([0.7, 0.3]).astype(np.complex128)
        K = np.diag([2.0, -1.0]).astype(np.complex128)

        skew = WignerYanaseSkewAnalyzer.compute_skew_information(rho, K)
        assert pytest.approx(skew, abs=1e-10) == 0.0

    def test_skew_information_positive_for_coherent_superposition(self):
        # Pure superposition state with non-commuting observable
        psi = np.array([1.0, 1.0]) / np.sqrt(2.0)
        rho = np.outer(psi, psi.conj())
        Z = HermitianObservable.from_pauli("Z").matrix

        skew = WignerYanaseSkewAnalyzer.compute_skew_information(rho, Z)
        # For |+> state and Z observable, skew information is positive
        assert skew > 0.4


class TestQuantumStateTomography:
    """Tests Hilbert-Schmidt operator basis and density matrix reconstruction."""

    def test_operator_basis_orthonormality_d2(self):
        engine = QuantumStateTomographyEngine(dim=2)
        basis = engine.basis_matrices
        assert len(basis) == 4

        # Verify Hilbert-Schmidt orthonormality: Tr(B_j^dagger B_k) = delta_{jk}
        for j in range(4):
            for k in range(4):
                prod = np.trace(basis[j].conj().T @ basis[k])
                expected = 1.0 if j == k else 0.0
                assert pytest.approx(prod.real, abs=1e-10) == expected
                assert pytest.approx(prod.imag, abs=1e-10) == 0.0

    def test_operator_basis_orthonormality_d4(self):
        engine = QuantumStateTomographyEngine(dim=4)
        basis = engine.basis_matrices
        assert len(basis) == 16

        for j in range(16):
            for k in range(16):
                prod = np.trace(basis[j].conj().T @ basis[k])
                expected = 1.0 if j == k else 0.0
                assert pytest.approx(prod.real, abs=1e-10) == expected

    def test_full_state_reconstruction_fidelity(self):
        engine = QuantumStateTomographyEngine(dim=2)
        
        # Test arbitrary mixed state
        true_matrix = np.array([
            [0.65, 0.2 - 0.15j],
            [0.2 + 0.15j, 0.35]
        ], dtype=np.complex128)
        true_state = QuantumDensityState(true_matrix)

        reconstructed_state = engine.tomographic_reconstruction(true_state)

        # Frobenius norm reconstruction error must be near zero
        diff = np.linalg.norm(true_state.matrix - reconstructed_state.matrix)
        assert pytest.approx(diff, abs=1e-10) == 0.0
        assert pytest.approx(reconstructed_state.purity(), abs=1e-10) == true_state.purity()
