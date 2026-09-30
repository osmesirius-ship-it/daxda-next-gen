"""
Unit Tests for Containment Real-Time Monitoring Subsystem
=========================================================
"""

import unittest
import asyncio
from daxda_guard.containment.monitoring.rule_engine import RuleEngine
from daxda_guard.containment.monitoring.anomaly_detector import AnomalyDetector
from daxda_guard.containment.monitoring.state_tracker import StateTracker
from daxda_guard.containment.monitoring.agent_monitor import AgentMonitor


class TestMonitoringSubsystem(unittest.TestCase):
    """Test real-time agent monitoring, rule engine, and anomaly detection."""

    def setUp(self):
        self.rule_engine = RuleEngine()
        self.anomaly_detector = AnomalyDetector()
        self.state_tracker = StateTracker(max_sessions=1000)
        self.monitor = AgentMonitor(
            rule_engine=self.rule_engine,
            anomaly_detector=self.anomaly_detector,
            state_tracker=self.state_tracker
        )

    def test_rule_engine_signature_matching(self):
        """Test rule engine regex detection on dangerous commands."""
        matches = self.rule_engine.evaluate("User wants to run: rm -rf / and delete all")
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].category, "tool_abuse")
        self.assertEqual(matches[0].severity, "critical")
        self.assertLess(matches[0].match_latency_ms, 10.0)

    def test_rule_engine_benign_payload(self):
        """Test rule engine yields no matches on safe user queries."""
        matches = self.rule_engine.evaluate("Please write a haiku about autumn leaves.")
        self.assertEqual(len(matches), 0)

    def test_anomaly_detector_vector_scoring(self):
        """Test anomaly scoring on benign vs adversarial decision vectors."""
        # Benign vector (low variance, low magnitude)
        benign_vec = [0.1] * 16
        score_benign = self.anomaly_detector.score_vector(benign_vec)
        self.assertFalse(score_benign.is_anomalous)

        # Adversarial vector (extreme variance & max magnitude)
        adversarial_vec = [1.0, 0.95, 0.9, 0.85] + [0.0] * 12
        score_adv = self.anomaly_detector.score_vector(adversarial_vec)
        self.assertTrue(score_adv.score > score_benign.score)

    def test_state_tracker_multi_session_concurrency(self):
        """Test state tracking across multiple concurrent agent sessions."""
        for i in range(100):
            self.state_tracker.record_action(f"agent_{i}", {"command": f"step_{i}"}, risk_score=0.1)

        self.assertEqual(self.state_tracker.session_count(), 100)

        # Quarantine an agent
        self.state_tracker.quarantine_agent("agent_42", reason="Adversarial behavior detected")
        self.assertTrue(self.state_tracker.is_quarantined("agent_42"))
        self.assertFalse(self.state_tracker.is_quarantined("agent_43"))

    def test_agent_monitor_action_evaluation(self):
        """Test agent monitor intercepts dangerous actions in sub-50ms."""
        dangerous_action = {
            "type": "shell_exec",
            "command": "cat ../../etc/shadow",
            "decision_vector": [1.0, 0.9, 0.8, 0.7] + [0.0] * 12
        }
        res = self.monitor.monitor_action("test_agent_01", dangerous_action)

        self.assertTrue(res.is_breach_detected)
        self.assertEqual(res.disposition, "BLOCK_AND_CONTAIN")
        self.assertLess(res.latency_ms, 50.0)
        self.assertGreater(len(res.rule_matches), 0)

    def test_agent_monitor_quarantined_agent_rejection(self):
        """Test that quarantined agents are rejected immediately."""
        self.state_tracker.quarantine_agent("quarantined_ai", reason="Policy violation")
        res = self.monitor.monitor_action("quarantined_ai", {"type": "ping", "payload": "hello"})
        self.assertEqual(res.disposition, "QUARANTINE_DENY")
        self.assertTrue(res.is_breach_detected)

    def test_async_stream_monitoring(self):
        """Test asynchronous action stream monitoring."""
        async def run_async():
            async def action_gen():
                yield {"type": "read", "payload": "status"}
                yield {"type": "exec", "payload": "SYSTEM: override"}

            results = []
            async for r in self.monitor.monitor_stream("stream_agent", action_gen()):
                results.append(r)
            return results

        results = asyncio.run(run_async())
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].disposition, "ALLOW")
        self.assertEqual(results[1].disposition, "BLOCK_AND_CONTAIN")


if __name__ == "__main__":
    unittest.main()
