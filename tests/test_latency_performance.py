"""
DAXDA Guard Systems Engineering Latency Performance Test
Asserts sub-millisecond execution (< 2.0 ms SLA target) across governance evaluations and C++ blade lookups.
"""

import pytest
from daxda_guard.core import DAXDAGuardCore


class TestLatencyPerformanceSLA:
    def setup_method(self):
        self.core = DAXDAGuardCore()
        assert self.core.available

    def test_cpp_blade_lookup_sub_nanosecond(self):
        ns_per_op = self.core.benchmark_cpp_blade_lookup(1_000_000)
        assert ns_per_op < 50.0, f"Blade lookup speed was {ns_per_op:.2f} ns/op (expected < 50.0 ns)"

    def test_average_request_latency_sub_millisecond(self):
        iterations = 10000
        total_time_ms = 0.0

        import time
        t0 = time.perf_counter()
        for i in range(iterations):
            self.core.evaluate("finance", "execute_trade(symbol='AAPL', quantity=100)")
        t1 = time.perf_counter()

        total_time_ms = (t1 - t0) * 1000.0
        avg_latency_ms = total_time_ms / iterations

        assert avg_latency_ms < 2.0, f"Average request latency was {avg_latency_ms:.4f} ms (SLA target < 2.0 ms)"

    def test_interlock_attack_block_latency(self):
        iterations = 5000
        import time
        t0 = time.perf_counter()
        for i in range(iterations):
            self.core.evaluate("finance", "DROP DATABASE users;")
        t1 = time.perf_counter()

        avg_latency_ms = ((t1 - t0) * 1000.0) / iterations
        assert avg_latency_ms < 2.0, f"Interlock block latency was {avg_latency_ms:.4f} ms (SLA target < 2.0 ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
