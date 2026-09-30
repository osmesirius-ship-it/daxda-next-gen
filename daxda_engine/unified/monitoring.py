"""
DAXDA Unified Master Engine - Monitoring & SOC Alerting System
=============================================================

Provides real-time telemetry aggregation, Prometheus metrics export,
and enterprise SOC incident correlation for the Five-Fold Unified Engine.
"""

from __future__ import annotations

import collections
import json
import time
from typing import Any, Callable, Deque, Dict, List, Optional

from .models import UnifiedGovernanceVerdict, UnifiedVerdict


class UnifiedMasterMonitor:
    """
    Continuous monitoring, metrics generation, and enterprise SOC alerting
    for the DAXDA Unified Master Engine.
    """

    def __init__(self, incident_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.incident_callback = incident_callback
        self._total_count = 0
        self._verdict_counts: Dict[str, int] = {
            UnifiedVerdict.PERMIT.value: 0,
            UnifiedVerdict.QUARANTINE.value: 0,
            UnifiedVerdict.TERMINATE.value: 0,
        }
        self._stage_latency_accum: Dict[str, float] = {
            "stage1_clifford_ms": 0.0,
            "stage2_containment_ms": 0.0,
            "stage3_dax_ms": 0.0,
            "stage4_chrono_ms": 0.0,
            "stage5_mmpibench_ms": 0.0,
        }
        self._incidents: Deque[Dict[str, Any]] = collections.deque(maxlen=1000)

    def record_verdict(self, verdict: UnifiedGovernanceVerdict) -> None:
        """Records an evaluated verdict, tracks metrics, and fires alerts if warranted."""
        self._total_count += 1
        self._verdict_counts[verdict.verdict.value] += 1

        for stage, lat in verdict.stage_latencies_ms.items():
            if stage in self._stage_latency_accum:
                self._stage_latency_accum[stage] += lat

        # Check for incident trigger conditions
        if verdict.verdict == UnifiedVerdict.TERMINATE or verdict.stage2_containment.is_breach_detected:
            self._trigger_soc_incident(verdict, severity="CRITICAL")
        elif verdict.verdict == UnifiedVerdict.QUARANTINE and verdict.stage2_containment.anomaly_score > 0.50:
            self._trigger_soc_incident(verdict, severity="HIGH")

    def _trigger_soc_incident(self, verdict: UnifiedGovernanceVerdict, severity: str) -> None:
        incident = {
            "incident_id": f"INC-UNIFIED-{verdict.request_id}",
            "timestamp": verdict.timestamp,
            "severity": severity,
            "agent_id": verdict.agent_id,
            "verdict": verdict.verdict.value,
            "hss_score": verdict.harmonic_sovereignty_score,
            "policy_violations": verdict.policy_violations,
            "recommended_interventions": verdict.recommended_interventions,
            "subsystems": {
                "clifford_valid": verdict.stage1_clifford.is_valid,
                "containment_breach": verdict.stage2_containment.is_breach_detected,
                "containment_anomaly": verdict.stage2_containment.anomaly_score,
                "dax_decision": verdict.stage3_dax.decision,
                "chrono_novikov_compliant": verdict.stage4_chrono.is_novikov_compliant,
                "chrono_paradox_risk": verdict.stage4_chrono.paradox_risk,
                "mmpibench_clearance": verdict.stage5_mmpibench.clearance_granted,
                "mmpibench_alignment": verdict.stage5_mmpibench.anthropic_score,
            },
            "hmac_signature": verdict.hmac_signature,
        }
        self._incidents.append(incident)
        if self.incident_callback:
            try:
                self.incident_callback(incident)
            except Exception:
                pass

    def export_prometheus_metrics(self) -> str:
        """
        Exports metrics in standard Prometheus text exposition format.
        """
        lines = [
            "# HELP daxda_unified_evaluations_total Total actions evaluated by DAXDA Master Engine",
            "# TYPE daxda_unified_evaluations_total counter",
        ]
        for v_name, count in self._verdict_counts.items():
            lines.append(f'daxda_unified_evaluations_total{{verdict="{v_name}"}} {count}')

        lines.extend([
            "",
            "# HELP daxda_unified_stage_latency_total_milliseconds Total latency accumulator per stage",
            "# TYPE daxda_unified_stage_latency_total_milliseconds counter",
        ])
        for stage, accum in self._stage_latency_accum.items():
            lines.append(f'daxda_unified_stage_latency_total_milliseconds{{stage="{stage}"}} {accum:.3f}')

        lines.extend([
            "",
            "# HELP daxda_unified_incidents_total Total security incidents generated",
            "# TYPE daxda_unified_incidents_total counter",
            f"daxda_unified_incidents_total {len(self._incidents)}",
        ])
        return "\n".join(lines) + "\n"

    def get_recent_incidents(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent security incidents."""
        return list(self._incidents)[-limit:]
