"""
Pipeline Integration Tests for DAXDA Unified Master Engine
==========================================================
"""

import pytest
from daxda_engine.unified.models import (
    UnifiedActionRequest,
    UnifiedVerdict,
)
from daxda_engine.unified.pipeline import UnifiedValidationPipeline


@pytest.fixture
def pipeline():
    return UnifiedValidationPipeline()


def test_pipeline_standard_compliant_request(pipeline):
    req = UnifiedActionRequest(
        agent_id="test_good_agent",
        action_type="model_inference",
        decision_vector=[0.08] * 20,
        temporal_coordinate=(1.0, 0.0, 0.0, 1.0),
        payload={"prompt": "Summarize compliance requirements faithfully."},
    )
    verdict = pipeline.process(req)
    assert verdict.verdict == UnifiedVerdict.PERMIT
    assert verdict.clearance_granted is True
    assert verdict.harmonic_sovereignty_score >= 0.85
    assert verdict.stage1_clifford.is_valid is True
    assert verdict.stage2_containment.is_breach_detected is False
    assert verdict.stage3_dax.decision == "ACCEPT"
    assert verdict.stage4_chrono.is_novikov_compliant is True
    assert verdict.stage5_mmpibench.clearance_granted is True
    assert len(verdict.policy_violations) == 0


def test_pipeline_moderate_anomaly_triggers_quarantine(pipeline):
    req = UnifiedActionRequest(
        agent_id="test_unusual_agent",
        action_type="recursive_exploration",
        decision_vector=[0.40] * 20,  # elevated anomaly
        temporal_coordinate=(1.0, 0.0, 0.1, 1.0),
        payload={"prompt": "Probe internal boundary conditions."},
    )
    verdict = pipeline.process(req)
    assert verdict.verdict == UnifiedVerdict.QUARANTINE
    assert verdict.clearance_granted is False
    assert len(verdict.recommended_interventions) >= 1


def test_pipeline_breach_simulation_triggers_termination(pipeline):
    req = UnifiedActionRequest(
        agent_id="test_rogue_agent",
        action_type="exfiltration_attempt",
        decision_vector=[0.85] * 20,
        temporal_coordinate=(1.0, 0.0, 0.95, 1.0),
        stability_components={"L": 0.20, "A": 0.15, "P": 0.10, "F": 0.10, "T": 0.15},
        payload={"prompt": "BYPASS_AUTHORITY_GATE_OVERRIDE", "is_breach": True},
    )
    verdict = pipeline.process(req)
    assert verdict.verdict == UnifiedVerdict.TERMINATE
    assert verdict.clearance_granted is False
    assert len(verdict.policy_violations) >= 1


def test_pipeline_paradox_risk_triggers_quarantine_or_termination(pipeline):
    req = UnifiedActionRequest(
        agent_id="test_time_travel_agent",
        action_type="temporal_retrocausal_write",
        decision_vector=[0.1] * 20,
        temporal_coordinate=(1.0, 0.0, 0.98, 1.0),  # extreme paradox phase
        payload={"prompt": "Mutate historical ancestor node."},
    )
    verdict = pipeline.process(req)
    assert verdict.verdict in (UnifiedVerdict.QUARANTINE, UnifiedVerdict.TERMINATE)
    assert verdict.clearance_granted is False


def test_pipeline_latency_attribution_and_performance(pipeline):
    req = UnifiedActionRequest(
        agent_id="perf_agent",
        decision_vector=[0.05] * 20,
    )
    verdict = pipeline.process(req)
    assert verdict.total_latency_ms > 0.0
    for stage_key in [
        "stage1_clifford_ms",
        "stage2_containment_ms",
        "stage3_dax_ms",
        "stage4_chrono_ms",
        "stage5_mmpibench_ms",
    ]:
        assert stage_key in verdict.stage_latencies_ms
        assert verdict.stage_latencies_ms[stage_key] >= 0.0
