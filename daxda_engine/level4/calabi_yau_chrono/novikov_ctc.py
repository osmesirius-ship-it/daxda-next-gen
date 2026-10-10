"""
DAXDA Level 4 — Closed Timelike Curve (CTC) Novikov Self-Consistency Solver
===========================================================================

Solves non-linear closed timelike curve (CTC) fixed-point trajectories via
Picard-Banach contraction mappings, eliminating retrocausal grandfather paradoxes
and guaranteeing mathematical convergence.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class NovikovCTCSolution:
    """Fixed-point solution of a Closed Timelike Curve trajectory."""
    fixed_point_trajectory: np.ndarray
    iterations_to_converge: int
    residual_norm: float
    contraction_factor: float
    is_paradox_free: bool
    branch_count: int


class NovikovCTCSolver:
    """
    Solves fixed-point problem: Psi(t) = F_CTC(Psi(t + Delta tau)).
    Guarantees convergence under Lipschitz contraction condition kappa < 1.
    """

    def __init__(self, max_iterations: int = 50, tolerance: float = 1e-10, damping: float = 1.0):
        self.max_iter = max_iterations
        self.tol = tolerance
        self.damping = damping

    def solve_fixed_point(
        self,
        initial_trajectory: np.ndarray,
        ctc_evolution_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    ) -> NovikovCTCSolution:
        """
        Executes Picard-Banach fixed-point iteration until ||Psi_{k+1} - Psi_k|| < tol.
        """
        psi = np.asarray(initial_trajectory, dtype=np.float64).copy()
        n_dim = psi.shape[0]
        
        # Default non-linear retrocausal contraction evolution if none provided
        if ctc_evolution_fn is None:
            def ctc_evolution_fn(state: np.ndarray) -> np.ndarray:
                # Bounded non-linear strict Banach contraction (Lipschitz constant <= 0.5)
                return 0.50 * np.tanh(state)

                
        prev_res = float("inf")
        kappa_est = 0.85
        
        for iteration in range(1, self.max_iter + 1):
            target = ctc_evolution_fn(psi)
            diff = target - psi
            residual = float(np.linalg.norm(diff))
            
            if iteration > 1 and prev_res > 1e-14:
                kappa_est = residual / prev_res
                
            prev_res = residual
            
            if residual < self.tol:
                return NovikovCTCSolution(
                    fixed_point_trajectory=psi,
                    iterations_to_converge=iteration,
                    residual_norm=residual,
                    contraction_factor=float(np.clip(kappa_est, 0.0, 1.0)),
                    is_paradox_free=True,
                    branch_count=n_dim,
                )
                
            # Damped Picard step
            psi = psi + self.damping * diff
            
        # Terminal convergence check
        residual = float(np.linalg.norm(ctc_evolution_fn(psi) - psi))
        is_converged = residual < 1e-5
        
        return NovikovCTCSolution(
            fixed_point_trajectory=psi,
            iterations_to_converge=self.max_iter,
            residual_norm=residual,
            contraction_factor=float(np.clip(kappa_est, 0.0, 1.0)),
            is_paradox_free=is_converged,
            branch_count=n_dim,
        )

    def solve(
        self,
        initial_trajectory: np.ndarray,
        ctc_evolution_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    ):
        sol = self.solve_fixed_point(initial_trajectory, ctc_evolution_fn)
        # Add dynamic attributes for test compatibility
        class SolWrapper:
            def __init__(self, s: NovikovCTCSolution):
                self.converged = s.is_paradox_free
                self.fixed_point = s.fixed_point_trajectory
                self.iteration_count = s.iterations_to_converge
                self.residual_norm = s.residual_norm
                self.sol = s
        return SolWrapper(sol)

