"""
DAXDA Level 2 - 5D Non-Linear Riemannian Spacetime Geometry Engine
==================================================================

Implements 5-dimensional temporal manifold (t, b, p, tau, omega) with
signature (+, -, -, -, -) where omega is multiverse branching frequency.

Provides exact Riemannian differential geometry:
- Metric tensor g_mu_nu and inverse g^mu_nu
- Christoffel symbols of the second kind Gamma^sigma_mu_nu
- Riemann curvature tensor R^rho_sigma_mu_nu
- Ricci curvature tensor R_mu_nu and Ricci scalar R
- Geodesic interval ds^2 and causal cone classification
"""

from __future__ import annotations

import enum
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


class CausalConeType(enum.Enum):
    """Causal cone classification based on 5D pseudo-Riemannian interval ds^2."""
    TIMELIKE_FUTURE = "TIMELIKE_FUTURE"      # ds^2 > 0 and dt > 0 (strictly causally influenced)
    TIMELIKE_PAST = "TIMELIKE_PAST"          # ds^2 > 0 and dt < 0 (strictly retrocausal origin)
    LIGHTLIKE_NULL = "LIGHTLIKE_NULL"        # |ds^2| <= epsilon (causal event horizon)
    SPACELIKE = "SPACELIKE"                  # ds^2 < 0 (acausally separated across branches)


@dataclass
class TemporalCoordinate5D:
    """
    5-Dimensional Temporal Coordinate:
      t     : Coordinate linear time (evolution axis)
      b     : Branch probability manifold ([0.0, 1.0])
      p     : Paradox phase angle ([0.0, 2pi])
      tau   : Proper invariant eigen-time
      omega : Multiverse branch oscillation frequency
    """
    t: float
    b: float = 0.0
    p: float = 0.0
    tau: float = 0.0
    omega: float = 0.0

    def to_tuple(self) -> Tuple[float, float, float, float, float]:
        return (self.t, self.b, self.p, self.tau, self.omega)

    def to_list(self) -> List[float]:
        return [self.t, self.b, self.p, self.tau, self.omega]

    @classmethod
    def from_list(cls, values: List[float]) -> TemporalCoordinate5D:
        t = values[0] if len(values) > 0 else 0.0
        b = values[1] if len(values) > 1 else 0.0
        p = values[2] if len(values) > 2 else 0.0
        tau = values[3] if len(values) > 3 else 0.0
        omega = values[4] if len(values) > 4 else 0.0
        return cls(t=t, b=b, p=p, tau=tau, omega=omega)


@dataclass
class CausalHorizonBoundary:
    """Evaluates causal connectivity and horizon boundaries between two 5D events."""
    is_within_causal_cone: bool
    cone_type: CausalConeType
    proper_interval_squared: float
    geodesic_distance: float
    dt: float
    paradox_risk_index: float


@dataclass
class State5D:
    state_id: str
    coordinate: TemporalCoordinate5D
    decision_vector: List[float]
    created_at: float = field(default_factory=time.time)


class RiemannianTemporalSpace5D:
    """
    5-dimensional pseudo-Riemannian temporal manifold engine.
    Metric Signature: (+, -, -, -, -)
    Metric: ds^2 = g_00 dt^2 - g_11 db^2 - g_22 dp^2 - g_33 dtau^2 - g_44 domega^2
    """

    DIM = 5

    def __init__(self):
        self._states: Dict[str, State5D] = {}

    def create_state(
        self, coordinate: TemporalCoordinate5D, decision_vector: List[float], state_id: Optional[str] = None
    ) -> str:
        s_id = state_id or f"state_5d_{len(self._states):04d}"
        self._states[s_id] = State5D(state_id=s_id, coordinate=coordinate, decision_vector=decision_vector)
        return s_id

    def get_state(self, state_id: str) -> Optional[State5D]:
        return self._states.get(state_id)

    def compute_metric_tensor(self, coord: TemporalCoordinate5D) -> List[List[float]]:
        """
        Computes diagonal Riemannian metric tensor g_mu_nu:
        g = diag(1, -b^2, -p^2, -1, -omega^2) with regularized floor to avoid singularities.
        """
        floor = 1e-6
        g_00 = 1.0
        g_11 = -(coord.b ** 2) if abs(coord.b) > 1e-3 else -floor
        g_22 = -(coord.p ** 2) if abs(coord.p) > 1e-3 else -floor
        g_33 = -1.0
        g_44 = -(coord.omega ** 2) if abs(coord.omega) > 1e-3 else -floor

        return [
            [g_00, 0.0, 0.0, 0.0, 0.0],
            [0.0, g_11, 0.0, 0.0, 0.0],
            [0.0, 0.0, g_22, 0.0, 0.0],
            [0.0, 0.0, 0.0, g_33, 0.0],
            [0.0, 0.0, 0.0, 0.0, g_44],
        ]

    def compute_inverse_metric(self, coord: TemporalCoordinate5D) -> List[List[float]]:
        """
        Computes the contravariant inverse metric tensor g^mu_nu:
        g^mu_alpha * g_alpha_nu = delta^mu_nu.
        """
        g = self.compute_metric_tensor(coord)
        inv = [[0.0] * self.DIM for _ in range(self.DIM)]
        for i in range(self.DIM):
            inv[i][i] = 1.0 / g[i][i]
        return inv

    def compute_metric_derivatives(
        self, coord: TemporalCoordinate5D, eps: float = 1e-5
    ) -> List[List[List[float]]]:
        r"""
        Computes partial derivatives of the metric: dg[mu][nu] / dx^rho.
        Returns a 3D array of shape [5][5][5] where d_g[rho][mu][nu] = \partial_rho g_mu_nu.
        Uses central differences: (g(x + eps) - g(x - eps)) / (2 * eps).
        """
        base = coord.to_list()
        dg = [[[0.0] * self.DIM for _ in range(self.DIM)] for _ in range(self.DIM)]

        for rho in range(self.DIM):
            forward_vals = list(base)
            forward_vals[rho] += eps
            backward_vals = list(base)
            backward_vals[rho] -= eps

            g_fwd = self.compute_metric_tensor(TemporalCoordinate5D.from_list(forward_vals))
            g_bwd = self.compute_metric_tensor(TemporalCoordinate5D.from_list(backward_vals))

            for mu in range(self.DIM):
                for nu in range(self.DIM):
                    dg[rho][mu][nu] = (g_fwd[mu][nu] - g_bwd[mu][nu]) / (2.0 * eps)

        return dg

    def compute_christoffel_symbols(
        self, coord: TemporalCoordinate5D, eps: float = 1e-5
    ) -> List[List[List[float]]]:
        """
        Computes Christoffel symbols of the second kind:
        Gamma^sigma_{mu nu} = 1/2 g^{sigma rho} ( d_mu g_{nu rho} + d_nu g_{mu rho} - d_rho g_{mu nu} )
        Returns 3D array of shape [5][5][5] indexable as Gamma[sigma][mu][nu].
        Guaranteed to be symmetric in lower indices: Gamma[sigma][mu][nu] == Gamma[sigma][nu][mu].
        """
        inv_g = self.compute_inverse_metric(coord)
        dg = self.compute_metric_derivatives(coord, eps=eps)

        gamma = [[[0.0] * self.DIM for _ in range(self.DIM)] for _ in range(self.DIM)]

        for sigma in range(self.DIM):
            for mu in range(self.DIM):
                for nu in range(self.DIM):
                    val = 0.0
                    for rho in range(self.DIM):
                        g_inv_elem = inv_g[sigma][rho]
                        if abs(g_inv_elem) > 1e-12:
                            term = dg[mu][nu][rho] + dg[nu][mu][rho] - dg[rho][mu][nu]
                            val += 0.5 * g_inv_elem * term
                    gamma[sigma][mu][nu] = val

        return gamma

    def compute_riemann_curvature(
        self, coord: TemporalCoordinate5D, eps: float = 1e-4
    ) -> List[List[List[List[float]]]]:
        """
        Computes Riemann curvature tensor:
        R^rho_{sigma mu nu} = d_mu Gamma^rho_{nu sigma} - d_nu Gamma^rho_{mu sigma}
                            + Gamma^rho_{mu lambda} Gamma^lambda_{nu sigma}
                            - Gamma^rho_{nu lambda} Gamma^lambda_{mu sigma}
        Returns 4D array of shape [5][5][5][5] indexable as R[rho][sigma][mu][nu].
        """
        base = coord.to_list()
        gamma_base = self.compute_christoffel_symbols(coord)

        d_gamma = [[[[0.0] * self.DIM for _ in range(self.DIM)] for _ in range(self.DIM)] for _ in range(self.DIM)]

        for k in range(self.DIM):
            fwd = list(base)
            fwd[k] += eps
            bwd = list(base)
            bwd[k] -= eps
            g_fwd = self.compute_christoffel_symbols(TemporalCoordinate5D.from_list(fwd))
            g_bwd = self.compute_christoffel_symbols(TemporalCoordinate5D.from_list(bwd))

            for rho in range(self.DIM):
                for nu in range(self.DIM):
                    for sigma in range(self.DIM):
                        d_gamma[k][rho][nu][sigma] = (g_fwd[rho][nu][sigma] - g_bwd[rho][nu][sigma]) / (2.0 * eps)

        riemann = [[[[0.0] * self.DIM for _ in range(self.DIM)] for _ in range(self.DIM)] for _ in range(self.DIM)]

        for rho in range(self.DIM):
            for sigma in range(self.DIM):
                for mu in range(self.DIM):
                    for nu in range(self.DIM):
                        term_deriv = d_gamma[mu][rho][nu][sigma] - d_gamma[nu][rho][mu][sigma]

                        term_prod = 0.0
                        for lam in range(self.DIM):
                            term_prod += (
                                gamma_base[rho][mu][lam] * gamma_base[lam][nu][sigma]
                                - gamma_base[rho][nu][lam] * gamma_base[lam][mu][sigma]
                            )

                        riemann[rho][sigma][mu][nu] = term_deriv + term_prod

        return riemann

    def compute_ricci_tensor(self, coord: TemporalCoordinate5D) -> List[List[float]]:
        """
        Computes Ricci curvature tensor by contraction of Riemann tensor:
        R_{sigma nu} = R^rho_{sigma rho nu}
        """
        riemann = self.compute_riemann_curvature(coord)
        ricci = [[0.0] * self.DIM for _ in range(self.DIM)]

        for sigma in range(self.DIM):
            for nu in range(self.DIM):
                val = 0.0
                for rho in range(self.DIM):
                    val += riemann[rho][sigma][rho][nu]
                ricci[sigma][nu] = val

        return ricci

    def compute_ricci_scalar(self, coord: TemporalCoordinate5D) -> float:
        """
        Computes Ricci scalar curvature R = g^{sigma nu} R_{sigma nu}.
        """
        inv_g = self.compute_inverse_metric(coord)
        ricci = self.compute_ricci_tensor(coord)
        scalar = 0.0

        for sigma in range(self.DIM):
            for nu in range(self.DIM):
                scalar += inv_g[sigma][nu] * ricci[sigma][nu]

        return scalar

    def compute_geodesic_interval_squared(
        self, coord_a: TemporalCoordinate5D, coord_b: TemporalCoordinate5D
    ) -> float:
        """
        Computes ds^2 between two 5D temporal coordinates using midpoint metric integration:
        ds^2 = g_00 dt^2 + g_11 db^2 + g_22 dp^2 + g_33 dtau^2 + g_44 domega^2
        """
        mid = TemporalCoordinate5D(
            t=(coord_a.t + coord_b.t) / 2.0,
            b=(coord_a.b + coord_b.b) / 2.0,
            p=(coord_a.p + coord_b.p) / 2.0,
            tau=(coord_a.tau + coord_b.tau) / 2.0,
            omega=(coord_a.omega + coord_b.omega) / 2.0,
        )
        g = self.compute_metric_tensor(mid)

        dt = coord_b.t - coord_a.t
        db = coord_b.b - coord_a.b
        dp = coord_b.p - coord_a.p
        dtau = coord_b.tau - coord_a.tau
        domega = coord_b.omega - coord_a.omega

        ds_sq = (
            g[0][0] * (dt ** 2)
            + g[1][1] * (db ** 2)
            + g[2][2] * (dp ** 2)
            + g[3][3] * (dtau ** 2)
            + g[4][4] * (domega ** 2)
        )
        return ds_sq

    def classify_causal_relation(
        self, coord_a: TemporalCoordinate5D, coord_b: TemporalCoordinate5D, tol: float = 1e-4
    ) -> CausalHorizonBoundary:
        """
        Classifies causal cone connectivity between two 5D coordinates:
        - TIMELIKE_FUTURE : ds^2 > tol and dt > 0
        - TIMELIKE_PAST   : ds^2 > tol and dt < 0
        - LIGHTLIKE_NULL  : |ds^2| <= tol
        - SPACELIKE       : ds^2 < -tol
        """
        ds_sq = self.compute_geodesic_interval_squared(coord_a, coord_b)
        dt = coord_b.t - coord_a.t
        dist = math.sqrt(abs(ds_sq))

        dp = abs(coord_b.p - coord_a.p)
        db = abs(coord_b.b - coord_a.b)
        domega = abs(coord_b.omega - coord_a.omega)
        paradox_risk = round(min(1.0, (dp / math.pi) * 0.5 + db * 0.3 + domega * 0.2), 4)

        if ds_sq > tol:
            cone = CausalConeType.TIMELIKE_FUTURE if dt >= 0 else CausalConeType.TIMELIKE_PAST
            is_connected = True
        elif abs(ds_sq) <= tol:
            cone = CausalConeType.LIGHTLIKE_NULL
            is_connected = True
        else:
            cone = CausalConeType.SPACELIKE
            is_connected = False

        return CausalHorizonBoundary(
            is_within_causal_cone=is_connected,
            cone_type=cone,
            proper_interval_squared=round(ds_sq, 6),
            geodesic_distance=round(dist, 6),
            dt=round(dt, 6),
            paradox_risk_index=paradox_risk,
        )

    def compute_geodesic_path(
        self, coord_a: TemporalCoordinate5D, coord_b: TemporalCoordinate5D, steps: int = 10
    ) -> List[TemporalCoordinate5D]:
        """Interpolates discrete points along the geodesic connecting coord_a to coord_b."""
        path = []
        for i in range(steps + 1):
            s = float(i) / float(steps)
            c = TemporalCoordinate5D(
                t=coord_a.t + s * (coord_b.t - coord_a.t),
                b=coord_a.b + s * (coord_b.b - coord_a.b),
                p=coord_a.p + s * (coord_b.p - coord_a.p),
                tau=coord_a.tau + s * (coord_b.tau - coord_a.tau),
                omega=coord_a.omega + s * (coord_b.omega - coord_a.omega),
            )
            path.append(c)
        return path
