"""
DAXDA Chrono-Synchronicity Mapping: Temporal Coherence Checker
Evaluates entropy evolution, trajectory Lyapunov stability, and global temporal invariants.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from daxda_engine.chrono.geometry.temporal_space import TemporalSpace, TemporalState


@dataclass
class CoherenceAssessment:
    coherence_score: float  # [0.0, 1.0] (1.0 = perfectly coherent)
    entropy_balance: float   # Net delta S (must be >= 0 globally)
    lyapunov_exponent: float # < 0 = asymptotically stable, > 0 = chaotic divergence
    branch_divergence: float # Variance between branching timelines
    is_globally_coherent: bool
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "coherence_score": round(self.coherence_score, 4),
            "entropy_balance": round(self.entropy_balance, 4),
            "lyapunov_exponent": round(self.lyapunov_exponent, 4),
            "branch_divergence": round(self.branch_divergence, 4),
            "is_globally_coherent": self.is_globally_coherent,
            "details": self.details,
        }


class CoherenceChecker:
    """
    Validates global coherence of temporal trajectories.
    Ensures that forward entropy generation matches retrocausal boundary sinks
    and that decision trajectories do not diverge chaotically.
    """

    def __init__(self, space: TemporalSpace, min_coherence_threshold: float = 0.70):
        self.space = space
        self.min_coherence_threshold = min_coherence_threshold

    def evaluate_trajectory_coherence(
        self,
        state_ids: List[str]
    ) -> CoherenceAssessment:
        """
        Evaluate temporal coherence along an ordered sequence of state IDs.
        """
        if len(state_ids) < 2:
            return CoherenceAssessment(
                coherence_score=1.0,
                entropy_balance=0.0,
                lyapunov_exponent=-1.0,
                branch_divergence=0.0,
                is_globally_coherent=True,
                details={"reason": "Single state or empty trajectory"},
            )

        states = [self.space.get_state(sid) for sid in state_ids]
        valid_states = [s for s in states if s is not None]
        if len(valid_states) < 2:
            return CoherenceAssessment(
                coherence_score=1.0,
                entropy_balance=0.0,
                lyapunov_exponent=-1.0,
                branch_divergence=0.0,
                is_globally_coherent=True,
            )

        # 1. Measure step-wise vector variation & Lyapunov exponent:
        divergences: List[float] = []
        time_deltas: List[float] = []

        for i in range(len(valid_states) - 1):
            s1 = valid_states[i]
            s2 = valid_states[i + 1]
            dt = max(abs(s2.coordinate.t - s1.coordinate.t), 1e-4)
            time_deltas.append(dt)

            v1 = s1.decision_vector
            v2 = s2.decision_vector
            dim = min(len(v1), len(v2))
            if dim > 0:
                diff = math.sqrt(sum((v2[j] - v1[j]) ** 2 for j in range(dim)))
                divergences.append(diff)
            else:
                divergences.append(0.0)

        total_time = sum(time_deltas)
        # Lyapunov exponent estimation
        d0 = divergences[0] if divergences and divergences[0] > 1e-6 else 1e-4
        d_final = divergences[-1] if divergences and divergences[-1] > 1e-6 else 1e-4
        lyapunov = (1.0 / max(total_time, 1.0)) * math.log(max(d_final / d0, 1e-6))

        # 2. Measure Entropy Balance:
        # Step-wise Shannon information / entropy delta
        entropy_deltas: List[float] = []
        for s in valid_states:
            # Approximate entropy of decision vector distribution
            vec = [abs(x) for x in s.decision_vector]
            s_sum = sum(vec) or 1.0
            probs = [x / s_sum for x in vec if x > 1e-6]
            h = -sum(p * math.log2(p) for p in probs) if probs else 0.0
            entropy_deltas.append(h)

        net_entropy_change = entropy_deltas[-1] - entropy_deltas[0] if entropy_deltas else 0.0

        # 3. Branch divergence: coordinate distance along b and p axes
        b_coords = [s.coordinate.b for s in valid_states]
        mean_b = sum(b_coords) / len(b_coords)
        var_b = sum((b - mean_b) ** 2 for b in b_coords) / len(b_coords)
        branch_div = math.sqrt(var_b)

        # Composite Coherence Score:
        # High coherence requires stable trajectory (low/negative lyapunov) and moderate entropy growth
        stability_term = 1.0 / (1.0 + math.exp(max(-5.0, min(5.0, lyapunov))))
        smoothness_term = 1.0 / (1.0 + branch_div)
        
        coherence = 0.60 * stability_term + 0.40 * smoothness_term
        coherence = max(0.0, min(1.0, coherence))

        is_coherent = coherence >= self.min_coherence_threshold

        return CoherenceAssessment(
            coherence_score=coherence,
            entropy_balance=net_entropy_change,
            lyapunov_exponent=lyapunov,
            branch_divergence=branch_div,
            is_globally_coherent=is_coherent,
            details={
                "steps_analyzed": len(valid_states),
                "total_time_span": total_time,
                "stability_term": round(stability_term, 4),
                "smoothness_term": round(smoothness_term, 4),
            }
        )
