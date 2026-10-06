"""
Riemannian Geometry on the Cone of Symmetric Positive Definite (SPD) Matrices S_+^n
===================================================================================
Rigorous implementation of:
1. Affine-Invariant Riemannian Metric (AIRM) geodesic distance
2. Riemannian Fréchet / Karcher mean center of mass via manifold gradient descent
3. Tangent space logarithmic and exponential maps
"""

from typing import List, Optional
import numpy as np


def _matrix_sqrt_and_inv_sqrt(P: np.ndarray, reg: float = 1e-8) -> tuple[np.ndarray, np.ndarray]:
    """Computes matrix square root P^{1/2} and inverse square root P^{-1/2} via eigendecomposition."""
    vals, vecs = np.linalg.eigh(P)
    vals_clamped = np.maximum(vals, reg)
    sqrt_vals = np.sqrt(vals_clamped)
    inv_sqrt_vals = 1.0 / sqrt_vals
    
    P_sqrt = vecs @ np.diag(sqrt_vals) @ vecs.T
    P_inv_sqrt = vecs @ np.diag(inv_sqrt_vals) @ vecs.T
    return P_sqrt, P_inv_sqrt


def _matrix_log(P: np.ndarray, reg: float = 1e-8) -> np.ndarray:
    """Computes symmetric matrix logarithm log(P)."""
    vals, vecs = np.linalg.eigh(P)
    vals_clamped = np.maximum(vals, reg)
    return vecs @ np.diag(np.log(vals_clamped)) @ vecs.T


def _matrix_exp(V: np.ndarray) -> np.ndarray:
    """Computes symmetric matrix exponential exp(V)."""
    vals, vecs = np.linalg.eigh(V)
    return vecs @ np.diag(np.exp(vals)) @ vecs.T


def airm_geodesic_distance(P1: np.ndarray, P2: np.ndarray, reg: float = 1e-8) -> float:
    """
    Affine-Invariant Riemannian Metric (AIRM) geodesic distance on S_+^n:
    delta_R(P1, P2) = || log(P1^{-1/2} P2 P1^{-1/2}) ||_F
                    = sqrt( sum ln^2(lambda_i(P1^{-1} P2)) )
    """
    P1_c = (P1 + P1.T) * 0.5
    P2_c = (P2 + P2.T) * 0.5
    
    _, P1_inv_sqrt = _matrix_sqrt_and_inv_sqrt(P1_c, reg=reg)
    M = P1_inv_sqrt @ P2_c @ P1_inv_sqrt
    M = (M + M.T) * 0.5
    
    vals = np.linalg.eigvalsh(M)
    vals_clamped = np.maximum(vals, reg)
    log_vals = np.log(vals_clamped)
    return float(np.sqrt(max(np.sum(log_vals ** 2), 0.0)))


def tangent_space_log_map(P: np.ndarray, base: np.ndarray, reg: float = 1e-8) -> np.ndarray:
    """
    Projects SPD matrix P onto the tangent space T_{base} S_+^n at base:
    Log_{base}(P) = base^{1/2} log(base^{-1/2} P base^{-1/2}) base^{1/2}
    """
    base_sqrt, base_inv_sqrt = _matrix_sqrt_and_inv_sqrt(base, reg=reg)
    M = base_inv_sqrt @ P @ base_inv_sqrt
    M = (M + M.T) * 0.5
    log_M = _matrix_log(M, reg=reg)
    tangent_vector = base_sqrt @ log_M @ base_sqrt
    return (tangent_vector + tangent_vector.T) * 0.5


def frechet_mean_spd(
    matrices: List[np.ndarray],
    max_iter: int = 30,
    tol: float = 1e-7,
    reg: float = 1e-8,
) -> np.ndarray:
    """
    Computes the Fréchet / Karcher mean center of mass on S_+^n
    via gradient descent on the Riemannian manifold:
    G^{(t+1)} = G^{1/2} exp( (1/K) sum log(G^{-1/2} P_k G^{-1/2}) ) G^{1/2}
    """
    assert len(matrices) > 0, "Matrix list cannot be empty"
    K = len(matrices)
    n = matrices[0].shape[0]
    
    # Initialize with Euclidean mean projected onto positive definite cone
    G = np.mean(matrices, axis=0)
    G = (G + G.T) * 0.5
    vals, vecs = np.linalg.eigh(G)
    G = vecs @ np.diag(np.maximum(vals, reg)) @ vecs.T
    
    for _ in range(max_iter):
        G_sqrt, G_inv_sqrt = _matrix_sqrt_and_inv_sqrt(G, reg=reg)
        
        sum_log = np.zeros((n, n), dtype=np.float64)
        for P in matrices:
            P_c = (P + P.T) * 0.5
            M = G_inv_sqrt @ P_c @ G_inv_sqrt
            M = (M + M.T) * 0.5
            sum_log += _matrix_log(M, reg=reg)
            
        avg_tangent = sum_log / float(K)
        step_norm = np.linalg.norm(avg_tangent, ord="fro")
        if step_norm < tol:
            break
            
        step_exp = _matrix_exp(avg_tangent)
        G = G_sqrt @ step_exp @ G_sqrt
        G = (G + G.T) * 0.5
        
    return G


class RiemannianEEGCovarianceEngine:
    """
    Estimates regularized sample covariance matrices from multi-channel EEG epochs
    and computes Riemannian manifold metrics.
    """

    def __init__(self, channels: int = 32, sampling_rate_hz: float = 250.0, shrinkage: float = 1e-4):
        self.channels = channels
        self.fs = sampling_rate_hz
        self.shrinkage = shrinkage

    def estimate_covariance(self, epoch: np.ndarray) -> np.ndarray:
        """
        Estimates regularized sample covariance matrix for C x T epoch:
        P = (1 / (T - 1)) E E^T
        Shrinkage: P_reg = (1 - alpha) P + alpha (Tr(P)/C) I_C
        """
        epoch = np.asarray(epoch, dtype=np.float64)
        C, T = epoch.shape
        assert C == self.channels, f"Channel count mismatch: {C} != {self.channels}"
        
        # Center epoch per channel
        epoch_c = epoch - np.mean(epoch, axis=1, keepdims=True)
        cov = (epoch_c @ epoch_c.T) / max(T - 1, 1)
        cov = (cov + cov.T) * 0.5
        
        # Ledoit-Wolf-style shrinkage toward scaled identity
        trace_mean = np.trace(cov) / float(C)
        cov_reg = (1.0 - self.shrinkage) * cov + self.shrinkage * trace_mean * np.eye(C)
        return (cov_reg + cov_reg.T) * 0.5

    def compute_airm_distance(self, P1: np.ndarray, P2: np.ndarray) -> float:
        """Computes AIRM Riemannian distance between two covariance matrices."""
        return airm_geodesic_distance(P1, P2)

    def compute_frechet_mean(self, cov_list: List[np.ndarray]) -> np.ndarray:
        """Computes Riemannian Fréchet mean of a list of covariance matrices."""
        return frechet_mean_spd(cov_list)
