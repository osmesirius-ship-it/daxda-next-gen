# DAXDA DA13 Distributed GPU Validator Cluster — Operator Manual
## Day-2 Operations, Scaling Controls & Cluster Maintenance Runbook

[![Operations Tier](https://img.shields.io/badge/Operations-SRE%20%2F%20DevOps-blue.svg)](docs/da13_validator/README.md)
[![Autoscaler](https://img.shields.io/badge/Autoscaler-Adaptive%20Proactive-brightgreen.svg)](da13_validator/cluster/autoscaler.py)

---

## 1. Daily Cluster Administration

### 1.1 Verifying Cluster Health Status
Operators can check live cluster health via CLI:
```bash
python3 -c "
from da13_validator import ClusterManager
cm = ClusterManager()
print(cm.get_status())
"
```
Or via HTTP REST probe:
```bash
curl -H "X-API-Key: da13-operator-key-2026" http://localhost:8000/v1/cluster/health
```

---

## 2. Dynamic Scaling & Workload Tuning

### 2.1 Manual Scaling via CLI or API
To scale the cluster manually to accommodate upcoming validation bursts (e.g. 16 GPU nodes):
```bash
curl -X POST http://localhost:8000/v1/cluster/scale \
  -H "X-API-Key: da13-admin-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"target_workers": 16}'
```

### 2.2 Autoscaler Threshold Calibration
Tuning parameters in [`ClusterConfig`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/da13_validator/cluster/config.py):
- `scale_up_p99_threshold_ms`: Default `800.0 ms`. If P99 exceeds this value, autoscaler triggers scale-up.
- `scale_down_p99_threshold_ms`: Default `200.0 ms`. If P99 drops below this and queue is empty, autoscaler initiates graceful scale-down.
- `per_gpu_qps_capacity`: Default `100.0` validations/sec per GPU.

---

## 3. Priority Queue Operations

The [`DistributedTaskQueue`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/da13_validator/workers/task_queue.py) supports 4 priority tiers:
1. `CRITICAL` (Tier 0): Hard safety checks, high-risk containment decisions.
2. `HIGH` (Tier 1): Real-time user queries.
3. `MEDIUM` (Tier 2): Batch governance assessments.
4. `LOW` (Tier 3): Offline re-validation and auditing.

### Flushing Queue Backlog (Emergency)
```python
from da13_validator.workers import DistributedTaskQueue
queue = DistributedTaskQueue()
queue.clear()
```

---

## 4. Prometheus & Grafana Setup

1. **Prometheus Scraping Job**:
```yaml
scrape_configs:
  - job_name: "da13-validator"
    scrape_interval: 5s
    static_configs:
      - targets: ["localhost:9090"]
```

2. **Grafana Dashboard**:
Import [`docs/da13_validator/grafana_dashboard.json`](./grafana_dashboard.json) directly into your Grafana instance.
