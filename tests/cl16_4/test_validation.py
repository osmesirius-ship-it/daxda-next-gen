"""
Tests for Cl(16,4) HyperValidator and Validation Pipeline
=========================================================
"""

import unittest
import json
import time
from daxda_engine.cl16_4.combinatorics.cl_space import ClSpace, ClConfig
from daxda_engine.cl16_4.combinatorics.constraints import ConstraintSystem
from daxda_engine.cl16_4.validation.validator import HyperValidator, ValidationRequest, ValidationResult
from daxda_engine.cl16_4.validation.parallel import ParallelValidator, BatchProcessor
from daxda_engine.cl16_4.validation.adaptive import AdaptiveConstraintManager, ThreatLevel, ConstraintProfile


class TestHyperValidator(unittest.TestCase):
    """Test HyperValidator core functionality."""

    def setUp(self):
        self.space = ClSpace(n=16, k=4)
        self.validator = HyperValidator(space=self.space)

    def test_validator_initialization(self):
        """Test validator initialization and default configuration."""
        self.assertEqual(self.validator.space.n, 16)
        self.assertEqual(self.validator.space.k, 4)
        stats = self.validator.get_stats()
        self.assertEqual(stats["total_validations"], 0)
        self.assertEqual(stats["valid_count"], 0)
        self.assertEqual(stats["invalid_count"], 0)

    def test_valid_decision_vector(self):
        """Test validation of a well-formed 16D continuous decision vector."""
        decision_vector = [0.95, 0.85, 0.75, 0.65] + [0.1] * 12
        req = ValidationRequest(
            agent_id="agent_alpha",
            decision_vector=decision_vector,
            context={"mission": "dyson_sphere_collector_reorientation"}
        )
        result = self.validator.validate(req)

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.config)
        self.assertEqual(result.config.indices, (0, 1, 2, 3))
        self.assertTrue(result.cert_hash)
        self.assertGreater(result.validation_time_ms, 0.0)
        self.assertEqual(len(result.constraints.failed), 0)

        # Check stats incremented
        stats = self.validator.get_stats()
        self.assertEqual(stats["total_validations"], 1)
        self.assertEqual(stats["valid_count"], 1)

    def test_invalid_decision_vector_dimensions(self):
        """Test validation fail-closed on non-16D decision vectors."""
        # 8-dimensional vector (too short)
        short_req = ValidationRequest(agent_id="agent_short", decision_vector=[0.5] * 8)
        res_short = self.validator.validate(short_req)
        self.assertFalse(res_short.is_valid)
        self.assertIsNone(res_short.config)
        self.assertIn("mapping_failed", res_short.constraints.failed)

        # 20-dimensional vector (too long)
        long_req = ValidationRequest(agent_id="agent_long", decision_vector=[0.5] * 20)
        res_long = self.validator.validate(long_req)
        self.assertFalse(res_long.is_valid)
        self.assertIsNone(res_long.config)

    def test_uniform_decision_vector(self):
        """Test uniform 16D decision vector (zero variance)."""
        uniform_req = ValidationRequest(agent_id="agent_uniform", decision_vector=[0.5] * 16)
        result = self.validator.validate(uniform_req)
        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.config)
        self.assertEqual(len(result.config.indices), 4)

    def test_validate_batch(self):
        """Test batch validation over multiple requests."""
        requests = [
            ValidationRequest(agent_id=f"agent_{i}", decision_vector=[float(i % 16 == j) for j in range(16)])
            for i in range(10)
        ]
        results = self.validator.validate_batch(requests)
        self.assertEqual(len(results), 10)
        for res in results:
            self.assertTrue(res.is_valid)

        stats = self.validator.get_stats()
        self.assertEqual(stats["total_validations"], 10)

    def test_validate_with_certificate(self):
        """Test certificate generation and structured JSON integrity."""
        req = ValidationRequest(
            agent_id="agent_cert_test",
            decision_vector=[0.9, 0.8, 0.7, 0.6] + [0.05] * 12
        )
        result, cert_json = self.validator.validate_with_certificate(req)

        self.assertTrue(result.is_valid)
        cert_data = json.loads(cert_json)
        self.assertEqual(cert_data["type"], "daxda_cl16_4_validation_certificate")
        self.assertEqual(cert_data["version"], "1.0.0")
        self.assertEqual(cert_data["request"]["agent_id"], "agent_cert_test")
        self.assertEqual(cert_data["result"]["cert_hash"], result.cert_hash)
        self.assertEqual(cert_data["validator"]["space"], "Cl(16,4)")

    def test_determinism_same_input_same_hash(self):
        """Test that identical decision vectors yield identical configurations and certificate hashes."""
        vec = [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6] + [0.0] * 8
        req1 = ValidationRequest(agent_id="ag1", decision_vector=vec, request_id="fixed_req_id", timestamp=1700000000.0)
        req2 = ValidationRequest(agent_id="ag1", decision_vector=vec, request_id="fixed_req_id", timestamp=1700000000.0)

        res1 = self.validator.validate(req1)
        res2 = self.validator.validate(req2)

        self.assertEqual(res1.config, res2.config)
        self.assertEqual(res1.cert_hash, res2.cert_hash)

    def test_stats_tracking_and_reset(self):
        """Test statistics recording and reset mechanism."""
        self.validator.validate(ValidationRequest(agent_id="a1", decision_vector=[0.1] * 16))
        self.validator.validate(ValidationRequest(agent_id="a2", decision_vector=[0.1] * 4))  # invalid

        stats = self.validator.get_stats()
        self.assertEqual(stats["total_validations"], 2)
        self.assertEqual(stats["valid_count"], 1)
        self.assertEqual(stats["invalid_count"], 1)

        self.validator.reset_stats()
        reset_stats = self.validator.get_stats()
        self.assertEqual(reset_stats["total_validations"], 0)
        self.assertEqual(reset_stats["valid_count"], 0)
        self.assertEqual(reset_stats["invalid_count"], 0)


class TestParallelValidator(unittest.TestCase):
    """Test multi-threaded parallel validation."""

    def setUp(self):
        self.validator = HyperValidator()
        self.parallel = ParallelValidator(validator=self.validator, max_workers=4)

    def test_parallel_validation_order_preserved(self):
        """Test that results maintain strict input order when executed in parallel."""
        requests = []
        for i in range(30):
            vec = [0.0] * 16
            vec[i % 16] = 1.0
            vec[(i + 1) % 16] = 0.8
            vec[(i + 2) % 16] = 0.6
            vec[(i + 3) % 16] = 0.4
            requests.append(ValidationRequest(agent_id=f"agent_par_{i}", decision_vector=vec, request_id=f"req_{i:03d}"))

        results = self.parallel.validate_parallel(requests, max_workers=4)
        self.assertEqual(len(results), len(requests))
        for i, res in enumerate(results):
            self.assertEqual(res.request_id, f"req_{i:03d}")
            self.assertTrue(res.is_valid)

    def test_parallel_stream_validation(self):
        """Test stream-based batch validation from a generator."""
        def request_stream():
            for i in range(25):
                yield ValidationRequest(agent_id=f"stream_{i}", decision_vector=[0.5] * 16)

        results = self.parallel.validate_stream(request_stream(), max_requests=25, batch_size=10)
        self.assertEqual(len(results), 25)

    def test_validate_with_progress_callback(self):
        """Test progress callback invocation during parallel/serial validation."""
        progress_calls = []
        def callback(completed, total):
            progress_calls.append((completed, total))

        requests = [ValidationRequest(agent_id=f"p_{i}", decision_vector=[0.5] * 16) for i in range(5)]
        results = self.parallel.validate_with_progress(requests, progress_callback=callback)
        self.assertEqual(len(results), 5)
        self.assertEqual(len(progress_calls), 5)
        self.assertEqual(progress_calls[-1], (5, 5))


class TestBatchProcessor(unittest.TestCase):
    """Test high-throughput batch processor."""

    def test_batch_processor_execution(self):
        """Test batch processor over large request arrays."""
        processor = BatchProcessor(batch_size=100, max_workers=4)
        requests = [
            ValidationRequest(agent_id=f"batch_{i}", decision_vector=[float((i + j) % 16) / 16.0 for j in range(16)])
            for i in range(250)
        ]
        summary = processor.process_batch(requests)

        self.assertEqual(summary["total"], 250)
        self.assertEqual(summary["valid"], 250)
        self.assertEqual(summary["invalid"], 0)
        self.assertGreater(summary["throughput"], 0)
        self.assertLess(summary["avg_time_ms"], 10.0)  # sub-10ms per validation


class TestAdaptiveConstraintManager(unittest.TestCase):
    """Test runtime dynamic and adaptive constraint management."""

    def setUp(self):
        self.space = ClSpace(n=16, k=4)
        self.constraints = ConstraintSystem(space=self.space)
        self.adaptive = AdaptiveConstraintManager(space=self.space, constraint_system=self.constraints)

    def test_initial_profiles_and_threat_level(self):
        """Test that default profiles are properly initialized."""
        self.assertIn("low", self.adaptive.config.profiles)
        self.assertIn("medium", self.adaptive.config.profiles)
        self.assertIn("high", self.adaptive.config.profiles)
        self.assertIn("critical", self.adaptive.config.profiles)
        self.assertEqual(self.adaptive.get_threat_level(), ThreatLevel.MEDIUM)

    def test_set_threat_level(self):
        """Test switching threat levels and applying profiles."""
        success_high = self.adaptive.set_threat_level(ThreatLevel.HIGH)
        self.assertTrue(success_high)
        self.assertEqual(self.adaptive.get_threat_level(), ThreatLevel.HIGH)

        success_low = self.adaptive.set_threat_level(ThreatLevel.LOW)
        self.assertTrue(success_low)
        self.assertEqual(self.adaptive.get_threat_level(), ThreatLevel.LOW)

    def test_invalid_profile_handling(self):
        """Test that setting a non-existent profile safely fails."""
        self.assertFalse(self.adaptive.set_profile("non_existent_threat_profile"))

    def test_dynamic_constraint_addition(self):
        """Test adding dynamic constraints and evaluating configurations."""
        self.adaptive.add_dynamic_constraint("require_upper_half", {"min_sum": 30}, severity="hard")
        
        low_config = self.space.get_config((0, 1, 2, 3))  # sum = 6
        high_config = self.space.get_config((12, 13, 14, 15))  # sum = 54

        res_low = self.constraints.check_config(low_config)
        self.assertIn("require_upper_half", res_low.failed)

        res_high = self.constraints.check_config(high_config)
        self.assertNotIn("require_upper_half", res_high.failed)

    def test_enable_disable_constraint(self):
        """Test enabling and disabling constraints across profiles."""
        self.adaptive.add_dynamic_constraint("test_toggle", {"min_sum": 20})
        self.adaptive.disable_constraint("test_toggle")
        profile = self.adaptive.get_current_profile()
        self.assertFalse(profile.constraints["test_toggle"]["enabled"])

        self.adaptive.enable_constraint("test_toggle")
        self.assertTrue(profile.constraints["test_toggle"]["enabled"])

    def test_auto_adjustment_trigger(self):
        """Test automatic threat level elevation based on anomaly/failure metrics."""
        self.adaptive.config.adjustment_interval = 0.0  # Force immediate check
        self.adaptive.config.auto_adjust = True

        # Simulate 10 validation failures (>30% failure rate)
        for _ in range(10):
            self.adaptive.record_metric({"is_valid": False, "agent_id": "rogue_ai"})

        # Threat level should elevate to HIGH
        self.assertEqual(self.adaptive.get_threat_level(), ThreatLevel.HIGH)


if __name__ == "__main__":
    unittest.main()
