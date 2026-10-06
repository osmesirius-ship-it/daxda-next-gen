"""
Centered Kernel Alignment (CKA) & Representational Similarity Analysis (RSA) Engine
===================================================================================
Rigorous mathematical implementation of Hilbert-Schmidt Independence Criterion (HSIC),
linear/RBF CKA, representational dissimilarity matrices, and permutation testing.
Pure NumPy implementation with zero external C-dependencies.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union
import numpy as np


@dataclass(frozen=True)
class SpearmanRSAResult:
    """Statistical outcome of Representational Similarity Analysis."""
    spearman_rho: float
    p_value: float
    stimulus_count: int
    is_significant: bool
    empirical_null_mean: float
    empirical_null_std: float


@dataclass(frozen=True)
class CKAResult:
    """Centered Kernel Alignment evaluation result."""
    cka_score: float
    hsic_cross: float
    hsic_source: float
    hsic_target: float
    kernel_type: str
    permutation_p_value: Optional[float] = None


def _rankdata(a: np.ndarray) -> np.ndarray:
    """Computes fractional/standard ranks of 1D array in pure NumPy."""
    a = np.asarray(a)
    order = np.argsort(a)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, len(a) + 1, dtype=np.float64)
    return ranks


def _spearmanr_1d(a: np.ndarray, b: np.ndarray) -> Tuple[float, float]:
    """Computes Spearman rank correlation rho between two 1D vectors."""
    ra = _rankdata(a)
    rb = _rankdata(b)
    
    ra_c = ra - np.mean(ra)
    rb_c = rb - np.mean(rb)
    
    norm_a = np.sqrt(np.sum(ra_c ** 2))
    norm_b = np.sqrt(np.sum(rb_c ** 2))
    
    if norm_a < 1e-12 or norm_b < 1e-12:
        return 0.0, 1.0
        
    rho = float(np.sum(ra_c * rb_c) / (norm_a * norm_b))
    rho = float(np.clip(rho, -1.0, 1.0))
    return rho, 0.0


def _pairwise_sqeuclidean(X: np.ndarray) -> np.ndarray:
    """Pairwise squared Euclidean distance matrix: ||x_i - x_j||^2."""
    dot = X @ X.T
    diag = np.diag(dot)
    dist_sq = diag[:, None] + diag[None, :] - 2.0 * dot
    return np.maximum(dist_sq, 0.0)


class CenteredKernelAlignment:
    """
    Mathematical Implementation of Centered Kernel Alignment (CKA)
    based on the Hilbert-Schmidt Independence Criterion (HSIC).
    
    Ref: Kornblith et al. (2019), "Similarity of Neural Network Representations Revisited"
    """
    
    @staticmethod
    def center_gram(K: np.ndarray) -> np.ndarray:
        """
        Fast O(N^2) centering of an N x N Gram matrix K without explicit H @ K @ H multiplication:
        H = I_N - (1/N) * 1 * 1^T
        tilde{K} = H @ K @ H = K - row_means - col_means + grand_mean
        """
        row_mean = np.mean(K, axis=1, keepdims=True)
        col_mean = np.mean(K, axis=0, keepdims=True)
        grand_mean = np.mean(K)
        return K - row_mean - col_mean + grand_mean

    @classmethod
    def hsic_biased(cls, K: np.ndarray, L: np.ndarray) -> float:
        """
        Computes the standard empirical (biased) HSIC:
        HSIC(K, L) = (1 / (N - 1)^2) * Tr(tilde{K} @ tilde{L})
        """
        N = K.shape[0]
        if N < 2:
            return 0.0
        tilde_K = cls.center_gram(K)
        tilde_L = cls.center_gram(L)
        return float(np.sum(tilde_K * tilde_L) / ((N - 1) ** 2))

    @classmethod
    def hsic_unbiased(cls, K: np.ndarray, L: np.ndarray) -> float:
        """
        Computes the Song et al. (2012) finite-sample unbiased estimator of HSIC:
        HSIC_unbiased(K, L) = (1 / (N(N-3))) * (Tr(tilde{K}_0 tilde{L}_0) + ...)
        """
        N = K.shape[0]
        if N < 4:
            return cls.hsic_biased(K, L)
        
        K_0 = K.copy()
        np.fill_diagonal(K_0, 0.0)
        L_0 = L.copy()
        np.fill_diagonal(L_0, 0.0)
        
        term1 = np.sum(K_0 * L_0)
        term2 = np.sum(K_0) * np.sum(L_0) / ((N - 1) * (N - 2))
        term3 = (K_0 @ L_0.sum(axis=1)).sum() * 2.0 / (N - 2)
        
        stat = (term1 + term2 - term3) / (N * (N - 3))
        return float(stat)

    @classmethod
    def linear_cka(cls, X: np.ndarray, Y: np.ndarray, unbiased: bool = False) -> CKAResult:
        """
        Computes linear CKA between activation matrices X (N x D_x) and Y (N x D_y):
        K = X @ X^T,  L = Y @ Y^T
        CKA(K, L) = HSIC(K, L) / sqrt(HSIC(K, K) * HSIC(L, L))
        """
        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        assert X.shape[0] == Y.shape[0], f"Sample mismatch: X has {X.shape[0]}, Y has {Y.shape[0]}"
        
        # Gram matrices
        K = X @ X.T
        L = Y @ Y.T
        
        hsic_func = cls.hsic_unbiased if unbiased else cls.hsic_biased
        hsic_xy = hsic_func(K, L)
        hsic_xx = hsic_func(K, K)
        hsic_yy = hsic_func(L, L)
        
        denominator = np.sqrt(max(hsic_xx, 1e-15) * max(hsic_yy, 1e-15))
        cka = float(np.clip(hsic_xy / denominator, 0.0, 1.0))
        
        return CKAResult(
            cka_score=cka,
            hsic_cross=float(hsic_xy),
            hsic_source=float(hsic_xx),
            hsic_target=float(hsic_yy),
            kernel_type="linear",
        )

    @classmethod
    def rbf_cka(
        cls,
        X: np.ndarray,
        Y: np.ndarray,
        sigma_x: Optional[float] = None,
        sigma_y: Optional[float] = None,
        unbiased: bool = False,
    ) -> CKAResult:
        """
        Computes non-linear RBF CKA using radial basis function kernels:
        K_ij = exp(- ||x_i - x_j||^2 / (2 * sigma_x^2))
        Default sigma: median heuristic across pairwise distances.
        """
        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        N = X.shape[0]
        assert N == Y.shape[0], "Sample dimension mismatch"
        
        dist_x_sq = _pairwise_sqeuclidean(X)
        dist_y_sq = _pairwise_sqeuclidean(Y)
        
        triu_idx = np.triu_indices(N, k=1)
        if sigma_x is None:
            vals_x = dist_x_sq[triu_idx]
            med_x = float(np.median(vals_x)) if len(vals_x) > 0 else 1.0
            sigma_x = float(np.sqrt(max(med_x, 1e-6)))
        if sigma_y is None:
            vals_y = dist_y_sq[triu_idx]
            med_y = float(np.median(vals_y)) if len(vals_y) > 0 else 1.0
            sigma_y = float(np.sqrt(max(med_y, 1e-6)))
            
        gamma_x = 1.0 / (2.0 * max(sigma_x ** 2, 1e-12))
        gamma_y = 1.0 / (2.0 * max(sigma_y ** 2, 1e-12))
        
        K = np.exp(-gamma_x * dist_x_sq)
        L = np.exp(-gamma_y * dist_y_sq)
        
        hsic_func = cls.hsic_unbiased if unbiased else cls.hsic_biased
        hsic_xy = hsic_func(K, L)
        hsic_xx = hsic_func(K, K)
        hsic_yy = hsic_func(L, L)
        
        denominator = np.sqrt(max(hsic_xx, 1e-15) * max(hsic_yy, 1e-15))
        cka = float(np.clip(hsic_xy / denominator, 0.0, 1.0))
        
        return CKAResult(
            cka_score=cka,
            hsic_cross=float(hsic_xy),
            hsic_source=float(hsic_xx),
            hsic_target=float(hsic_yy),
            kernel_type=f"rbf(sx={sigma_x:.3f},sy={sigma_y:.3f})",
        )

    @classmethod
    def permutation_test(
        cls,
        X: np.ndarray,
        Y: np.ndarray,
        permutations: int = 1000,
        seed: int = 42,
    ) -> Tuple[float, float]:
        """
        Permutes stimulus ordering to compute non-parametric empirical p-value.
        Returns: (observed_cka, p_value)
        """
        rng = np.random.default_rng(seed)
        obs_res = cls.linear_cka(X, Y)
        obs_score = obs_res.cka_score
        
        null_distribution = np.zeros(permutations, dtype=np.float64)
        N = X.shape[0]
        
        for p in range(permutations):
            perm_idx = rng.permutation(N)
            Y_perm = Y[perm_idx]
            null_distribution[p] = cls.linear_cka(X, Y_perm).cka_score
            
        p_val = float(np.mean(null_distribution >= obs_score))
        return obs_score, p_val


class RepresentationalDissimilarityMatrix:
    """
    Constructs second-order Representational Dissimilarity Matrices (RDMs).
    RDM_{ij} = d(v_i, v_j) where d is a dissimilarity metric.
    """

    SUPPORTED_METRICS = ["correlation", "cosine", "euclidean", "mahalanobis"]

    @classmethod
    def compute(cls, matrix: np.ndarray, metric: str = "correlation") -> np.ndarray:
        """
        Computes N x N RDM from N x D activation matrix in pure NumPy.
        Diagonal is identically 0.0.
        """
        assert metric in cls.SUPPORTED_METRICS, f"Unsupported metric: {metric}"
        X = np.asarray(matrix, dtype=np.float64)
        N, D = X.shape
        
        if metric == "euclidean":
            dist_sq = _pairwise_sqeuclidean(X)
            rdm = np.sqrt(dist_sq)
        elif metric == "cosine":
            norms = np.linalg.norm(X, axis=1, keepdims=True)
            norms = np.maximum(norms, 1e-12)
            X_norm = X / norms
            sim = X_norm @ X_norm.T
            rdm = np.clip(1.0 - sim, 0.0, 2.0)
        elif metric == "correlation":
            # Center each stimulus vector
            X_c = X - np.mean(X, axis=1, keepdims=True)
            norms = np.linalg.norm(X_c, axis=1, keepdims=True)
            norms = np.maximum(norms, 1e-12)
            X_std = X_c / norms
            corr = X_std @ X_std.T
            rdm = np.clip(1.0 - corr, 0.0, 2.0)
        elif metric == "mahalanobis":
            cov = np.cov(X, rowvar=False)
            inv_cov = np.linalg.pinv(cov + 1e-6 * np.eye(D))
            # d_M^2(x_i, x_j) = (x_i - x_j)^T inv_cov (x_i - x_j)
            rdm = np.zeros((N, N), dtype=np.float64)
            for i in range(N):
                diff = X - X[i]
                rdm[i] = np.sqrt(np.maximum(np.sum((diff @ inv_cov) * diff, axis=1), 0.0))
                
        np.fill_diagonal(rdm, 0.0)
        return rdm

    @classmethod
    def spearman_rsa(
        cls,
        rdm_source: np.ndarray,
        rdm_target: np.ndarray,
        permutations: int = 1000,
        alpha: float = 0.05,
        seed: int = 42,
    ) -> SpearmanRSAResult:
        """
        Spearman rank correlation of upper-triangular RDM vectors
        with non-parametric permutation testing.
        """
        N = rdm_source.shape[0]
        assert N == rdm_target.shape[0], "RDM dimension mismatch"
        
        triu_idx = np.triu_indices(N, k=1)
        vec_source = rdm_source[triu_idx]
        vec_target = rdm_target[triu_idx]
        
        rho, _ = _spearmanr_1d(vec_source, vec_target)
            
        # Permutation testing on condition labels (not vector entries)
        rng = np.random.default_rng(seed)
        null_rhos = np.zeros(permutations, dtype=np.float64)
        
        for i in range(permutations):
            perm = rng.permutation(N)
            rdm_perm = rdm_target[perm, :][:, perm]
            null_vec = rdm_perm[triu_idx]
            null_r, _ = _spearmanr_1d(vec_source, null_vec)
            null_rhos[i] = null_r
            
        p_value = float(np.mean(null_rhos >= rho))
        
        return SpearmanRSAResult(
            spearman_rho=float(rho),
            p_value=p_value,
            stimulus_count=N,
            is_significant=(p_value < alpha),
            empirical_null_mean=float(np.mean(null_rhos)),
            empirical_null_std=float(np.std(null_rhos)),
        )


class RepresentationalAlignmentEngine:
    """
    High-level orchestration engine for measuring representational concordance
    between agent internal representations and empirical neuroimaging signals.
    """

    def __init__(self, d_model: int = 4096, roi_count: int = 180):
        self.d_model = d_model
        self.roi_count = roi_count
        self.cka = CenteredKernelAlignment()
        self.rdm = RepresentationalDissimilarityMatrix()

    def compute_linear_cka(self, agent_residuals: np.ndarray, human_voxels: np.ndarray) -> float:
        """Computes Linear Centered Kernel Alignment score in [0.0, 1.0]."""
        res = self.cka.linear_cka(agent_residuals, human_voxels)
        return res.cka_score

    def compute_rbf_cka(self, agent_residuals: np.ndarray, human_voxels: np.ndarray) -> float:
        """Computes RBF Centered Kernel Alignment score in [0.0, 1.0]."""
        res = self.cka.rbf_cka(agent_residuals, human_voxels)
        return res.cka_score

    def compute_grassmannian_distance(
        self,
        agent_residuals: np.ndarray,
        human_voxels: np.ndarray,
        rank: int = 32,
    ) -> float:
        """Computes geodesic Riemannian distance on Grassmannian manifold Gr(rank, D)."""
        from .manifold import GrassmannianManifoldDistance
        return GrassmannianManifoldDistance.compute_geodesic(
            agent_residuals, human_voxels, rank=rank
        )
