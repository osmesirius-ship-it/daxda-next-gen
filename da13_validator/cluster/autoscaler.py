"""
DA13 Dynamic GPU Autoscaler
===========================

Monitors validation queue depth, QPS throughput, and P99 latency to dynamically
scale Ray GPU worker nodes between 1 and 1024 GPUs with linear efficiency.
"""

import time
from collections import deque
from typing import Dict, Any, List, Optional
from .config import ClusterConfig


class DA13Autoscaler:
    """Dynamic scaling controller for GPU validator cluster."""

    def __init__(self, config: ClusterConfig):
        self.config = config
        self.metrics_window = deque(maxlen=60)  # 60 samples sliding window
        self.last_scale_time = 0.0
        self.cooldown_sec = 10.0
        self.scale_history: List[Dict[str, Any]] = []

    def record_metrics(
        self,
        current_qps: float,
        latency_p99_ms: float,
        queue_depth: int,
        gpu_utilization_pct: float = 0.0
    ) -> None:
        """Records a timestamped telemetry sample."""
        self.metrics_window.append({
            "timestamp": time.time(),
            "qps": max(0.0, current_qps),
            "latency_p99_ms": max(0.0, latency_p99_ms),
            "queue_depth": max(0, queue_depth),
            "gpu_utilization_pct": max(0.0, min(100.0, gpu_utilization_pct))
        })

    def recommend_scale(self, current_workers: int) -> int:
        """
        Computes recommended target worker count based on:
        1. P99 latency vs threshold (<800ms target, <1000ms SLA)
        2. Queue backlog depth
        3. Total QPS load vs cluster capacity
        4. Cooldown time enforcement
        """
        now = time.time()
        if not self.metrics_window:
            return current_workers

        # Check cooldown
        if (now - self.last_scale_time) < self.cooldown_sec:
            return current_workers

        # Calculate sliding averages
        avg_qps = sum(m["qps"] for m in self.metrics_window) / len(self.metrics_window)
        avg_latency = sum(m["latency_p99_ms"] for m in self.metrics_window) / len(self.metrics_window)
        latest_queue = self.metrics_window[-1]["queue_depth"]

        cluster_capacity_qps = current_workers * self.config.per_gpu_qps_capacity
        utilization = avg_qps / max(cluster_capacity_qps, 1.0)

        target_workers = current_workers

        # Scale UP conditions:
        # High latency (>800ms) OR queue backlog (>100 tasks) OR high utilization (>80%)
        if (
            avg_latency > self.config.scale_up_p99_threshold_ms
            or latest_queue > self.config.scale_up_queue_threshold
            or utilization > 0.80
        ):
            # Scale proactively by ratio needed + queue drain buffer
            required_workers = int((avg_qps + (latest_queue / 5.0)) / self.config.per_gpu_qps_capacity) + 1
            # Step scaling: at least +50% or +2 workers
            step_increase = max(2, int(current_workers * 1.5))
            target_workers = max(current_workers + 1, min(required_workers, step_increase))
            target_workers = min(target_workers, self.config.max_workers)

        # Scale DOWN conditions:
        # Low latency (<200ms) AND small queue (<10 tasks) AND low utilization (<30%)
        elif (
            avg_latency < self.config.scale_down_p99_threshold_ms
            and latest_queue < 10
            and utilization < 0.30
            and current_workers > self.config.min_workers
        ):
            desired_workers = max(self.config.min_workers, int(avg_qps / self.config.per_gpu_qps_capacity) + 1)
            target_workers = max(self.config.min_workers, min(current_workers - 1, desired_workers))

        if target_workers != current_workers:
            self.last_scale_time = now
            self.scale_history.append({
                "timestamp": now,
                "previous_workers": current_workers,
                "target_workers": target_workers,
                "reason": f"Latency: {avg_latency:.1f}ms, Queue: {latest_queue}, QPS: {avg_qps:.1f}"
            })

        return target_workers
