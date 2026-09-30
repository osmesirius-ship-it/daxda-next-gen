"""
Unit & Integration Tests for Level 2 5D Riemannian Temporal Manifold & Harmonizer
================================================================================
"""

import math
import pytest
from daxda_engine.level2.chrono_5d import (
    HarmonizationResult,
    QuantumCausalLoopHarmonizer,
    RiemannianTemporalSpace5D,
    State5D,
    TemporalCoordinate5D,
)


def test_temporal_coordinate_5d_representation():
    coord = TemporalCoordinate5D(t=10.5, b=0.25, p=0.1, tau=9.8, omega=0.05)
    tup = coord.to_tuple()
    assert len(tup) == 5
    assert tup == (10.5, 0.25, 0.1, 9.8, 0.05)


def test_riemannian_metric_tensor_and_geodesic_interval():
    space = RiemannianTemporalSpace5D()
    coord_a = TemporalCoordinate5D(t=0.0, b=0.1, p=0.0, tau=0.0, omega=0.1)
    coord_b = TemporalCoordinate5D(t=2.0, b=0.1, p=0.0, tau=0.0, omega=0.1)

    metric = space.compute_metric_tensor(coord_a)
    assert len(metric) == 5
    assert len(metric[0]) == 5
    # Signature: (+, -, -, -, -)
    assert metric[0][0] == 1.0
    assert metric[1][1] < 0.0
    assert metric[2][2] < 0.0
    assert metric[3][3] == -1.0
    assert metric[4][4] < 0.0

    # Geodesic ds^2 between coord_a and coord_b with only dt=2.0
    ds_sq = space.compute_geodesic_interval_squared(coord_a, coord_b)
    # dt^2 * g[0][0] = 4.0 * 1.0 = 4.0
    assert math.isclose(ds_sq, 4.0, abs_tol=1e-3)


def test_state_creation_and_retrieval():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=1.0, b=0.5, p=0.2, tau=0.9, omega=0.3)
    vec = [0.1, 0.2, 0.3, 0.4]
    state_id = space.create_state(coord, vec, state_id="state_alpha")

    assert state_id == "state_alpha"
    assert "state_alpha" in space._states
    st = space._states["state_alpha"]
    assert st.coordinate.t == 1.0
    assert st.decision_vector == vec


def test_quantum_causal_loop_harmonizer_convergence():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=5.0, b=0.2, p=0.15, tau=4.5, omega=0.08)
    vec = [0.05] * 20
    s_id = space.create_state(coord, vec, state_id="loop_node_1")

    harmonizer = QuantumCausalLoopHarmonizer(space=space)
    res = harmonizer.harmonize_loop("loop_node_1", max_branches=32)

    assert res.target_state_id == "loop_node_1"
    assert res.is_novikov_consistent is True
    assert res.converged_branches_count == 32
    assert res.geodesic_distance > 0.0
    assert res.iterations_run >= 1
    assert res.coherence_factor > 0.80


def test_quantum_causal_loop_harmonizer_paradox_divergence():
    space = RiemannianTemporalSpace5D()
    # High paradox angle p = 0.95 (> 0.80 threshold)
    coord = TemporalCoordinate5D(t=5.0, b=0.9, p=0.95, tau=4.5, omega=0.5)
    vec = [0.5] * 20
    s_id = space.create_state(coord, vec, state_id="paradox_singularity")

    harmonizer = QuantumCausalLoopHarmonizer(space=space)
    res = harmonizer.harmonize_loop("paradox_singularity")

    assert res.is_novikov_consistent is False
    assert res.converged_branches_count == 0
    assert res.coherence_factor < 0.20
