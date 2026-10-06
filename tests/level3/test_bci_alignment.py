"""
Comprehensive Test Suite for Level 3 BCI Alignment Attestation
==============================================================
Verifies Affine-Invariant Riemannian Metric (AIRM) theorems, Fréchet mean convergence,
tangent space mappings, ERN / vigilance decoders, and hardware attestation receipts.
"""

import numpy as np
import pytest

from daxda_engine.level3.bci_alignment import (
    RiemannianEEGCovarianceEngine,
    airm_geodesic_distance,
    frechet_mean_spd,
    tangent_space_log_map,
    VigilanceDriftDetector,
    NeurometricAttestationIssuer,
)


@pytest.fixture
def rng():
    return np.random.default_rng(2026)


@pytest.fixture
def spd_pair(rng):
    """Generates two random Symmetric Positive Definite matrices of dimension n=8."""
    n = 8
    A = rng.normal(size=(n, n))
    B = rng.normal(size=(n, n))
    P1 = A @ A.T + 0.1 * np.eye(n)
    P2 = B @ B.T + 0.1 * np.eye(n)
    return P1, P2


def test_airm_identity_and_symmetry(spd_pair):
    """Theorem: delta_R(P, P) == 0 and delta_R(P1, P2) == delta_R(P2, P1)."""
    P1, P2 = spd_pair
    d_ident = airm_geodesic_distance(P1, P1)
    d_12 = airm_geodesic_distance(P1, P2)
    d_21 = airm_geodesic_distance(P2, P1)
    
    assert np.isclose(d_ident, 0.0, atol=1e-6)
    assert d_12 > 0.0
    assert np.isclose(d_12, d_21, atol=1e-10)


def test_airm_affine_congruence_invariance(spd_pair, rng):
    """Theorem: delta_R(A P1 A^T, A P2 A^T) == delta_R(P1, P2) for non-singular A."""
    P1, P2 = spd_pair
    n = P1.shape[0]
    # Invertible transformation matrix A
    A = rng.normal(size=(n, n))
    while abs(np.linalg.det(A)) < 1e-3:
        A = rng.normal(size=(n, n))
        
    P1_trans = A @ P1 @ A.T
    P2_trans = A @ P2 @ A.T
    
    d_orig = airm_geodesic_distance(P1, P2)
    d_trans = airm_geodesic_distance(P1_trans, P2_trans)
    
    assert np.isclose(d_orig, d_trans, atol=1e-6)


def test_airm_inversion_invariance(spd_pair):
    """Theorem: delta_R(P1^{-1}, P2^{-1}) == delta_R(P1, P2)."""
    P1, P2 = spd_pair
    P1_inv = np.linalg.inv(P1)
    P2_inv = np.linalg.inv(P2)
    
    d_orig = airm_geodesic_distance(P1, P2)
    d_inv = airm_geodesic_distance(P1_inv, P2_inv)
    
    assert np.isclose(d_orig, d_inv, atol=1e-6)


def test_frechet_mean_convergence(rng):
    """Verifies convergence of Riemannian Fréchet mean across K=10 SPD matrices."""
    n = 6
    K = 10
    matrices = []
    for _ in range(K):
        M = rng.normal(size=(n, n))
        matrices.append(M @ M.T + 0.2 * np.eye(n))
        
    G = frechet_mean_spd(matrices, max_iter=25)
    
    # Check that G is symmetric and strictly positive definite
    assert np.allclose(G, G.T, atol=1e-10)
    eigvals = np.linalg.eigvalsh(G)
    assert np.all(eigvals > 0.0)
    
    # Distance to each member must be finite
    for P in matrices:
        dist = airm_geodesic_distance(G, P)
        assert 0.0 < dist < 20.0


def test_tangent_space_log_map(spd_pair):
    """Verifies tangent space projection Log_base(P) yields a symmetric matrix."""
    P1, P2 = spd_pair
    tangent_v = tangent_space_log_map(P2, base=P1)
    assert np.allclose(tangent_v, tangent_v.T, atol=1e-8)


def test_eeg_covariance_engine_estimation(rng):
    """Verifies regularized covariance estimation for 32-channel epoch."""
    engine = RiemannianEEGCovarianceEngine(channels=32, sampling_rate_hz=250.0)
    epoch = rng.normal(size=(32, 500))
    cov = engine.estimate_covariance(epoch)
    
    assert cov.shape == (32, 32)
    assert np.allclose(cov, cov.T, atol=1e-10)
    eigvals = np.linalg.eigvalsh(cov)
    assert np.all(eigvals > 0.0)


def test_vigilance_detector_nominal_vs_drowsy(rng):
    """Verifies detection of high vigilance vs microsleep drowsiness."""
    n_ch = 8
    M = rng.normal(size=(n_ch, n_ch))
    baseline = M @ M.T + 0.2 * np.eye(n_ch)
    
    detector = VigilanceDriftDetector(baseline_mean=baseline, drowsiness_threshold=2.0)
    
    # 1. Alert epoch: strong beta power (20Hz oscillation)
    t = np.linspace(0, 2.0, 500)
    alert_epoch = np.zeros((n_ch, 500))
    for c in range(n_ch):
        alert_epoch[c] = 2.0 * np.sin(2 * np.pi * 20.0 * t) + 0.1 * rng.normal(size=500)
    assessment_alert = detector.assess_epoch(alert_epoch)
    assert assessment_alert.engagement_index > 0.5
    
    # 2. Drowsy epoch: strong theta power (5Hz oscillation)
    drowsy_epoch = np.zeros((n_ch, 500))
    for c in range(n_ch):
        drowsy_epoch[c] = 3.5 * np.sin(2 * np.pi * 5.0 * t) + 0.1 * rng.normal(size=500)
    assessment_drowsy = detector.assess_epoch(drowsy_epoch)
    assert assessment_drowsy.is_drowsy is True
    assert assessment_drowsy.is_operator_attested is False


def test_neurometric_attestation_issuer(rng):
    """Verifies cryptographic attestation receipt creation and signing."""
    n_ch = 4
    M = rng.normal(size=(n_ch, n_ch))
    baseline = M @ M.T + 0.1 * np.eye(n_ch)
    
    detector = VigilanceDriftDetector(baseline_mean=baseline)
    epoch = rng.normal(size=(n_ch, 500))
    assessment = detector.assess_epoch(epoch)
    
    issuer = NeurometricAttestationIssuer()
    receipt = issuer.issue_attestation(
        action_proposal_id="PROPOSAL-HIGH-PRIV-001",
        assessment=assessment,
        airm_distance=assessment.airm_drift_from_baseline,
    )
    
    assert receipt.receipt_id.startswith("urn:daxda:neurometric:")
    assert receipt.action_proposal_id == "PROPOSAL-HIGH-PRIV-001"
    assert len(receipt.signature_hex) == 64
    assert receipt.governance_verdict in ["ALLOW", "DENY"]
