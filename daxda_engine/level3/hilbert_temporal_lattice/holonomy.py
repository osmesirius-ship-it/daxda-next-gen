"""
Holonomy Phase Shift Calculation Engine.
Computes path-ordered holonomy transformations along closed loops in 5D manifolds,
verifying geometric phase shifts and Stokes-Cartan curvature relations.
"""

from dataclasses import dataclass
from typing import Callable, Tuple
import math
import numpy as np
from .metric import TemporalManifold5D
from .geodesic import GeodesicParallelTransportSolver


@dataclass(frozen=True)
class HolonomyLoopResult:
    """Stores the holonomy computation result along a closed loop."""
    loop_name: str
    num_loop_points: int
    holonomy_matrix: np.ndarray       # shape (5, 5)
    trace: float
    eigenvalues: np.ndarray          # shape (5,)
    holonomy_phase_shift: float      # radians
    is_trivial_holonomy: bool
    riemann_predicted_shift: float
    stokes_discrepancy: float


class HolonomyPhaseCalculator:
    r"""
    Calculates the holonomy group transformation U(C) \in SO(1, 4)
    along a closed loop C: [0, 2\pi] -> M^5:
    U(C) = \mathcal{P} \exp \left( - \oint_C \Gamma^\mu_{\alpha\beta} dx^\beta \right).
    """

    def __init__(self, manifold: TemporalManifold5D):
        self.manifold = manifold
        self.solver = GeodesicParallelTransportSolver(manifold)

    def generate_planar_circle_loop(
        self,
        center: np.ndarray,
        radius: float,
        plane_indices: Tuple[int, int] = (1, 2),
        num_points: int = 200,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generates coordinates x(s) and tangents dx/ds for a circle in the specified 2D plane.
        """
        mu, nu = plane_indices
        s = np.linspace(0.0, 2.0 * math.pi, num_points + 1)
        coords = np.zeros((num_points + 1, 5), dtype=np.float64)
        tangents = np.zeros((num_points + 1, 5), dtype=np.float64)

        for i, angle in enumerate(s):
            x = center.copy()
            x[mu] += radius * math.cos(angle)
            x[nu] += radius * math.sin(angle)
            coords[i] = x

            dx = np.zeros(5, dtype=np.float64)
            dx[mu] = -radius * math.sin(angle)
            dx[nu] = radius * math.cos(angle)
            tangents[i] = dx

        return coords, tangents, s

    def compute_loop_holonomy(
        self,
        loop_coords: np.ndarray,
        loop_tangents: np.ndarray,
        lambdas: np.ndarray,
        loop_name: str = "Planar Closed Loop",
    ) -> HolonomyLoopResult:
        """
        Transports all 5 standard basis vectors around the closed loop to reconstruct
        the 5x5 holonomy matrix U(C).
        """
        n_dim = 5
        U = np.zeros((n_dim, n_dim), dtype=np.float64)

        for basis_idx in range(n_dim):
            e_k = np.zeros(n_dim, dtype=np.float64)
            e_k[basis_idx] = 1.0

            res = self.solver.parallel_transport_along_path(
                path_coordinates=loop_coords,
                path_tangents=loop_tangents,
                initial_vector=e_k,
                lambdas=lambdas,
            )
            # The transported basis vector is the basis_idx-th column of U
            U[:, basis_idx] = res.final_vector

        tr = float(np.trace(U))
        eigvals = np.linalg.eigvals(U)

        # Holonomy phase angle: max phase among complex conjugate eigenvalues
        angles = [abs(float(np.angle(ev))) for ev in eigvals]
        phase_shift = float(np.max(angles))

        # Check if trivial (identity matrix)
        is_trivial = bool(np.linalg.norm(U - np.eye(n_dim)) < 1e-3)

        # Estimate Riemann curvature area term at loop center
        center = loop_coords[0]
        R = self.manifold.riemann_tensor(center)
        # Approximate loop area: radius^2 * pi
        loop_diam = float(np.max(np.linalg.norm(loop_coords - center, axis=1)))
        area = math.pi * (loop_diam / 2.0)**2
        # Max R component in the plane
        r_pred = float(np.max(np.abs(R))) * area
        discrepancy = abs(phase_shift - r_pred)

        return HolonomyLoopResult(
            loop_name=loop_name,
            num_loop_points=len(loop_coords),
            holonomy_matrix=U,
            trace=tr,
            eigenvalues=eigvals,
            holonomy_phase_shift=phase_shift,
            is_trivial_holonomy=is_trivial,
            riemann_predicted_shift=r_pred,
            stokes_discrepancy=discrepancy,
        )
