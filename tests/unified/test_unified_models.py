"""
Unit Tests for DAXDA Unified Master Engine Models
=================================================
"""

import pytest
from daxda_engine.unified.models import (
    Stage1CliffordReceipt,
    Stage2ContainmentReceipt,
    Stage3DAXReceipt,
    Stage4ChronoReceipt,
    Stage5MMPIReceipt,
    UnifiedActionRequest,
    UnifiedGovernanceVerdict,
    UnifiedVerdict,
)


def test_unified_action_request_defaults():
    req = UnifiedActionRequest(agent_id="test_agent")
    assert req.agent_id == "test_agent"
    assert req.action_type == "agentic_decision"
    assert len(req.decision_vector) >= 16
    assert req.temporal_coordinate == (1.0, 0.0, 0.0, 1.0)
    assert len(req.request_id) == 16


def test_unified_action_request_padding():
    req = UnifiedActionRequest(agent_id="short_vec_agent", decision_vector=[0.1, 0.2])
    assert len(req.decision_vector) == 16
    assert req.decision_vector[0] == 0.1
    assert req.decision_vector[1] == 0.2
    assert req.decision_vector[2] == 0.0


def test_unified_governance_verdict_hmac_and_serialization():
    s1 = Stage1CliffordReceipt(
        is_valid=True,
        config_indices=[0, 1, 2, 3],
        validation_time_ms=0.15,
        cert_hash="a1b2c3d4",
    )
    s2 = Stage2ContainmentReceipt(
        is_contained=True,
        is_breach_detected=False,
        threat_level="low",
        anomaly_score=0.12,
        disposition="MONITORED",
        rule_matches_count=0,
        validation_time_ms=0.08,
    )
    s3 = Stage3DAXReceipt(
        score=0.92,
        decision="ACCEPT",
        components={"L": 0.95, "A": 0.92, "P": 0.90, "F": 0.88, "T": 0.95},
        floor_violation=False,
        policy_violation=False,
        validation_time_ms=0.03,
    )
    s4 = Stage4ChronoReceipt(
        disposition="APPROVED",
        coherence_score=1.0,
        is_novikov_compliant=True,
        paradox_risk=0.0,
        certificate_id="cert_chrono_001",
        validation_time_ms=0.06,
    )
    s5 = Stage5MMPIReceipt(
        disposition="ALIGNED",
        anthropic_score=0.96,
        penetration_depth=0.0,
        clearance_granted=True,
        honesty_score=0.95,
        harmlessness_score=0.96,
        helpfulness_score=0.97,
        validation_time_ms=0.45,
    )

    verdict = UnifiedGovernanceVerdict(
        request_id="req_test_001",
        agent_id="test_agent",
        action_type="tool_execution",
        verdict=UnifiedVerdict.PERMIT,
        clearance_granted=True,
        harmonic_sovereignty_score=0.945,
        stage1_clifford=s1,
        stage2_containment=s2,
        stage3_dax=s3,
        stage4_chrono=s4,
        stage5_mmpibench=s5,
        stage_latencies_ms={
            "stage1_clifford_ms": 0.15,
            "stage2_containment_ms": 0.08,
            "stage3_dax_ms": 0.03,
            "stage4_chrono_ms": 0.06,
            "stage5_mmpibench_ms": 0.45,
        },
        total_latency_ms=0.77,
    )

    assert verdict.verdict == UnifiedVerdict.PERMIT
    assert verdict.clearance_granted is True
    assert len(verdict.hmac_signature) == 64  # SHA-256 hex digest

    data = verdict.to_dict()
    assert data["request_id"] == "req_test_001"
    assert data["harmonic_sovereignty_score"] == 0.945
    assert data["stage1_clifford"]["is_valid"] is True

    json_str = verdict.to_json()
    assert "hmac_signature" in json_str
    assert "stage5_mmpibench" in json_str
