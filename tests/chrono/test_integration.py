"""
Integration Tests for Chrono Integration: Cl16_4ChronoBridge, ChronoDAXDAAdapter, ChronoGuardHooks, ChronoAnomalyIntegrator.
"""

import pytest
from daxda_engine.chrono.geometry.temporal_space import TemporalSpace
from daxda_engine.chrono.integration.cl16_4_integration import Cl16_4ChronoBridge
from daxda_engine.chrono.integration.daxda_engine import ChronoDAXDAAdapter
from daxda_engine.chrono.integration.guard_hooks import ChronoGuardHooks
from daxda_engine.chrono.integration.anomaly_integration import ChronoAnomalyIntegrator
from daxda_engine.chrono.geometry.synchronicity import SynchronicityEvent
from daxda_engine.chrono.validation.paradox_detector import ParadoxAnomaly, ParadoxType


class TestChronoIntegration:

    def test_cl16_4_chrono_bridge(self):
        bridge = Cl16_4ChronoBridge()
        # 20-dimensional multivector
        vec = [1.0] * 20
        coord = bridge.project_decision_vector_to_coord(vec, base_t=42.0)
        assert coord.t == 42.1
        assert coord.b > 0.0
        assert coord.p > 0.0

        state = bridge.create_temporal_state_from_cl16_4("cl_state_1", vec, base_t=42.0)
        assert state.state_id == "cl_state_1"
        stability = bridge.compute_hypercombinatorial_stability(state)
        assert 0.0 <= stability <= 1.0

    def test_chrono_daxda_adapter_flow(self):
        adapter = ChronoDAXDAAdapter()
        approved, cert = adapter.process_agent_decision(
            agent_id="agent_nexus_01",
            decision_vector=[0.1, 0.2, 0.3],
            action_name="QUERY_DATABASE",
        )
        assert approved is True
        assert cert.disposition.value == "APPROVED"

        history = adapter.get_agent_history("agent_nexus_01")
        assert len(history) == 1

    def test_chrono_guard_hooks(self):
        hooks = ChronoGuardHooks()
        allowed, reason, meta = hooks.pre_decision_check(
            agent_id="agent_sentinel",
            action_name="DISPATCH_INSTRUCTION",
            proposed_vector=[0.2, 0.4, 0.6],
        )
        assert allowed is True
        assert reason == "TEMPORALLY_COHERENT"

        post_meta = hooks.post_decision_check(
            agent_id="agent_sentinel",
            action_name="DISPATCH_INSTRUCTION",
            execution_status="SUCCESS",
            observed_vector=[0.21, 0.39, 0.60],
        )
        assert post_meta["execution_status"] == "SUCCESS"
        assert post_meta["vector_divergence"] < 0.1

        stats = hooks.get_stats()
        assert stats["allowed_decisions"] == 1
        assert stats["denied_decisions"] == 0

    def test_chrono_anomaly_and_soc_integration(self):
        alerts = []
        integrator = ChronoAnomalyIntegrator(alert_callback=lambda a: alerts.append(a))

        # Test synchronicity alert
        sync_event = SynchronicityEvent(
            event_id="SYNC-001",
            state_a_id="node_a",
            state_b_id="node_b",
            synchronicity_score=0.94,
            spacelike_interval=12.5,
            time_delta=0.05,
            cosine_similarity=0.98,
            p_value=0.001,
            is_anomaly=True,
        )
        inc = integrator.handle_synchronicity_event(sync_event)
        assert inc is not None
        assert inc["severity"] == "CRITICAL"
        assert len(alerts) == 1

        # Test paradox alert
        paradox = ParadoxAnomaly(
            paradox_type=ParadoxType.GRANDFATHER,
            severity=0.95,
            description="Causal feedback loop breach",
            cycle_nodes=["N1", "N2"],
            offending_state_id="N1",
            mitigation_recommendation="Quarantine node",
        )
        inc2 = integrator.handle_paradox_anomaly(paradox)
        assert inc2["severity"] == "CRITICAL"
        assert len(alerts) == 2
