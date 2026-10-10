"""
Tests for DAXDA Level 4 — Domain 2: 6D Calabi-Yau Chrono Metric & Novikov CTC Consistency
"""

import numpy as np
import pytest

from daxda_engine.level4.calabi_yau_chrono import (
    CalabiYau6DMetric,
    NovikovCTCSolver,
    SU3HolonomyGate,
)


def test_calabi_yau_metric_positive_definite():
    cy = CalabiYau6DMetric(r=1.0)
    x = np.array([0.1, 0.2, 0.0, 0.1, 0.3, 0.2])
    g = cy.metric_tensor(x)
    
    # 6x6 symmetric positive definite
    assert g.shape == (6, 6)
    assert np.allclose(g, g.T, atol=1e-10)
    eigenvalues = np.linalg.eigvalsh(g)
    assert np.all(eigenvalues > 0)


def test_calabi_yau_christoffel_symbols():
    cy = CalabiYau6DMetric(r=1.0)
    x = np.zeros(6)
    gamma = cy.christoffel_symbols(x)
    
    assert gamma.shape == (6, 6, 6)
    # Torsion-free Levi-Civita connection: Gamma^lambda_mu_nu = Gamma^lambda_nu_mu
    assert np.allclose(gamma, np.transpose(gamma, (0, 2, 1)), atol=1e-8)


def test_novikov_ctc_solver_convergence():
    solver = NovikovCTCSolver(max_iterations=50, tolerance=1e-6)
    x_init = np.array([1.0, -0.5, 0.2])
    
    res = solver.solve(x_init)
    assert res.converged is True
    assert res.residual_norm < 1e-6
    assert res.iteration_count > 0
    assert len(res.fixed_point) == 3


def test_su3_holonomy_gate_verification():
    gate = SU3HolonomyGate(tolerance=0.01)
    
    # Valid unitary SU(3) trace = 3.0 (angle 0)
    assert gate.verify_holonomy(1.0, 0.0) is True
    
    # Deficit beyond tolerance triggers quarantine
    assert gate.verify_holonomy(0.95, 0.1) is False
    assert len(gate.quarantine_events) == 1
