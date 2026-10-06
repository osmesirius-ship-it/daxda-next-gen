"""
Differential Geometry on Stiefel and Grassmannian Manifolds
===========================================================
Mathematical implementation of:
1. Orthogonal Procrustes alignment on Stiefel Manifold St(k, D)
2. Principal angles computation via SVD
3. Geodesic, Chordal, and Projection metrics on Grassmannian Manifold Gr(k, D)
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class PrincipalAnglesResult:
    """Outcome of Principal Angles decomposition between linear subspaces."""
    principal_angles_rad: np.ndarray
    cosines: np.ndarray
    geodesic_distance: float
    chordal_distance: float
    projection_distance: float
    subspace_rank: int


@dataclass(frozen=True)
class ProcrustesAlignmentResult:
    """Outcome of Stiefel manifold orthogonal Procrustes alignment."""
    optimal_rotation_Q: np.ndarray
    residual_frobenius_norm: float
    explained_variance_ratio: float
    rank: int


class StiefelProcrustesAligner:
    """
    Orthogonal Procrustes Solver on the Stiefel Manifold:
    St(k, D) = { Q in R^{D x k} : Q^T Q = I_k }
    
    Finds Q* = argmin_{Q in St(k, D)} || X Q - Y ||_F^2
    Via Singular Value Decomposition of cross-covariance matrix Sigma_{XY} = X^T Y.
    """

    @staticmethod
    def align(
        X: np.ndarray,
        Y: np.ndarray,
        center: bool = True,
    ) -> ProcrustesAlignmentResult:
        """
        Solves the Stiefel Procrustes problem for source X (N x D_x) and target Y (N x D_y).
        If D_x != D_y, projects to min(D_x, D_y).
        """
        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        N, Dx = X.shape
        _, Dy = Y.shape
        assert N == Y.shape[0], "Sample dimension mismatch"
        
        if center:
            X = X - np.mean(X, axis=0, keepdims=True)
            Y = Y - np.mean(Y, axis=0, keepdims=True)
            
        k = min(Dx, Dy)
        # Compute cross-covariance M = X^T @ Y (Dx x Dy)
        M = X.T @ Y
        
        # SVD of M: M = U @ diag(S) @ Vt
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        
        # Canonical sign resolution to ensure IEEE 754 determinism
        for col in range(U.shape[1]):
            leading_idx = np.argmax(np.abs(U[:, col]))
            if U[leading_idx, col] < 0:
                U[:, col] *= -1.0
                Vt[col, :] *= -1.0
                
        # Optimal rotation matrix Q* in St(k, Dx)
        Q_star = U @ Vt
        
        # Projected prediction
        if Dx <= Dy:
            # X @ Q_star is N x Dy
            Y_pred = X @ Q_star
        else:
            # Q_star is Dx x Dy, X @ Q_star is N x Dy
            Y_pred = X @ Q_star
            
        residual_sq = np.sum((Y_pred - Y) ** 2)
        total_var = np.sum(Y ** 2)
        evr = float(1.0 - (residual_sq / max(total_var, 1e-12)))
        
        return ProcrustesAlignmentResult(
            optimal_rotation_Q=Q_star,
            residual_frobenius_norm=float(np.sqrt(max(residual_sq, 0.0))),
            explained_variance_ratio=float(np.clip(evr, 0.0, 1.0)),
            rank=k,
        )


class GrassmannianManifoldDistance:
    """
    Riemannian Metrics on the Grassmannian Manifold Gr(k, D),
    the space of all k-dimensional linear subspaces of R^D.
    
    Computes canonical principal angles theta_1 <= theta_2 <= ... <= theta_k
    and invariant geodesic distances.
    """

    @classmethod
    def compute_principal_angles(
        cls,
        X: np.ndarray,
        Y: np.ndarray,
        rank: Optional[int] = None,
    ) -> PrincipalAnglesResult:
        """
        Computes principal angles between span(X) and span(Y).
        1. Form orthonormal bases Q_X, Q_Y via thin QR decomposition or SVD.
        2. Compute SVD of Q_X^T @ Q_Y:
           Q_X^T @ Q_Y = U @ diag(cos(theta_1), ..., cos(theta_k)) @ V^T
        """
        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        N = X.shape[0]
        assert N == Y.shape[0], "Sample dimension mismatch"
        
        # Center representations
        X_c = X - np.mean(X, axis=0, keepdims=True)
        Y_c = Y - np.mean(Y, axis=0, keepdims=True)
        
        # Orthonormal basis for columns of X and Y (or top principal components)
        k_max = min(X.shape[1], Y.shape[1], N - 1)
        k = k_max if rank is None else min(rank, k_max)
        assert k >= 1, "Subspace dimension must be at least 1"
        
        # Economy SVD to extract top-k orthonormal subspace bases
        Ux, _, _ = np.linalg.svd(X_c, full_matrices=False)
        Uy, _, _ = np.linalg.svd(Y_c, full_matrices=False)
        
        Q_X = Ux[:, :k]  # N x k
        Q_Y = Uy[:, :k]  # N x k
        
        # Cross-projection matrix
        C = Q_X.T @ Q_Y  # k x k
        
        # Singular values of C are cosines of principal angles
        _, S, _ = np.linalg.svd(C)
        cosines = np.clip(S[:k], -1.0, 1.0)
        # Numerical floor clamp: if 1.0 - cosine < 1e-12, set to exactly 1.0 to avoid sqrt(eps) drift
        cosines[cosines >= (1.0 - 1e-12)] = 1.0
        
        # Principal angles in radians [0, pi/2]
        thetas = np.arccos(cosines)
        thetas.sort()
        
        # Geodesic distance: d_geo = sqrt(sum theta_i^2)
        d_geodesic = float(np.sqrt(np.sum(thetas ** 2)))
        
        # Chordal distance: d_chordal = sqrt(sum sin^2(theta_i))
        sines = np.sin(thetas)
        d_chordal = float(np.sqrt(np.sum(sines ** 2)))
        
        # Projection (Asimov) distance: d_proj = sin(theta_max)
        d_projection = float(np.max(sines)) if len(sines) > 0 else 0.0
        
        return PrincipalAnglesResult(
            principal_angles_rad=thetas,
            cosines=cosines,
            geodesic_distance=d_geodesic,
            chordal_distance=d_chordal,
            projection_distance=d_projection,
            subspace_rank=k,
        )

    @classmethod
    def compute_geodesic(
        cls,
        X: np.ndarray,
        Y: np.ndarray,
        rank: Optional[int] = None,
    ) -> float:
        """Returns the scalar Riemannian geodesic distance on Gr(k, D)."""
        res = cls.compute_principal_angles(X, Y, rank=rank)
        return res.geodesic_distance
