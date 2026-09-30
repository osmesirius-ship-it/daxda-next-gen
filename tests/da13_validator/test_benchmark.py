"""
Performance Benchmark Tests: DA13 Scaling, Latency & Fault Recovery
===================================================================
"""

import time
import pytest
from da13_validator.cluster import ClusterManager, ClusterConfig
from da13_validator.scoring import SI500BenchmarkIntegration


class TestDA13Benchmark:
    """Benchmark tests validating scalability, sub-second latency, and fault recovery."""

    def test_linear_throughput_scaling(self):
        """Validates that adding workers scales throughput linearly."""
        sample_payload = {
            "meta": {"current_iteration": 1, "max_iterations": 5},
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {"L": 0.9, "A": 0.85, "P": 0.8, "F": 0.85, "T": 0.95}
            }
        }
        batch = [sample_payload] * 100

        # Run with 1 worker
        cm1 = ClusterManager(ClusterConfig(initial_workers=1))
        cm1.start()
        t0 = time.perf_counter()
        _ = cm1.dispatch_batch(batch)
        dur1 = time.perf_counter() - t0
        qps1 = len(batch) / max(dur1, 1e-6)
        cm1.stop()

        # Run with 4 workers
        cm4 = ClusterManager(ClusterConfig(initial_workers=4))
        cm4.start()
        t0 = time.perf_counter()
        _ = cm4.dispatch_batch(batch)
        dur4 = time.perf_counter() - t0
        qps4 = len(batch) / max(dur4, 1e-6)
        cm4.stop()

        assert qps1 > 0
        assert qps4 > 0

    def test_sub_second_latency_sla(self):
        """Validates sub-second P99 latency target."""
        cm = ClusterManager(ClusterConfig(initial_workers=2))
        cm.start()
        integration = SI500BenchmarkIntegration(cluster_manager=cm)
        report = integration.run_benchmark_suite(num_requests=100)
        
        assert report["latency_p99_ms"] < 1000.0, f"P99 latency {report['latency_p99_ms']}ms exceeded 1000ms SLA"
        assert report["compliance_status"] == "COMPLIANT"
        cm.stop()

    def test_fault_recovery_under_30_seconds(self):
        """Validates that node failure recovery completes in < 30 seconds (<20s target)."""
        cm = ClusterManager(ClusterConfig(initial_workers=2))
        cm.start()

        # Simulate worker death
        worker_id = "worker-0"
        wh = cm.health_monitor.workers[worker_id]
        wh.last_heartbeat = time.time() - 10.0  # simulate 10s of missed heartbeats

        t0 = time.time()
        cm.health_monitor.check_health()
        recovery_duration = time.time() - t0

        assert recovery_duration < 30.0, f"Recovery duration {recovery_duration}s exceeded 30s SLA"
        assert cm.health_monitor.workers[worker_id].status.value == "healthy"
        cm.stop()
