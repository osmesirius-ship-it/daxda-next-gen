"""
Unit & Integration Tests: DA13 Cluster Management & Autoscaling
==============================================================
"""

import time
import pytest
from da13_validator.cluster import (
    ClusterConfig,
    ClusterManager,
    HealthMonitor,
    WorkerHealthStatus,
    DA13Autoscaler
)


class TestDA13Cluster:
    """Tests for cluster configuration, lifecycle, health monitoring, and autoscaling."""

    def test_cluster_config_defaults_and_env(self, monkeypatch):
        cfg = ClusterConfig()
        assert cfg.min_workers == 1
        assert cfg.max_workers == 1024
        assert cfg.initial_workers == 4
        assert cfg.gpu_per_worker == 1
        assert cfg.fault_recovery_timeout_sec == 30.0

        monkeypatch.setenv("DA13_INITIAL_WORKERS", "8")
        monkeypatch.setenv("DA13_MIN_WORKERS", "2")
        env_cfg = ClusterConfig.from_env()
        assert env_cfg.initial_workers == 8
        assert env_cfg.min_workers == 2

    def test_cluster_manager_lifecycle_and_scaling(self):
        cm = ClusterManager(ClusterConfig(min_workers=1, max_workers=32, initial_workers=3))
        assert not cm.is_running
        cm.start()
        assert cm.is_running
        assert len(cm.workers) == 3

        # Scale UP to 6 workers
        res_up = cm.scale(6)
        assert res_up["current_workers"] == 6
        assert len(cm.workers) == 6

        # Scale DOWN to 2 workers
        res_down = cm.scale(2)
        assert res_down["current_workers"] == 2
        assert len(cm.workers) == 2

        # Enforce min/max boundaries
        res_min = cm.scale(0)
        assert res_min["current_workers"] == 1
        res_max = cm.scale(100)
        assert res_max["current_workers"] == 32

        cm.stop()
        assert not cm.is_running
        assert len(cm.workers) == 0

    def test_health_monitor_heartbeat_and_timeout(self):
        recovered = []
        def mock_recover(wid):
            recovered.append(wid)
            return True

        monitor = HealthMonitor(node_timeout_sec=0.1, recovery_callback=mock_recover)
        wh = monitor.register_worker("test-worker-1", gpu_id=0)
        assert wh.status == WorkerHealthStatus.HEALTHY

        # Record active heartbeat
        monitor.record_heartbeat("test-worker-1", latency_ms=5.0, gpu_utilization_pct=75.0)
        assert wh.gpu_utilization_pct == 75.0

        # Wait for timeout to trigger failure
        time.sleep(0.15)
        health_status = monitor.check_health()
        assert "test-worker-1" in recovered
        assert health_status["test-worker-1"].status == WorkerHealthStatus.HEALTHY

    def test_autoscaler_recommendations(self):
        config = ClusterConfig(
            min_workers=1,
            max_workers=64,
            per_gpu_qps_capacity=100.0,
            scale_up_p99_threshold_ms=800.0,
            scale_down_p99_threshold_ms=200.0
        )
        autoscaler = DA13Autoscaler(config)
        autoscaler.cooldown_sec = 0.0  # zero cooldown for instant test evaluation

        # Under heavy load: P99 latency = 950ms, QPS = 500
        for _ in range(5):
            autoscaler.record_metrics(current_qps=500.0, latency_p99_ms=950.0, queue_depth=200)

        recommended = autoscaler.recommend_scale(current_workers=2)
        assert recommended > 2, "Autoscaler should recommend scaling up under high latency and queue backlog"

        # Under light load: P99 latency = 50ms, QPS = 20, queue = 0
        autoscaler.metrics_window.clear()
        for _ in range(5):
            autoscaler.record_metrics(current_qps=20.0, latency_p99_ms=50.0, queue_depth=0)

        recommended_down = autoscaler.recommend_scale(current_workers=8)
        assert recommended_down < 8, "Autoscaler should recommend scaling down under low latency and idle load"
