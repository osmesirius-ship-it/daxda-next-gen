"""
DA13 Cluster Visualization Dashboard
====================================

Generates terminal dashboard views and JSON telemetry summaries for operator monitoring.
"""

import time
from typing import Dict, Any, List, Optional
from .metrics_collector import DA13MetricsCollector
from ..cluster.manager import ClusterManager


class ClusterDashboard:
    """Renders visual cluster status and telemetry dashboards."""

    def __init__(self, cluster_manager: ClusterManager, metrics_collector: DA13MetricsCollector):
        self.cluster = cluster_manager
        self.metrics = metrics_collector

    def render_ascii_dashboard(self) -> str:
        """Renders an ASCII terminal dashboard of cluster health and throughput."""
        status = self.cluster.get_status()
        m = self.metrics.get_summary()

        lines = [
            "================================================================================",
            " DAXDA DA13 DISTRIBUTED GPU VALIDATOR CLUSTER — MULTIVERSAL TRANSIT HUB",
            "================================================================================",
            f" Cluster ID:      {status['cluster_id']} | Uptime: {m['uptime_sec']}s",
            f" Active Workers:  {status['total_workers']} | Healthy: {status['healthy_workers']} | Failed: {status['failed_workers']}",
            f" Availability:    {status['availability_pct']}% (Target: 99.99%)",
            "--------------------------------------------------------------------------------",
            " WORKLOAD PERFORMANCE & SLA METRICS:",
            f"   Total Processed:   {m['total_validations']} (Passed: {m['passed_validations']} | Failed: {m['failed_validations']})",
            f"   Current QPS:       {m['throughput_qps']:.1f} validations/sec",
            f"   Latency P50:       {m['latency_p50_ms']:.2f} ms",
            f"   Latency P95:       {m['latency_p95_ms']:.2f} ms",
            f"   Latency P99:       {m['latency_p99_ms']:.2f} ms (Target: < 1000.0 ms)",
            f"   Task Queue Backlog:{m['queue_depth']} tasks",
            f"   Autoscale Events:  {m['autoscale_events']}",
            "--------------------------------------------------------------------------------",
            " WORKER NODE TOPOLOGY:",
        ]

        workers = status.get("workers", {})
        for w_id, w_info in workers.items():
            gpu_str = f"GPU #{w_info.get('gpu_id', 0)}" if w_info.get('gpu_id') is not None else "CPU"
            lines.append(
                f"   [{w_info['status'].upper():^9}] {w_id:<12} | {gpu_str:<8} | "
                f"Latency: {w_info['latency_ms']:>6.2f}ms | Util: {w_info['gpu_utilization_pct']:>5.1f}%"
            )

        lines.extend([
            "================================================================================",
            f" Status: {'✅ OPTIMAL' if status['availability_pct'] >= 99.99 and m['latency_p99_ms'] < 1000 else '⚠️ ATTENTION REQUIRED'}",
            "================================================================================"
        ])
        return "\n".join(lines)

    def render_json(self) -> Dict[str, Any]:
        """Returns JSON telemetry block for web dashboards."""
        return {
            "timestamp": time.time(),
            "cluster": self.cluster.get_status(),
            "metrics": self.metrics.get_summary()
        }
