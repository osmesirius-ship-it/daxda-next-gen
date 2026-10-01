"""
Unit & Integration Tests for Level 2 5D Riemannian Temporal Manifold & Harmonizer
================================================================================
Comprehensive test suite verifying:
- 5D metric tensor, inverse, Christoffel symbols, Riemann/Ricci curvature
- Causal cone boundaries (timelike future/past, null, spacelike)
- Geodesic interpolation
- Multi-branch quantum causal loop harmonization (up to 64 branches)
- Dynamic branch collapsing and probability weight renormalization
- Retrocausal perturbation resilience (zero grandfather paradox states)
- 5D Causal graph, CTC cycle detection, and high-throughput batch evaluation
- Chrono 5D unified integration bridge and validation certificates
"""

import math
import pytest
from daxda_engine.level2.chrono_5d import (
    BranchCollapsingReport,
    CausalConeType,
    CausalEdge5D,
    CausalGraph5D,
    CausalHorizonBoundary,
    CausalNode5D,
    Chrono5DUnifiedBridge,
    HarmonizationResult,
    QuantumCausalLoopHarmonizer,
    RetrocausalPerturbationReceipt,
    RiemannianTemporalSpace5D,
    State5D,
    TemporalCoordinate5D,
    TimelineBranch,
    TrajectoryValidationCertificate5D,
)


# ============================================================================
# Section 1: 5D Coordinates and Metric Space
# ============================================================================

def test_temporal_coordinate_5d_representation():
    coord = TemporalCoordinate5D(t=10.5, b=0.25, p=0.1, tau=9.8, omega=0.05)
    tup = coord.to_tuple()
    lst = coord.to_list()
    assert len(tup) == 5
    assert tup == (10.5, 0.25, 0.1, 9.8, 0.05)
    assert lst == [10.5, 0.25, 0.1, 9.8, 0.05]

    restored = TemporalCoordinate5D.from_list(lst)
    assert restored.t == coord.t
    assert restored.omega == coord.omega


def test_riemannian_metric_tensor_values_and_signature():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=1.0, b=0.5, p=0.3, tau=1.0, omega=0.4)
    g = space.compute_metric_tensor(coord)

    assert len(g) == 5
    assert len(g[0]) == 5
    # Signature: (+, -, -, -, -)
    assert g[0][0] == 1.0
    assert g[1][1] == -(0.5 ** 2)
    assert g[2][2] == -(0.3 ** 2)
    assert g[3][3] == -1.0
    assert g[4][4] == -(0.4 ** 2)


def test_metric_tensor_symmetry():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=2.0, b=0.6, p=0.4, tau=1.5, omega=0.7)
    g = space.compute_metric_tensor(coord)

    for i in range(5):
        for j in range(5):
            assert g[i][j] == g[j][i], f"Metric asymmetry at ({i}, {j})"


def test_inverse_metric_tensor():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=2.0, b=0.5, p=0.2, tau=1.0, omega=0.3)
    g = space.compute_metric_tensor(coord)
    inv_g = space.compute_inverse_metric(coord)

    # g * inv_g == Identity
    for i in range(5):
        for j in range(5):
            val = sum(g[i][k] * inv_g[k][j] for k in range(5))
            expected = 1.0 if i == j else 0.0
            assert abs(val - expected) < 1e-6


def test_metric_derivatives():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=1.0, b=0.5, p=0.2, tau=1.0, omega=0.4)
    dg = space.compute_metric_derivatives(coord, eps=1e-5)

    # d_b g_11 = d/db (-b^2) = -2b = -1.0
    # dg[rho][mu][nu] where rho=1 (b), mu=1, nu=1
    assert math.isclose(dg[1][1][1], -1.0, rel_tol=1e-3)
    # d_p g_22 = -2p = -0.4
    assert math.isclose(dg[2][2][2], -0.4, rel_tol=1e-3)
    # d_omega g_44 = -2*omega = -0.8
    assert math.isclose(dg[4][4][4], -0.8, rel_tol=1e-3)


# ============================================================================
# Section 2: Differential Geometry: Christoffel, Riemann, Ricci
# ============================================================================

def test_christoffel_symbols_torsion_free_symmetry():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=1.5, b=0.4, p=0.25, tau=1.1, omega=0.3)
    gamma = space.compute_christoffel_symbols(coord)

    assert len(gamma) == 5
    assert len(gamma[0]) == 5
    assert len(gamma[0][0]) == 5

    # Check torsion-free condition: Gamma^sigma_mu_nu == Gamma^sigma_nu_mu
    for sigma in range(5):
        for mu in range(5):
            for nu in range(5):
                assert abs(gamma[sigma][mu][nu] - gamma[sigma][nu][mu]) < 1e-4


def test_riemann_curvature_skew_symmetry():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=1.0, b=0.5, p=0.3, tau=1.0, omega=0.2)
    riemann = space.compute_riemann_curvature(coord)

    # Check skew-symmetry in last two indices: R^rho_sigma_mu_nu == -R^rho_sigma_nu_mu
    for rho in range(5):
        for sigma in range(5):
            for mu in range(5):
                for nu in range(5):
                    val1 = riemann[rho][sigma][mu][nu]
                    val2 = riemann[rho][sigma][nu][mu]
                    assert abs(val1 + val2) < 1e-3


def test_ricci_tensor_and_scalar():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=2.0, b=0.4, p=0.2, tau=1.8, omega=0.3)
    ricci = space.compute_ricci_tensor(coord)
    scalar = space.compute_ricci_scalar(coord)

    assert len(ricci) == 5
    assert len(ricci[0]) == 5
    assert isinstance(scalar, float)
    assert not math.isnan(scalar)


# ============================================================================
# Section 3: Geodesics and Causal Cone Classifications
# ============================================================================

def test_geodesic_interval_and_path_interpolation():
    space = RiemannianTemporalSpace5D()
    coord_a = TemporalCoordinate5D(t=0.0, b=0.1, p=0.0, tau=0.0, omega=0.1)
    coord_b = TemporalCoordinate5D(t=2.0, b=0.1, p=0.0, tau=0.0, omega=0.1)

    ds_sq = space.compute_geodesic_interval_squared(coord_a, coord_b)
    assert math.isclose(ds_sq, 4.0, abs_tol=1e-3)

    path = space.compute_geodesic_path(coord_a, coord_b, steps=5)
    assert len(path) == 6
    assert path[0].t == 0.0
    assert path[-1].t == 2.0
    assert path[3].t == 1.2


def test_causal_cone_timelike_future():
    space = RiemannianTemporalSpace5D()
    c1 = TemporalCoordinate5D(t=1.0, b=0.1, p=0.0, tau=1.0, omega=0.1)
    c2 = TemporalCoordinate5D(t=3.0, b=0.1, p=0.0, tau=1.0, omega=0.1)

    boundary = space.classify_causal_relation(c1, c2)
    assert boundary.is_within_causal_cone is True
    assert boundary.cone_type == CausalConeType.TIMELIKE_FUTURE
    assert boundary.proper_interval_squared > 0.0
    assert boundary.dt > 0.0


def test_causal_cone_timelike_past():
    space = RiemannianTemporalSpace5D()
    c1 = TemporalCoordinate5D(t=3.0, b=0.1, p=0.0, tau=2.0, omega=0.1)
    c2 = TemporalCoordinate5D(t=1.0, b=0.1, p=0.0, tau=1.0, omega=0.1)

    boundary = space.classify_causal_relation(c1, c2)
    assert boundary.is_within_causal_cone is True
    assert boundary.cone_type == CausalConeType.TIMELIKE_PAST
    assert boundary.dt < 0.0


def test_causal_cone_null_boundary():
    space = RiemannianTemporalSpace5D()
    # Setting dt and dtau equal with other deltas zero: ds^2 = dt^2 - dtau^2 = 0
    c1 = TemporalCoordinate5D(t=0.0, b=0.0, p=0.0, tau=0.0, omega=0.0)
    c2 = TemporalCoordinate5D(t=1.0, b=0.0, p=0.0, tau=1.0, omega=0.0)

    boundary = space.classify_causal_relation(c1, c2, tol=1e-3)
    assert boundary.cone_type == CausalConeType.LIGHTLIKE_NULL
    assert boundary.is_within_causal_cone is True


def test_causal_cone_spacelike_acausal():
    space = RiemannianTemporalSpace5D()
    # Large dtau relative to dt: ds^2 = 0.1^2 - 5.0^2 < 0
    c1 = TemporalCoordinate5D(t=1.0, b=0.1, p=0.0, tau=0.0, omega=0.1)
    c2 = TemporalCoordinate5D(t=1.1, b=0.1, p=0.0, tau=5.0, omega=0.1)

    boundary = space.classify_causal_relation(c1, c2)
    assert boundary.cone_type == CausalConeType.SPACELIKE
    assert boundary.is_within_causal_cone is False
    assert boundary.proper_interval_squared < 0.0


# ============================================================================
# Section 4: Quantum Causal Loop Harmonizer & Fixed-Point Solver
# ============================================================================

def test_quantum_causal_loop_harmonizer_16_branches():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=5.0, b=0.2, p=0.15, tau=4.5, omega=0.08)
    vec = [0.05] * 20
    s_id = space.create_state(coord, vec, state_id="loop_node_16")

    harmonizer = QuantumCausalLoopHarmonizer(space=space)
    res = harmonizer.harmonize_loop("loop_node_16", max_branches=16)

    assert res.target_state_id == "loop_node_16"
    assert res.is_novikov_consistent is True
    assert res.converged_branches_count == 16
    assert res.total_branches_evaluated == 16
    assert res.geodesic_distance > 0.0
    assert res.iterations_run <= 50
    assert res.coherence_factor > 0.80
    assert len(res.fixed_point_vector) == 20


def test_quantum_causal_loop_harmonizer_64_branches():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=4.0, b=0.3, p=0.10, tau=3.5, omega=0.12)
    vec = [0.08] * 16
    s_id = space.create_state(coord, vec, state_id="loop_node_64")

    harmonizer = QuantumCausalLoopHarmonizer(space=space)
    res = harmonizer.harmonize_loop("loop_node_64", max_branches=64)

    assert res.is_novikov_consistent is True
    assert res.converged_branches_count == 64
    assert res.total_branches_evaluated == 64
    assert res.residual_norm < 1e-5


def test_quantum_causal_loop_branch_collapsing_and_pruning():
    space = RiemannianTemporalSpace5D()
    # High base paradox phase p=0.75, some generated branches will exceed 0.80
    coord = TemporalCoordinate5D(t=2.0, b=0.4, p=0.75, tau=1.5, omega=0.2)
    vec = [0.1] * 10
    s_id = space.create_state(coord, vec, state_id="near_critical_state")

    harmonizer = QuantumCausalLoopHarmonizer(space=space, paradox_threshold=0.80)
    res = harmonizer.harmonize_loop("near_critical_state", max_branches=32)

    # Some branches should be pruned
    assert res.collapsing_report.surviving_branch_count <= 32
    if len(res.collapsing_report.pruned_branch_ids) > 0:
        assert len(res.collapsing_report.prune_reasons) > 0
        # Renormalized weights must sum to approximately 1.0
        total_w = sum(res.collapsing_report.renormalized_weights.values())
        assert abs(total_w - 1.0) < 1e-3


def test_quantum_causal_loop_catastrophic_paradox_divergence():
    space = RiemannianTemporalSpace5D()
    # Extreme paradox phase angle p = 1.80 (far above threshold 0.80)
    coord = TemporalCoordinate5D(t=5.0, b=0.9, p=1.80, tau=4.5, omega=0.5)
    vec = [0.5] * 16
    s_id = space.create_state(coord, vec, state_id="paradox_catastrophe")

    harmonizer = QuantumCausalLoopHarmonizer(space=space, paradox_threshold=0.80)
    res = harmonizer.harmonize_loop("paradox_catastrophe")

    assert res.is_novikov_consistent is False
    assert res.converged_branches_count == 0
    assert res.coherence_factor < 0.50


def test_retrocausal_invariant_verification_zero_grandfather_paradox():
    space = RiemannianTemporalSpace5D()
    coord = TemporalCoordinate5D(t=3.0, b=0.25, p=0.08, tau=2.8, omega=0.15)
    vec = [0.05] * 16
    s_id = space.create_state(coord, vec, state_id="retrocausal_target")

    harmonizer = QuantumCausalLoopHarmonizer(space=space)
    pert = [0.1 * math.sin(k) for k in range(16)]

    receipt = harmonizer.verify_retrocausal_invariant(
        target_state_id=s_id,
        perturbation=pert,
        delta_tau=-0.5,
    )

    assert isinstance(receipt, RetrocausalPerturbationReceipt)
    assert receipt.target_state_id == "retrocausal_target"
    assert receipt.delta_tau == -0.5
    assert receipt.grandfather_paradox_detected is False
    assert receipt.novikov_restabilized is True


# ============================================================================
# Section 5: 5D Causal Graph and CTC Loop Detection
# ============================================================================

def test_causal_graph_node_and_edge_management():
    graph = CausalGraph5D()
    c1 = TemporalCoordinate5D(t=1.0, b=0.2, p=0.05, tau=0.9, omega=0.1)
    c2 = TemporalCoordinate5D(t=2.0, b=0.2, p=0.05, tau=1.5, omega=0.1)

    n1 = graph.add_node("node_01", c1)
    n2 = graph.add_node("node_02", c2)
    edge = graph.add_edge("node_01", "node_02")

    assert len(graph.nodes) == 2
    assert edge is not None
    assert edge.source_id == "node_01"
    assert edge.target_id == "node_02"
    assert edge.cone_type == CausalConeType.TIMELIKE_FUTURE


def test_causal_graph_batch_evaluation_throughput():
    graph = CausalGraph5D()
    for i in range(100):
        c = TemporalCoordinate5D(t=float(i) * 0.1, b=0.2, p=0.05, tau=float(i) * 0.09, omega=0.1)
        graph.add_node(f"n_{i}", c)

    pairs = [(f"n_{i}", f"n_{i+1}") for i in range(99)]
    boundaries = graph.batch_check_causal_relations(pairs)

    assert len(boundaries) == 99
    for b in boundaries:
        assert b.is_within_causal_cone is True


def test_causal_graph_ctc_cycle_detection_and_harmonization():
    graph = CausalGraph5D()
    c = TemporalCoordinate5D(t=1.0, b=0.2, p=0.05, tau=1.0, omega=0.1)
    graph.add_node("ctc_0", c)
    graph.add_node("ctc_1", c)
    graph.add_node("ctc_2", c)

    # Form a directed cycle: 0 -> 1 -> 2 -> 0
    graph.add_edge("ctc_0", "ctc_1", verify_geometry=False)
    graph.add_edge("ctc_1", "ctc_2", verify_geometry=False)
    graph.add_edge("ctc_2", "ctc_0", verify_geometry=False)

    ctcs = graph.detect_closed_timelike_curves(max_depth=4)
    assert len(ctcs) >= 1

    report = graph.harmonize_causal_graph()
    assert report["ctc_loops_detected"] >= 1
    assert report["harmonized_loops"] >= 1
    assert report["all_novikov_consistent"] is True


def test_synthetic_graph_generation():
    graph = CausalGraph5D.generate_synthetic_graph(node_count=200, seed=123)
    assert len(graph.nodes) == 200
    assert sum(len(e) for e in graph.edges.values()) > 200


# ============================================================================
# Section 6: Chrono 5D Unified Bridge
# ============================================================================

def test_chrono_5d_unified_bridge_lifting_and_validation():
    bridge = Chrono5DUnifiedBridge()

    # Lift 4D coordinate
    c5d = bridge.upgrade_4d_coordinate(t=10.0, b=0.4, p=0.05, tau=9.5, omega=0.25)
    assert c5d.t == 10.0
    assert c5d.omega == 0.25

    # Build sequence
    seq = [
        TemporalCoordinate5D(t=float(i), b=0.2, p=0.02, tau=float(i) * 0.98, omega=0.1)
        for i in range(5)
    ]
    cert = bridge.validate_trajectory(trajectory_id="traj_alpha_01", coordinates=seq)

    assert isinstance(cert, TrajectoryValidationCertificate5D)
    assert cert.trajectory_id == "traj_alpha_01"
    assert cert.is_valid is True
    assert cert.disposition == "APPROVED_5D_NOVIKOV_CONSISTENT"
    assert cert.total_steps == 5
    assert cert.timelike_steps == 4
    assert cert.spacelike_deviations == 0
    assert len(cert.audit_hash) == 64
