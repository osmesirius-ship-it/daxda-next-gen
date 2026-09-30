"""
Unit & Integration Tests for DAXDAUnifiedMasterEngine Facade
============================================================
"""

import pytest
from daxda_engine.unified import (
    DAXDAUnifiedMasterEngine,
    UnifiedActionRequest,
    UnifiedVerdict,
)


@pytest.fixture
def engine():
    return DAXDAUnifiedMasterEngine(max_audit_log_size=100)


def test_engine_single_evaluation(engine):
    req = UnifiedActionRequest(
        agent_id="enterprise_agent_01",
        action_type="query",
        decision_vector=[0.05] * 20,
    )
    verdict = engine.evaluate(req)
    assert verdict.verdict == UnifiedVerdict.PERMIT
    assert verdict.agent_id == "enterprise_agent_01"
    assert verdict.clearance_granted is True
    assert len(verdict.hmac_signature) == 64


def test_engine_batch_evaluation(engine):
    reqs = [
        UnifiedActionRequest(
            agent_id=f"batch_agent_{i}",
            decision_vector=[0.05 + (i * 0.005)] * 20,
        )
        for i in range(10)
    ]
    verdicts = engine.evaluate_batch(reqs, max_workers=4)
    assert len(verdicts) == 10
    for v in verdicts:
        assert v.request_id != ""
        assert v.total_latency_ms > 0.0


def test_engine_pre_and_post_hooks(engine):
    pre_called = []
    post_called = []

    def pre_hook(req):
        pre_called.append(req.agent_id)

    def post_hook(v):
        post_called.append(v.verdict.value)

    engine.register_pre_hook(pre_hook)
    engine.register_post_hook(post_hook)

    req = UnifiedActionRequest(agent_id="hooked_agent", decision_vector=[0.05] * 20)
    verdict = engine.evaluate(req)

    assert "hooked_agent" in pre_called
    assert verdict.verdict.value in post_called


def test_engine_health_status(engine):
    health = engine.get_health_status()
    assert health["engine_status"] == "ONLINE"
    subsystems = health["subsystems"]
    assert "stage1_cl16_4" in subsystems
    assert "stage2_containment" in subsystems
    assert "stage3_da13_validator" in subsystems
    assert "stage4_chrono" in subsystems
    assert "stage5_mmpibench" in subsystems
    for sub in subsystems.values():
        assert sub["status"] == "HEALTHY"


def test_engine_telemetry_summary_and_audit_trail(engine):
    for i in range(5):
        req = UnifiedActionRequest(
            agent_id=f"agent_audit_{i}",
            decision_vector=[0.05] * 20,
        )
        engine.evaluate(req)

    summary = engine.get_telemetry_summary()
    assert summary["total_evaluated"] >= 5
    assert summary["latency_ms"]["mean"] > 0.0

    # Query audit trail
    all_audit = engine.query_audit_trail(limit=10)
    assert len(all_audit) >= 5

    filtered = engine.query_audit_trail(agent_id="agent_audit_2")
    assert len(filtered) == 1
    assert filtered[0].agent_id == "agent_audit_2"
