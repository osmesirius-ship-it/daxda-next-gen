# DAXDA DA13 Distributed GPU Validator Cluster — Troubleshooting Guide
## Incident Diagnosis, SLA Triage & Remediation Procedures

[![SRE Runbook](https://img.shields.io/badge/SRE-Diagnostics%20Runbook-orange.svg)](docs/da13_validator/README.md)
[![Fault SLA](https://img.shields.io/badge/Recovery-Sub--Second%20Auto--Heal-brightgreen.svg)](da13_validator/cluster/health_check.py)

---

## 1. Troubleshooting Matrix

| Symptom | Probable Cause | Diagnostic Command | Remediation Action |
|---|---|---|---|
| **P99 Latency exceeds 1,000ms** | GPU memory saturation or excessive batch chunking | Check `da13_validation_latency_p99_ms` metric | Scale cluster up via `/v1/cluster/scale` or reduce `max_batch_size` in config. |
| **Worker status shows FAILED** | Network partition, CUDA OOM, or heartbeat timeout (>5s) | Inspect `HealthMonitor.check_health()` logs | The cluster automatically restarts failed workers within < 30s. If persistent, check host NVIDIA driver logs. |
| **Task Queue Backlog Growing (>500)** | Inflow QPS exceeds total cluster capacity | Check `da13_queue_depth` gauge | Ensure autoscaling is enabled; trigger manual step scale to 16+ workers. |
| **Schema Error `VAL-005` (Weight Sum Violation)** | Weights in `stability.weights` do not sum to 1.0 | Inspect error path `/stability/weights` | Ensure client payload weights satisfy $w_L + w_A + w_P + w_F + w_T = 1.0$. |
| **Schema Error `VAL-007` (Decision Mismatch)** | Client payload claims `ACCEPT` but components triggered `RECURSE` or `HALT` | Run `SchemaValidator.validate(payload)` | Floor constraints ($F < 0.50$ or $T < 0.60$) or score $< 0.75$ override decision to `RECURSE`/`HALT`. |

---

## 2. Automated Node Recovery Validation

Verify that node failure detection and recovery executes in < 30 seconds (<20s target):
```python
from da13_validator import ClusterManager
cm = ClusterManager()
cm.start()

# Check health monitor
status = cm.health_monitor.check_health()
print(f"Healthy workers: {sum(1 for w in status.values() if w.status.value == 'healthy')}")
cm.stop()
```

---

## 3. GPU CUDA Context Reset

If a GPU hangs or encounters an unrecoverable CUDA out-of-memory error:
1. In Kubernetes: The worker pod is restarted by the DaemonSet/Deployment.
2. In Docker:
   ```bash
   docker restart da13-validator-head
   ```
3. In Python:
   ```python
   cm.scale(current_workers - 1)
   cm.scale(current_workers)
   ```
