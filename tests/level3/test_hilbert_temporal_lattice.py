"""
Tests for 5D Hilbert Temporal Lattice and Geodesic Engine.
Verifies Levi-Civita connection, Riemann curvature, geodesic integration,
parallel transport norm conservation, and holonomy phase shifts.
"""

import math
import numpy as np
import pytest

from daxda_engine.level3.hilbert_temporal_lattice import (
    TemporalManifold5D,
    GeodesicParallelTransportSolver,
    GeodesicTrajectory,
    ParallelTransportResult,
    HolonomyPhaseCalculator,
    HolonomyLoopResult,
    HilbertTemporalLattice,
    LatticeIntervalResult,
)


def test_flat_minkowski_christoffel_zero():
    """Verify that flat 5D Minkowski-Kaluza spacetime has zero Christoffel symbols and zero curvature."""
    manifold = TemporalManifold5D.flat_minkowski_5d()
    x = np.array([1.0, 2.0, -1.0, 0.5, 3.0])

    gamma = manifold.christoffel_symbols(x)
    assert np.allclose(gamma, 0.0, atol=1e-8)

    riemann = manifold.riemann_tensor(x)
    assert np.allclose(riemann, 0.0, atol=1e-7)

    ricci = manifold.ricci_tensor(x)
    assert np.allclose(ricci, 0.0, atol=1e-7)

    r_scalar = manifold.ricci_scalar(x)
    assert abs(r_scalar) < 1e-7


def test_curved_soliton_torsion_free_symmetry():
    r"""Verify that Levi-Civita connection is torsion-free: Gamma^\sigma_{\mu\nu} = Gamma^\sigma_{\nu\mu}."""
    manifold = TemporalManifold5D.curved_temporal_soliton(mass_parameter=0.2, frequency_omega=1.5)
    x = np.array([0.5, 1.0, 0.0, -0.5, 1.2])

    gamma = manifold.christoffel_symbols(x)
    
    # Check torsion-free condition: Gamma[sigma, mu, nu] == Gamma[sigma, nu, mu]
    for s in range(5):
        diff = np.max(np.abs(gamma[s] - gamma[s].T))
        assert diff < 1e-8, f"Torsion detected in component {s}: diff={diff}"

    # Verify that curvature is non-zero
    riemann = manifold.riemann_tensor(x)
    assert np.max(np.abs(riemann)) > 1e-4

    r_scalar = manifold.ricci_scalar(x)
    assert abs(r_scalar) > 1e-5


def test_geodesic_integration_norm_conservation():
    r"""Verify that geodesic integration conserves the velocity metric norm u^\mu g_{\mu\nu} u^\nu."""
    manifold = TemporalManifold5D.curved_temporal_soliton(mass_parameter=0.1, frequency_omega=1.0)
    solver = GeodesicParallelTransportSolver(manifold)

    x0 = np.array([0.0, 0.5, 0.0, 0.0, 0.0])
    u0 = np.array([1.0, 0.2, 0.1, 0.0, 0.05])

    traj: GeodesicTrajectory = solver.integrate_geodesic(
        initial_position=x0,
        initial_velocity=u0,
        lambda_max=0.5,
        num_steps=80,
    )

    assert traj.is_norm_conserved is True
    assert traj.norm_drift_max < 1e-4
    assert len(traj.coordinates) == 81


def test_parallel_transport_inner_product_conservation():
    r"""Verify that parallel transport of a vector along a trajectory conserves V^\mu g_{\mu\nu} V^\nu."""
    manifold = TemporalManifold5D.curved_temporal_soliton(mass_parameter=0.15)
    solver = GeodesicParallelTransportSolver(manifold)

    # Discretized path
    lambdas = np.linspace(0.0, 1.0, 50)
    coords = np.zeros((50, 5))
    coords[:, 0] = lambdas * 0.5
    coords[:, 1] = np.sin(lambdas * 2.0) * 0.3
    coords[:, 4] = lambdas * 0.2

    tangents = np.zeros((50, 5))
    tangents[:, 0] = 0.5
    tangents[:, 1] = 2.0 * np.cos(lambdas * 2.0) * 0.3
    tangents[:, 4] = 0.2

    v0 = np.array([0.0, 1.0, 0.0, 0.0, 0.0])

    res: ParallelTransportResult = solver.parallel_transport_along_path(
        path_coordinates=coords,
        path_tangents=tangents,
        initial_vector=v0,
        lambdas=lambdas,
    )

    assert res.is_inner_product_conserved is True
    assert res.inner_product_drift_max < 1e-4


def test_holonomy_trivial_in_flat_spacetime():
    """Verify that holonomy around any closed loop in flat spacetime is the identity matrix I_5."""
    manifold = TemporalManifold5D.flat_minkowski_5d()
    calculator = HolonomyPhaseCalculator(manifold)

    center = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    coords, tangents, s = calculator.generate_planar_circle_loop(center, radius=0.5, plane_indices=(1, 2))

    res: HolonomyLoopResult = calculator.compute_loop_holonomy(coords, tangents, s)

    assert res.is_trivial_holonomy is True
    assert abs(res.trace - 5.0) < 1e-4
    assert res.holonomy_phase_shift < 1e-5


def test_holonomy_phase_shift_in_curved_manifold():
    """Verify that holonomy around a closed loop in a curved manifold generates non-zero geometric phase."""
    manifold = TemporalManifold5D.curved_temporal_soliton(mass_parameter=0.3, frequency_omega=1.0)
    calculator = HolonomyPhaseCalculator(manifold)

    center = np.array([0.0, 0.2, 0.2, 0.0, 0.1])
    coords, tangents, s = calculator.generate_planar_circle_loop(center, radius=0.4, plane_indices=(1, 2), num_points=120)

    res: HolonomyLoopResult = calculator.compute_loop_holonomy(coords, tangents, s)

    # In curved space, holonomy phase shift is non-zero
    assert res.holonomy_phase_shift > 1e-5
    assert res.holonomy_matrix.shape == (5, 5)


def test_lattice_causal_interval_evaluation():
    """Verify timelike, spacelike, and null-like intervals in the 5D Hilbert lattice."""
    lattice = HilbertTemporalLattice()

    p0 = np.zeros(5)
    # Timelike displacement (large dt)
    p_time = np.array([2.0, 0.0, 0.0, 0.0, 0.0])
    res_time: LatticeIntervalResult = lattice.evaluate_interval(p0, p_time)
    assert res_time.is_timelike is True
    assert res_time.is_spacelike is False
    assert res_time.spacetime_interval_ds2 < 0.0

    # Spacelike displacement (large dx)
    p_space = np.array([0.0, 3.0, 0.0, 0.0, 0.0])
    res_space: LatticeIntervalResult = lattice.evaluate_interval(p0, p_space)
    assert res_space.is_spacelike is True
    assert res_space.is_timelike is False
    assert res_space.spacetime_interval_ds2 > 0.0

    # Null / lightlike displacement (dt = dx)
    p_null = np.array([1.0, 1.0, 0.0, 0.0, 0.0])
    res_null: LatticeIntervalResult = lattice.evaluate_interval(p0, p_null)
    assert abs(res_null.spacetime_interval_ds2) < 1e-12
    assert res_null.is_null_lightlike is True


def test_laplace_beltrami_and_wave_propagation():
    """Verify 1D temporal Laplace-Beltrami operator and wave propagation simulation."""
    lattice = HilbertTemporalLattice()

    # Gaussian initial wave packet
    x = np.linspace(-2.0, 2.0, 50)
    psi0 = np.exp(-x**2)

    lap = lattice.laplace_beltrami_1d_time(psi0)
    assert len(lap) == 50
    # At center (x=0), second derivative of exp(-x^2) is negative (-2)
    assert lap[25] < 0.0

    # Simulate wave evolution
    history = lattice.simulate_wave_propagation(psi0, num_steps=20, dt=0.01)
    assert history.shape == (21, 50)
    # Energy / wave should remain bounded
    assert np.all(np.isfinite(history))
