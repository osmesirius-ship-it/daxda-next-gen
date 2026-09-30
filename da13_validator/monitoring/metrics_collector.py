"""
DA13 Metrics Collector
======================

Prometheus-compatible metrics collector for GPU validator cluster observability.
Tracks validation latency (P50, P95, P99), throughput QPS, GPU utilization,
memory usage, queue depth, error rates, and autoscaling transitions.
"""

import time
import math
from typing import Dict, Any, List, Optional
from collections import deque


class DA13MetricsCollector:
    """Prometheus-compatible telemetry and metrics collector."""

    def __init__(self):
        self.total_validations = 0
        self.passed_validations = 0
        self.failed_validations = 0
        self.total_errors = 0
        self.latencies: deque = deque(maxlen=5000)
        self.gpu_utilizations: Dict[str, float] = {}
        self.gpu_memory_used_mb: Dict[str, float] = {}
        self.queue_depth = 0
        self.autoscale_events = 0
        self.start_time = time.time()

    def record_validation(self, latency_ms: float, is_valid: bool) -> None:
        """Records a completed validation measurement."""
        self.total_validations += 1
        if is_valid:
            self.passed_validations += 1
        else:
            self.failed_validations += 1
        self.latencies.append(latency_ms)

    def record_error(self) -> None:
        """Records a validation error."""
        self.total_errors += 1

    def update_gpu_metrics(self, worker_id: str, utilization_pct: float, memory_mb: float) -> None:
        """Updates GPU utilization and memory for a worker."""
        self.gpu_utilizations[worker_id] = utilization_pct
        self.gpu_memory_used_mb[worker_id] = memory_mb

    def update_queue_depth(self, depth: int) -> None:
        """Updates current queue depth gauge."""
        self.queue_depth = depth

    def record_scale_event(self) -> None:
        """Increments autoscale counter."""
        self.autoscale_events += 1

    def get_summary(self) -> Dict[str, Any]:
        """Calculates current cluster metrics summary."""
        elapsed = max(1e-6, time.time() - self.start_time)
        qps = self.total_validations / elapsed

        if self.latencies:
            sorted_lat = sorted(self.latencies)
            n = len(sorted_lat)
            p50 = sorted_lat[int(n * 0.50)]
            p95 = sorted_lat[int(n * 0.95)]
            p99 = sorted_lat[min(int(n * 0.99), n - 1)]
            avg_lat = sum(sorted_lat) / n
        else:
            p50 = p95 = p99 = avg_lat = 0.0

        avg_gpu_util = (
            sum(self.gpu_utilizations.values()) / max(1, len(self.gpu_utilizations))
            if self.gpu_utilizations else 0.0
        )

        return {
            "uptime_sec": round(elapsed, 2),
            "total_validations": self.total_validations,
            "passed_validations": self.passed_validations,
            "failed_validations": self.failed_validations,
            "error_count": self.total_errors,
            "throughput_qps": round(qps, 2),
            "latency_p50_ms": round(p50, 3),
            "latency_p95_ms": round(p95, 3),
            "latency_p99_ms": round(p99, 3),
            "avg_latency_ms": round(avg_lat, 3),
            "queue_depth": self.queue_depth,
            "avg_gpu_utilization_pct": round(avg_gpu_util, 2),
            "autoscale_events": self.autoscale_events
        }

    def export_prometheus_text(self) -> str:
        """Exports metrics in standard Prometheus exposition format."""
        s = self.get_summary()
        lines = [
            "# HELP da13_validation_throughput_total Total validations processed",
            "# TYPE da13_validation_throughput_total counter",
            f"da13_validation_throughput_total {s['total_validations']}",
            "",
            "# HELP da13_validation_passed_total Total validations passed",
            "# TYPE da13_validation_passed_total counter",
            f"da13_validation_passed_total {s['passed_validations']}",
            "",
            "# HELP da13_validation_failed_total Total validations failed or halted",
            "# TYPE da13_validation_failed_total counter",
            f"da13_validation_failed_total {s['failed_validations']}",
            "",
            "# HELP da13_validation_latency_p99_ms P99 latency in milliseconds",
            "# TYPE da13_validation_latency_p99_ms gauge",
            f"da13_validation_latency_p99_ms {s['latency_p99_ms']}",
            "",
            "# HELP da13_validation_latency_p50_ms P50 latency in milliseconds",
            "# TYPE da13_validation_latency_p50_ms gauge",
            f"da13_validation_latency_p50_ms {s['latency_p50_ms']}",
            "",
            "# HELP da13_queue_depth Pending tasks in priority queue",
            "# TYPE da13_queue_depth gauge",
            f"da13_queue_depth {s['queue_depth']}",
            "",
            "# HELP da13_gpu_utilization_pct Average GPU utilization across workers",
            "# TYPE da13_gpu_utilization_pct gauge",
            f"da13_gpu_utilization_pct {s['avg_gpu_utilization_pct']}",
            "",
            "# HELP da13_autoscale_events_total Total dynamic scaling events",
            "# TYPE da13_autoscale_events_total counter",
            f"da13_autoscale_events_total {s['autoscale_events']}",
            ""
        ]
        return "\n".join(lines)
