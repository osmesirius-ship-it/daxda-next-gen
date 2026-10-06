"""
Tests for DAXDA Level 3: Multiversal Consensus Engine (Sub-Bounty 5.4)
=====================================================================
Validates Generalized Nash Bargaining Solution (NBS), Pareto frontier,
Byzantine-robust Huber-Weiszfeld geometric median, (epsilon, delta)-DP,
and tamper-evident cryptographic consensus receipts.
"""

import numpy as np
import pytest

from daxda_engine.level3.multiversal_consensus import (
    NashBargainingSolver,
    WeiszfeldGeometricMedian,
    CardinalWelfareOptimizer,
    DifferentialPrivacyAggregator,
    ConsensusReceipt,
    MultiversalConsensusManager,
)


class TestNashBargainingSolver:
    """Tests Generalized Nash Bargaining Solution and Pareto efficiency."""

    def test_nash_objective_and_threat_point_boundary(self):
        # 3 agents
        threat_point = np.array([1.0, 1.0, 1.0])
        weights = np.array([1/3, 1/3, 1/3])

        # Valid utility above threat point
        valid_u = np.array([3.0, 2.0, 5.0])
        obj = NashBargainingSolver.compute_nash_objective(valid_u, threat_point, weights)
        # sum 1/3 * (ln(2) + ln(1) + ln(4)) = 1/3 * (ln(8))
        assert pytest.approx(obj, abs=1e-10) == np.log(8.0) / 3.0

        # Invalid utility violating threat point
        invalid_u = np.array([0.5, 2.0, 5.0])
        obj_inv = NashBargainingSolver.compute_nash_objective(invalid_u, threat_point, weights)
        assert obj_inv == -float("inf")

    def test_solve_discrete_candidates(self):
        # 3 candidates, 2 agents
        # Threat point: [0.0, 0.0]
        # Candidate 0: [2.0, 8.0] -> product (2)*(8) = 16
        # Candidate 1: [5.0, 5.0] -> product (5)*(5) = 25 (Nash winner)
        # Candidate 2: [8.0, 2.0] -> product (8)*(2) = 16
        candidates = np.array([
            [2.0, 8.0],
            [5.0, 5.0],
            [8.0, 2.0],
        ])
        threat = np.array([0.0, 0.0])
        
        best_k, best_u, obj = NashBargainingSolver.solve_discrete(candidates, threat)
        assert best_k == 1
        assert np.allclose(best_u, [5.0, 5.0])
        assert pytest.approx(obj, abs=1e-10) == np.log(5.0)

    def test_asymmetric_bargaining_weights(self):
        # With unequal weights: alpha = [0.8, 0.2] favoring Agent 0
        candidates = np.array([
            [2.0, 8.0],
            [5.0, 5.0],
            [8.0, 2.0],
        ])
        threat = np.array([0.0, 0.0])
        weights = np.array([0.8, 0.2])

        best_k, best_u, obj = NashBargainingSolver.solve_discrete(candidates, threat, weights=weights)
        # Candidate 2 gives 8.0 to Agent 0, 0.8 * ln(8) + 0.2 * ln(2) = 1.6635 + 0.1386 = 1.802 > 1.609
        assert best_k == 2
        assert np.allclose(best_u, [8.0, 2.0])

    def test_pareto_efficiency_and_frontier(self):
        candidates = np.array([
            [1.0, 1.0],  # Dominated by Candidate 1
            [3.0, 3.0],  # Pareto frontier
            [4.0, 2.0],  # Pareto frontier
            [2.0, 4.0],  # Pareto frontier
        ])
        
        assert not NashBargainingSolver.is_pareto_efficient(candidates, selected_idx=0)
        assert NashBargainingSolver.is_pareto_efficient(candidates, selected_idx=1)
        assert NashBargainingSolver.is_pareto_efficient(candidates, selected_idx=2)

        frontier = NashBargainingSolver.extract_pareto_frontier(candidates)
        assert set(frontier) == {1, 2, 3}


class TestWeiszfeldGeometricMedian:
    """Tests high-dimensional geometric median and Byzantine outlier isolation."""

    def test_symmetric_geometric_median(self):
        # 4 vertices of a square centered at (0, 0)
        points = np.array([
            [1.0, 1.0],
            [1.0, -1.0],
            [-1.0, 1.0],
            [-1.0, -1.0],
        ])
        med = WeiszfeldGeometricMedian.compute_median(points)
        assert np.allclose(med, [0.0, 0.0], atol=1e-6)

    def test_byzantine_breakdown_resilience(self):
        # 10 honest agents clustered near (5.0, 5.0)
        rng = np.random.default_rng(42)
        honest = rng.normal(loc=5.0, scale=0.1, size=(10, 2))
        
        # 2 Byzantine adversarial agents (20% < 33%) sending extreme values at (1000.0, -500.0)
        byzantine = np.array([
            [1000.0, -500.0],
            [1000.0, -500.0],
        ])
        all_agents = np.vstack([honest, byzantine])

        med = WeiszfeldGeometricMedian.compute_median(all_agents)
        # Geometric median remains closely anchored around honest cluster (5.0, 5.0)
        assert np.allclose(med, [5.0, 5.0], atol=0.5)

        # Standard mean would be severely shifted: mean > 150
        arithmetic_mean = np.mean(all_agents, axis=0)
        assert arithmetic_mean[0] > 150.0

    def test_detect_byzantine_outliers(self):
        honest = np.full((12, 3), 2.0) + np.random.default_rng(0).normal(0, 0.05, (12, 3))
        # Add 2 extreme sybils
        sybils = np.array([
            [50.0, 50.0, 50.0],
            [-40.0, 80.0, -20.0],
        ])
        points = np.vstack([honest, sybils])

        outliers = WeiszfeldGeometricMedian.detect_byzantine_outliers(points)
        assert set(outliers) == {12, 13}


class TestCardinalWelfareOptimizer:
    """Tests cardinal welfare function with variance consensus penalizer."""

    def test_polarization_penalty(self):
        # Configuration A: High consensus (low variance), mean = 5.0
        conf_consensus = np.array([
            [5.0, 5.0],
            [5.1, 4.9],
            [4.9, 5.1],
        ])

        # Configuration B: High polarization (high variance), mean = 5.0
        conf_polarized = np.array([
            [1.0, 1.0],
            [9.0, 9.0],
            [5.0, 5.0],
        ])

        w_cons = CardinalWelfareOptimizer.evaluate_social_welfare(conf_consensus, lambda_reg=0.1)
        w_pol = CardinalWelfareOptimizer.evaluate_social_welfare(conf_polarized, lambda_reg=0.1)

        # Consensus configuration must yield higher regularized social welfare
        assert w_cons > w_pol


class TestDifferentialPrivacyAndConsensusReceipt:
    """Tests DP Gaussian mechanism, noise calibration, and tamper-evident receipts."""

    def test_l2_clip_norms(self):
        vecs = np.array([
            [3.0, 4.0],  # norm is 5.0
            [0.3, 0.4],  # norm is 0.5
        ])
        clipped = DifferentialPrivacyAggregator.clip_l2_norms(vecs, max_norm=2.0)
        
        # First vector clipped to norm 2.0
        assert pytest.approx(np.linalg.norm(clipped[0]), abs=1e-10) == 2.0
        # Second vector unchanged
        assert pytest.approx(np.linalg.norm(clipped[1]), abs=1e-10) == 0.5

    def test_gaussian_sigma_scaling(self):
        sigma1 = DifferentialPrivacyAggregator.compute_gaussian_sigma(epsilon=1.0, delta=1e-5, sensitivity=1.0)
        sigma2 = DifferentialPrivacyAggregator.compute_gaussian_sigma(epsilon=0.5, delta=1e-5, sensitivity=1.0)
        # Halving epsilon doubles required noise standard deviation
        assert pytest.approx(sigma2 / sigma1, abs=1e-6) == 2.0

    def test_end_to_end_consensus_manager_and_receipt_verification(self):
        manager = MultiversalConsensusManager(secret_key=b"test-secret-key-12345")
        
        # 5 candidates, 10 agents
        rng = np.random.default_rng(123)
        candidates = rng.uniform(2.0, 8.0, size=(5, 10))
        # Inject one Byzantine agent sending bad utilities
        candidates[:, 9] = 100.0
        threat = np.full(10, 1.0)

        receipt, dp_consensus = manager.reach_consensus(
            candidate_utilities=candidates,
            threat_point=threat,
            epsilon=1.0,
            delta=1e-5,
            seed=42,
        )

        assert isinstance(receipt, ConsensusReceipt)
        assert receipt.byzantine_filtered_count == 1
        assert receipt.total_agents == 10
        assert len(receipt.consensus_vector) == 9  # 9 remaining active agents

        # Verify signature with correct key
        assert receipt.verify_signature(secret_key=b"test-secret-key-12345")

        # Verify signature fails with wrong key
        assert not receipt.verify_signature(secret_key=b"wrong-key")

        # Tampering with any value invalidates signature
        receipt.selected_candidate_idx = 999
        assert not receipt.verify_signature(secret_key=b"test-secret-key-12345")
