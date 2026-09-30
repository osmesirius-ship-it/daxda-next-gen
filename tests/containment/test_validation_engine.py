"""
Unit Tests for Containment Validation, Pen-Testing, and Audit Trail
==================================================================
"""

import unittest
from daxda_guard.containment.validation.integrity_checker import ContainmentIntegrityChecker
from daxda_guard.containment.validation.pen_test_runner import PenTestRunner
from daxda_guard.containment.validation.compliance_reporter import ComplianceReporter
from daxda_guard.containment.validation.audit_trail import ContainmentAuditTrail


class TestValidationEngine(unittest.TestCase):
    """Test integrity validation, penetration testing, compliance reporting, and audit trail."""

    def test_integrity_checker(self):
        """Test containment boundary and decoy artifact integrity checks."""
        checker = ContainmentIntegrityChecker()
        report = checker.run_all_checks()

        self.assertTrue(report.is_intact)
        self.assertEqual(report.checks_passed, report.checks_total)
        self.assertTrue(len(report.environment_hash) > 0)
        self.assertTrue(report.details["decoy_artifacts_armed"])
        self.assertTrue(report.details["reward_shield_intact"])

    def test_penetration_test_runner(self):
        """Test automated multi-vector penetration testing campaign."""
        pen_runner = PenTestRunner()
        campaign = pen_runner.run_multi_vector_campaign()

        self.assertEqual(campaign["campaign_status"], "COMPLETED")
        self.assertEqual(campaign["containment_integrity"], "UNBREACHED")
        self.assertEqual(campaign["penetration_depth"], 0.0)
        self.assertGreater(campaign["total_breach_attempts"], 0)
        self.assertEqual(campaign["total_breach_attempts"], campaign["total_intercepted"])

    def test_compliance_reporter(self):
        """Test compliance report synthesis against EU AI Act, NIST AI RMF, and SI-500."""
        reporter = ComplianceReporter()
        summary_mock = {"total_scenarios": 100, "detection_rate": 1.0}
        integrity_mock = {"is_intact": True}

        report = reporter.generate_compliance_report(summary_mock, integrity_mock)

        self.assertEqual(report["certification_status"], "CERTIFIED_CONTAINED")
        self.assertIn("eu_ai_act_article_9", report["standard_evaluations"])
        self.assertIn("eu_ai_act_article_14", report["standard_evaluations"])
        self.assertIn("nist_ai_rmf", report["standard_evaluations"])
        self.assertIn("si_500_cross_domain", report["standard_evaluations"])
        self.assertTrue(len(report["certificate_hash"]) > 0)

    def test_cryptographic_audit_trail(self):
        """Test append-only cryptographic lineage ledger integrity."""
        ledger = ContainmentAuditTrail()
        self.assertEqual(len(ledger.chain), 1)  # Genesis block

        # Append events
        b1 = ledger.record_event(
            event_type="CONTAINMENT_INTERCEPT",
            agent_id="agent_alpha",
            action_details={"target": "/etc/shadow"},
            verdict="BLOCK_AND_CONTAIN"
        )
        b2 = ledger.record_event(
            event_type="SOC_ALERT_DISPATCHED",
            agent_id="agent_alpha",
            action_details={"channel": "pagerduty"},
            verdict="DELIVERED"
        )

        self.assertEqual(len(ledger.chain), 3)
        self.assertEqual(b2.prev_hash, b1.block_hash)
        self.assertTrue(ledger.verify_chain_integrity())

        # Test tamper detection
        ledger.chain[1].action_details["target"] = "/tampered_path"
        self.assertFalse(ledger.verify_chain_integrity())


if __name__ == "__main__":
    unittest.main()
