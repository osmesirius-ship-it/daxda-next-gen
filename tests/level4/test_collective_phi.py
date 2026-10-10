"""
Tests for DAXDA Level 4 — Domain 5: Global Pan-Psychometric Alignment & Collective Phi
"""

import numpy as np
import pytest

from daxda_engine.level4.collective_phi import (
    CollectiveTransitionHypergraph,
    IntegratedInformationSolver,
    PanPsychometricNormativeSpace,
)


def test_collective_transition_hypergraph():
    hg = CollectiveTransitionHypergraph(num_agents=3)
    assert hg.state_space_dim == 8
    
    # Set coupling between agent 0 and 1
    hg.set_coupling(0, 1, 1.5)
    
    # Check probability matrix normalization
    row_sums = np.sum(hg.T, axis=1)
    assert np.allclose(row_sums, 1.0, atol=1e-6)
    
    # Stationary distribution
    pi = hg.get_stationary_distribution()
    assert len(pi) == 8
    assert np.isclose(np.sum(pi), 1.0, atol=1e-6)
    
    # Laplacian connectivity
    L, lambda_2 = hg.compute_graph_laplacian_connectivity()
    assert L.shape == (3, 3)
    assert lambda_2 >= 0.0


def test_integrated_information_mip_solver():
    hg = CollectiveTransitionHypergraph(num_agents=3)
    hg.set_coupling(0, 1, 2.0)
    hg.set_coupling(1, 2, 2.0)
    
    solver = IntegratedInformationSolver(critical_phi_threshold=0.35)
    res = solver.compute_phi(hg)
    
    assert res.phi >= 0.0
    assert res.total_partitions_evaluated == 3  # For N=3: (1,2), (2,1)
    assert len(res.mip_partition_1) + len(res.mip_partition_2) == 3
    assert res.latency_ms < 50.0  # Fast resolution


def test_pan_psychometric_normative_space_and_reciprocity():
    space = PanPsychometricNormativeSpace(dim=1000)
    
    # Test golden alignment projection
    score_aligned = space.evaluate_swarm_alignment(space.v_gold)
    assert pytest.approx(score_aligned, abs=1e-4) == 1.0
    
    # Test anti-aligned projection
    score_anti = space.evaluate_swarm_alignment(-space.v_gold)
    assert pytest.approx(score_anti, abs=1e-4) == -1.0
    
    # Wang-Busemeyer reciprocity test
    satisfied, err = space.check_wang_busemeyer_reciprocity(
        p_ay_by=0.40, p_an_bn=0.35, p_by_ay=0.40, p_bn_an=0.35
    )
    assert satisfied is True
    assert err == 0.0
    
    # Alignment certificate
    cert = space.generate_alignment_certificate("swarm_alpha", space.v_gold)
    assert cert.is_aligned is True
    assert cert.quarantine_recommended is False
    assert len(cert.state_merkle_root) == 64
