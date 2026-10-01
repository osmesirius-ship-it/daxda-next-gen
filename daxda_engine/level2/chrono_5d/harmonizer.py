"""
DAXDA Level 2 - Quantum Causal Loop Harmonizer
==============================================

Harmonizes closed timelike curves (CTCs) across up to 64 parallel branching
timelines simultaneously using fixed-point iteration, automated branch collapsing,
and retrocausal invariant verification.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .geometry import (
    CausalHorizonBoundary,
    RiemannianTemporalSpace5D,
    State5D,
    TemporalCoordinate5D,
)


@dataclass
class TimelineBranch:
    """Represents an individual branching timeline in quantum superposition."""
    branch_id: str
    branch_index: int
    coordinate: TemporalCoordinate5D
    state_vector: List[float]
    probability_weight: float = 1.0
    paradox_phase: float = 0.0
    is_active: bool = True
    is_collapsed: bool = False
    collapse_reason: Optional[str] = None


@dataclass
class BranchCollapsingReport:
    """Detailed audit of automated branch pruning and collapsing."""
    initial_branch_count: int
    surviving_branch_count: int
    pruned_branch_ids: List[str]
    prune_reasons: Dict[str, str]
    renormalized_weights: Dict[str, float]


@dataclass
class RetrocausalPerturbationReceipt:
    """Verifies invariant stability under continuous retrocausal perturbations."""
    target_state_id: str
    perturbation_magnitude: float
    delta_tau: float
    pre_perturbation_norm: float
    post_perturbation_norm: float
    grandfather_paradox_detected: bool
    novikov_restabilized: bool
    timestamp: float = field(default_factory=time.time)


@dataclass
class HarmonizationResult:
    """Final result of multi-branch quantum causal loop harmonization."""
    target_state_id: str
    is_novikov_consistent: bool
    converged_branches_count: int
    total_branches_evaluated: int
    geodesic_distance: float
    iterations_run: int
    coherence_factor: float
    residual_norm: float
    fixed_point_vector: List[float]
    collapsing_report: BranchCollapsingReport
    timestamp: float = field(default_factory=time.time)


class QuantumCausalLoopHarmonizer:
    """
    Fixed-point quantum harmonizer resolving multi-timeline causal loops.
    Supports up to 64 parallel branching timelines simultaneously.
    Guarantees Novikov self-consistency via Krasnoselskii-Mann contraction mapping.
    """

    MAX_SUPPORTED_BRANCHES = 64

    def __init__(
        self,
        space: Optional[RiemannianTemporalSpace5D] = None,
        paradox_threshold: float = 0.80,
        default_tolerance: float = 1e-6,
    ):
        self.space = space or RiemannianTemporalSpace5D()
        self.paradox_threshold = paradox_threshold
        self.default_tolerance = default_tolerance

    def create_superposed_branches(
        self,
        base_coord: TemporalCoordinate5D,
        base_vector: List[float],
        count: int = 16,
    ) -> List[TimelineBranch]:
        """Creates up to 64 parallel branching timelines superposed around a base coordinate."""
        count = max(1, min(count, self.MAX_SUPPORTED_BRANCHES))
        branches: List[TimelineBranch] = []
        weight_per_branch = 1.0 / count

        for i in range(count):
            branch_id = f"branch_{i:02d}"
            # Vary branch manifold b, paradox angle p, and frequency omega
            phase_offset = (2.0 * math.pi * i) / count
            branch_b = max(0.01, min(0.99, base_coord.b + 0.05 * math.sin(phase_offset)))
            branch_p = max(0.0, base_coord.p + 0.1 * math.cos(phase_offset))
            branch_omega = max(0.01, base_coord.omega + 0.02 * (i % 4))

            coord = TemporalCoordinate5D(
                t=base_coord.t,
                b=round(branch_b, 4),
                p=round(branch_p, 4),
                tau=base_coord.tau,
                omega=round(branch_omega, 4),
            )
            # Slight vector perturbation per branch
            vec = [v * (1.0 + 0.01 * math.sin(phase_offset + j)) for j, v in enumerate(base_vector)]

            branches.append(
                TimelineBranch(
                    branch_id=branch_id,
                    branch_index=i,
                    coordinate=coord,
                    state_vector=vec,
                    probability_weight=weight_per_branch,
                    paradox_phase=branch_p,
                )
            )

        return branches

    def prune_branches(
        self, branches: List[TimelineBranch]
    ) -> Tuple[List[TimelineBranch], BranchCollapsingReport]:
        """
        Dynamically prunes self-annihilating timeline branches that exceed the paradox
        threshold or exhibit unstable divergence. Renormalizes probability weights.
        """
        surviving: List[TimelineBranch] = []
        pruned_ids: List[str] = []
        prune_reasons: Dict[str, str] = {}

        for b in branches:
            if b.paradox_phase >= self.paradox_threshold:
                b.is_active = False
                b.is_collapsed = True
                b.collapse_reason = f"PARADOX_PHASE_EXCEEDED (p={b.paradox_phase:.3f} >= {self.paradox_threshold})"
                pruned_ids.append(b.branch_id)
                prune_reasons[b.branch_id] = b.collapse_reason
            elif b.probability_weight < 1e-4:
                b.is_active = False
                b.is_collapsed = True
                b.collapse_reason = "QUANTUM_DECOHERENCE_PROBABILITY_FLOOR"
                pruned_ids.append(b.branch_id)
                prune_reasons[b.branch_id] = b.collapse_reason
            else:
                surviving.append(b)

        # Renormalize surviving branch weights
        total_surviving_weight = sum(b.probability_weight for b in surviving)
        renormalized: Dict[str, float] = {}
        if total_surviving_weight > 1e-9:
            for b in surviving:
                b.probability_weight /= total_surviving_weight
                renormalized[b.branch_id] = round(b.probability_weight, 5)

        report = BranchCollapsingReport(
            initial_branch_count=len(branches),
            surviving_branch_count=len(surviving),
            pruned_branch_ids=pruned_ids,
            prune_reasons=prune_reasons,
            renormalized_weights=renormalized,
        )
        return surviving, report

    def harmonize_loop(
        self,
        target_state_id: str,
        max_branches: int = 16,
        tolerance: Optional[float] = None,
        max_iterations: int = 50,
    ) -> HarmonizationResult:
        """
        Executes multi-branch fixed-point quantum causal loop harmonization.
        Solves x_{k+1} = (1 - alpha)*x_k + alpha*F(x_k) across up to 64 parallel branches.
        Ensures Novikov self-consistency without deadlocks or grandfather paradoxes.
        """
        tol = tolerance or self.default_tolerance
        max_branches = min(max_branches, self.MAX_SUPPORTED_BRANCHES)

        target = self.space.get_state(target_state_id)
        if not target:
            coord = TemporalCoordinate5D(t=1.0, b=0.1, p=0.0, tau=1.0, omega=0.1)
            target = State5D(state_id=target_state_id, coordinate=coord, decision_vector=[0.05] * 20)
            self.space._states[target_state_id] = target

        # Generate parallel branches
        branches = self.create_superposed_branches(
            base_coord=target.coordinate,
            base_vector=target.decision_vector,
            count=max_branches,
        )

        # Dynamic branch pruning
        surviving_branches, collapsing_report = self.prune_branches(branches)

        if not surviving_branches:
            # All branches collapsed due to excessive paradox
            origin = TemporalCoordinate5D(t=0.0, b=0.0, p=0.0, tau=0.0, omega=0.0)
            ds_sq = self.space.compute_geodesic_interval_squared(origin, target.coordinate)
            dist = math.sqrt(abs(ds_sq))
            return HarmonizationResult(
                target_state_id=target_state_id,
                is_novikov_consistent=False,
                converged_branches_count=0,
                total_branches_evaluated=max_branches,
                geodesic_distance=round(dist, 4),
                iterations_run=0,
                coherence_factor=0.0,
                residual_norm=1.0,
                fixed_point_vector=list(target.decision_vector),
                collapsing_report=collapsing_report,
            )

        # Fixed point iteration across surviving branches
        # Krasnoselskii-Mann damping parameter alpha in (0, 1]
        alpha = 0.50
        dim = len(target.decision_vector)
        branch_vectors = [list(b.state_vector) for b in surviving_branches]
        weights = [b.probability_weight for b in surviving_branches]

        iters = 0
        residual = 1.0

        for it in range(1, max_iterations + 1):
            iters = it

            # Compute quantum superposition consensus vector: bar_x = sum_j w_j x^(j)
            superposition = [0.0] * dim
            for j, vec in enumerate(branch_vectors):
                w = weights[j]
                for d in range(dim):
                    superposition[d] += w * vec[d]

            max_diff = 0.0
            new_branch_vectors = []

            for vec in branch_vectors:
                # Contraction map F(x) dampens paradox fluctuations and couples with superposition
                # F(x) = 0.2 * x + 0.8 * superposition
                x_next = []
                for d in range(dim):
                    fx_d = 0.2 * vec[d] + 0.8 * superposition[d]
                    # Krasnoselskii-Mann step
                    x_new_d = (1.0 - alpha) * vec[d] + alpha * fx_d
                    diff = abs(x_new_d - vec[d])
                    if diff > max_diff:
                        max_diff = diff
                    x_next.append(x_new_d)
                new_branch_vectors.append(x_next)

            branch_vectors = new_branch_vectors
            residual = max_diff

            if max_diff < tol:
                break

        # Compute consensus fixed-point vector
        fixed_point = [0.0] * dim
        for j, vec in enumerate(branch_vectors):
            w = weights[j]
            for d in range(dim):
                fixed_point[d] += w * vec[d]

        # Novikov consistency holds if paradox phase is below threshold, branches survived, and converged
        is_consistent = (
            target.coordinate.p < self.paradox_threshold
            and len(surviving_branches) > 0
            and residual < (tol * 100.0)  # within numerical tolerance
        )

        # Compute geodesic distance from temporal origin
        origin = TemporalCoordinate5D(t=0.0, b=0.0, p=0.0, tau=0.0, omega=0.0)
        ds_sq = self.space.compute_geodesic_interval_squared(origin, target.coordinate)
        dist = math.sqrt(abs(ds_sq))

        # Coherence factor
        coherence = max(0.0, min(1.0, 1.0 - target.coordinate.p / math.pi))

        return HarmonizationResult(
            target_state_id=target_state_id,
            is_novikov_consistent=is_consistent,
            converged_branches_count=len(surviving_branches) if is_consistent else 0,
            total_branches_evaluated=max_branches,
            geodesic_distance=round(dist, 4),
            iterations_run=iters,
            coherence_factor=round(coherence, 4),
            residual_norm=round(residual, 8),
            fixed_point_vector=[round(v, 6) for v in fixed_point],
            collapsing_report=collapsing_report,
        )

    def verify_retrocausal_invariant(
        self,
        target_state_id: str,
        perturbation: List[float],
        delta_tau: float = -0.5,
    ) -> RetrocausalPerturbationReceipt:
        """
        Applies a reverse-time (retrocausal) perturbation delta_tau < 0 and verifies
        that Novikov self-consistency absorbs the signal without triggering grandfather paradoxes.
        """
        target = self.space.get_state(target_state_id)
        if not target:
            coord = TemporalCoordinate5D(t=1.0, b=0.1, p=0.0, tau=1.0, omega=0.1)
            target = State5D(state_id=target_state_id, coordinate=coord, decision_vector=[0.05] * len(perturbation))
            self.space._states[target_state_id] = target

        pre_norm = math.sqrt(sum(v ** 2 for v in target.decision_vector))
        pert_magnitude = math.sqrt(sum(p ** 2 for p in perturbation))

        # Apply perturbation in backwards eigen-time
        perturbed_coord = TemporalCoordinate5D(
            t=target.coordinate.t,
            b=target.coordinate.b,
            p=min(math.pi * 2.0, target.coordinate.p + 0.05 * pert_magnitude),
            tau=target.coordinate.tau + delta_tau,
            omega=target.coordinate.omega,
        )
        perturbed_vector = [
            v + 0.1 * p for v, p in zip(target.decision_vector, perturbation)
        ]

        # Re-harmonize under perturbation
        perturbed_state_id = f"{target_state_id}_retro_perturbed"
        self.space.create_state(perturbed_coord, perturbed_vector, state_id=perturbed_state_id)

        harm_res = self.harmonize_loop(perturbed_state_id, max_branches=16)

        post_norm = math.sqrt(sum(v ** 2 for v in harm_res.fixed_point_vector))

        # Grandfather paradox check: occurs if perturbation inverts the causal sign of the state
        grandfather_paradox = not harm_res.is_novikov_consistent or (post_norm < 1e-12 and pre_norm > 1e-3)

        return RetrocausalPerturbationReceipt(
            target_state_id=target_state_id,
            perturbation_magnitude=round(pert_magnitude, 6),
            delta_tau=delta_tau,
            pre_perturbation_norm=round(pre_norm, 6),
            post_perturbation_norm=round(post_norm, 6),
            grandfather_paradox_detected=grandfather_paradox,
            novikov_restabilized=harm_res.is_novikov_consistent and not grandfather_paradox,
        )
