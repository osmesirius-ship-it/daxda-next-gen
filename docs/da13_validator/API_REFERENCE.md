# DAXDA DA13 Distributed GPU Validator Cluster — API Reference
## REST API & WebSocket Streaming Protocol Specifications

[![API Version](https://img.shields.io/badge/API-v2.0.0-blue.svg)](da13_validator/api/rest_server.py)
[![Auth](https://img.shields.io/badge/Auth-API%20Key%20%2F%20Bearer-orange.svg)](da13_validator/api/auth_middleware.py)

---

## 1. Authentication & RBAC

All requests to protected endpoints must supply an API key via header:
```http
X-API-Key: da13-validator-key-2026
```
Or via standard Bearer authorization:
```http
Authorization: Bearer da13-validator-key-2026
```

### Roles and Privileges

| Role | Permitted Actions |
|---|---|
| `ADMIN` | `validate`, `validate_batch`, `scale`, `health`, `metrics` |
| `VALIDATOR` | `validate`, `validate_batch`, `health`, `metrics` |
| `OPERATOR` | `scale`, `health`, `metrics` |
| `READONLY` | `health`, `metrics` |

---

## 2. REST Endpoints

### 2.1 Single Payload Validation
- **Method**: `POST`
- **Path**: `/v1/validate`
- **Permission**: `VALIDATOR` or `ADMIN`
- **Request Body**:
```json
{
  "meta": {
    "schema_version": "2.0",
    "run_id": "run-001",
    "current_iteration": 1,
    "max_iterations": 5
  },
  "stability": {
    "weights": { "wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15 },
    "components": {
      "L": { "value": 0.90 },
      "A": { "value": 0.85 },
      "P": { "value": 0.80 },
      "F": { "value": 0.85 },
      "T": { "value": 0.95 }
    },
    "score": 0.8675
  },
  "dax_decision": {
    "status": "ACCEPT"
  }
}
```
- **Response** (`200 OK`):
```json
{
  "status": "SUCCESS",
  "validation": {
    "worker_id": "worker-0",
    "gpu_id": 0,
    "is_valid": true,
    "decision": "ACCEPT",
    "score": 0.8675,
    "cl_valid": true,
    "latency_ms": 0.045,
    "receipt_hash": "a1b2c3d4..."
  },
  "schema_errors": [],
  "latency_ms": 0.065
}
```

---

### 2.2 Batch Validation
- **Method**: `POST`
- **Path**: `/v1/validate/batch`
- **Permission**: `VALIDATOR` or `ADMIN`
- **Request Body**: Array of validation payload objects (`[ {...}, {...} ]`).
- **Response** (`200 OK`):
```json
{
  "status": "SUCCESS",
  "total": 100,
  "passed": 98,
  "failed": 2,
  "results": [ ... ],
  "batch_latency_ms": 4.12
}
```

---

### 2.3 Cluster Health & Worker Topology
- **Method**: `GET`
- **Path**: `/v1/cluster/health`
- **Permission**: `READONLY`, `OPERATOR`, `VALIDATOR`, `ADMIN`
- **Response** (`200 OK`):
```json
{
  "status": "SUCCESS",
  "cluster": {
    "cluster_id": "da13-gpu-validator-cluster",
    "is_running": true,
    "total_workers": 4,
    "healthy_workers": 4,
    "failed_workers": 0,
    "availability_pct": 100.0,
    "workers": {
      "worker-0": { "status": "healthy", "gpu_id": 0, "latency_ms": 0.02, "gpu_utilization_pct": 65.0 }
    }
  }
}
```

---

### 2.4 Dynamic Scaling
- **Method**: `POST`
- **Path**: `/v1/cluster/scale`
- **Permission**: `OPERATOR` or `ADMIN`
- **Request Body**:
```json
{
  "target_workers": 8
}
```
- **Response** (`200 OK`):
```json
{
  "status": "SUCCESS",
  "scale_result": {
    "previous_workers": 4,
    "current_workers": 8,
    "target_workers": 8,
    "status": "SCALED"
  }
}
```

---

### 2.5 Prometheus Metrics
- **Method**: `GET`
- **Path**: `/v1/metrics`
- **Response** (`200 OK`, `text/plain`):
```
# HELP da13_validation_throughput_total Total validations processed
# TYPE da13_validation_throughput_total counter
da13_validation_throughput_total 10450
da13_validation_latency_p99_ms 0.0332
da13_queue_depth 0
da13_gpu_utilization_pct 68.4
```

---

## 3. WebSocket Streaming Protocol

Connect to `ws://<HOST>:8765/ws/telemetry`.

### Subscription Frame (Client $\rightarrow$ Server):
```json
{
  "action": "subscribe",
  "channels": ["validation_events", "cluster_health", "telemetry"]
}
```

### Event Notification Frame (Server $\rightarrow$ Client):
```json
{
  "channel": "validation_events",
  "timestamp": 1790745000.123,
  "data": {
    "task_id": "task-4491",
    "decision": "ACCEPT",
    "score": 0.875,
    "worker_id": "worker-2",
    "latency_ms": 0.032
  }
}
```
