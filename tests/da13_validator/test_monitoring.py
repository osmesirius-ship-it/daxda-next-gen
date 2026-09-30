"""
Unit & Integration Tests: DA13 Observability, Tracing, Alerter & Dashboard
=========================================================================
"""

import pytest
from da13_validator.monitoring import (
    DA13MetricsCollector,
    DistributedTracer,
    DA13ClusterAlerter,
    ClusterDashboard
)
from da13_validator.cluster import ClusterManager, ClusterConfig


class TestDA13Monitoring:
    """Tests for metrics collection, distributed tracing, alerting, and dashboard rendering."""

    def test_metrics_collector(self):
        collector = DA13MetricsCollector()
        for i in range(10):
            collector.record_validation(latency_ms=10.0 + i, is_valid=(i % 2 == 0))

        collector.update_queue_depth(15)
        collector.record_scale_event()
        collector.record_error()

        s = collector.get_summary()
        assert s["total_validations"] == 10
        assert s["passed_validations"] == 5
        assert s["failed_validations"] == 5
        assert s["error_count"] == 1
        assert s["queue_depth"] == 15
        assert s["autoscale_events"] == 1
        assert s["latency_p99_ms"] > 0.0

        prom_text = collector.export_prometheus_text()
        assert "da13_queue_depth 15" in prom_text

    def test_distributed_tracer(self):
        tracer = DistributedTracer(service_name="da13-unit-test")
        span = tracer.start_span("validate_payload")
        assert span.trace_id is not None
        assert span.span_id is not None

        duration = span.finish()
        assert duration >= 0.0
        assert span.end_time is not None

        trace = tracer.get_trace(span.trace_id)
        assert len(trace) == 1
        assert trace[0]["name"] == "validate_payload"

    def test_cluster_alerter_sla_checks(self):
        alerter = DA13ClusterAlerter()
        # Normal condition -> no alerts
        alerts_ok = alerter.check_sla_and_alert(
            p99_latency_ms=50.0,
            failed_worker_count=0,
            queue_depth=10,
            availability_pct=100.0
        )
        assert len(alerts_ok) == 0

        # Degradation condition -> P99 latency breach + failed workers
        alerts_bad = alerter.check_sla_and_alert(
            p99_latency_ms=1250.0,  # > 1000ms SLA
            failed_worker_count=3,  # > 2 critical
            queue_depth=600,        # > 500 saturated
            availability_pct=98.5   # < 99.99%
        )
        assert len(alerts_bad) == 4
        types = [a.alert_type for a in alerts_bad]
        assert "P99_LATENCY_BREACH" in types
        assert "WORKER_NODE_FAILED" in types
        assert "QUEUE_DEPTH_SATURATED" in types
        assert "AVAILABILITY_SLA_BREACH" in types

    def test_dashboard_rendering(self):
        cm = ClusterManager(ClusterConfig(initial_workers=2))
        cm.start()
        collector = DA13MetricsCollector()
        collector.record_validation(latency_ms=12.5, is_valid=True)

        dashboard = ClusterDashboard(cluster_manager=cm, metrics_collector=collector)
        ascii_view = dashboard.render_ascii_dashboard()
        assert "DAXDA DA13 DISTRIBUTED GPU VALIDATOR CLUSTER" in ascii_view
        assert "WORKER NODE TOPOLOGY:" in ascii_view

        json_view = dashboard.render_json()
        assert "cluster" in json_view
        assert "metrics" in json_view

        cm.stop()
