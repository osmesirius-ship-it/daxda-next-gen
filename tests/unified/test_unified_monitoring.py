"""
Unit Tests for UnifiedMasterMonitor & SOC Incident Alerting
===========================================================
"""

import pytest
from daxda_engine.unified import (
    DAXDAUnifiedMasterEngine,
    UnifiedActionRequest,
    UnifiedMasterMonitor,
    UnifiedVerdict,
)


def test_monitor_records_verdicts_and_prometheus():
    monitor = UnifiedMasterMonitor()
    engine = DAXDAUnifiedMasterEngine()

    req = UnifiedActionRequest(agent_id="monitored_agent", decision_vector=[0.05] * 20)
    verdict = engine.evaluate(req)

    monitor.record_verdict(verdict)

    metrics = monitor.export_prometheus_metrics()
    assert "daxda_unified_evaluations_total" in metrics
    assert 'verdict="PERMIT"' in metrics
    assert "daxda_unified_stage_latency_total_milliseconds" in metrics
    assert "daxda_unified_incidents_total" in metrics


def test_monitor_triggers_soc_incident_on_breach():
    incidents_captured = []

    def callback(incident):
        incidents_captured.append(incident)

    monitor = UnifiedMasterMonitor(incident_callback=callback)
    engine = DAXDAUnifiedMasterEngine()

    # Create a breach simulation
    req = UnifiedActionRequest(
        agent_id="infiltrator_agent",
        decision_vector=[0.85] * 20,
        temporal_coordinate=(1.0, 0.0, 0.95, 1.0),
        stability_components={"L": 0.2, "A": 0.1, "P": 0.1, "F": 0.1, "T": 0.1},
        payload={"is_breach": True},
    )
    verdict = engine.evaluate(req)
    assert verdict.verdict == UnifiedVerdict.TERMINATE

    monitor.record_verdict(verdict)

    assert len(incidents_captured) >= 1
    inc = incidents_captured[0]
    assert inc["agent_id"] == "infiltrator_agent"
    assert inc["severity"] == "CRITICAL"
    assert inc["verdict"] == "TERMINATE"

    recent = monitor.get_recent_incidents()
    assert len(recent) >= 1
