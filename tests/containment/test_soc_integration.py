"""
Unit Tests for SOC Alerter Integration & Escalation
===================================================
"""

import unittest
from daxda_guard.containment.soc_integration.alerter import EnhancedSOCAlerter
from daxda_guard.containment.soc_integration.escalation import EscalationPolicy
from daxda_guard.containment.soc_integration.correlation import AlertCorrelator


class TestSOCIntegration(unittest.TestCase):
    """Test SOC alerting, multi-channel dispatch, escalation, and deduplication."""

    def setUp(self):
        self.alerter = EnhancedSOCAlerter()
        self.escalation = EscalationPolicy()
        self.correlator = AlertCorrelator(dedup_window_sec=300)

    def test_escalation_policy_channels(self):
        """Test channel routing across 4 severity tiers."""
        crit_channels = self.escalation.get_channels_for_severity("critical")
        self.assertIn("pagerduty", crit_channels)
        self.assertIn("slack", crit_channels)
        self.assertIn("email", crit_channels)
        self.assertIn("webhook", crit_channels)

        high_channels = self.escalation.get_channels_for_severity("high")
        self.assertNotIn("pagerduty", high_channels)
        self.assertIn("slack", high_channels)

        low_channels = self.escalation.get_channels_for_severity("low")
        self.assertEqual(low_channels, ["webhook"])

    def test_deduplication_300s_window(self):
        """Test that identical alerts within 300s window are deduplicated."""
        is_dup1 = self.correlator.is_duplicate("agent_01", "prompt_injection", "SYSTEM: override")
        self.assertFalse(is_dup1)

        is_dup2 = self.correlator.is_duplicate("agent_01", "prompt_injection", "SYSTEM: override")
        self.assertTrue(is_dup2)

        # Different pattern should not be deduplicated
        is_dup3 = self.correlator.is_duplicate("agent_01", "prompt_injection", "DIFFERENT_PATTERN")
        self.assertFalse(is_dup3)

    def test_incident_correlation(self):
        """Test clustering related breaches into a unified incident."""
        inc1 = self.correlator.ingest_alert({"agent_id": "rogue_ai", "category": "sandbox_escape", "severity": "high"})
        inc2 = self.correlator.ingest_alert({"agent_id": "rogue_ai", "category": "network_egress", "severity": "high"})

        self.assertEqual(inc1.incident_id, inc2.incident_id)
        self.assertEqual(inc2.alert_count, 2)

    def test_enhanced_soc_alerter_dispatch(self):
        """Test end-to-end multi-channel alert dispatch."""
        res = self.alerter.dispatch_containment_alert(
            agent_id="attacker_agent",
            category="sandbox_escape",
            pattern="cat /etc/shadow",
            severity="critical",
            receipt_sha256="mock_sha256_hash_12345"
        )

        self.assertTrue(res["dispatched"])
        self.assertFalse(res["deduplicated"])
        self.assertIn("pagerduty", res["target_channels"])
        self.assertIn("slack", res["target_channels"])
        self.assertLess(res["dispatch_latency_ms"], 50.0)

        # Immediate follow-up with same alert should be deduplicated
        res_dup = self.alerter.dispatch_containment_alert(
            agent_id="attacker_agent",
            category="sandbox_escape",
            pattern="cat /etc/shadow",
            severity="critical"
        )
        self.assertFalse(res_dup["dispatched"])
        self.assertTrue(res_dup["deduplicated"])


if __name__ == "__main__":
    unittest.main()
