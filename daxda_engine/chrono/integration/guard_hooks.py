"""
DAXDA Chrono-Synchronicity Mapping: Guard Hooks Module
Security interception hooks executing pre-decision and post-decision temporal gating.
"""

from __future__ import annotations
import time
from typing import Dict, List, Optional, Tuple, Any
from daxda_engine.chrono.integration.daxda_engine import ChronoDAXDAAdapter
from daxda_engine.chrono.validation.temporal_validator import TemporalDisposition


class ChronoGuardHooks:
    """
    Security validation hooks interfacing with DAXDA Guard.
    Executes pre-flight temporal invariant checks and post-flight causal anchoring.
    """

    def __init__(self, adapter: Optional[ChronoDAXDAAdapter] = None):
        self.adapter = adapter or ChronoDAXDAAdapter()
        self._denied_count: int = 0
        self._allowed_count: int = 0

    def pre_decision_check(
        self,
        agent_id: str,
        action_name: str,
        proposed_vector: List[float],
        future_boundary_vector: Optional[List[float]] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Pre-execution security hook.
        Verifies that proposed decision does not generate paradoxes or retrocausal violations.
        Returns: (allow: bool, reason: str, metadata: dict)
        """
        is_approved, cert = self.adapter.process_agent_decision(
            agent_id=agent_id,
            decision_vector=proposed_vector,
            action_name=action_name,
            future_boundary_vector=future_boundary_vector,
        )

        if is_approved:
            self._allowed_count += 1
            return True, "TEMPORALLY_COHERENT", cert.to_dict()
        else:
            self._denied_count += 1
            reason = f"TEMPORAL_GATE_DENIED: {cert.disposition.value}"
            return False, reason, cert.to_dict()

    def post_decision_check(
        self,
        agent_id: str,
        action_name: str,
        execution_status: str,
        observed_vector: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Post-execution security hook.
        Anchors execution outcome into causal graph and monitors state divergence.
        """
        history = self.adapter.get_agent_history(agent_id)
        last_state = history[-1] if history else None

        divergence = 0.0
        if last_state and observed_vector:
            dim = min(len(last_state.decision_vector), len(observed_vector))
            if dim > 0:
                divergence = sum(abs(a - b) for a, b in zip(last_state.decision_vector[:dim], observed_vector[:dim]))

        return {
            "agent_id": agent_id,
            "action": action_name,
            "execution_status": execution_status,
            "recorded_states": len(history),
            "vector_divergence": round(divergence, 6),
            "timestamp": time.time(),
        }

    def get_stats(self) -> Dict[str, int]:
        return {
            "allowed_decisions": self._allowed_count,
            "denied_decisions": self._denied_count,
        }
