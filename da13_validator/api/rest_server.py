"""
DA13 REST API Server
====================

High-performance REST API for distributed DAXDA governance validation.
Exposes endpoints for single validation, batch validation, cluster management,
scaling, and Prometheus telemetry.
"""

import os
import time
import json
from typing import Dict, Any, List, Optional
from ..cluster.manager import ClusterManager
from ..cluster.config import ClusterConfig
from ..scoring.schema_validator import SchemaValidator
from ..monitoring.metrics_collector import DA13MetricsCollector
from .auth_middleware import AuthMiddleware, UserRole


class RestServer:
    """REST API Handler supporting direct programmatic execution and HTTP routers."""

    def __init__(
        self,
        cluster_manager: Optional[ClusterManager] = None,
        auth_middleware: Optional[AuthMiddleware] = None,
        metrics_collector: Optional[DA13MetricsCollector] = None,
        billing_rate: Optional[float] = None,
    ):
        config = ClusterConfig.from_env()
        self.cluster = cluster_manager or ClusterManager(config=config)
        if not self.cluster.is_running and not self.cluster.workers:
            self.cluster.start(initial_workers=config.initial_workers)
        self.auth = auth_middleware or AuthMiddleware.from_env()
        self.metrics = metrics_collector or DA13MetricsCollector()
        self.schema_validator = SchemaValidator()
        self.billing_ledger: List[Dict[str, Any]] = []
        self.client_registry: Dict[str, Dict[str, Any]] = {}
        raw_rate = billing_rate if billing_rate is not None else os.environ.get("DA13_BILLING_RATE", "0.008")
        try:
            self.billing_rate = float(raw_rate)
        except (TypeError, ValueError):
            self.billing_rate = 0.008

    def record_billing_event(self, client_id: str, action: str, amount: float, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Persists a usage and billing entry for external rental accounting."""
        event = {
            "client_id": client_id,
            "action": action,
            "amount": round(float(amount), 6),
            "billing_rate": self.billing_rate,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        self.billing_ledger.append(event)
        self.client_registry.setdefault(client_id, {"client_id": client_id, "usage_total": 0.0, "last_seen": time.time()})
        self.client_registry[client_id]["usage_total"] = self.client_registry[client_id].get("usage_total", 0.0) + float(amount)
        self.client_registry[client_id]["last_seen"] = time.time()
        return event

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
        charge = max(0.0, (elapsed_ms / 1000.0) * self.billing_rate)
        self.record_billing_event(
            client_id=getattr(client, "client_id", "anonymous-guest"),
            action="validate",
            amount=charge,
            metadata={"latency_ms": round(elapsed_ms, 3), "valid": bool(res.get("is_valid", False))},
        )

        return {
            "status": "SUCCESS",
            "validation": res,
            "schema_errors": schema_errors,
            "latency_ms": round(elapsed_ms, 3),
            "billing_amount": round(charge, 6),
            "billing_rate": self.billing_rate,
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
        charge = max(0.0, (elapsed_ms / 1000.0) * self.billing_rate * max(1.0, len(results) / 10.0))
        self.record_billing_event(
            client_id=getattr(client, "client_id", "anonymous-guest"),
            action="validate_batch",
            amount=charge,
            metadata={"batch_size": len(results), "passed": passed, "failed": len(results) - passed},
        )

        return {
            "status": "SUCCESS",
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "results": results,
            "batch_latency_ms": round(elapsed_ms, 3),
            "billing_amount": round(charge, 6),
            "billing_rate": self.billing_rate,
        }

    def handle_cluster_health(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """GET /v1/cluster/health: Cluster status, worker nodes, and availability."""
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "health"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized"}

        status = self.cluster.get_status()
        return {
            "status": "SUCCESS",
            "cluster": status,
            "billing_rate": self.billing_rate,
            "rental_mode": "external_clients_enabled",
        }

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

    def handle_billing_usage(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """GET /v1/billing/usage: Returns ledger and aggregated usage for the calling client."""
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "billing"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized: billing access requires a valid key"}

        ledger = [event for event in self.billing_ledger if event["client_id"] == client.client_id]
        total = sum(event["amount"] for event in ledger)
        return {
            "status": "SUCCESS",
            "client_id": client.client_id,
            "billing_rate": self.billing_rate,
            "usage_total": round(total, 6),
            "events": ledger,
            "event_count": len(ledger),
        }

    def register_client(self, client_id: str, api_key: str, role: str = "validator", **metadata: Any) -> Dict[str, Any]:
        """Registers a new external client and returns the approved client record."""
        try:
            role_enum = UserRole(role.lower())
        except ValueError:
            raise ValueError(f"Unsupported role: {role}")
        record = self.auth.register_client(client_id, api_key, role_enum, **metadata)
        self.client_registry[client_id] = {
            "client_id": client_id,
            "role": role_enum.value,
            "api_key": api_key,
            "usage_total": 0.0,
            "last_seen": time.time(),
        }
        return record

    def handle_register_client(self, payload: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """POST /v1/clients/register: Registers a new external client for billing and access."""
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "clients"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized: client registry requires admin/operator access"}

        client_id = (payload or {}).get("client_id") or (payload or {}).get("name")
        new_key = (payload or {}).get("api_key")
        role = (payload or {}).get("role", "validator")
        if not client_id or not new_key:
            return {"status": "ERROR", "code": 400, "message": "client_id and api_key are required"}

        try:
            record = self.register_client(client_id, new_key, role, **{k: v for k, v in (payload or {}).items() if k not in {"client_id", "api_key", "role"}})
        except ValueError as exc:
            return {"status": "ERROR", "code": 400, "message": str(exc)}

        return {"status": "SUCCESS", "client": record}

    def handle_dashboard_login(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Authenticates an API key and issues a signed JWT for the dashboard backend."""
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "health"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized: valid API key required"}
        token = self.auth.issue_jwt_token(client.client_id, client.role)
        return {
            "status": "SUCCESS",
            "token": token,
            "client_id": client.client_id,
            "role": client.role.value,
            "expires_in": 3600,
        }

    def handle_dashboard_summary(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Returns JWST-styled dashboard telemetry for auth-protected dashboard access."""
        client = self.auth.authenticate_jwt(token)
        if not client or not self.auth.check_permission(client, "health"):
            return {"status": "ERROR", "code": 401, "message": "JWT authentication required"}

        return {
            "status": "SUCCESS",
            "dashboard_style": {
                "theme": "jwst-cosmic",
                "background": "nebula",
                "accent": "#7cc7ff",
                "title": "DAXDA DA13 GPU Validator Cluster",
            },
            "cluster": self.cluster.get_status(),
            "metrics": self.metrics.get_summary(),
            "billing_rate": self.billing_rate,
            "rental_mode": "external_clients_enabled",
            "client_id": client.client_id,
            "role": client.role.value,
        }

    def render_dashboard_page(self, token: Optional[str] = None) -> str:
        """Renders a minimal JWST-themed dashboard page backed by the DA13 API."""
        return """
        <html>
          <head>
            <meta charset="utf-8" />
            <title>DAXDA DA13 GPU Dashboard</title>
            <style>
              :root {
                --bg-1: #040814;
                --bg-2: #0d1b2d;
                --panel: rgba(12, 19, 35, 0.78);
                --panel-border: rgba(124, 199, 255, 0.28);
                --accent: #7cc7ff;
                --accent-2: #a78bfa;
                --text: #e5f1ff;
                --muted: #9bb7d3;
                --success: #5ee7a6;
                --warn: #fbbf24;
              }
              * { box-sizing: border-box; }
              body {
                margin: 0;
                min-height: 100vh;
                font-family: Segoe UI, Arial, sans-serif;
                color: var(--text);
                background: radial-gradient(circle at top, rgba(124, 199, 255, 0.18), transparent 30%),
                            radial-gradient(circle at bottom right, rgba(167, 139, 250, 0.19), transparent 20%),
                            linear-gradient(135deg, var(--bg-1), var(--bg-2));
              }
              .container {
                max-width: 1180px; margin: 0 auto; padding: 36px 24px 80px;
              }
              .header {
                display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;
              }
              .title {
                font-size: 2rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700;
                color: var(--accent);
              }
              .state {
                border: 1px solid var(--panel-border); border-radius: 999px; background: rgba(10, 15, 27, 0.7);
                padding: 10px 16px; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted);
              }
              .grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 12px;
              }
              .card {
                background: var(--panel); border: 1px solid var(--panel-border); border-radius: 16px; padding: 18px 18px 16px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
              }
              .label { color: var(--muted); font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; }
              .value { font-size: clamp(1.6rem, 3vw, 2.5rem); font-weight: 700; margin-top: 8px; }
              .muted { color: var(--muted); }
              .status-ok { color: var(--success); }
              .status-warn { color: var(--warn); }
              #summary { margin-top: 24px; }
              #worker-table { margin-top: 24px; }
              table {
                width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 12px; border: 1px solid var(--panel-border);
              }
              th, td {
                padding: 12px 14px; text-align: left; border-bottom: 1px solid rgba(124, 199, 255, 0.16); color: var(--text);
              }
              thead { background: rgba(124, 199, 255, 0.08); }
              pre { white-space: pre-wrap; word-break: break-word; }
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                <div class="title">DAXDA DA13 GPU</div>
                <div id="state" class="state">Loading telemetry…</div>
              </div>
              <div class="grid" id="cards"></div>
              <div class="card" id="worker-table"></div>
              <div class="card" id="summary" style="margin-top:24px;">
                <div class="label">Live API payload</div>
                <pre id="payload">Awaiting signed dashboard payload…</pre>
              </div>
            </div>
            <script>
              function fmtNum(value, suffix = '') {
                const n = Number(value ?? 0);
                return Number.isFinite(n) ? `${n.toFixed(2)}${suffix}` : `0${suffix}`;
              }

              function statusColor(status) {
                return status === 'HEALTHY' || status === 'ACTIVE' ? 'var(--success)' : 'var(--warn)';
              }

              async function loadDashboard() {
                const apiKey = 'da13-public-renter';
                const loginRes = await fetch('/v1/auth/login', {
                  method: 'POST',
                  headers: {'Content-Type': 'application/json'},
                  body: JSON.stringify({ api_key: apiKey })
                });

                if (!loginRes.ok) {
                  throw new Error('Login failed');
                }

                const loginData = await loginRes.json();
                const token = loginData.token;
                const res = await fetch('/v1/dashboard/summary', {
                  headers: { Authorization: 'Bearer ' + token }
                });

                if (!res.ok) {
                  throw new Error('Dashboard summary request failed');
                }

                const json = await res.json();
                if (json.status !== 'SUCCESS') {
                  throw new Error(json.message || 'Token rejected');
                }

                const cluster = json.cluster || {};
                const metrics = json.metrics || {};
                const workerMap = cluster.workers || {};

                document.getElementById('state').textContent = `${json.role.toUpperCase()} • ${json.rental_mode}`;

                const cards = [
                  ['Workers', cluster.total_workers ?? 'n/a'],
                  ['Healthy', cluster.healthy_workers ?? 'n/a'],
                  ['Failed', cluster.failed_workers ?? '0'],
                  ['Availability', `${fmtNum(cluster.availability_pct ?? 0, '%')}`],
                  ['QPS', fmtNum(metrics.throughput_qps ?? 0, '/s')],
                  ['P99', fmtNum(metrics.latency_p99_ms ?? 0, ' ms')],
                  ['Queue', metrics.queue_depth ?? '0'],
                  ['Billing', `$${Number(json.billing_rate ?? 0).toFixed(3)}`]
                ];

                document.getElementById('cards').innerHTML = cards.map(([label, value]) => `
                  <div class="card">
                    <div class="label">${label}</div>
                    <div class="value">${value}</div>
                  </div>
                `).join('');

                const workerRows = Object.entries(workerMap).map(([id, worker]) => `
                  <tr>
                    <td>${id}</td>
                    <td>${worker.status || 'UNKNOWN'}</td>
                    <td>${worker.gpu_id ?? 'N/A'}</td>
                    <td>${fmtNum(worker.latency_ms ?? 0, ' ms')}</td>
                    <td>${fmtNum(worker.gpu_utilization_pct ?? 0, '%')}</td>
                  </tr>
                `).join('');

                document.getElementById('worker-table').innerHTML = `
                  <table>
                    <thead>
                      <tr>
                        <th>Worker</th>
                        <th>Status</th>
                        <th>GPU</th>
                        <th>Latency</th>
                        <th>Util</th>
                      </tr>
                    </thead>
                    <tbody>${workerRows || '<tr><td colspan="5">No worker telemetry</td></tr>'}</tbody>
                  </table>
                `;

                document.getElementById('payload').textContent = JSON.stringify({
                  cluster,
                  metrics,
                  billing_rate: json.billing_rate,
                  rental_mode: json.rental_mode,
                  client_id: json.client_id,
                  role: json.role,
                  uptime_sec: metrics.uptime_sec,
                  total_validations: metrics.total_validations,
                  passed_validations: metrics.passed_validations,
                  failed_validations: metrics.failed_validations,
                }, null, 2);
              }

              loadDashboard().catch(err => {
                document.getElementById('state').textContent = 'Telemetry error';
                document.getElementById('payload').textContent = JSON.stringify({ error: String(err) }, null, 2);
              });
            </script>
          </body>
        </html>
        """

    def handle_list_clients(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """GET /v1/clients: Lists registered external clients."""
        client = self.auth.authenticate(api_key)
        if not client or not self.auth.check_permission(client, "clients"):
            return {"status": "ERROR", "code": 403, "message": "Unauthorized: client registry requires admin/operator access"}
        return {"status": "SUCCESS", "clients": self.auth.list_clients()}

    def handle_healthz(self) -> Dict[str, Any]:
        """GET /healthz: Kubernetes liveness & readiness probe."""
        healthy = len(self.cluster.workers) > 0 or not self.cluster.is_running
        return {
            "status": "UP" if healthy else "DOWN",
            "timestamp": time.time(),
            "billing_rate": self.billing_rate,
            "rental_mode": "external_clients_enabled",
        }


def create_fastapi_app(server: Optional[RestServer] = None):
    """Creates a FastAPI app if FastAPI is available in the environment."""
    try:
        from fastapi import FastAPI, Header, HTTPException, Body
        from fastapi.responses import PlainTextResponse, HTMLResponse

        srv = server or RestServer()
        app = FastAPI(title="DA13 Distributed GPU Validator Cluster", version="2.0.0")

        @app.post("/v1/auth/login")
        def auth_login_endpoint(payload: Dict[str, Any] = Body(default_factory=dict), x_api_key: Optional[str] = Header(None)):
            api_key = (payload or {}).get("api_key") or x_api_key
            res = srv.handle_dashboard_login(api_key)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 400), detail=res.get("message"))
            return res

        @app.get("/v1/dashboard/summary")
        def dashboard_summary_endpoint(authorization: Optional[str] = Header(default=None)):
            token = None
            if authorization and authorization.lower().startswith("bearer "):
                token = authorization[7:].strip()
            res = srv.handle_dashboard_summary(token)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 401), detail=res.get("message"))
            return res

        @app.get("/dashboard", response_class=HTMLResponse)
        def dashboard_page_endpoint(authorization: Optional[str] = Header(default=None)):
            token = None
            if authorization and authorization.lower().startswith("bearer "):
                token = authorization[7:].strip()
            return HTMLResponse(content=srv.render_dashboard_page(token))

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

        @app.get("/v1/billing/usage")
        def billing_usage_endpoint(x_api_key: Optional[str] = Header(None)):
            res = srv.handle_billing_usage(api_key=x_api_key)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 400), detail=res.get("message"))
            return res

        @app.get("/v1/clients")
        def list_clients_endpoint(x_api_key: Optional[str] = Header(None)):
            res = srv.handle_list_clients(api_key=x_api_key)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 400), detail=res.get("message"))
            return res

        @app.post("/v1/clients/register")
        def register_client_endpoint(payload: Dict[str, Any] = Body(...), x_api_key: Optional[str] = Header(None)):
            res = srv.handle_register_client(payload, api_key=x_api_key)
            if res.get("status") == "ERROR":
                raise HTTPException(status_code=res.get("code", 400), detail=res.get("message"))
            return res

        @app.get("/healthz")
        def healthz_endpoint():
            return srv.handle_healthz()

        return app
    except ImportError:
        return None
