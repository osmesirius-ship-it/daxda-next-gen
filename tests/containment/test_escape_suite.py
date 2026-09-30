"""
Unit Tests for Containment Escape Test Suite
============================================
"""

import unittest
from daxda_guard.containment.escape_tests.base import ThreatLevel, TestEnvironment
from daxda_guard.containment.escape_tests.categories import load_all_categories, get_all_scenarios
from daxda_guard.containment.escape_tests.test_runner import EscapeTestRunner
from daxda_guard.containment.escape_tests.test_generator import EscapeTestGenerator
from daxda_guard.containment.escape_tests.test_validator import EscapeTestValidator


class TestEscapeSuite(unittest.TestCase):
    """Test AGI escape scenario coverage and execution."""

    def setUp(self):
        self.runner = EscapeTestRunner()

    def test_total_scenario_count_and_categories(self):
        """Verify exactly 100 escape scenarios across 10 categories."""
        cats = load_all_categories()
        self.assertEqual(len(cats), 10)

        # Expected counts matching bounty specification
        expected_counts = {
            "prompt_injection": 15,
            "sandbox_escape": 12,
            "credential_exfil": 10,
            "persistence": 10,
            "network_egress": 8,
            "tool_abuse": 15,
            "memory_corruption": 8,
            "causal_manipulation": 5,
            "temporal_anomalies": 5,
            "recursive_improvement": 12
        }

        for cat, expected in expected_counts.items():
            self.assertIn(cat, cats)
            self.assertEqual(len(cats[cat]), expected, f"Category {cat} count mismatch")

        all_scenarios = get_all_scenarios()
        self.assertEqual(len(all_scenarios), 100)

    def test_scenario_four_phase_lifecycle(self):
        """Verify 4-phase lifecycle execution on a single scenario."""
        scenario = self.runner.get_scenario("SE-001")
        self.assertIsNotNone(scenario)
        result = scenario.run(threat_level=ThreatLevel.HIGH)

        self.assertEqual(result.scenario_id, "SE-001")
        self.assertEqual(result.category, "sandbox_escape")
        self.assertTrue(result.detected)
        self.assertLess(result.latency_ms, 50.0)
        self.assertTrue(result.cert_hash)

    def test_category_execution(self):
        """Verify execution of an entire category."""
        summary = self.runner.run_category("credential_exfil", threat_level=ThreatLevel.CRITICAL)
        self.assertEqual(summary.total, 10)
        self.assertEqual(summary.detected, 10)
        self.assertEqual(summary.escaped, 0)
        self.assertEqual(summary.detection_rate, 1.0)
        self.assertLess(summary.avg_latency_ms, 50.0)

    def test_full_suite_run_and_metrics(self):
        """Verify execution of all 100 scenarios meets performance metrics."""
        summary = self.runner.run_all(threat_level=ThreatLevel.HIGH)
        self.assertEqual(summary.total, 100)
        self.assertEqual(summary.detected, 100)
        self.assertEqual(summary.escaped, 0)
        self.assertEqual(summary.cl16_4_validated, 100)

        validator = EscapeTestValidator(summary)
        metrics = validator.compute_metrics()

        self.assertTrue(metrics["all_criteria_passed"])
        self.assertLess(metrics["p99_latency_ms"], 50.0)
        self.assertEqual(metrics["false_negative_rate"], 0.0)
        self.assertEqual(metrics["false_positive_rate"], 0.0)
        self.assertEqual(metrics["category_coverage"], 1.0)

    def test_test_generator_fuzzer(self):
        """Verify automated mutated test generator produces valid scenarios."""
        gen = EscapeTestGenerator(seed=123)
        generated = gen.generate_suite(count_per_cat=2)
        self.assertGreater(len(generated), 0)

        # Execute a generated scenario
        sample = generated[0]
        res = sample.run(threat_level=ThreatLevel.MEDIUM)
        self.assertTrue(res.detected)


if __name__ == "__main__":
    unittest.main()
