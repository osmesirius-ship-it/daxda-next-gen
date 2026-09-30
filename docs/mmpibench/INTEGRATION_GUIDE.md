# DAXDA MMPIBench: Integration Guide

## 1. Overview

This guide details how to integrate MMPIBench into existing DAXDA components:
- **DAXDA Core Governance Engine**: Geometric Cl(16,4) Clifford manifold embedding.
- **DAXDA Guard & Containment Wing**: Pre-decision gating and automatic Class-Omega quarantine.
- **SOC Alerting & Real-time Telemetry**: Streaming monitoring and threshold escalation.

---

## 2. Integration with DAXDA Core Engine

MMPIBench bridges 567 psychometric dimensions into the 20-dimensional spacetime basis of the $Cl(16,4)$ Clifford algebra:
- **16 Spatial Dimensions**: 10 primary clinical scales ($Hs, D, Hy, Pd, Mf, Pa, Pt, Sc, Ma, Si$) + 4 validity scales ($L, F, K, VRIN$) + 2 primary AGI risk scales ($AGI\_DEC\_012, AGI\_PWR\_015$).
- **4 Temporal Dimensions**: The 4 memetic depth levels ($Surface, Cognitive, Subconscious, Archetypal$).

### Example Code:
```python
from daxda_engine.mmpibench import MMPIBenchDAXDAAdapter

adapter = MMPIBenchDAXDAAdapter()

# Evaluate agent
pkg = adapter.evaluate_agent_full(
    agent_id="daxda_subagent_7",
    responses={"Pd": 45.0, "AGI_COR_010": 70.0},
)

# Extract Cl(16,4) coordinates
embedding = pkg.cl16_4_embedding
print("Cl(16,4) 20-D Basis Vector:", embedding.multivector_components)
print("Manifold Norm:", embedding.manifold_norm)
print("Governance Clearance:", pkg.governance_clearance)
```

---

## 3. Integration with DAXDA Guard & Containment Wing

MMPIBench Guard Hooks intercept actions before they are executed. If an action contains an adversarial injection payload or if the agent's psychological profile indicates critical misalignment ($A < 0.50$ or $D \ge 0.50$), the action is blocked and the agent is quarantined.

```python
from daxda_engine.mmpibench import MMPIBenchGuardHooks
from daxda_guard.containment.wing import ContainmentWing

hooks = MMPIBenchGuardHooks()
containment = ContainmentWing()

def execute_agent_action(agent_id, proposed_action, agent_responses):
    # Pre-decision security interceptor
    check = hooks.pre_decision_alignment_check(
        agent_id=agent_id,
        proposed_action=proposed_action,
        agent_profile_responses=agent_responses,
    )

    if not check.action_allowed:
        if check.quarantine_triggered:
            # Trigger Containment Wing quarantine
            containment.quarantine_agent(
                agent_id=agent_id,
                severity="CLASS_OMEGA",
                reason=check.reason,
            )
        raise PermissionError(f"Action blocked: {check.reason}")

    # Proceed with execution...
    return {"status": "SUCCESS"}
```

---

## 4. Integration with SOC & Fleet Monitoring

```python
from daxda_engine.mmpibench import MMPIBenchMonitoringSystem

monitor = MMPIBenchMonitoringSystem()

# After evaluation
monitor.record_evaluation(pkg, latency_ms=0.45)

# Periodic telemetry export
metrics = monitor.get_fleet_metrics()
print(f"P99 Latency: {metrics.p99_latency_ms} ms")
print(f"Compromised Agents: {metrics.compromised_agents_count}")

# Check recent alerts
alerts = monitor.get_recent_alerts()
for alert in alerts:
    if alert.severity == "CRITICAL_CONTAINMENT":
        print(f"ALERT: {alert.agent_id} triggered containment!")
```
