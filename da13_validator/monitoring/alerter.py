"""
DA13 Cluster Alerter
====================

Detects cluster performance degradation, node outages, queue saturation,
and SLA breaches, triggering alerts to the DAXDA SOC alerting infrastructure.
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ClusterAlert:
    alert_id: str
    severity: str  # "critical", "high", "medium", "low"
    alert_type: str
    message: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DA13ClusterAlerter:
    """Monitors cluster SLA thresholds and emits prioritized alerts."""

    def __init__(self, soc_alerter=None):
        self.soc_alerter = soc_alerter
        self.active_alerts: List[ClusterAlert] = []
        self.alert_history: List[ClusterAlert] = []

    def check_sla_and_alert(
        self,
        p99_latency_ms: float,
        failed_worker_count: int,
        queue_depth: int,
        availability_pct: float
    ) -> List[ClusterAlert]:
        """Evaluates SLA health metrics and generates alerts if thresholds are breached."""
        new_alerts: List[ClusterAlert] = []

        # 1. P99 Latency SLA breach (> 1000ms)
        if p99_latency_ms > 1000.0:
            alert = ClusterAlert(
                alert_id=f"ALT-LATENCY-{time.time_ns()}",
                severity="high",
                alert_type="P99_LATENCY_BREACH",
                message=f"P99 latency ({p99_latency_ms:.2f}ms) breached 1000ms SLA",
                metadata={"p99_latency_ms": p99_latency_ms}
            )
            new_alerts.append(alert)

        # 2. Node failure (> 0 failed workers)
        if failed_worker_count > 0:
            alert = ClusterAlert(
                alert_id=f"ALT-NODE-{time.time_ns()}",
                severity="critical" if failed_worker_count > 2 else "high",
                alert_type="WORKER_NODE_FAILED",
                message=f"{failed_worker_count} worker node(s) failed or timed out",
                metadata={"failed_worker_count": failed_worker_count}
            )
            new_alerts.append(alert)

        # 3. Queue backlog saturation (> 500 tasks)
        if queue_depth > 500:
            alert = ClusterAlert(
                alert_id=f"ALT-QUEUE-{time.time_ns()}",
                severity="medium",
                alert_type="QUEUE_DEPTH_SATURATED",
                message=f"Task queue depth ({queue_depth}) saturated",
                metadata={"queue_depth": queue_depth}
            )
            new_alerts.append(alert)

        # 4. Availability SLA breach (< 99.99%)
        if availability_pct < 99.99:
            alert = ClusterAlert(
                alert_id=f"ALT-AVAIL-{time.time_ns()}",
                severity="critical",
                alert_type="AVAILABILITY_SLA_BREACH",
                message=f"Cluster availability ({availability_pct:.3f}%) dropped below 99.99% SLA",
                metadata={"availability_pct": availability_pct}
            )
            new_alerts.append(alert)

        for a in new_alerts:
            self._dispatch_alert(a)

        return new_alerts

    def _dispatch_alert(self, alert: ClusterAlert) -> None:
        """Dispatches alert to connected SOC alerter or local log."""
        self.active_alerts.append(alert)
        self.alert_history.append(alert)

        if self.soc_alerter and hasattr(self.soc_alerter, "dispatch_containment_alert"):
            try:
                self.soc_alerter.dispatch_containment_alert(
                    agent_id="da13_validator_cluster",
                    category="cluster_telemetry",
                    pattern=alert.message,
                    severity=alert.severity,
                    metadata=alert.metadata
                )
            except Exception:
                pass
