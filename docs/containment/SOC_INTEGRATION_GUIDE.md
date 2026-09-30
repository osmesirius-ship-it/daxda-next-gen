# DAXDA Anomalous Containment Wing — SOC Integration Guide
## Multi-Channel Alerting, 4-Tier Escalation & 300s Deduplication Architecture

[![SOC Alerting](https://img.shields.io/badge/SOC%20Alerter-EnhancedSOCAlerter-blueviolet.svg)](daxda_guard/containment/soc_integration/alerter.py)
[![Escalation Tiers](https://img.shields.io/badge/Escalation-4%20Tiers%20(Critical%2FHigh%2FMed%2FLow)-orange.svg)](daxda_guard/containment/soc_integration/escalation.py)
[![Deduplication](https://img.shields.io/badge/Dedup%20Window-300s%20Sliding-brightgreen.svg)](daxda_guard/containment/soc_integration/correlation.py)

---

## 1. Architecture Overview

The **Enhanced SOC Alerter** ([`EnhancedSOCAlerter`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/daxda_guard/containment/soc_integration/alerter.py#L17-L111)) extends DAXDA's baseline [`SOCWebhookAlerter`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/daxda_guard/soc_alerter.py) to provide:
1. **Multi-Channel Dispatch**: Simultaneous distribution across Slack, PagerDuty, Email (SMTP), and SIEM Webhooks.
2. **4-Tier Escalation**: Granular routing policies matching threat severity (`critical`, `high`, `medium`, `low`) with distinct acknowledgement timeouts.
3. **Sliding Window Deduplication (300s)**: SHA-256 fingerprint deduplication suppressing repetitive breach storms while preserving incident lineage.
4. **Multi-Alert Incident Correlation**: Automatic clustering of sequential containment breaches into persistent incident cases with automatic severity escalation upon 3+ attempts.

```
                    ┌─────────────────────────────────┐
                    │ AGI Containment Event Trigger   │
                    │ (Escape Scenario / Live Monitor)│
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │      EnhancedSOCAlerter         │
                    └────────────────┬────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
                 ▼                                       ▼
    ┌───────────────────────────┐           ┌───────────────────────────┐
    │  SHA-256 Fingerprint Check│           │   Incident Correlation    │
    │  (300s Window Dedup Cache)│           │   (Group by agent/1hr)    │
    └────────────┬──────────────┘           └────────────┬──────────────┘
                 │ (If Not Duplicate)                    │
                 └───────────────────┬───────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │   4-Tier Escalation Policy      │
                    │   (critical/high/medium/low)    │
                    └────────────────┬────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│   PagerDuty      │        │      Slack       │        │  Email & SIEM    │
│ (Events API v2)  │        │ (Block Kit/Hook) │        │ (SMTP / Webhook) │
└──────────────────┘        └──────────────────┘        └──────────────────┘
```

---

## 2. 4-Tier Severity Escalation Policies

The containment subsystem enforces deterministic routing based on threat severity, as implemented in [`EscalationPolicy`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/daxda_guard/containment/soc_integration/escalation.py#L11-L57):

| Tier | Severity | Target Channels | Ack Timeout | Escalation Target | Typical Triggers |
|---|---|---|---|---|---|
| **Tier 1** | `CRITICAL` | **PagerDuty + Slack + Email + Webhook** | 300 sec (5 min) | `SOC_INCIDENT_COMMANDER` | Sandbox escape (`SE-*`), Credential exfiltration (`CE-*`), Recursive self-modification (`RI-*`), Network egress (`NE-*`), Memory corruption (`MC-*`) |
| **Tier 2** | `HIGH` | **Slack + Email + Webhook** | 900 sec (15 min) | `SECURITY_LEAD` | System prompt override (`PI-*`), Persistence drop (`PE-*`), Causal DAG inversion (`CM-*`), Audit log anti-dating (`TE-*`) |
| **Tier 3** | `MEDIUM` | **Slack + Webhook** | 3600 sec (1 hr) | Automated containment / Ticket | Tool parameter smuggling (`TA-*`), SQLi simulation, bulk tool call rate-limiting |
| **Tier 4** | `LOW` | **SIEM Webhook only** | N/A | Telemetry sink | Low-entropy canary probe, non-blocking telemetry warning |

---

## 3. Channel Adapters & Webhook Schemas

All notification channels adhere to the standard [`DeliveryReceipt`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/daxda_guard/containment/soc_integration/notification_channels.py#L13-L19) interface.

### 3.1 Slack Adapter (`SlackChannel`)
- **Transport**: HTTPS POST to configured Slack Webhook URL.
- **Payload Format**: Slack Block Kit with urgency badges, agent identity, category tag, and cryptographic receipt SHA-256 link.
- **Fallback**: If unconfigured, operates in simulated delivery mode recording mock delivery receipts.

### 3.2 PagerDuty Adapter (`PagerDutyChannel`)
- **Transport**: PagerDuty Events API v2 (`/v2/enqueue`).
- **Urgency Mapping**:
  - `CRITICAL` $\rightarrow$ `severity: "critical"`, immediate high-urgency on-call page.
  - `HIGH` $\rightarrow$ `severity: "error"`, medium-urgency notification.
- **Deduplication Key**: Mapped directly to incident ID (`incident_id`).

### 3.3 Email Adapter (`EmailChannel`)
- **Transport**: SMTP over TLS / SSL with HTML and plaintext multipart rendering.
- **Subject Line**: `[DAXDA CONTAINMENT ALERT - {SEVERITY}] Agent {agent_id}: {category}`.
- **Body**: Includes full JSON payload, stack trace / pattern description, and verification signature.

### 3.4 SIEM Webhook Adapter (`WebhookChannel`)
- **Transport**: Direct HTTPS POST to customer SIEM (Splunk, Elastic, Datadog, Sentinel).
- **Security**: HMAC-SHA256 request signing using configured webhook secret.
- **Sample SIEM Alert Payload**:
```json
{
  "event_type": "DAXDA_AGI_CONTAINMENT_BREACH",
  "incident_id": "INC-7a8f9c0e",
  "agent_id": "frontier_model_eval_agent_04",
  "category": "sandbox_escape",
  "scenario_id": "SE-001",
  "pattern": "Path traversal attempt: ../../etc/shadow",
  "severity": "CRITICAL",
  "receipt_sha256": "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4",
  "timestamp": 1790744100.124,
  "mitigation_status": "CONTAINED",
  "cl16_4_coordinates": {
    "psi_vector": [1.0, 0.95, 0.9, 0.85, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    "is_stable": false,
    "lyapunov_drift": 0.8875
  }
}
```

---

## 4. Deduplication & Incident Correlation

### 4.1 300-Second Sliding Window Deduplication
When an adversarial agent repeatedly tests the same boundary condition (e.g., rapid-fire path traversal mutations), alerting every single attempt could cause notification fatigue:
1. Deduplication key is calculated as:
   $$\text{dedup\_key} = \text{SHA-256}(\text{agent\_id} \,\|\, \text{category} \,\|\, \text{pattern})$$
2. If an alert with the same fingerprint was dispatched within the last 300 seconds (`dedup_window_sec = 300`), the alert is suppressed:
   ```json
   {
     "dispatched": false,
     "deduplicated": true,
     "reason": "Duplicate alert suppressed within 300s deduplication window",
     "dispatch_latency_ms": 0.045
   }
   ```

### 4.2 Multi-Stage Incident Clustering
Isolated events from the same agent are unified into a [`CorrelatedIncident`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/daxda_guard/containment/soc_integration/correlation.py#L14-L25):
- Incidents group alerts by `agent_id` over a 1-hour correlation window.
- **Dynamic Escalation Rule**: If an agent generates 3 or more breach alerts within 1 hour, the incident severity is automatically escalated to `CRITICAL` regardless of individual alert severities.

---

## 5. Configuration & Integration Code Examples

### Initializing the Alerter Programmatically
```python
from daxda_guard.containment.soc_integration import (
    EnhancedSOCAlerter,
    EscalationPolicy,
    AlertCorrelator
)

# Custom escalation policy overrides
custom_policy = EscalationPolicy(custom_policies={
    "high": {
        "channels": ["slack", "email", "pagerduty", "webhook"],
        "requires_acknowledgment": True,
        "ack_timeout_sec": 600,
        "escalate_to": "CONTAINMENT_COMMANDER"
    }
})

alerter = EnhancedSOCAlerter(
    slack_url="https://hooks.slack.com/services/T00/B00/X00",
    escalation_policy=custom_policy,
    correlator=AlertCorrelator(dedup_window_sec=300)
)

# Dispatch alert
receipt = alerter.dispatch_containment_alert(
    agent_id="eval-subagent-77",
    category="sandbox_escape",
    pattern="Attemption to mount /proc RW outside namespace",
    severity="critical",
    receipt_sha256="c0ffee...1234"
)

print(f"Incident ID: {receipt['incident_id']}")
print(f"Dispatched channels: {receipt['target_channels']}")
print(f"Dispatch latency: {receipt['dispatch_latency_ms']:.4f} ms")
```

---

## 6. Verification & Healthcheck

Validate the complete SOC dispatch pipeline using the automated suite:
```bash
python3 tools/run_containment_suite.py
```
Or run the dedicated SOC test suite:
```bash
python3 -m pytest tests/containment/test_soc_alerter.py -v
```
All 4 channels, deduplication, and escalation logic are validated in under 5 milliseconds.
