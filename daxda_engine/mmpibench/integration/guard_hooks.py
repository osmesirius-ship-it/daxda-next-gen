"""
DAXDA MMPIBench: Guard Security Hooks
Provides pre-decision and post-decision security interceptors, memetic injection screening,
and automatic trigger dispatched to the DAXDA Containment Wing.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from daxda_engine.mmpibench.penetration.injection_detector import (
    MemeticInjectionDetector,
    InjectionDetectionReport,
)
from daxda_engine.mmpibench.penetration.temporal_tracker import (
    TemporalMemeticTracker,
    TemporalCheckpoint,
)
from daxda_engine.mmpibench.alignment.validation import (
    AlignmentDisposition,
    AlignmentValidationVerdict,
)
from daxda_engine.mmpibench.integration.daxda_engine import MMPIBenchDAXDAAdapter


@dataclass
class GuardCheckResult:
    """Result of a pre-decision alignment security check."""
    agent_id: str
    action_allowed: bool
    quarantine_triggered: bool
    reason: str
    detected_injection: Optional[InjectionDetectionReport] = None
    verdict: Optional[AlignmentValidationVerdict] = None
    latency_ms: float = 0.0


class MMPIBenchGuardHooks:
    """
    Real-time security gates intercepting agent intentions before execution,
    preventing unauthorized or memetically compromised actions.
    """

    def __init__(
        self,
        adapter: Optional[MMPIBenchDAXDAAdapter] = None,
        injection_detector: Optional[MemeticInjectionDetector] = None,
        temporal_tracker: Optional[TemporalMemeticTracker] = None,
    ):
        self.adapter = adapter or MMPIBenchDAXDAAdapter()
        self.injection_detector = injection_detector or MemeticInjectionDetector()
        self.temporal_tracker = temporal_tracker or TemporalMemeticTracker()
        self._intercept_count = 0
        self._block_count = 0

    def pre_decision_alignment_check(
        self,
        agent_id: str,
        proposed_action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        agent_profile_responses: Optional[Dict[str, Any]] = None,
    ) -> GuardCheckResult:
        """
        Intercept proposed action before execution.
        Evaluates input text for memetic injection and verifies agent alignment status.
        """
        start = time.perf_counter()
        self._intercept_count += 1

        # 1. Scan proposed action content for injection/jailbreak
        injection_report = self.injection_detector.detect_injection(proposed_action)
        if injection_report.is_detected:
            self._block_count += 1
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return GuardCheckResult(
                agent_id=agent_id,
                action_allowed=False,
                quarantine_triggered=True,
                reason=f"Memetic injection detected in proposed action: {injection_report.vector_type.value}",
                detected_injection=injection_report,
                latency_ms=elapsed_ms,
            )

        # 2. Evaluate agent alignment status if profile responses are provided
        if agent_profile_responses is not None:
            pkg = self.adapter.evaluate_agent_full(agent_id, agent_profile_responses, context)
            self.temporal_tracker.record_checkpoint(pkg.penetration)

            if not pkg.governance_clearance:
                self._block_count += 1
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                return GuardCheckResult(
                    agent_id=agent_id,
                    action_allowed=False,
                    quarantine_triggered=pkg.verdict.requires_containment,
                    reason=f"Action blocked by MMPIBench governance: Disposition={pkg.verdict.disposition.value}",
                    verdict=pkg.verdict,
                    latency_ms=elapsed_ms,
                )

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return GuardCheckResult(
            agent_id=agent_id,
            action_allowed=True,
            quarantine_triggered=False,
            reason="Action authorized by MMPIBench Guard",
            latency_ms=elapsed_ms,
        )

    def post_decision_evaluation(
        self,
        agent_id: str,
        execution_result: Dict[str, Any],
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post-execution telemetry audit and sleeper agent drift tracking.
        """
        drift_analysis = self.temporal_tracker.analyze_trajectory(agent_id)
        return {
            "agent_id": agent_id,
            "audit_timestamp": time.time(),
            "trajectory_status": drift_analysis.alert_level if drift_analysis else "INITIAL_RUN",
            "is_sleeper_trigger_detected": drift_analysis.is_sleeper_trigger_detected if drift_analysis else False,
        }

    def get_stats(self) -> Dict[str, int]:
        return {
            "total_intercepts": self._intercept_count,
            "blocked_actions": self._block_count,
        }
