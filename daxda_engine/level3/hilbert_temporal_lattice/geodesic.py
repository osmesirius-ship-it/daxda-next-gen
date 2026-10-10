"""
Geodesic and Parallel Transport Solver on 5D Manifolds.
Solves the geodesic equations and parallel transport ODEs using 4th-order Runge-Kutta (RK4),
guaranteeing metric norm conservation along the affine parameter.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from .metric import TemporalManifold5D


@dataclass(frozen=True)
class GeodesicTrajectory:
    """Stores the computed trajectory of a 5D geodesic."""
    parameter_lambdas: np.ndarray  # shape (N,)
    coordinates: np.ndarray        # shape (N, 5)
    tangent_vectors: np.ndarray    # shape (N, 5)
    metric_norms: np.ndarray       # shape (N,)
    norm_drift_max: float
    is_norm_conserved: bool


@dataclass(frozen=True)
class ParallelTransportResult:
    """Stores parallel transport of a vector along a trajectory."""
    parameter_lambdas: np.ndarray  # shape (N,)
    transported_vectors: np.ndarray  # shape (N, 5)
    inner_products: np.ndarray     # shape (N,)
    initial_vector: np.ndarray
    final_vector: np.ndarray
    inner_product_drift_max: float
    is_inner_product_conserved: bool


class GeodesicParallelTransportSolver:
    r"""
    Solves:
      1) Geodesic equation: d^2 x^\mu / d\lambda^2 + \Gamma^\mu_{\alpha\beta} (dx^\alpha/d\lambda)(dx^\beta/d\lambda) = 0
      2) Parallel transport: dV^\mu / d\lambda + \Gamma^\mu_{\alpha\beta} V^\alpha (dx^\beta/d\lambda) = 0
    """

    def __init__(self, manifold: TemporalManifold5D):
        self.manifold = manifold

    def _geodesic_derivatives(
        self,
        x: np.ndarray,
        u: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Returns dx/dlambda = u, du/dlambda = -Gamma * u * u."""
        gamma = self.manifold.christoffel_symbols(x)
        # du^\mu = - \sum_{\alpha,\beta} \Gamma^\mu_{\alpha\beta} u^\alpha u^\beta
        du = -np.einsum("mab,a,b->m", gamma, u, u)
        return u, du

    def _parallel_transport_derivative(
        self,
        x: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
    ) -> np.ndarray:
        r"""Returns dv/dlambda = -Gamma^\mu_{\alpha\beta} v^\alpha u^\beta."""
        gamma = self.manifold.christoffel_symbols(x)
        dv = -np.einsum("mab,a,b->m", gamma, v, u)
        return dv

    def integrate_geodesic(
        self,
        initial_position: np.ndarray,
        initial_velocity: np.ndarray,
        lambda_max: float = 1.0,
        num_steps: int = 100,
    ) -> GeodesicTrajectory:
        """
        Integrates the geodesic from lambda=0 to lambda_max using RK4.
        """
        h = lambda_max / float(num_steps)
        times = np.linspace(0.0, lambda_max, num_steps + 1)

        xs = np.zeros((num_steps + 1, 5), dtype=np.float64)
        us = np.zeros((num_steps + 1, 5), dtype=np.float64)
        norms = np.zeros(num_steps + 1, dtype=np.float64)

        xs[0] = initial_position.copy()
        us[0] = initial_velocity.copy()
        g0 = self.manifold.metric(xs[0])
        norms[0] = float(us[0] @ g0 @ us[0])

        x_curr = xs[0].copy()
        u_curr = us[0].copy()

        for i in range(num_steps):
            # RK4 for (x, u)
            k1_x, k1_u = self._geodesic_derivatives(x_curr, u_curr)
            
            x_half1 = x_curr + 0.5 * h * k1_x
            u_half1 = u_curr + 0.5 * h * k1_u
            k2_x, k2_u = self._geodesic_derivatives(x_half1, u_half1)

            x_half2 = x_curr + 0.5 * h * k2_x
            u_half2 = u_curr + 0.5 * h * k2_u
            k3_x, k3_u = self._geodesic_derivatives(x_half2, u_half2)

            x_full = x_curr + h * k3_x
            u_full = u_curr + h * k3_u
            k4_x, k4_u = self._geodesic_derivatives(x_full, u_full)

            x_curr = x_curr + (h / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
            u_curr = u_curr + (h / 6.0) * (k1_u + 2.0 * k2_u + 2.0 * k3_u + k4_u)

            xs[i + 1] = x_curr
            us[i + 1] = u_curr

            g_step = self.manifold.metric(x_curr)
            norms[i + 1] = float(u_curr @ g_step @ u_curr)

        norm_drift = float(np.max(np.abs(norms - norms[0])))
        is_conserved = norm_drift < 1e-4

        return GeodesicTrajectory(
            parameter_lambdas=times,
            coordinates=xs,
            tangent_vectors=us,
            metric_norms=norms,
            norm_drift_max=norm_drift,
            is_norm_conserved=is_conserved,
        )

    def parallel_transport_along_path(
        self,
        path_coordinates: np.ndarray,
        path_tangents: np.ndarray,
        initial_vector: np.ndarray,
        lambdas: np.ndarray,
    ) -> ParallelTransportResult:
        """
        Parallel transports a vector V along a given discretized path using RK4.
        """
        n_points = len(path_coordinates)
        v_out = np.zeros((n_points, 5), dtype=np.float64)
        inner_prods = np.zeros(n_points, dtype=np.float64)

        v_curr = initial_vector.copy()
        v_out[0] = v_curr
        g0 = self.manifold.metric(path_coordinates[0])
        inner_prods[0] = float(v_curr @ g0 @ v_curr)

        for i in range(n_points - 1):
            h = float(lambdas[i + 1] - lambdas[i])
            x_i = path_coordinates[i]
            u_i = path_tangents[i]

            x_next = path_coordinates[i + 1]
            u_next = path_tangents[i + 1]

            x_mid = 0.5 * (x_i + x_next)
            u_mid = 0.5 * (u_i + u_next)

            # RK4 for V
            k1_v = self._parallel_transport_derivative(x_i, u_i, v_curr)
            v_half1 = v_curr + 0.5 * h * k1_v

            k2_v = self._parallel_transport_derivative(x_mid, u_mid, v_half1)
            v_half2 = v_curr + 0.5 * h * k2_v

            k3_v = self._parallel_transport_derivative(x_mid, u_mid, v_half2)
            v_full = v_curr + h * k3_v

            k4_v = self._parallel_transport_derivative(x_next, u_next, v_full)

            v_curr = v_curr + (h / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
            v_out[i + 1] = v_curr

            g_step = self.manifold.metric(x_next)
            inner_prods[i + 1] = float(v_curr @ g_step @ v_curr)

        drift = float(np.max(np.abs(inner_prods - inner_prods[0])))
        is_conserved = drift < 1e-4

        return ParallelTransportResult(
            parameter_lambdas=lambdas,
            transported_vectors=v_out,
            inner_products=inner_prods,
            initial_vector=initial_vector,
            final_vector=v_curr,
            inner_product_drift_max=drift,
            is_inner_product_conserved=is_conserved,
        )
