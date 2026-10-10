"""
DAXDA Level 3 Unit Tests: Multi-Agent Quantum Temporal Consensus Engine
=======================================================================
Validates multi-partite GHZ entanglement, pseudo-telepathy 100% win rate,
classical Bell bound limits (<= 0.75), Novikov causal loop fixed-point
convergence across 64 branches, Tsirelson bound verification (2*sqrt(2)),
and Byzantine sybil isolation tripwires.
"""

import math
import pytest
import numpy as np

from daxda_engine.level3.quantum_temporal_consensus import (
    GHZStateRouter,
    MerminPseudoTelepathyEngine,
    MagicSquareGame,
    NovikovCausalLoopHarmonizer,
    TimelineBranch,
    NovikovFixedPointResult,
    ParadoxDivergenceTripwire,
    ByzantineEntanglementFilter,
    CHSHEvaluationResult,
    QuantumConsensusReceipt,
    QuantumTemporalConsensusEngine,
    TSIRELSON_BOUND,
    CLASSICAL_BELL_BOUND,
    MERMIN_QUANTUM_BOUND,
    MERMIN_CLASSICAL_BOUND,
)


def test_ghz_state_creation_and_properties():
    """Verify |GHZ_3> state normalization, dimension, and purity."""
    router = GHZStateRouter(num_qubits=3)
    psi = router.ideal_state_vector

    assert len(psi) == 8
    # Norm ||psi|| = 1.0
    norm = np.linalg.norm(psi)
    assert abs(norm - 1.0) < 1e-12

    # Verify |000> and |111> have 1/sqrt(2) amplitude
    assert abs(psi[0] - 1.0 / math.sqrt(2.0)) < 1e-12
    assert abs(psi[7] - 1.0 / math.sqrt(2.0)) < 1e-12
    assert abs(np.sum(np.abs(psi[1:7]))) < 1e-12

    # Density matrix purity
    rho = router.ideal_density_matrix
    assert rho.shape == (8, 8)
    purity = float(np.real(np.trace(rho @ rho)))
    assert abs(purity - 1.0) < 1e-12


def test_ghz_reduced_density_matrix_and_entropy():
    """Verify partial trace and von Neumann entanglement entropy S_E = ln(2) = 1 ebit."""
    router = GHZStateRouter(num_qubits=3)
    rho = router.ideal_density_matrix

    # Trace out qubits 1 and 2, keeping qubit 0
    rho_1 = router.partial_trace(rho, keep_qubits=[0])
    assert rho_1.shape == (2, 2)

    # Subsystem density matrix must be maximally mixed: diag(0.5, 0.5)
    expected_rho_1 = np.eye(2, dtype=np.complex128) * 0.5
    assert np.allclose(rho_1, expected_rho_1, atol=1e-12)

    # Natural log entropy: ln(2) ~= 0.693147
    s_nat = router.von_neumann_entropy(rho_1, base=math.e)
    assert abs(s_nat - math.log(2.0)) < 1e-12

    # Base-2 entropy: 1.0 ebit
    s_ebits = router.von_neumann_entropy(rho_1, base=2.0)
    assert abs(s_ebits - 1.0) < 1e-12


def test_ghz_decoherence_detection():
    """Verify that state depolarizing noise lowers purity and triggers decoherence alert."""
    router = GHZStateRouter(num_qubits=3)
    rho_ideal = router.ideal_density_matrix

    t_ideal = router.analyze_telemetry(rho_ideal)
    assert t_ideal.is_maximally_entangled is True
    assert t_ideal.is_decohered is False
    assert abs(t_ideal.fidelity_to_ideal - 1.0) < 1e-12

    # Apply 10% depolarizing noise
    rho_noisy = router.apply_depolarizing_noise(rho_ideal, p=0.10)
    t_noisy = router.analyze_telemetry(rho_noisy)

    assert t_noisy.purity < 0.99
    assert t_noisy.fidelity_to_ideal < 0.95
    assert t_noisy.is_decohered is True


def test_mermin_pseudo_telepathy_perfect_win_rate():
    """Verify that quantum strategy achieves 100% win rate across all Mermin game queries."""
    engine = MerminPseudoTelepathyEngine()

    # Execute 200 rounds per valid query
    suite_res = engine.benchmark_game_suite(rounds_per_query=200, seed=123)
    assert suite_res["total_rounds"] == 800
    assert suite_res["total_wins"] == 800
    assert suite_res["quantum_win_rate"] == 1.0
    assert suite_res["perfect_pseudo_telepathy"] is True


def test_mermin_classical_strategy_bound():
    """Verify that no classical deterministic strategy can exceed 75% winning probability."""
    engine = MerminPseudoTelepathyEngine()
    classical_eval = engine.evaluate_all_classical_strategies()

    assert classical_eval["total_strategies"] == 64
    assert classical_eval["max_classical_wins"] == 3
    assert classical_eval["max_classical_win_rate"] == 0.75
    assert classical_eval["classical_bound_verified"] is True


def test_magic_square_game():
    """Verify Mermin-Peres magic square game bounds and quantum intersection matching."""
    classical_bound = MagicSquareGame.evaluate_classical_bound()
    assert abs(classical_bound - 8.0 / 9.0) < 1e-12

    # Test all 9 combinations of (row, col)
    for r in range(3):
        for c in range(3):
            alice_out, bob_out, match = MagicSquareGame.execute_quantum_strategy(r, c)
            assert len(alice_out) == 3
            assert len(bob_out) == 3
            assert match is True, f"Mismatch at ({r}, {c})"


def test_novikov_fixed_point_convergence():
    """Verify that Picard iteration with Krasnoselskii-Mann damping converges to tolerance < 1e-8."""
    harmonizer = NovikovCausalLoopHarmonizer(
        num_branches=4,
        damping_alpha=0.5,
        tolerance=1e-8,
        max_iterations=50,
    )
    branch0 = harmonizer.branches[0]
    result: NovikovFixedPointResult = harmonizer.solve_branch_fixed_point(branch0)

    assert result.converged is True
    assert result.iterations <= 50
    assert result.final_frobenius_error < 1e-8
    assert result.is_positive_semidefinite is True
    assert result.trace_error < 1e-12
    assert abs(result.circulation_integral) < 1e-12

    # Check that fixed point rho* satisfies T(rho*) ~= rho*
    rho_star = result.fixed_point_density_matrix
    U = branch0.interaction_unitary(coupling_strength=0.35)
    rho_in = np.array([[0.8, 0.1], [0.1, 0.2]], dtype=np.complex128)
    rho_in = harmonizer.enforce_density_matrix_physicality(rho_in)
    t_rho = harmonizer.evaluate_ctc_transition_operator(rho_star, rho_in, U)

    diff = float(np.linalg.norm(t_rho - rho_star, ord="fro"))
    assert diff < 1e-7, f"Fixed point residual {diff} too large"


def test_novikov_64_branch_harmonization():
    """Verify that all 64 divergent timeline branches converge within the 50 iteration SLA."""
    harmonizer = NovikovCausalLoopHarmonizer(
        num_branches=64,
        damping_alpha=0.5,
        tolerance=1e-8,
        max_iterations=50,
    )
    results = harmonizer.harmonize_all_64_branches()

    assert len(results) == 64
    metrics = harmonizer.verify_global_multigraph_consistency(results)

    assert metrics["converged_branches"] == 64
    assert metrics["convergence_rate_pct"] == 100.0
    assert metrics["max_iterations_used"] <= 50
    assert metrics["max_frobenius_error"] < 1e-8
    assert metrics["all_positive_semidefinite"] is True
    assert metrics["sla_passed"] is True


def test_paradox_divergence_tripwire():
    """Verify that non-contractive loops or max iteration exhaustion trigger ParadoxDivergenceTripwire."""
    harmonizer = NovikovCausalLoopHarmonizer(
        num_branches=1,
        damping_alpha=0.5,
        tolerance=1e-15,  # Unattainably tight tolerance for 1 iteration
        max_iterations=1,
    )
    with pytest.raises(ParadoxDivergenceTripwire):
        harmonizer.solve_branch_fixed_point(harmonizer.branches[0])


def test_chsh_tsirelson_bound_verification():
    """Verify exact Bell-CHSH quantum correlation <B> = 2*sqrt(2)."""
    filter_engine = ByzantineEntanglementFilter()
    chsh_res: CHSHEvaluationResult = filter_engine.evaluate_ideal_chsh()

    assert abs(chsh_res.bell_parameter - TSIRELSON_BOUND) < 1e-14
    assert chsh_res.violates_classical_bound is True
    assert chsh_res.is_maximal_tsirelson is True
    assert chsh_res.residual_to_tsirelson < 1e-14
    assert chsh_res.bell_parameter > CLASSICAL_BELL_BOUND


def test_mermin_operator_expectation():
    """Verify 3-qubit Mermin operator expectation on |GHZ_3> equals 4.0."""
    router = GHZStateRouter(num_qubits=3)
    psi = router.ideal_state_vector

    filter_engine = ByzantineEntanglementFilter()
    m_exp = filter_engine.evaluate_mermin_operator_expectation(psi)

    assert abs(m_exp - MERMIN_QUANTUM_BOUND) < 1e-12
    assert m_exp > MERMIN_CLASSICAL_BOUND


def test_byzantine_sybil_isolation():
    """Verify that classical sybils (S <= 2.0) and super-quantum spoofers are isolated."""
    filter_engine = ByzantineEntanglementFilter(bell_threshold=2.4)

    # 1. Honest quantum agent reporting Tsirelson bound
    assert filter_engine.screen_agent_correlation("agent-quantum-0", TSIRELSON_BOUND) is True
    assert "agent-quantum-0" not in filter_engine.isolated_sybils

    # 2. Classical sybil reporting S = 1.95 <= 2.0
    assert filter_engine.screen_agent_correlation("agent-sybil-classical", 1.95) is False
    assert "agent-sybil-classical" in filter_engine.isolated_sybils

    # 3. Super-quantum spoofer reporting S = 3.2 > 2*sqrt(2)
    assert filter_engine.screen_agent_correlation("agent-sybil-superquantum", 3.20) is False
    assert "agent-sybil-superquantum" in filter_engine.isolated_sybils


def test_cryptographic_consensus_receipt_determinism():
    """Verify deterministic SHA-256 Merkle root and receipt generation."""
    filter_engine = ByzantineEntanglementFilter()
    receipt1 = filter_engine.generate_consensus_receipt(
        epoch=101,
        branch_omega=0.0,
        active_agents=["agent-1", "agent-2", "agent-3"],
        bell_param=TSIRELSON_BOUND,
        novikov_converged=True,
        novikov_error=5e-9,
    )

    receipt2 = filter_engine.generate_consensus_receipt(
        epoch=101,
        branch_omega=0.0,
        active_agents=["agent-1", "agent-2", "agent-3"],
        bell_param=TSIRELSON_BOUND,
        novikov_converged=True,
        novikov_error=5e-9,
    )

    assert receipt1.consensus_decision == "ACCEPT"
    assert receipt1.violates_bell_bound is True
    assert len(receipt1.merkle_state_root) == 64
    assert len(receipt1.receipt_hash) == 64

    # Determinism: identical inputs must yield identical hashes
    assert receipt1.merkle_state_root == receipt2.merkle_state_root
    assert receipt1.receipt_hash == receipt2.receipt_hash


def test_end_to_end_quantum_temporal_consensus_engine():
    """Verify full end-to-end multi-timeline consensus cycle across 64 branches."""
    engine = QuantumTemporalConsensusEngine(num_branches=64, num_agents=3)

    agents = ["node-alpha", "node-beta", "node-gamma"]
    sybils = {"node-fake-1": 1.85, "node-fake-2": 2.0}

    outcome = engine.run_temporal_consensus_cycle(
        epoch=1,
        agent_ids=agents,
        sybil_candidates=sybils,
        game_rounds=50,
        seed=42,
    )

    assert outcome.epoch == 1
    assert outcome.num_branches == 64
    assert outcome.all_branches_harmonized is True
    assert outcome.max_fixed_point_error < 1e-8
    assert outcome.pseudo_telepathy_win_rate == 1.0
    assert abs(outcome.bell_parameter - TSIRELSON_BOUND) < 1e-12
    assert outcome.classical_bound_violated is True
    assert outcome.active_agent_count == 3
    assert outcome.isolated_sybil_count == 2
    assert outcome.consensus_receipt.consensus_decision == "ACCEPT"
    assert len(outcome.branch_summaries) == 8
