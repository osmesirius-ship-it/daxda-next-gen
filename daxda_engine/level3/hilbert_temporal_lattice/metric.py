r"""
5D Metric and Levi-Civita Connection Engine.
Defines 5-dimensional spacetime-temporal manifolds with metric tensor g_{\mu\nu},
Christoffel symbols of the second kind, and Riemann/Ricci curvature tensors.
"""

from typing import Callable, Tuple
import numpy as np


class TemporalManifold5D:
    r"""
    Represents a 5-dimensional pseudo-Riemannian manifold (t, x, y, z, \tau_5)
    with metric g_{\mu\nu} of signature (-, +, +, +, +).
    """

    DIM = 5

    def __init__(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        name: str = "5D Hilbert Temporal Manifold",
    ):
        r"""
        metric_fn: function taking point x in R^5 -> symmetric 5x5 matrix g_{\mu\nu}(x).
        """
        self.metric_fn = metric_fn
        self.name = name

    @classmethod
    def flat_minkowski_5d(cls, phase_scale: float = 1.0) -> "TemporalManifold5D":
        """Flat 5D Minkowski-Kaluza spacetime: ds^2 = -dt^2 + dx^2 + dy^2 + dz^2 + phase_scale * dtau^2."""
        def g_flat(x: np.ndarray) -> np.ndarray:
            g = np.diag([-1.0, 1.0, 1.0, 1.0, float(phase_scale)])
            return g
        return cls(metric_fn=g_flat, name="Flat 5D Minkowski-Kaluza")

    @classmethod
    def curved_temporal_soliton(
        cls,
        mass_parameter: float = 0.1,
        frequency_omega: float = 1.0,
    ) -> "TemporalManifold5D":
        r"""
        Curved 5D temporal manifold with metric:
        g_{00} = -(1 - 2M / (r^2 + 1))
        g_{11} = g_{22} = g_{33} = 1 + 2M / (r^2 + 1)
        g_{44} = 1 + M \cos(\omega t) / (r^2 + 1)
        g_{04} = g_{40} = 0.5 M \sin(\omega \tau_5) / (r^2 + 1)
        """
        def g_curved(x: np.ndarray) -> np.ndarray:
            t, x_pos, y_pos, z_pos, tau = x[0], x[1], x[2], x[3], x[4]
            r2 = float(x_pos**2 + y_pos**2 + z_pos**2)
            denom = r2 + 1.0
            pot = float(mass_parameter) / denom

            g = np.zeros((5, 5), dtype=np.float64)
            g[0, 0] = -(1.0 - 2.0 * pot)
            g[1, 1] = 1.0 + 2.0 * pot
            g[2, 2] = 1.0 + 2.0 * pot
            g[3, 3] = 1.0 + 2.0 * pot
            g[4, 4] = 1.0 + pot * np.cos(frequency_omega * t)
            
            # Off-diagonal temporal cross-coupling
            cross = 0.5 * pot * np.sin(frequency_omega * tau)
            g[0, 4] = cross
            g[4, 0] = cross
            return g

        return cls(metric_fn=g_curved, name="Curved 5D Temporal Soliton")

    def metric(self, x: np.ndarray) -> np.ndarray:
        r"""Evaluates metric tensor g_{\mu\nu} at coordinate x (shape (5,))."""
        g = self.metric_fn(x)
        if g.shape != (5, 5):
            raise ValueError(f"Metric must be 5x5, got {g.shape}")
        return (g + g.T) * 0.5

    def inverse_metric(self, x: np.ndarray) -> np.ndarray:
        r"""Evaluates inverse metric tensor g^{\mu\nu} at coordinate x."""
        g = self.metric(x)
        return np.linalg.inv(g)

    def metric_derivatives(self, x: np.ndarray, eps: float = 1e-5) -> np.ndarray:
        r"""
        Computes partial derivatives \partial_\alpha g_{\mu\nu} using central finite differences.
        Returns tensor dg of shape (5, 5, 5) where dg[alpha, mu, nu] = \partial_\alpha g_{\mu\nu}.
        """
        dg = np.zeros((5, 5, 5), dtype=np.float64)
        for alpha in range(5):
            dx_plus = x.copy()
            dx_plus[alpha] += eps
            dx_minus = x.copy()
            dx_minus[alpha] -= eps

            g_plus = self.metric(dx_plus)
            g_minus = self.metric(dx_minus)
            dg[alpha, :, :] = (g_plus - g_minus) / (2.0 * eps)
        return dg

    def christoffel_symbols(self, x: np.ndarray, eps: float = 1e-5) -> np.ndarray:
        r"""
        Computes the Levi-Civita connection coefficients (Christoffel symbols of the 2nd kind):
        \Gamma^\sigma_{\mu\nu} = \frac{1}{2} g^{\sigma\rho} (\partial_\mu g_{\nu\rho} + \partial_\nu g_{\mu\rho} - \partial_\rho g_{\mu\nu}).
        Returns tensor of shape (5, 5, 5) indexed as [sigma, mu, nu].
        """
        g_inv = self.inverse_metric(x)
        dg = self.metric_derivatives(x, eps=eps)

        gamma = np.zeros((5, 5, 5), dtype=np.float64)
        for sigma in range(5):
            for mu in range(5):
                for nu in range(5):
                    term = 0.0
                    for rho in range(5):
                        # \partial_\mu g_{\nu\rho} is dg[mu, nu, rho]
                        # \partial_\nu g_{\mu\rho} is dg[nu, mu, rho]
                        # \partial_\rho g_{\mu\nu} is dg[rho, mu, nu]
                        bracket = dg[mu, nu, rho] + dg[nu, mu, rho] - dg[rho, mu, nu]
                        term += g_inv[sigma, rho] * bracket
                    gamma[sigma, mu, nu] = 0.5 * term
        return gamma

    def riemann_tensor(self, x: np.ndarray, eps: float = 1e-4) -> np.ndarray:
        r"""
        Computes Riemann curvature tensor:
        R^\rho_{\ \sigma\mu\nu} = \partial_\mu \Gamma^\rho_{\nu\sigma} - \partial_\nu \Gamma^\rho_{\mu\sigma}
                               + \Gamma^\rho_{\mu\lambda} \Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda} \Gamma^\lambda_{\mu\sigma}.
        Returns tensor of shape (5, 5, 5, 5) indexed as [rho, sigma, mu, nu].
        """
        gamma = self.christoffel_symbols(x, eps=eps)
        
        # Finite difference of Gamma: dGamma[alpha, rho, mu, nu] = \partial_\alpha \Gamma^\rho_{\mu\nu}
        d_gamma = np.zeros((5, 5, 5, 5), dtype=np.float64)
        for alpha in range(5):
            dx_plus = x.copy()
            dx_plus[alpha] += eps
            dx_minus = x.copy()
            dx_minus[alpha] -= eps
            g_p = self.christoffel_symbols(dx_plus, eps=eps)
            g_m = self.christoffel_symbols(dx_minus, eps=eps)
            d_gamma[alpha] = (g_p - g_m) / (2.0 * eps)

        R = np.zeros((5, 5, 5, 5), dtype=np.float64)
        for rho in range(5):
            for sigma in range(5):
                for mu in range(5):
                    for nu in range(5):
                        # \partial_\mu \Gamma^\rho_{\nu\sigma} - \partial_\nu \Gamma^\rho_{\mu\sigma}
                        term1 = d_gamma[mu, rho, nu, sigma] - d_gamma[nu, rho, mu, sigma]
                        # \Gamma^\rho_{\mu\lambda} \Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda} \Gamma^\lambda_{\mu\sigma}
                        term2 = 0.0
                        for lam in range(5):
                            term2 += gamma[rho, mu, lam] * gamma[lam, nu, sigma] - gamma[rho, nu, lam] * gamma[lam, mu, sigma]
                        R[rho, sigma, mu, nu] = term1 + term2
        return R

    def ricci_tensor(self, x: np.ndarray, eps: float = 1e-4) -> np.ndarray:
        r"""Ricci tensor R_{\sigma\nu} = R^\rho_{\ \sigma\rho\nu}."""
        R = self.riemann_tensor(x, eps=eps)
        ric = np.zeros((5, 5), dtype=np.float64)
        for sigma in range(5):
            for nu in range(5):
                ric[sigma, nu] = float(np.sum([R[rho, sigma, rho, nu] for rho in range(5)]))
        return ric

    def ricci_scalar(self, x: np.ndarray, eps: float = 1e-4) -> float:
        r"""Ricci scalar curvature R = g^{\sigma\nu} R_{\sigma\nu}."""
        g_inv = self.inverse_metric(x)
        ric = self.ricci_tensor(x, eps=eps)
        return float(np.sum(g_inv * ric))
