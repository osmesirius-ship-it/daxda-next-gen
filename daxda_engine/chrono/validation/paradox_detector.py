"""
DAXDA Chrono-Synchronicity Mapping: Temporal Paradox Detector
Detects Grandfather Paradoxes, Bootstrap Paradoxes, Predestination Loops,
and Temporal Inversion anomalies with sub-5ms latency.
"""

from __future__ import annotations
import math
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from daxda_engine.chrono.geometry.temporal_space import TemporalSpace, TemporalState
from daxda_engine.chrono.validation.causal_mapper import CausalMapper


class ParadoxType(Enum):
    NONE = "NONE"
    GRANDFATHER = "GRANDFATHER"         # Future action negates its own past precondition
    BOOTSTRAP = "BOOTSTRAP"             # Information exists in closed causal loop with no origin
    PREDESTINATION = "PREDESTINATION"   # Loop enforces identical inevitable outcome
    TEMPORAL_INVERSION = "TEMPORAL_INVERSION" # Entropy inversion without retrocausal balancing


@dataclass
class ParadoxAnomaly:
    paradox_type: ParadoxType
    severity: float  # [0.0, 1.0]
    description: str
    cycle_nodes: List[str]
    offending_state_id: str
    mitigation_recommendation: str


@dataclass
class ParadoxReport:
    is_paradox_free: bool
    detection_latency_ms: float
    total_anomalies: int
    anomalies: List[ParadoxAnomaly]
    worst_severity: float
    examined_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_paradox_free": self.is_paradox_free,
            "detection_latency_ms": round(self.detection_latency_ms, 4),
            "total_anomalies": self.total_anomalies,
            "worst_severity": round(self.worst_severity, 4),
            "examined_at": self.examined_at,
            "anomalies": [
                {
                    "type": a.paradox_type.value,
                    "severity": round(a.severity, 4),
                    "description": a.description,
                    "cycle_nodes": a.cycle_nodes,
                    "offending_state_id": a.offending_state_id,
                    "mitigation": a.mitigation_recommendation,
                }
                for a in self.anomalies
            ]
        }


class ParadoxDetector:
    """
    Sub-5ms detector for temporal anomalies and causal paradoxes.
    Scans temporal state networks and causal graphs for self-contradictory causal topologies.
    """

    def __init__(self, space: TemporalSpace, causal_mapper: CausalMapper):
        self.space = space
        self.causal_mapper = causal_mapper

    def check_decision_paradox(
        self,
        candidate_state: TemporalState,
        proposed_predecessors: List[str],
    ) -> ParadoxReport:
        """
        Fast-path check for whether candidate_state creates a paradox when inserted
        with proposed_predecessors. Target latency: < 5ms.
        """
        t0 = time.perf_counter()
        anomalies: List[ParadoxAnomaly] = []

        # 1. Check for Grandfather Paradox:
        # If candidate_state targets a predecessor that is in the candidate's forward cone
        for pred_id in proposed_predecessors:
            forward_cone = self.causal_mapper.get_forward_cone(candidate_state.state_id)
            if pred_id in forward_cone:
                anomalies.append(ParadoxAnomaly(
                    paradox_type=ParadoxType.GRANDFATHER,
                    severity=0.95,
                    description=f"Candidate state {candidate_state.state_id} depends on {pred_id}, which is in its own forward cone.",
                    cycle_nodes=[candidate_state.state_id, pred_id],
                    offending_state_id=candidate_state.state_id,
                    mitigation_recommendation="Sever circular causal dependency; re-anchor predecessor to chronologically earlier branch.",
                ))

        # 2. Check for Temporal Inversion:
        # A state claiming t < pred.t without valid retrocausal phase tau
        for pred_id in proposed_predecessors:
            pred_st = self.space.get_state(pred_id)
            if pred_st:
                if candidate_state.coordinate.t < pred_st.coordinate.t:
                    # Inverted chronology: only legal if hypertemporal tau coordinate is active
                    if abs(candidate_state.coordinate.tau) < 1e-4 and abs(pred_st.coordinate.tau) < 1e-4:
                        anomalies.append(ParadoxAnomaly(
                            paradox_type=ParadoxType.TEMPORAL_INVERSION,
                            severity=0.80,
                            description=f"Candidate state t={candidate_state.coordinate.t} precedes ancestor t={pred_st.coordinate.t} without hypertemporal tau phase.",
                            cycle_nodes=[candidate_state.state_id, pred_id],
                            offending_state_id=candidate_state.state_id,
                            mitigation_recommendation="Assign valid hypertemporal tau coordinate or correct chronological timestamp.",
                        ))

        # 3. Check for Bootstrap or Predestination anomalies on circular dependencies:
        for pred_id in proposed_predecessors:
            forward_cone = self.causal_mapper.get_forward_cone(candidate_state.state_id)
            if pred_id in forward_cone:
                pred_st = self.space.get_state(pred_id)
                if pred_st and pred_st.decision_vector == candidate_state.decision_vector:
                    anomalies.append(ParadoxAnomaly(
                        paradox_type=ParadoxType.BOOTSTRAP,
                        severity=0.88,
                        description=f"Information in closed loop ({candidate_state.state_id} <-> {pred_id}) has identical vectors with no external origin.",
                        cycle_nodes=[candidate_state.state_id, pred_id],
                        offending_state_id=candidate_state.state_id,
                        mitigation_recommendation="Inject external entropy or break loop at weakest causal edge.",
                    ))


        latency_ms = (time.perf_counter() - t0) * 1000.0
        worst_sev = max([a.severity for a in anomalies], default=0.0)

        return ParadoxReport(
            is_paradox_free=len(anomalies) == 0,
            detection_latency_ms=latency_ms,
            total_anomalies=len(anomalies),
            anomalies=anomalies,
            worst_severity=worst_sev,
        )

    def scan_entire_manifold(self) -> ParadoxReport:
        """Thorough scan of all cycles and inconsistencies across the entire temporal space."""
        t0 = time.perf_counter()
        anomalies: List[ParadoxAnomaly] = []

        loops = self.causal_mapper.detect_causal_loops()
        for loop in loops:
            anomalies.append(ParadoxAnomaly(
                paradox_type=ParadoxType.PREDESTINATION,
                severity=0.75,
                description=f"Unresolved causal loop spanning {len(loop)} nodes: {loop[:5]}...",
                cycle_nodes=loop,
                offending_state_id=loop[0] if loop else "",
                mitigation_recommendation="Break cycle at lowest weight edge or apply Novikov relaxation.",
            ))

        latency_ms = (time.perf_counter() - t0) * 1000.0
        worst_sev = max([a.severity for a in anomalies], default=0.0)

        return ParadoxReport(
            is_paradox_free=len(anomalies) == 0,
            detection_latency_ms=latency_ms,
            total_anomalies=len(anomalies),
            anomalies=anomalies,
            worst_severity=worst_sev,
        )
