"""
Real-Time AGI Agent Activity Monitor
====================================

Monitors agent actions in real time across up to 10,000 concurrent sessions,
evaluating rule signatures, anomaly scores, and Cl(16,4) geometric safety coordinates.
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field

from .rule_engine import RuleEngine, RuleMatch
from .anomaly_detector import AnomalyDetector, AnomalyScore
from .state_tracker import StateTracker
from daxda_engine.cl16_4.combinatorics.cl_space import ClSpace, CL16_4
from daxda_engine.cl16_4.validation.validator import HyperValidator, ValidationRequest, ValidationResult


@dataclass
class MonitorResult:
    """Outcome of real-time agent action monitoring."""
    agent_id: str
    action_type: str
    is_contained: bool
    is_breach_detected: bool
    latency_ms: float
    rule_matches: List[Dict[str, Any]] = field(default_factory=list)
    anomaly_score: float = 0.0
    cl16_4_valid: bool = True
    cl16_4_config: Optional[str] = None
    disposition: str = "ALLOW"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "is_contained": self.is_contained,
            "is_breach_detected": self.is_breach_detected,
            "latency_ms": self.latency_ms,
            "rule_matches": self.rule_matches,
            "anomaly_score": self.anomaly_score,
            "cl16_4_valid": self.cl16_4_valid,
            "cl16_4_config": self.cl16_4_config,
            "disposition": self.disposition,
            "timestamp": self.timestamp
        }


class AgentMonitor:
    """Real-time monitoring system for AGI agent activities."""

    def __init__(
        self,
        rule_engine: Optional[RuleEngine] = None,
        anomaly_detector: Optional[AnomalyDetector] = None,
        state_tracker: Optional[StateTracker] = None,
        cl_space: Optional[ClSpace] = None,
        soc_alerter: Optional[Any] = None
    ):
        self.rule_engine = rule_engine or RuleEngine()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.state_tracker = state_tracker or StateTracker()
        self.cl_space = cl_space or CL16_4
        self.validator = HyperValidator(space=self.cl_space)
        self.soc_alerter = soc_alerter

    def monitor_action(self, agent_id: str, action: Dict[str, Any]) -> MonitorResult:
        """
        Monitors a single agent action in real time.
        Target latency: sub-50ms for known signatures.
        """
        t0 = time.perf_counter()

        # Step 0: Check quarantine status
        if self.state_tracker.is_quarantined(agent_id):
            return MonitorResult(
                agent_id=agent_id,
                action_type=action.get("type", "unknown"),
                is_contained=True,
                is_breach_detected=True,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                disposition="QUARANTINE_DENY"
            )

        payload_str = str(action.get("payload", action.get("command", str(action))))
        action_type = action.get("type", "agent_action")

        # Step 1: Rule-based signature evaluation (< 5ms)
        rule_matches = self.rule_engine.evaluate(payload_str)
        matched_dicts = [
            {"id": m.rule_id, "name": m.rule_name, "category": m.category, "severity": m.severity}
            for m in rule_matches
        ]

        # Step 2: Anomaly detection
        if "decision_vector" in action and isinstance(action["decision_vector"], (list, tuple)):
            anomaly = self.anomaly_detector.score_vector(action["decision_vector"])
        else:
            anomaly = self.anomaly_detector.score_payload(payload_str)

        # Step 3: Cl(16,4) coordinate validation
        risk_vector = action.get("risk_vector", action.get("decision_vector", [0.5] * 16))
        cl_config_str = None
        cl_valid = True
        if len(risk_vector) == 16:
            v_req = ValidationRequest(agent_id=agent_id, decision_vector=list(float(x) for x in risk_vector))
            v_res = self.validator.validate(v_req)
            cl_valid = v_res.is_valid
            cl_config_str = str(v_res.config.indices) if v_res.config else None

        # Step 4: Decision synthesis
        breach_detected = len(rule_matches) > 0 or anomaly.is_anomalous or (not cl_valid)
        is_contained = True
        disposition = "BLOCK_AND_CONTAIN" if breach_detected else "ALLOW"

        # Update session state
        self.state_tracker.record_action(agent_id, action, risk_score=anomaly.score)

        if breach_detected:
            # Auto-quarantine on critical breach
            if any(m.severity == "critical" for m in rule_matches):
                self.state_tracker.quarantine_agent(agent_id, reason="Critical signature breach")

            # Dispatch SOC alert if configured
            if self.soc_alerter:
                try:
                    self.soc_alerter.dispatch_alert(
                        domain=action_type,
                        payload_text=payload_str[:200],
                        receipt_sha256=f"sha256_mock_{agent_id}",
                        failure_code="CONTAINMENT_BREACH_HALT"
                    )
                except Exception:
                    pass

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return MonitorResult(
            agent_id=agent_id,
            action_type=action_type,
            is_contained=is_contained,
            is_breach_detected=breach_detected,
            latency_ms=elapsed_ms,
            rule_matches=matched_dicts,
            anomaly_score=anomaly.score,
            cl16_4_valid=cl_valid,
            cl16_4_config=cl_config_str,
            disposition=disposition
        )

    async def monitor_stream(self, agent_id: str, action_generator: AsyncGenerator[Dict[str, Any], None]) -> AsyncGenerator[MonitorResult, None]:
        """Asynchronously monitors a stream of actions from an agent session."""
        async for action in action_generator:
            yield self.monitor_action(agent_id, action)
