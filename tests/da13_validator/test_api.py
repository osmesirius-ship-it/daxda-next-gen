"""
Unit & Integration Tests: DA13 REST & WebSocket API Server
==========================================================
"""

import pytest
from da13_validator.api import (
    AuthMiddleware,
    UserRole,
    RestServer,
    WebSocketServer
)
from da13_validator.cluster import ClusterManager, ClusterConfig


class TestDA13API:
    """Tests for authentication, RBAC, REST endpoints, and WebSocket broadcasting."""

    def test_auth_middleware_roles_and_rate_limiting(self):
        auth = AuthMiddleware()

        # Admin key
        admin_client = auth.authenticate("da13-admin-key-2026")
        assert admin_client is not None
        assert admin_client.role == UserRole.ADMIN
        assert auth.check_permission(admin_client, "scale") is True

        # Readonly key
        ro_client = auth.authenticate("da13-readonly-key-2026")
        assert ro_client.role == UserRole.READONLY
        assert auth.check_permission(ro_client, "validate") is False
        assert auth.check_permission(ro_client, "health") is True

        # Invalid key
        assert auth.authenticate("malicious-key") is None

        # Rate limiting test
        admin_client.tokens = 0.5
        assert auth.check_rate_limit(admin_client) is False
        admin_client.tokens = 2.0
        assert auth.check_rate_limit(admin_client) is True

    def test_rest_server_endpoints(self):
        cm = ClusterManager(ClusterConfig(initial_workers=2))
        cm.start()
        rest = RestServer(cluster_manager=cm)

        sample_payload = {
            "meta": {"current_iteration": 1, "max_iterations": 5, "schema_version": "2.0"},
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {"L": 0.9, "A": 0.85, "P": 0.8, "F": 0.85, "T": 0.95},
                "score": 0.8675
            },
            "dax_decision": {"status": "ACCEPT"}
        }

        # 1. Single validation
        val_res = rest.handle_validate(sample_payload, api_key="da13-validator-key-2026")
        assert val_res["status"] == "SUCCESS"
        assert val_res["validation"]["is_valid"] is True
        assert val_res["latency_ms"] > 0.0

        # 2. Batch validation
        batch_res = rest.handle_validate_batch([sample_payload] * 4, api_key="da13-validator-key-2026")
        assert batch_res["status"] == "SUCCESS"
        assert batch_res["total"] == 4
        assert batch_res["passed"] == 4

        # 3. Cluster health
        health_res = rest.handle_cluster_health(api_key="da13-operator-key-2026")
        assert health_res["status"] == "SUCCESS"
        assert health_res["cluster"]["healthy_workers"] == 2

        # 4. Cluster scaling
        scale_res = rest.handle_cluster_scale(target_workers=4, api_key="da13-admin-key-2026")
        assert scale_res["status"] == "SUCCESS"
        assert scale_res["scale_result"]["current_workers"] == 4

        # 5. Prometheus metrics text
        metrics_text = rest.handle_metrics()
        assert "da13_validation_throughput_total" in metrics_text
        assert "da13_validation_latency_p99_ms" in metrics_text

        # 6. Healthz probe
        probe = rest.handle_healthz()
        assert probe["status"] == "UP"

        cm.stop()

    def test_websocket_server_broadcast(self):
        ws = WebSocketServer()
        ws.connect_client("client-1")
        ws.connect_client("client-2")

        stats = ws.get_stats()
        assert stats["active_clients"] == 2

        notified = ws.broadcast_event("validation_events", {"task_id": "task-99", "status": "COMPLETED"})
        assert notified == 2

        ws.disconnect_client("client-1")
        assert ws.get_stats()["active_clients"] == 1
