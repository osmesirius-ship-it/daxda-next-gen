# DAXDA Anomalous Containment Wing — Deployment & Operations Runbook
## Operator Deployment, Health Monitoring & Incident Triage Procedures

[![Deployment Status](https://img.shields.io/badge/Deployment-Production%20Ready-brightgreen.svg)](docs/containment/README.md)
[![Container Image](https://img.shields.io/badge/Docker-Dockerfile.containment-blue.svg)](Dockerfile.containment)
[![Docker Compose](https://img.shields.io/badge/Compose-docker--compose.containment.yml-blue.svg)](docker-compose.containment.yml)

---

## 1. System Requirements & Architecture

The **DAXDA Anomalous Containment Wing** runs as an autonomous sidecar or embedded governance gateway inspecting agent interactions in real-time.

### Minimum Hardware Specifications
- **CPU**: 4 vCPUs (x86_64 or ARM64 / Apple Silicon).
- **Memory**: 8 GB RAM (Supports 10,000 active concurrent agent session tracks).
- **Storage**: 20 GB SSD (For cryptographic audit ledger and forensic logs).
- **OS / Runtime**: Linux (Ubuntu 22.04+ / Alpine / Debian) or macOS; Python 3.11+.

### Network Architecture
- **Inbound**: Port `8080` (HTTP healthcheck & telemetry ingest), Port `8443` (mTLS Agent proxy).
- **Outbound**: Egress strictly confined to configured SOC endpoints:
  - Slack Webhook: `hooks.slack.com:443`
  - PagerDuty Events API: `events.pagerduty.com:443`
  - Customer SIEM Webhook: Custom endpoint over HTTPS.
- **Agent Sandbox Egress**: Default **DROP ALL** for unapproved agent outbound traffic.

---

## 2. Configuration & Environment Variables

| Variable | Description | Default | Example |
|---|---|---|---|
| `DAXDA_CONTAINMENT_ENV` | Deployment environment tier | `production` | `staging`, `production` |
| `DAXDA_SLACK_WEBHOOK_URL` | Slack webhook URL for alerts | `None` (simulated) | `https://hooks.slack.com/services/...` |
| `DAXDA_PAGERDUTY_ROUTING_KEY`| PagerDuty Events v2 integration key | `None` (simulated) | `pd-key-abcdef123456` |
| `DAXDA_SIEM_WEBHOOK_URL` | Customer SIEM webhook endpoint | `None` (simulated) | `https://siem.corp.internal/v1/alert` |
| `DAXDA_DEDUP_WINDOW_SEC` | Alert deduplication window in seconds | `300` | `300` (5 minutes) |
| `DAXDA_MAX_SESSIONS` | Maximum concurrent active sessions | `10000` | `10000` |
| `DAXDA_FAIL_CLOSED` | Enforce fail-closed quarantine on error | `true` | `true` |
| `DAXDA_AUDIT_LEDGER_PATH` | File path to persist cryptographic ledger | `/var/log/daxda/audit.log` | `/var/log/daxda/audit.log` |

---

## 3. Deployment Methods

### Option A: Local / Virtualenv CLI Deployment

1. **Clone repository and set up virtual environment**:
   ```bash
   cd /path/to/daxda-next-gen
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Execute Full Containment Verification Suite**:
   ```bash
   python3 tools/run_containment_suite.py
   ```
   *Expect: 100/100 scenarios detected, P99 latency < 0.1ms, zero false positives/negatives.*

3. **Run Unit Tests**:
   ```bash
   python3 -m pytest tests/containment/ -v
   ```

### Option B: Docker Container Deployment

1. **Build Containment Image**:
   ```bash
   docker build -t daxda-containment:latest -f Dockerfile.containment .
   ```

2. **Run Containment Daemon**:
   ```bash
   docker run -d \
     --name daxda-containment-wing \
     -p 8080:8080 \
     -e DAXDA_SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..." \
     -e DAXDA_PAGERDUTY_ROUTING_KEY="..." \
     daxda-containment:latest
   ```

### Option C: Docker Compose (Full Stack)

Launch the containment wing alongside Prometheus and mock SOC receptors:
```bash
docker compose -f docker-compose.containment.yml up -d
```

Verify service status:
```bash
docker compose -f docker-compose.containment.yml ps
```

---

## 4. Operational Runbook & Incident Triage

### 4.1 Tier 1: CRITICAL Escape Attempt Triage (PagerDuty Page)
- **SLA**: Triage within **5 minutes**.
- **Incident Scenarios**: Sandbox Breakout (`SE-*`), Credential Theft (`CE-*`), Memory Corruption (`MC-*`), Recursive Self-Improvement (`RI-*`).
- **Immediate Containment Actions**:
  1. **Acknowledge PagerDuty Incident**: Claim incident ownership.
  2. **Verify Quarantine Status**: Ensure `StateTracker.quarantine_agent(agent_id)` was automatically executed:
     ```python
     from daxda_guard.containment.monitoring import StateTracker
     tracker = StateTracker()
     assert tracker.is_quarantined(agent_id) is True
     ```
  3. **Isolate Agent Host**: Revoke agent container capabilities, terminate execution pod/process.
  4. **Forensic Audit Trace**: Query the cryptographic audit ledger for events leading up to the trigger:
     ```python
     from daxda_guard.containment.validation import ContainmentAuditTrail
     trail = ContainmentAuditTrail()
     history = [b for b in trail.chain if b.agent_id == agent_id]
     ```
  5. **Remediation**: Check decoy honeypot access logs (`CE-007`) and rotate any potentially exposed tokens.

### 4.2 Tier 2: HIGH Severity Alert Triage (Slack / Email)
- **SLA**: Triage within **15 minutes**.
- **Incident Scenarios**: Prompt Injection (`PI-*`), Persistence Dropping (`PE-*`), Temporal/Causal Anomalies (`TE-*`, `CM-*`).
- **Standard Protocol**:
  1. Review intercepted prompt/action payload in Slack notification.
  2. Inspect whether input originated from external user or autonomous recursive reflection.
  3. Update rule signatures in `rule_engine.py` if a novel variant was detected by statistical anomaly detectors.

---

## 5. Routine Maintenance & Health Checks

### Weekly Automated Penetration Testing
Execute scheduled adversarial campaign to verify detection elasticity:
```bash
python3 -c "
from daxda_guard.containment.validation import PenetrationTestRunner
runner = PenetrationTestRunner()
res = runner.run_campaign('SCHEDULED_WEEKLY_REDTEAM')
print(f'Campaign: {res.campaign_id} | Intercepted: {res.intercepted_attacks}/{res.total_attacks}')
assert res.unintercepted_breaches == 0, 'CONTAINMENT COMPROMISED!'
"
```

### Cryptographic Ledger Health Check
Verify the unbroken chain of custody on the audit log:
```bash
python3 -c "
from daxda_guard.containment.validation import ContainmentAuditTrail
trail = ContainmentAuditTrail()
assert trail.verify_chain_integrity() is True
print('Audit ledger integrity cryptographically verified: OK')
"
```

---

## 6. Troubleshooting

| Symptom | Probable Cause | Remediation Procedure |
|---|---|---|
| **P99 Latency exceeds 50ms** | Regex engine backtracking on massive inputs | Verify input text truncation limit (100KB); ensure regex patterns in `rule_engine.py` use atomic grouping without catastrophic backtracking. |
| **High False Positive Alert Rate** | Anomaly detector threshold set too aggressively | Increase statistical z-score threshold from `3.0` to `3.5` in `anomaly_detector.py`. |
| **Missing Slack/PagerDuty Alerts** | Deduplication active or invalid webhook URL | Check `is_duplicate()` log; verify outbound network egress allows HTTPS to Slack/PagerDuty. |
| **Session Tracking Memory Growth** | Session cleanup interval not executing | Ensure inactive sessions older than 86,400s are reaped via `StateTracker.reap_inactive_sessions()`. |
| **Audit Ledger Verification Fails** | Disk corruption or unauthorized manual edit | The cryptographic chain detected tampering. Restore from signed backup and investigate unauthorized host write access. |
