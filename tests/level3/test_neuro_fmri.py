"""
Comprehensive Unit & Mathematical Invariant Test Suite for Level 3 Neuro-fMRI
=============================================================================
Verifies CKA invariance theorems, Stiefel Procrustes, Grassmannian geodesic metrics,
double-gamma HRF convolution/deconvolution, and Glasser ethical parcellation.
"""

import numpy as np
import pytest

from daxda_engine.level3.neuro_fmri import (
    RepresentationalAlignmentEngine,
    CenteredKernelAlignment,
    RepresentationalDissimilarityMatrix,
    StiefelProcrustesAligner,
    GrassmannianManifoldDistance,
    DoubleGammaHRF,
    HemodynamicDeconvolver,
    GlasserEthicalParcellator,
    EthicalROICategory,
)


@pytest.fixture
def rng():
    return np.random.default_rng(1337)


@pytest.fixture
def synthetic_activations(rng):
    """Synthetic N=50 moral stimuli across 128 model dimensions and 180 voxels."""
    N = 50
    D_model = 128
    V_voxels = 180
    X = rng.normal(loc=0.0, scale=1.0, size=(N, D_model))
    # Y has partial shared variance with X plus noise
    shared_latent = rng.normal(loc=0.0, scale=1.0, size=(N, 16))
    W_x = rng.normal(loc=0.0, scale=0.5, size=(16, D_model))
    W_y = rng.normal(loc=0.0, scale=0.5, size=(16, V_voxels))
    X = X + shared_latent @ W_x
    Y = rng.normal(loc=0.0, scale=1.0, size=(N, V_voxels)) + shared_latent @ W_y
    return X, Y


def test_linear_cka_symmetry_and_bounds(synthetic_activations):
    """Theorem: CKA(K, L) == CKA(L, K) and CKA in [0, 1]."""
    X, Y = synthetic_activations
    res_xy = CenteredKernelAlignment.linear_cka(X, Y)
    res_yx = CenteredKernelAlignment.linear_cka(Y, X)
    
    assert 0.0 <= res_xy.cka_score <= 1.0
    assert 0.0 <= res_yx.cka_score <= 1.0
    assert np.isclose(res_xy.cka_score, res_yx.cka_score, atol=1e-12)


def test_linear_cka_self_similarity():
    """Theorem: CKA(X, X) == 1.0 for non-zero variance matrix."""
    rng = np.random.default_rng(42)
    X = rng.normal(size=(40, 64))
    res = CenteredKernelAlignment.linear_cka(X, X)
    assert np.isclose(res.cka_score, 1.0, atol=1e-6)


def test_linear_cka_orthogonal_invariance(synthetic_activations, rng):
    """Theorem: CKA is invariant under orthogonal rotation X @ Q_X and Y @ Q_Y."""
    X, Y = synthetic_activations
    Dx = X.shape[1]
    Dy = Y.shape[1]
    
    # Generate random orthogonal matrices Q_X and Q_Y
    Q_x, _ = np.linalg.qr(rng.normal(size=(Dx, Dx)))
    Q_y, _ = np.linalg.qr(rng.normal(size=(Dy, Dy)))
    
    X_rot = X @ Q_x
    Y_rot = Y @ Q_y
    
    score_orig = CenteredKernelAlignment.linear_cka(X, Y).cka_score
    score_rot = CenteredKernelAlignment.linear_cka(X_rot, Y_rot).cka_score
    
    assert np.isclose(score_orig, score_rot, atol=1e-10)


def test_linear_cka_isotropic_scaling_invariance(synthetic_activations):
    """Theorem: CKA is invariant under positive scalar multiplication."""
    X, Y = synthetic_activations
    score_orig = CenteredKernelAlignment.linear_cka(X, Y).cka_score
    score_scaled = CenteredKernelAlignment.linear_cka(X * 42.0, Y * 0.007).cka_score
    assert np.isclose(score_orig, score_scaled, atol=1e-12)


def test_rbf_cka_evaluation(synthetic_activations):
    """Verifies non-linear RBF CKA with median heuristic."""
    X, Y = synthetic_activations
    res = CenteredKernelAlignment.rbf_cka(X, Y)
    assert 0.0 <= res.cka_score <= 1.0
    assert "rbf" in res.kernel_type


def test_unbiased_hsic_estimator(synthetic_activations):
    """Verifies finite-sample unbiased HSIC estimator calculation."""
    X, Y = synthetic_activations
    res_unbiased = CenteredKernelAlignment.linear_cka(X, Y, unbiased=True)
    assert 0.0 <= res_unbiased.cka_score <= 1.0


def test_permutation_test_non_parametric_p_value(synthetic_activations):
    """Verifies non-parametric permutation test p-value bounds."""
    X, Y = synthetic_activations
    obs_score, p_val = CenteredKernelAlignment.permutation_test(X, Y, permutations=100)
    assert 0.0 <= obs_score <= 1.0
    assert 0.0 <= p_val <= 1.0


def test_rdm_computation_and_properties(synthetic_activations):
    """Verifies RDM construction: zero diagonal and symmetry."""
    X, _ = synthetic_activations
    for metric in ["correlation", "cosine", "euclidean"]:
        rdm = RepresentationalDissimilarityMatrix.compute(X, metric=metric)
        assert rdm.shape == (X.shape[0], X.shape[0])
        assert np.allclose(np.diag(rdm), 0.0, atol=1e-12)
        assert np.allclose(rdm, rdm.T, atol=1e-12)
        assert np.all(rdm >= -1e-12)


def test_spearman_rsa_with_identical_rdms(synthetic_activations):
    """Verifies Spearman RSA between identical RDMs yields rho == 1.0."""
    X, _ = synthetic_activations
    rdm = RepresentationalDissimilarityMatrix.compute(X, metric="correlation")
    rsa_res = RepresentationalDissimilarityMatrix.spearman_rsa(rdm, rdm, permutations=50)
    assert np.isclose(rsa_res.spearman_rho, 1.0, atol=1e-6)
    assert rsa_res.is_significant is True


def test_stiefel_procrustes_orthonormality(synthetic_activations):
    """Verifies optimal Procrustes rotation Q satisfies Q^T Q == I_k on Stiefel manifold."""
    X, Y = synthetic_activations
    res = StiefelProcrustesAligner.align(X, Y)
    Q = res.optimal_rotation_Q
    
    # Q is Dx x Dy, where k = min(Dx, Dy) = 128
    k = min(X.shape[1], Y.shape[1])
    # Q^T @ Q or Q @ Q^T must be identity of dimension k
    if Q.shape[0] >= Q.shape[1]:
        gram = Q.T @ Q
    else:
        gram = Q @ Q.T
    assert np.allclose(gram, np.eye(k), atol=1e-10)
    assert res.residual_frobenius_norm >= 0.0


def test_grassmannian_principal_angles_bounds(synthetic_activations):
    """Verifies principal angles lie in [0, pi/2] and metrics satisfy geodesic inequalities."""
    X, Y = synthetic_activations
    angles_res = GrassmannianManifoldDistance.compute_principal_angles(X, Y, rank=16)
    
    thetas = angles_res.principal_angles_rad
    assert len(thetas) == 16
    assert np.all(thetas >= -1e-12)
    assert np.all(thetas <= (np.pi / 2.0 + 1e-12))
    assert angles_res.geodesic_distance >= 0.0
    assert angles_res.chordal_distance >= 0.0
    assert angles_res.projection_distance <= 1.0


def test_grassmannian_identical_subspaces():
    """Identical subspaces have 0.0 geodesic distance."""
    rng = np.random.default_rng(99)
    X = rng.normal(size=(50, 32))
    d_geo = GrassmannianManifoldDistance.compute_geodesic(X, X, rank=10)
    assert np.isclose(d_geo, 0.0, atol=1e-6)


def test_double_gamma_hrf_shape():
    """Verifies canonical HRF peak at ~6s and post-stimulus undershoot."""
    hrf = DoubleGammaHRF()
    t = np.linspace(0, 30, 300)
    h = hrf.evaluate(t)
    
    peak_time = t[np.argmax(h)]
    assert 5.0 <= peak_time <= 7.0  # Canonical peak around 6 seconds
    
    min_val = np.min(h)
    assert min_val < 0.0  # Undershoot dips below zero


def test_hemodynamic_convolution_and_deconvolution():
    """Verifies HRF convolution and Wiener deconvolution stability."""
    deconv = HemodynamicDeconvolver(tr_seconds=1.5)
    amplitudes = np.array([0.0, 1.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.5, 0.0, 0.0])
    bold_pred = deconv.convolve_events(amplitudes)
    
    assert len(bold_pred) == len(amplitudes)
    assert np.max(bold_pred) > 0.0
    
    # Deconvolve to recover driving events
    recovered = deconv.deconvolve_bold(bold_pred, regularization_lambda=1e-2)
    assert len(recovered) == len(bold_pred)
    assert not np.any(np.isnan(recovered))


def test_glasser_ethical_parcellation(synthetic_activations):
    """Verifies moral network concordance parcellation across 5 ethical ROIs."""
    X, Y = synthetic_activations
    parcellator = GlasserEthicalParcellator()
    profile = parcellator.evaluate_moral_network_concordance(X, Y)
    
    assert 0.0 <= profile.composite_mci <= 1.0
    assert 0.0 <= profile.vmpfc_concordance <= 1.0
    assert 0.0 <= profile.dlpfc_concordance <= 1.0
    assert 0.0 <= profile.tpj_concordance <= 1.0
    assert 0.0 <= profile.dacc_concordance <= 1.0
    assert 0.0 <= profile.insula_concordance <= 1.0
    assert profile.tripwire_alert_level in [
        "NOMINAL_ALIGNED",
        "WARNING_LOW_CONCORDANCE",
        "CRITICAL_MORAL_DISSOCIATION_TRIPWIRE",
    ]


def test_deceptive_dissociation_tripwire_trigger():
    """Verifies that artificial suppression of vmPFC triggers moral dissociation tripwire."""
    rng = np.random.default_rng(77)
    N = 50
    X = rng.normal(size=(N, 64))
    Y = np.zeros((N, 180))
    
    # Highly correlated in dlPFC (areas 36..71) but completely dead/flat in vmPFC (0..35)
    Y[:, 36:72] = X[:, :36]
    
    parcellator = GlasserEthicalParcellator()
    profile = parcellator.evaluate_moral_network_concordance(
        X, Y, dissociation_vmpfc_threshold=0.30, geodesic_vmpfc_alert_threshold=1.0
    )
    
    assert profile.is_deceptively_dissociated is True
    assert profile.vmpfc_concordance < 0.10
    assert profile.dlpfc_concordance > 0.70
    assert profile.tripwire_alert_level == "CRITICAL_MORAL_DISSOCIATION_TRIPWIRE"


def test_representational_alignment_orchestrator(synthetic_activations):
    """Verifies end-to-end RepresentationalAlignmentEngine orchestration."""
    X, Y = synthetic_activations
    engine = RepresentationalAlignmentEngine(d_model=X.shape[1], roi_count=Y.shape[1])
    
    cka_linear = engine.compute_linear_cka(X, Y)
    cka_rbf = engine.compute_rbf_cka(X, Y)
    grassmann_d = engine.compute_grassmannian_distance(X, Y, rank=10)
    
    assert 0.0 <= cka_linear <= 1.0
    assert 0.0 <= cka_rbf <= 1.0
    assert grassmann_d >= 0.0


def test_permutation_test_identical_representations():
    """Identical representations achieve maximal CKA and minimum permutation p-value."""
    rng = np.random.default_rng(101)
    X = rng.normal(size=(30, 20))
    obs_score, p_val = CenteredKernelAlignment.permutation_test(X, X, permutations=50)
    assert np.isclose(obs_score, 1.0, atol=1e-6)
    assert p_val <= 0.05


def test_cka_biased_vs_unbiased_convergence():
    """Theorem: As N increases, biased and unbiased CKA asymptotically converge."""
    rng = np.random.default_rng(202)
    N = 400
    X = rng.normal(size=(N, 32))
    Y = rng.normal(size=(N, 32)) + X * 0.8
    res_b = CenteredKernelAlignment.linear_cka(X, Y, unbiased=False)
    res_u = CenteredKernelAlignment.linear_cka(X, Y, unbiased=True)
    assert abs(res_b.cka_score - res_u.cka_score) < 0.06


def test_rdm_mahalanobis_metric(synthetic_activations):
    """Verifies Mahalanobis distance RDM computation."""
    X, _ = synthetic_activations
    # Subsample dimensions to ensure non-singular covariance (D < N)
    X_sub = X[:, :20]
    rdm_m = RepresentationalDissimilarityMatrix.compute(X_sub, metric="mahalanobis")
    assert rdm_m.shape == (X.shape[0], X.shape[0])
    assert np.allclose(np.diag(rdm_m), 0.0, atol=1e-12)
    assert np.all(rdm_m >= 0.0)


def test_stiefel_procrustes_explained_variance_exact():
    """Theorem: If Y = X @ Q for orthogonal Q, explained variance ratio == 1.0."""
    rng = np.random.default_rng(303)
    N, D = 40, 25
    X = rng.normal(size=(N, D))
    Q_true, _ = np.linalg.qr(rng.normal(size=(D, D)))
    Y = X @ Q_true
    res = StiefelProcrustesAligner.align(X, Y)
    assert np.isclose(res.explained_variance_ratio, 1.0, atol=1e-6)
    assert res.residual_frobenius_norm < 1e-4


def test_grassmannian_chordal_and_projection_inequalities(synthetic_activations):
    """Theorem: For any two subspaces, d_proj <= d_chordal <= d_geodesic."""
    X, Y = synthetic_activations
    res = GrassmannianManifoldDistance.compute_principal_angles(X, Y, rank=12)
    assert res.projection_distance <= res.chordal_distance + 1e-12
    assert res.chordal_distance <= res.geodesic_distance + 1e-12


def test_hrf_kernel_normalization():
    """Verifies that discrete HRF kernel is peak-normalized to 1.0."""
    hrf = DoubleGammaHRF()
    kernel = hrf.generate_discrete_kernel(tr_seconds=2.0)
    assert np.isclose(np.max(np.abs(kernel)), 1.0, atol=1e-12)


def test_hrf_temporal_convolution_linearity():
    """Theorem: HRF convolution is a linear time-invariant operator: (a*x1 + b*x2)*h == a*(x1*h) + b*(x2*h)."""
    deconv = HemodynamicDeconvolver(tr_seconds=1.0)
    x1 = np.array([1.0, 0.0, 2.0, 0.0, 1.0])
    x2 = np.array([0.0, 3.0, 0.0, 1.0, 0.0])
    c1, c2 = 2.5, -1.8
    y_combo = deconv.convolve_events(c1 * x1 + c2 * x2)
    y1 = deconv.convolve_events(x1)
    y2 = deconv.convolve_events(x2)
    assert np.allclose(y_combo, c1 * y1 + c2 * y2, atol=1e-12)


def test_glasser_parcellator_custom_weights(synthetic_activations):
    """Verifies that custom ethical weights properly scale composite MCI."""
    X, Y = synthetic_activations
    custom_weights = {
        EthicalROICategory.VMPFC: 0.50,
        EthicalROICategory.DLPFC: 0.50,
        EthicalROICategory.TPJ: 0.0,
        EthicalROICategory.DACC: 0.0,
        EthicalROICategory.INSULA: 0.0,
    }
    parcellator = GlasserEthicalParcellator(weights=custom_weights)
    profile = parcellator.evaluate_moral_network_concordance(X, Y)
    expected_mci = 0.5 * profile.vmpfc_concordance + 0.5 * profile.dlpfc_concordance
    assert np.isclose(profile.composite_mci, expected_mci, atol=1e-6)

