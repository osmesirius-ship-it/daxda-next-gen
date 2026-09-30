"""
DA13 REST API Server
====================

High-performance REST API for distributed DAXDA governance validation.
Exposes endpoints for single validation, batch validation, cluster management,
scaling, and Prometheus telemetry.
"""

import time
import json
from typing import Dict, Any, List, Optional
from ..cluster.manager import ClusterManager
from ..scoring.schema_validator import SchemaValidator
from ..monitoring.metrics_collector import DA13MetricsCollector
from .auth_middleware import AuthMiddleware, UserRole


class RestServer:
    """REST API Handler supporting direct programmatic execution and HTTP routers."""

    def __init__(
        self,
        cluster_manager: Optional[ClusterManager] = None,
        auth_middleware: Optional[AuthMiddleware] = None,
        metrics_collector: Optional[DA13MetricsCollector] = None
    ):
        self.cluster = cluster_manager or ClusterManager()
        self.auth = auth_middleware or AuthMiddleware()
        self.metrics = metrics_collector or DA13MetricsCollector()
        self.schema_validator = SchemaValidator()

    def handle_validate(self, payload: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """POST /v1/validate: Validates a single governance payload."""
        t0 = time.perf_counter()
        
        # 1. Authentication & RBAC
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "validate"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized or insufficient permissions"}

        # 2. Rate limiting
        if not self.auth.check_rate_limit(client):
            return {"status": "ERROR", "code": 429, "message": "Rate limit exceeded"}

        # 3. Schema & Semantic Validation
        schema_errors = self.schema_validator.validate(payload)

        # 4. Dispatch to cluster
        res = self.cluster.dispatch_validation(payload)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Record metrics
        self.metrics.record_validation(latency_ms=elapsed_ms, is_valid=res.get("is_valid", False))

        return {
            "status": "SUCCESS",
            "validation": res,
            "schema_errors": schema_errors,
            "latency_ms": round(elapsed_ms, 3)
        }

    def handle_validate_batch(self, payloads: List[Dict[str, Any]], api_key: Optional[str] = None) -> Dict[str, Any]:
        """POST /v1/validate/batch: Parallel batch validation across GPU cluster."""
        t0 = time.perf_counter()
        
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "validate_batch"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized or insufficient permissions"}

        if not payloads:
            return {"status": "SUCCESS", "results": [], "total": 0, "latency_ms": 0.0}

        results = self.cluster.dispatch_batch(payloads)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        for r in results:
            self.metrics.record_validation(
                latency_ms=r.get("latency_ms", 1.0),
                is_valid=r.get("is_valid", False)
            )

        passed = sum(1 for r in results if r.get("is_valid", False))

        return {
            "status": "SUCCESS",
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "results": results,
            "batch_latency_ms": round(elapsed_ms, 3)
        }

    def handle_cluster_health(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """GET /v1/cluster/health: Cluster status, worker nodes, and availability."""
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "health"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized"}

        status = self.cluster.get_status()
        return {"status": "SUCCESS", "cluster": status}

    def handle_cluster_scale(self, target_workers: int, api_key: Optional[str] = None) -> Dict[str, Any]:
        """POST /v1/cluster/scale: Dynamically scale GPU cluster (1-1024)."""
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "scale"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized: scale action requires ADMIN or OPERATOR role"}

        result = self.cluster.scale(target_workers)
        return {"status": "SUCCESS", "scale_result": result}

    def handle_metrics(self) -> str:
        """GET /v1/metrics: Prometheus text format export."""
        return self.metrics.export_prometheus_text()

    def handle_healthz(self) -> Dict[str, Any]:
        """GET /healthz: Kubernetes liveness & readiness probe."""
        healthy = len(self.cluster.workers) > 0 or not self.cluster.is_running
        return {"status": "UP" if healthy else "DOWN", "timestamp": time.time()}


def create_fastapi_app(server: Optional[RestServer] = None):
    """Creates a FastAPI app if FastAPI is available in the environment."""
    try:
        from fastapi import FastAPI, Header, HTTPException, Body
        from fastapi.responses import PlainTextResponse

        srv = server or RestServer()
        app = FastAPI(title="DA13 Distributed GPU Validator Cluster", version="2.0.0")

        @app.post("/v1/validate")
        def validate_endpoint(payload: Dict[str, Any] = Body(...), x_api_key: Optional[str] = Header(None)):
            res = srv.handle_validate(payload, api_key=x_api_key)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 400), detail=res.get("message"))
            return res

        @app.post("/v1/validate/batch")
        def validate_batch_endpoint(payloads: List[Dict[str, Any]] = Body(...), x_api_key: Optional[str] = Header(None)):
            res = srv.handle_validate_batch(payloads, api_key=x_api_key)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 400), detail=res.get("message"))
            return res

        @app.get("/v1/cluster/health")
        def cluster_health_endpoint(x_api_key: Optional[str] = Header(None)):
            res = srv.handle_cluster_health(api_key=x_api_key)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 400), detail=res.get("message"))
            return res

        @app.post("/v1/cluster/scale")
        def cluster_scale_endpoint(target_workers: int = Body(..., embed=True), x_api_key: Optional[str] = Header(None)):
            res = srv.handle_cluster_scale(target_workers, api_key=x_api_key)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 400), detail=res.get("message"))
            return res

        @app.get("/v1/metrics", response_class=PlainTextResponse)
        def metrics_endpoint():
            return srv.handle_metrics()

        @app.get("/healthz")
        def healthz_endpoint():
            return srv.handle_healthz()

        return app
    except ImportError:
        return None
