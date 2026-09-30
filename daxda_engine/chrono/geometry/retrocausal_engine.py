"""
DAXDA Chrono-Synchronicity Mapping: Geometric Retrocausality Engine
Implements backward causation fields, geodesic propagation, and Novikov self-consistency resolution.
"""

from __future__ import annotations
import math
import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from daxda_engine.chrono.geometry.temporal_space import (
    TemporalCoordinate,
    TemporalState,
    TemporalSpace,
)


@dataclass
class RetrocausalInfluence:
    """Represents a backward-in-time causal influence edge."""
    source_state_id: str       # Future state asserting boundary condition
    target_state_id: str       # Past state being constrained
    influence_strength: float  # Attenuation factor in [0.0, 1.0]
    constraint_vector: List[float] # Target subspace constraint
    is_novikov_consistent: bool = True
    geodesic_distance: float = 0.0
    paradox_risk: float = 0.0


@dataclass
class TemporalPath:
    """A trajectory through temporal space."""
    path_states: List[str]
    total_geodesic_length: float
    is_causally_valid: bool
    contains_ctc: bool  # Closed Timelike Curve
    consistency_score: float


class RetrocausalEngine:
    """
    Geometric engine for computing retrocausal relationships and boundary constraints.
    Enforces that past agent decisions satisfy terminal containment invariants
    propagated backwards along temporal geodesics.
    """

    def __init__(
        self,
        space: TemporalSpace,
        c_t: float = 1.0,
        decay_lambda: float = 0.15,
        paradox_threshold: float = 0.75,
    ):
        self.space = space
        self.c_t = c_t
        self.decay_lambda = decay_lambda
        self.paradox_threshold = paradox_threshold
        self._retro_influences: Dict[str, List[RetrocausalInfluence]] = {}

    def compute_retrocausal_influence(
        self,
        future_state: TemporalState,
        past_state: TemporalState
    ) -> RetrocausalInfluence:
        """
        Compute backward influence from future_state (t_future) to past_state (t_past).
        Requires future_state.coordinate.t >= past_state.coordinate.t.
        """
        c_fut = future_state.coordinate
        c_past = past_state.coordinate
        dt = c_fut.t - c_past.t
        if dt < 0:
            # If inverted, swap conceptually or treat as forward influence
            dt = abs(dt)

        interval = c_fut.interval_squared(c_past, self.c_t)
        euclid = c_fut.euclidean_distance(c_past)

        # Attenuation decreases exponentially with Euclidean/proper distance
        strength = math.exp(-self.decay_lambda * max(euclid, 0.001))

        # Dot product / vector divergence between future constraint and past decision
        v_fut = future_state.decision_vector
        v_past = past_state.decision_vector
        dot = sum(a * b for a, b in zip(v_fut, v_past)) if v_fut and v_past else 1.0
        norm_f = math.sqrt(sum(a * a for a in v_fut)) or 1.0
        norm_p = math.sqrt(sum(b * b for b in v_past)) or 1.0
        cosine_sim = dot / (norm_f * norm_p)

        # Paradox risk increases if interval is spacelike (violates lightcone)
        # or if cosine similarity indicates direct contradiction of future invariant
        paradox_risk = 0.0
        if interval > 0:  # Spacelike separation
            paradox_risk += 0.35 * min(1.0, interval)
        if cosine_sim < 0:  # Invariant divergence / negative alignment
            paradox_risk += 0.50 + 0.45 * abs(cosine_sim)

        is_consistent = paradox_risk < self.paradox_threshold

        influence = RetrocausalInfluence(
            source_state_id=future_state.state_id,
            target_state_id=past_state.state_id,
            influence_strength=round(strength, 6),
            constraint_vector=v_fut,
            is_novikov_consistent=is_consistent,
            geodesic_distance=round(euclid, 6),
            paradox_risk=round(min(1.0, paradox_risk), 6),
        )

        if past_state.state_id not in self._retro_influences:
            self._retro_influences[past_state.state_id] = []
        self._retro_influences[past_state.state_id].append(influence)
        past_state.retrocausal_influences.add(future_state.state_id)

        return influence

    def propagate_future_boundary(
        self,
        terminal_state: TemporalState,
        max_depth_steps: int = 50,
        temporal_window: float = 60.0,
    ) -> List[RetrocausalInfluence]:
        """
        Propagate future invariant boundary conditions backward to all past states
        within the past lightcone of terminal_state.
        """
        t_term = terminal_state.coordinate.t
        past_states = self.space.query_interval(max(0.0, t_term - temporal_window), t_term)
        influences: List[RetrocausalInfluence] = []

        for p_state in past_states:
            if p_state.state_id == terminal_state.state_id:
                continue
            # Check if within past lightcone
            if self.space.c_t > 0:
                ds2 = terminal_state.coordinate.interval_squared(p_state.coordinate, self.space.c_t)
                if ds2 <= 0:  # Timelike / null connected
                    infl = self.compute_retrocausal_influence(terminal_state, p_state)
                    influences.append(infl)

        return influences

    def solve_novikov_fixed_point(
        self,
        loop_state_ids: List[str],
        max_iterations: int = 25,
        tolerance: float = 1e-4
    ) -> Tuple[bool, List[float], float]:
        """
        Novikov Self-Consistency Principle Solver:
        Evaluates a potential causal loop / CTC across `loop_state_ids`.
        Determines whether a stable fixed point exists: f(x) = x with zero invariant breakdown.
        Returns: (is_consistent, converged_equilibrium_vector, residual_error)
        """
        if not loop_state_ids:
            return True, [], 0.0

        states = [self.space.get_state(sid) for sid in loop_state_ids]
        valid_states = [s for s in states if s is not None]
        if len(valid_states) < 2:
            return True, valid_states[0].decision_vector if valid_states else [], 0.0

        dim = len(valid_states[0].decision_vector)
        # Average vector across the loop
        current_v = [0.0] * dim
        for st in valid_states:
            for i, val in enumerate(st.decision_vector[:dim]):
                current_v[i] += val / len(valid_states)

        residual = 1.0
        for _ in range(max_iterations):
            next_v = [0.0] * dim
            for st in valid_states:
                # Apply contraction mapping towards self-consistent state
                for i in range(dim):
                    st_val = st.decision_vector[i] if i < len(st.decision_vector) else 0.0
                    next_v[i] += 0.5 * (current_v[i] + st_val) / len(valid_states)
            
            diff = math.sqrt(sum((next_v[i] - current_v[i]) ** 2 for i in range(dim)))
            current_v = next_v
            residual = diff
            if diff < tolerance:
                return True, current_v, diff

        # If residual did not converge, loop is paradoxical
        return False, current_v, residual

    def find_temporal_geodesic(
        self,
        start_state_id: str,
        end_state_id: str,
        allow_retrocausal: bool = True
    ) -> Optional[TemporalPath]:
        """
        Find shortest geodesic path through temporal state graph using A* search.
        Accounts for forward causal edges, branching, and retrocausal transitions.
        """
        start_state = self.space.get_state(start_state_id)
        end_state = self.space.get_state(end_state_id)
        if not start_state or not end_state:
            return None

        # Priority queue: (f_score, current_state_id, path_list)
        open_set: List[Tuple[float, str, List[str]]] = []
        h_start = start_state.coordinate.euclidean_distance(end_state.coordinate)
        heapq.heappush(open_set, (h_start, start_state_id, [start_state_id]))

        g_scores: Dict[str, float] = {start_state_id: 0.0}
        visited: Set[str] = set()

        while open_set:
            f_score, curr_id, path = heapq.heappop(open_set)
            if curr_id == end_state_id:
                # Path found
                is_ctc = len(path) > len(set(path))
                consistency = 1.0 - (0.5 if is_ctc else 0.0)
                return TemporalPath(
                    path_states=path,
                    total_geodesic_length=g_scores.get(curr_id, 0.0),
                    is_causally_valid=True,
                    contains_ctc=is_ctc,
                    consistency_score=consistency,
                )

            if curr_id in visited and len(path) > 1:
                continue
            visited.add(curr_id)

            curr_state = self.space.get_state(curr_id)
            if not curr_state:
                continue

            # Neighbors: successors (forward) + retrocausal targets (backward)
            neighbors: List[Tuple[str, float]] = []
            for succ_id in curr_state.successors:
                succ = self.space.get_state(succ_id)
                if succ:
                    d = curr_state.coordinate.euclidean_distance(succ.coordinate)
                    neighbors.append((succ_id, d))

            if allow_retrocausal:
                for retro_id in curr_state.retrocausal_influences:
                    retro = self.space.get_state(retro_id)
                    if retro:
                        d = curr_state.coordinate.euclidean_distance(retro.coordinate) * 1.25
                        neighbors.append((retro_id, d))

            for n_id, step_cost in neighbors:
                tentative_g = g_scores[curr_id] + step_cost
                if n_id not in g_scores or tentative_g < g_scores[n_id]:
                    g_scores[n_id] = tentative_g
                    n_state = self.space.get_state(n_id)
                    h = n_state.coordinate.euclidean_distance(end_state.coordinate) if n_state else 0.0
                    heapq.heappush(open_set, (tentative_g + h, n_id, path + [n_id]))

        return None

    def get_retrocausal_influences_for_state(self, state_id: str) -> List[RetrocausalInfluence]:
        return self._retro_influences.get(state_id, [])
