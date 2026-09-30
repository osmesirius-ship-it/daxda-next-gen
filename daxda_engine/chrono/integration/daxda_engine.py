"""
DAXDA Chrono-Synchronicity Mapping: DAXDA Engine Adapter
Integrates temporal consistency validation and retrocausality with the core DAXDA Engine pipeline.
"""

from __future__ import annotations
import time
from typing import Dict, List, Optional, Any, Tuple
from daxda_engine.chrono.geometry.temporal_space import (
    TemporalSpace,
    TemporalState,
    TemporalCoordinate,
    TemporalDimension,
)
from daxda_engine.chrono.validation.temporal_validator import (
    TemporalValidator,
    TemporalValidationCertificate,
    TemporalDisposition,
)
from daxda_engine.chrono.integration.cl16_4_integration import Cl16_4ChronoBridge


class ChronoDAXDAAdapter:
    """
    Adapter interfacing the Chrono-Synchronicity Layer with the main DAXDA Engine.
    Provides agent decision validation, timeline state management, and certification.
    """

    def __init__(
        self,
        space: Optional[TemporalSpace] = None,
        validator: Optional[TemporalValidator] = None,
    ):
        self.space = space or TemporalSpace(dimension=TemporalDimension.D4_HYPERTEMPORAL)
        self.validator = validator or TemporalValidator(self.space)
        self.bridge = Cl16_4ChronoBridge(self.space)
        self._agent_timelines: Dict[str, List[str]] = {}

    def process_agent_decision(
        self,
        agent_id: str,
        decision_vector: List[float],
        action_name: str,
        payload: Optional[Dict[str, Any]] = None,
        future_boundary_vector: Optional[List[float]] = None,
    ) -> Tuple[bool, TemporalValidationCertificate]:
        """
        Processes an agent decision through the Chrono temporal pipeline.
        Returns: (is_approved, certificate)
        """
        current_time = time.time()
        state_id = f"STATE-{agent_id[:6]}-{int(current_time * 1000) % 1000000}"

        # Retrieve prior state for agent to establish causal predecessor
        history = self._agent_timelines.get(agent_id, [])
        predecessors = [history[-1]] if history else []

        # Construct TemporalState
        state = self.bridge.create_temporal_state_from_cl16_4(
            state_id=state_id,
            decision_vector=decision_vector,
            base_t=current_time,
            payload={"action": action_name, **(payload or {})},
        )
        state.predecessors = set(predecessors)

        # Build optional future boundary state if provided
        future_boundary_state = None
        if future_boundary_vector:
            future_coord = TemporalCoordinate(t=current_time + 10.0, b=state.coordinate.b, p=state.coordinate.p)
            future_boundary_state = TemporalState(
                state_id=f"BOUNDARY-{agent_id[:6]}",
                coordinate=future_coord,
                decision_vector=future_boundary_vector,
            )

        cert = self.validator.validate_decision(
            state=state,
            predecessor_ids=predecessors,
            future_boundary_state=future_boundary_state,
        )

        is_approved = cert.disposition == TemporalDisposition.APPROVED

        if is_approved:
            if agent_id not in self._agent_timelines:
                self._agent_timelines[agent_id] = []
            self._agent_timelines[agent_id].append(state_id)

        return is_approved, cert

    def get_agent_history(self, agent_id: str) -> List[TemporalState]:
        ids = self._agent_timelines.get(agent_id, [])
        return [self.space.get_state(sid) for sid in ids if self.space.get_state(sid)]
