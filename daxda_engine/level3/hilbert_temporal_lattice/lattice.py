r"""
5D Hilbert Temporal Lattice Engine.
Implements discretized 5D spacetime-temporal lattices \mathcal{H}_T,
Laplace-Beltrami diffusion operators, and causal diamond interval evaluations.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
from .metric import TemporalManifold5D


@dataclass(frozen=True)
class LatticeIntervalResult:
    """Spacetime interval between two lattice events."""
    point_a: np.ndarray
    point_b: np.ndarray
    spacetime_interval_ds2: float
    is_timelike: bool
    is_spacelike: bool
    is_null_lightlike: bool


class HilbertTemporalLattice:
    r"""
    Discrete 5D Hilbert temporal lattice \mathcal{H}_T with coordinate dimensions:
    (t, x, y, z, \tau_5).
    """

    def __init__(
        self,
        grid_shape: Tuple[int, int, int, int, int] = (5, 5, 5, 5, 5),
        grid_spacings: Tuple[float, float, float, float, float] = (0.2, 0.2, 0.2, 0.2, 0.2),
        manifold: TemporalManifold5D = None,
    ):
        self.grid_shape = grid_shape
        self.grid_spacings = grid_spacings
        self.manifold = manifold or TemporalManifold5D.flat_minkowski_5d()
        self.num_nodes = int(np.prod(grid_shape))

    def evaluate_interval(self, point_a: np.ndarray, point_b: np.ndarray) -> LatticeIntervalResult:
        r"""
        Evaluates the 5D pseudo-Riemannian interval ds^2 = g_{\mu\nu} dx^\mu dx^\nu.
        """
        midpoint = 0.5 * (point_a + point_b)
        g = self.manifold.metric(midpoint)
        dx = point_b - point_a
        ds2 = float(dx @ g @ dx)

        timelike = ds2 < -1e-8
        spacelike = ds2 > 1e-8
        null_like = abs(ds2) <= 1e-8

        return LatticeIntervalResult(
            point_a=point_a,
            point_b=point_b,
            spacetime_interval_ds2=ds2,
            is_timelike=timelike,
            is_spacelike=spacelike,
            is_null_lightlike=null_like,
        )

    def laplace_beltrami_1d_time(
        self,
        field_values: np.ndarray,
        time_index: int = 0,
    ) -> np.ndarray:
        r"""
        Computes the discrete 2nd order Laplace-Beltrami temporal operator on a field:
        \Delta_0 \Phi \approx \frac{\Phi(t+\Delta t) - 2\Phi(t) + \Phi(t-\Delta t)}{(\Delta t)^2}.
        """
        dt = self.grid_spacings[time_index]
        laplacian = np.zeros_like(field_values)
        laplacian[1:-1] = (field_values[2:] - 2.0 * field_values[1:-1] + field_values[:-2]) / (dt**2)
        # Boundary Neumann conditions
        laplacian[0] = laplacian[1]
        laplacian[-1] = laplacian[-2]
        return laplacian

    def simulate_wave_propagation(
        self,
        initial_state: np.ndarray,
        num_steps: int = 50,
        dt: float = 0.05,
        wave_speed: float = 1.0,
    ) -> np.ndarray:
        r"""
        Simulates 1D temporal wave propagation using finite differences:
        \partial_t^2 \psi = c^2 \nabla^2 \psi.
        """
        psi = initial_state.copy()
        psi_prev = initial_state.copy()
        c2 = (wave_speed * dt)**2

        history = [psi.copy()]

        for _ in range(num_steps):
            psi_next = np.zeros_like(psi)
            # 1D second spatial derivative
            d2 = np.zeros_like(psi)
            d2[1:-1] = psi[2:] - 2.0 * psi[1:-1] + psi[:-2]
            d2[0] = d2[1]
            d2[-1] = d2[-2]

            psi_next = 2.0 * psi - psi_prev + c2 * d2
            psi_prev = psi.copy()
            psi = psi_next.copy()
            history.append(psi.copy())

        return np.array(history)
