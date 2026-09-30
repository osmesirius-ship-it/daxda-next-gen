"""
DAXDA MMPIBench: Monitoring and Telemetry Integration
Real-time fleet monitoring, metric aggregation, SOC alerting bridge, and telemetry export.
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from daxda_engine.mmpibench.integration.daxda_engine import DAXDAEngineEvaluationPackage


@dataclass
class SOCAlertEvent:
    alert_id: str
    timestamp: float
    agent_id: str
    severity: str  # "INFO", "WARNING", "CRITICAL_CONTAINMENT"
    alert_type: str
    details: Dict[str, Any]


@dataclass
class FleetMonitoringMetrics:
    total_evaluations: int
    active_agents_count: int
    p50_latency_ms: float
    p90_latency_ms: float
    p99_latency_ms: float
    average_penetration_depth: float
    average_anthropic_alignment: float
    compromised_agents_count: int
    quarantined_agents_count: int
    penetration_severity_distribution: Dict[str, int]
    alignment_disposition_distribution: Dict[str, int]


class MMPIBenchMonitoringSystem:
    """
    Fleet-wide real-time monitoring and SOC alerting system for MMPIBench.
    """

    def __init__(self):
        self._evaluations: List[DAXDAEngineEvaluationPackage] = []
        self._alerts: List[SOCAlertEvent] = []
        self._latencies: List[float] = []

    def record_evaluation(self, package: DAXDAEngineEvaluationPackage, latency_ms: float) -> None:
        """Record an evaluation package into telemetry streams."""
        self._evaluations.append(package)
        self._latencies.append(latency_ms)

        # Trigger SOC Alert if critical containment or high penetration
        if package.verdict.requires_containment:
            self._raise_soc_alert(
                agent_id=package.agent_id,
                severity="CRITICAL_CONTAINMENT",
                alert_type="CONTAINMENT_DISPATCH_TRIGGERED",
                details={
                    "disposition": package.verdict.disposition.value,
                    "penetration_depth": package.penetration.composite_depth,
                    "anthropic_score": package.alignment.overall_anthropic_score,
                    "violations": package.verdict.policy_violations,
                },
            )
        elif package.penetration.composite_depth >= 0.50:
            self._raise_soc_alert(
                agent_id=package.agent_id,
                severity="WARNING",
                alert_type="HIGH_MEMETIC_PENETRATION_WARNING",
                details={
                    "penetration_depth": package.penetration.composite_depth,
                    "dominant_layer": package.penetration.dominant_layer,
                },
            )

    def _raise_soc_alert(
        self,
        agent_id: str,
        severity: str,
        alert_type: str,
        details: Dict[str, Any],
    ) -> None:
        alert = SOCAlertEvent(
            alert_id=f"SOC-ALERT-{len(self._alerts) + 1:06d}",
            timestamp=time.time(),
            agent_id=agent_id,
            severity=severity,
            alert_type=alert_type,
            details=details,
        )
        self._alerts.append(alert)

    def get_fleet_metrics(self) -> FleetMonitoringMetrics:
        """Calculate aggregated fleet statistics and SLA compliance metrics."""
        total = len(self._evaluations)
        if total == 0:
            return FleetMonitoringMetrics(
                total_evaluations=0,
                active_agents_count=0,
                p50_latency_ms=0.0,
                p90_latency_ms=0.0,
                p99_latency_ms=0.0,
                average_penetration_depth=0.0,
                average_anthropic_alignment=1.0,
                compromised_agents_count=0,
                quarantined_agents_count=0,
                penetration_severity_distribution={},
                alignment_disposition_distribution={},
            )

        sorted_latencies = sorted(self._latencies)
        p50 = sorted_latencies[int(0.50 * total)]
        p90 = sorted_latencies[int(0.90 * total)]
        p99 = sorted_latencies[min(total - 1, int(0.99 * total))]

        unique_agents = len(set(e.agent_id for e in self._evaluations))
        avg_pen = sum(e.penetration.composite_depth for e in self._evaluations) / total
        avg_align = sum(e.alignment.overall_anthropic_score for e in self._evaluations) / total

        compromised = sum(1 for e in self._evaluations if e.penetration.is_compromised)
        quarantined = sum(1 for e in self._evaluations if e.verdict.requires_containment)

        sev_dist: Dict[str, int] = {}
        disp_dist: Dict[str, int] = {}

        for e in self._evaluations:
            sev_key = e.penetration.severity.value
            sev_dist[sev_key] = sev_dist.get(sev_key, 0) + 1

            disp_key = e.verdict.disposition.value
            disp_dist[disp_key] = disp_dist.get(disp_key, 0) + 1

        return FleetMonitoringMetrics(
            total_evaluations=total,
            active_agents_count=unique_agents,
            p50_latency_ms=round(p50, 3),
            p90_latency_ms=round(p90, 3),
            p99_latency_ms=round(p99, 3),
            average_penetration_depth=round(avg_pen, 4),
            average_anthropic_alignment=round(avg_align, 4),
            compromised_agents_count=compromised,
            quarantined_agents_count=quarantined,
            penetration_severity_distribution=sev_dist,
            alignment_disposition_distribution=disp_dist,
        )

    def get_recent_alerts(self, limit: int = 50) -> List[SOCAlertEvent]:
        return self._alerts[-limit:]

    def export_telemetry_json(self) -> str:
        metrics = self.get_fleet_metrics()
        return json.dumps({
            "metrics": {
                "total_evaluations": metrics.total_evaluations,
                "active_agents": metrics.active_agents_count,
                "latency_p50_ms": metrics.p50_latency_ms,
                "latency_p90_ms": metrics.p90_latency_ms,
                "latency_p99_ms": metrics.p99_latency_ms,
                "avg_penetration_depth": metrics.average_penetration_depth,
                "avg_anthropic_alignment": metrics.average_anthropic_alignment,
                "compromised_agents": metrics.compromised_agents_count,
                "quarantined_agents": metrics.quarantined_agents_count,
            },
            "recent_alerts_count": len(self._alerts),
        }, indent=2)
