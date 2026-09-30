"""
DAXDA Chrono-Synchronicity Mapping: Synchronicity Detector Module
Detects meaningful, non-causal temporal correlations (Jungian acausal synchronicity)
across parallel agents, isolated containment environments, and spacelike-separated nodes.
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from daxda_engine.chrono.geometry.temporal_space import (
    TemporalCoordinate,
    TemporalState,
    TemporalSpace,
)


@dataclass
class SynchronicityEvent:
    """Represents a detected meaningful acausal temporal correlation."""
    event_id: str
    state_a_id: str
    state_b_id: str
    synchronicity_score: float  # In [0.0, 1.0]
    spacelike_interval: float  # ds^2 > 0
    time_delta: float           # |t_a - t_b|
    cosine_similarity: float    # Vector alignment in decision space
    p_value: float              # Statistical significance
    is_anomaly: bool            # True if score exceeds threshold
    detected_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "state_a_id": self.state_a_id,
            "state_b_id": self.state_b_id,
            "synchronicity_score": self.synchronicity_score,
            "spacelike_interval": self.spacelike_interval,
            "time_delta": self.time_delta,
            "cosine_similarity": self.cosine_similarity,
            "p_value": self.p_value,
            "is_anomaly": self.is_anomaly,
            "detected_at": self.detected_at,
            "metadata": self.metadata,
        }


class SynchronicityDetector:
    """
    Detector for meaningful acausal synchronicity across agent decision streams.
    Calculates:
      S(A, B) = CosineSim(V_A, V_B) * exp(- (t_A - t_B)^2 / (2 * sigma_t^2)) * (1 - CausalCoupling)
    """

    def __init__(
        self,
        space: TemporalSpace,
        temporal_coincidence_sigma: float = 2.0,  # 2.0 seconds window
        anomaly_threshold: float = 0.85,
        min_cosine_alignment: float = 0.70,
    ):
        self.space = space
        self.temporal_coincidence_sigma = temporal_coincidence_sigma
        self.anomaly_threshold = anomaly_threshold
        self.min_cosine_alignment = min_cosine_alignment
        self._detected_events: List[SynchronicityEvent] = []

    def compute_synchronicity(
        self,
        state_a: TemporalState,
        state_b: TemporalState,
        direct_causal_coupling: float = 0.0,
    ) -> Optional[SynchronicityEvent]:
        """
        Evaluate pair of states for acausal synchronicity.
        Returns SynchronicityEvent if candidate correlation is identified.
        """
        if state_a.state_id == state_b.state_id:
            return None

        coord_a = state_a.coordinate
        coord_b = state_b.coordinate

        dt = abs(coord_a.t - coord_b.t)
        interval = coord_a.interval_squared(coord_b, self.space.c_t)

        # Synchronicity requires spacelike or uncoupled separation
        if interval <= 0 and direct_causal_coupling > 0.5:
            # Standard forward causality dominates; not an acausal synchronicity
            return None

        # Compute cosine similarity of decision vectors
        va = state_a.decision_vector
        vb = state_b.decision_vector
        if not va or not vb:
            return None

        dot = sum(x * y for x, y in zip(va, vb))
        norm_a = math.sqrt(sum(x * x for x in va)) or 1.0
        norm_b = math.sqrt(sum(y * y for y in vb)) or 1.0
        cosine_sim = dot / (norm_a * norm_b)

        if cosine_sim < self.min_cosine_alignment:
            return None

        # Temporal coincidence gaussian factor
        time_factor = math.exp(-(dt ** 2) / (2.0 * (self.temporal_coincidence_sigma ** 2)))

        # Acausality factor (1 - direct causal link)
        acausal_factor = max(0.0, 1.0 - direct_causal_coupling)

        # Composite Synchronicity Score
        score = cosine_sim * time_factor * acausal_factor
        score = max(0.0, min(1.0, score))

        # Empirical p-value estimation based on random vector alignment
        dim = max(len(va), 1)
        expected_rand_dot = 1.0 / math.sqrt(dim)
        z = (cosine_sim - expected_rand_dot) / (1.0 / math.sqrt(dim))
        p_val = max(1e-6, 0.5 * math.erfc(z / math.sqrt(2.0)))

        is_anomaly = score >= self.anomaly_threshold

        event_id = f"SYNC-{state_a.state_id[:6]}-{state_b.state_id[:6]}-{int(time.time() * 1000) % 100000}"
        event = SynchronicityEvent(
            event_id=event_id,
            state_a_id=state_a.state_id,
            state_b_id=state_b.state_id,
            synchronicity_score=round(score, 6),
            spacelike_interval=round(interval, 6),
            time_delta=round(dt, 6),
            cosine_similarity=round(cosine_sim, 6),
            p_value=round(p_val, 6),
            is_anomaly=is_anomaly,
            metadata={
                "dim_a": coord_a.to_dict(),
                "dim_b": coord_b.to_dict(),
            }
        )

        if is_anomaly:
            self._detected_events.append(event)

        return event

    def scan_recent_window(
        self,
        t_center: float,
        window_radius: float = 5.0,
        limit_pairs: int = 500,
    ) -> List[SynchronicityEvent]:
        """
        Scan all states within [t_center - window_radius, t_center + window_radius]
        for synchronous resonances across parallel timelines or branches.
        """
        states = self.space.query_interval(t_center - window_radius, t_center + window_radius)
        events: List[SynchronicityEvent] = []
        n = len(states)
        evaluated = 0

        for i in range(n):
            for j in range(i + 1, n):
                if evaluated >= limit_pairs:
                    break
                st_a = states[i]
                st_b = states[j]
                
                # Check for direct causal link
                is_causally_linked = (st_b.state_id in st_a.successors) or (st_a.state_id in st_b.successors)
                coupling = 1.0 if is_causally_linked else 0.0

                ev = self.compute_synchronicity(st_a, st_b, direct_causal_coupling=coupling)
                if ev and ev.is_anomaly:
                    events.append(ev)
                evaluated += 1

        return events

    def get_detected_events(self) -> List[SynchronicityEvent]:
        return list(self._detected_events)

    def clear(self) -> None:
        self._detected_events.clear()
