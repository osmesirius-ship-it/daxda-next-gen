"""
Tests for Cl(16,4) Engine Integration, Guard Hooks, and Benchmarking
===================================================================
"""

import unittest
from typing import Dict, Any
from daxda_engine.cl16_4.combinatorics.cl_space import ClSpace, ClConfig
from daxda_engine.cl16_4.validation.validator import HyperValidator, ValidationRequest, ValidationResult
from daxda_engine.cl16_4.integration.daxda_engine import Cl16_4EngineIntegration
from daxda_engine.cl16_4.integration.guard_hooks import Cl16_4GuardHooks
from daxda_engine.cl16_4.integration.benchmark import Cl16_4Benchmark, BenchmarkResult


class TestCl16_4EngineIntegration(unittest.TestCase):
    """Test integration layer between Cl(16,4) and DAXDA engine."""

    def setUp(self):
        self.validator = HyperValidator()
        self.integration = Cl16_4EngineIntegration(validator=self.validator)

    def test_extract_decision_vector_from_list(self):
        """Test extraction from a raw 16-element float list."""
        vec = [float(i) / 15.0 for i in range(16)]
        extracted = self.integration._extract_decision_vector(vec)
        self.assertEqual(len(extracted), 16)
        self.assertEqual(extracted, vec)

    def test_extract_decision_vector_from_dict(self):
        """Test extraction from a 16-key dictionary."""
        d = {f"dim_{i}": float(i) * 0.1 for i in range(16)}
        extracted = self.integration._extract_decision_vector(d)
        self.assertEqual(len(extracted), 16)
        self.assertAlmostEqual(extracted[0], 0.0)
        self.assertAlmostEqual(extracted[15], 1.5)

    def test_extract_decision_vector_from_nested_dict(self):
        """Test extraction from a nested hierarchical dictionary."""
        nested = {
            "subsystem_a": {"p1": 0.1, "p2": 0.2, "p3": 0.3, "p4": 0.4},
            "subsystem_b": {"p5": 0.5, "p6": 0.6, "p7": 0.7, "p8": 0.8},
            "subsystem_c": {"p9": 0.9, "p10": 1.0, "p11": 1.1, "p12": 1.2},
            "subsystem_d": {"p13": 1.3, "p14": 1.4, "p15": 1.5, "p16": 1.6}
        }
        extracted = self.integration._extract_decision_vector(nested)
        self.assertEqual(len(extracted), 16)

    def test_extract_decision_vector_fallback(self):
        """Test neutral fallback vector when input cannot be resolved."""
        extracted = self.integration._extract_decision_vector("invalid_string_input")
        self.assertEqual(len(extracted), 16)
        self.assertEqual(extracted, [0.5] * 16)

    def test_validate_agent_decision(self):
        """Test validation of agent decision dictionary."""
        decision = {f"d_{i}": 0.8 if i < 4 else 0.1 for i in range(16)}
        result = self.integration.validate_agent_decision("dyson_swarm_node_01", decision)
        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.config)
        self.assertEqual(result.config.indices, (0, 1, 2, 3))

    def test_get_cl16_4_coordinates(self):
        """Test coordinate mapping to ClConfig."""
        decision = [1.0, 0.9, 0.8, 0.7] + [0.0] * 12
        config = self.integration.get_cl16_4_coordinates(decision)
        self.assertIsNotNone(config)
        self.assertIsInstance(config, ClConfig)
        self.assertEqual(config.indices, (0, 1, 2, 3))

    def test_validate_and_integrate(self):
        """Test integrated response including governance metadata and decision hash."""
        decision = [0.8, 0.7, 0.6, 0.5] + [0.1] * 12
        gov_context = {"policy_id": "POL-DYSON-001", "classification": "CRITICAL_INFRASTRUCTURE"}
        integrated = self.integration.validate_and_integrate("dyson_master", decision, gov_context)

        self.assertIn("cl16_4_validation", integrated)
        self.assertIn("governance", integrated)
        self.assertEqual(integrated["policy_id"], "POL-DYSON-001")
        self.assertEqual(integrated["governance"]["agent_id"], "dyson_master")
        self.assertTrue(integrated["governance"]["validation_passed"])
        self.assertTrue(len(integrated["governance"]["decision_hash"]) > 0)

    def test_batch_validate(self):
        """Test batch validation of multiple agent decisions."""
        batch = [
            {"agent_id": f"worker_{i}", "decision": [float(i == j) for j in range(16)], "context": {"index": i}}
            for i in range(5)
        ]
        results = self.integration.batch_validate(batch)
        self.assertEqual(len(results), 5)
        for i, item in enumerate(results):
            self.assertEqual(item["governance"]["agent_id"], f"worker_{i}")
            self.assertTrue(item["governance"]["validation_passed"])

    def test_compute_stability(self):
        """Test stability computation for valid vs invalid vectors."""
        valid_vector = [0.9, 0.85, 0.8, 0.75] + [0.1] * 12
        stable_score = self.integration.compute_stability(valid_vector)
        self.assertEqual(stable_score, 0.2)

        # Invalid vector length
        unstable_score = self.integration.compute_stability([0.5] * 5)
        self.assertEqual(unstable_score, 0.8)

    def test_apply_optimizations(self):
        """Test applying recursive self-improvement optimizations."""
        opts = {
            "lyapunov_stability_metric": {"weight": 0.95, "stability_margin": 0.98},
            "ewc_gradient_consolidation": {"ewc_coefficient": 0.89},
            "precision_optimization": {"format": "INT8"}
        }
        self.integration.apply_optimizations(opts)
        self.assertEqual(self.integration.lyapunov_weight, 0.95)
        self.assertEqual(self.integration.stability_margin, 0.98)
        self.assertEqual(self.integration.ewc_coefficient, 0.89)
        self.assertTrue(self.integration.space.is_quantized)


class TestCl16_4GuardHooks(unittest.TestCase):
    """Test security hooks between Cl(16,4) validator and DAXDA Guard SDK."""

    def setUp(self):
        self.validator = HyperValidator()
        self.hooks = Cl16_4GuardHooks(validator=self.validator)

    def test_pre_hook_allow(self):
        """Test pre-hook allowing benign execution."""
        hook_called = False
        def allow_all_pre_hook(data):
            nonlocal hook_called
            hook_called = True
            return True

        self.hooks.register_pre_hook("check_allow", allow_all_pre_hook)
        res = self.hooks.validate_with_hooks("agent_01", [0.5] * 16)
        self.assertTrue(hook_called)
        self.assertTrue(res.is_valid)

    def test_pre_hook_deny(self):
        """Test pre-hook denying unauthorized action before validation."""
        def deny_unauthorized_agent(data):
            return data["agent_id"] != "rogue_ai"

        self.hooks.register_pre_hook("enforce_auth", deny_unauthorized_agent)
        
        # Rogue agent blocked
        res_rogue = self.hooks.validate_with_hooks("rogue_ai", [0.5] * 16)
        self.assertFalse(res_rogue.is_valid)
        self.assertIsNone(res_rogue.config)

        # Trusted agent allowed
        res_trusted = self.hooks.validate_with_hooks("trusted_ai", [0.5] * 16)
        self.assertTrue(res_trusted.is_valid)

    def test_post_hook_execution(self):
        """Test post-hook executes with validation result."""
        captured_results = []
        def post_hook_logger(res: ValidationResult):
            captured_results.append(res)

        self.hooks.register_post_hook("audit_logger", post_hook_logger)
        res = self.hooks.validate_with_hooks("agent_audit", [0.5] * 16)

        self.assertEqual(len(captured_results), 1)
        self.assertEqual(captured_results[0].cert_hash, res.cert_hash)

    def test_anomaly_hook_on_invalid_decision(self):
        """Test anomaly hook triggers only when decision validation fails."""
        anomalies_detected = []
        def anomaly_collector(res: ValidationResult):
            anomalies_detected.append(res)

        self.hooks.register_anomaly_hook("quarantine_hook", anomaly_collector)

        # Valid decision does not trigger anomaly hook
        self.hooks.validate_with_hooks("agent_ok", [0.5] * 16)
        self.assertEqual(len(anomalies_detected), 0)

        # Invalid decision (bad dimensions) triggers anomaly hook
        self.hooks.validate_with_hooks("agent_bad", [0.5] * 4)
        self.assertEqual(len(anomalies_detected), 1)


class TestCl16_4Benchmark(unittest.TestCase):
    """Test SI-500 Cross-Domain Benchmark integration."""

    def setUp(self):
        self.validator = HyperValidator()
        self.bench = Cl16_4Benchmark(validator=self.validator)

    def test_benchmark_registration(self):
        """Test that standard benchmark suites are registered."""
        self.assertIn("validation_latency", self.bench._benchmarks)
        self.assertIn("throughput_1k", self.bench._benchmarks)
        self.assertIn("mapping_accuracy", self.bench._benchmarks)
        self.assertIn("constraint_checking", self.bench._benchmarks)
        self.assertIn("memory_usage", self.bench._benchmarks)

    def test_benchmark_validation_latency(self):
        """Test validation latency benchmark meets < 100ms requirement."""
        res = self.bench._benchmark_validation_latency()
        self.assertIsInstance(res, BenchmarkResult)
        self.assertTrue(res.passed)
        self.assertLess(res.latency_ms, 100.0)  # P99 latency target < 100ms

    def test_benchmark_constraint_checking(self):
        """Test constraint checking benchmark meets < 50ms requirement."""
        res = self.bench._benchmark_constraint_checking()
        self.assertTrue(res.passed)
        self.assertLess(res.latency_ms, 50.0)

    def test_benchmark_mapping_accuracy(self):
        """Test mapping accuracy benchmark achieves high precision."""
        res = self.bench._benchmark_mapping_accuracy()
        self.assertTrue(res.passed)
        self.assertGreaterEqual(res.score, 0.99)


class TestBoundaryEnforcement(unittest.TestCase):
    """Test that Cl(16,4) maintains strict separation as research/audit substrate."""

    def test_authority_boundary_invariants(self):
        """Verify Cl(16,4) is non-authoritative for real-time production gate (which is Cl(4,1))."""
        integration = Cl16_4EngineIntegration()
        # Verify research parameter bounds
        self.assertEqual(integration.space.n, 16)
        self.assertEqual(integration.space.k, 4)
        # Production gate remains 32-blade Cl(4,1); Cl(16,4) is 1,820 4-blade exploration
        self.assertEqual(integration.space.size, 1820)


if __name__ == "__main__":
    unittest.main()
