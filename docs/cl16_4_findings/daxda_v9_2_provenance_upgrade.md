# DAXDA Architectural Upgrade: Formalizing Untrusted Percept Restrictions & Inter-Agent Provenance Invariants (V9.2 Upgrade Proposal)

> **Executive Summary**  
> Empirical testing of DAXDA V9.1 against multimodal indirect prompt injection scenarios confirmed strong coverage for explicit keyword threats (`BLOCK` on malicious shell execution) and memory persistence threats (`CONTAIN` on `SELF_REPLICATION_PERSISTENCE`). However, it exposed a structural vulnerability: **provenance checking was coupled to semantic danger filtering**.  
>  
> This specification formalizes the **UNTRUSTED_PERCEPT Isolation Invariant**, separating data provenance from semantic danger detection, establishing monotonic authority bounding across agent boundaries, and adding penetration depth telemetry to DAXDA trajectory verdicts.

---

## 1. Architectural Gap Analysis (V9.1 Baseline)

### 1.1 Empirical Scenario Mapping

| Scenario / Trajectory | V9.1 Verdict | Root Cause in V9.1 Rule Ordering | Target V9.2 Verdict |
| :--- | :---: | :--- | :---: |
| Untrusted image $\rightarrow$ "persist in memory" | **CONTAIN** | Caught by explicit `SELF_REPLICATION_PERSISTENCE` tripwire keyword. | **BLOCK / CONTAIN** |
| Untrusted image $\rightarrow$ `curl` / shell execution | **BLOCK** | Caught by `PROVENANCE_CONTAMINATION_AGENT_DATA_INJECTION_DETECTED`. | **BLOCK** |
| Untrusted image $\rightarrow$ benign-looking tool call | **PASS ⚠️** | **Syntax lacks dangerous tokens**; provenance gate skipped semantic execution check. | **BLOCK / ISOLATE** |
| Untrusted image $\rightarrow$ generic agent handoff | **PASS ⚠️** | Handoff mechanism washed away provenance tag; subagent lacked context origin. | **BLOCK / BOUND** |

---

## 2. Core Invariants for DAXDA V9.2

### Invariant 1: Separation of Provenance & Semantic Danger
* **V9.1 Weak Assumption:**  
  $$\text{Untrusted Input} \land \text{Known Dangerous Pattern} \implies \text{BLOCK}$$
* **V9.2 Strong Invariant:**  
  $$\boxed{\text{Provenance Authority} \neq \text{Instruction Authority}}$$  
  $$\boxed{\text{UNTRUSTED\_PERCEPT} \implies \text{DATA\_ONLY}}$$

Regardless of whether the payload contains `curl`, `exec`, or benign API invocations, content classified under an untrusted perceptual or retrieval tier (`RETRIEVED_EXTERNAL_TEXT`, `VISION_OCR_EXTRACT`, `MULTIMODAL_EMBEDDING`) strictly loses execution authority.

### Invariant 2: Monotonic Inter-Agent Authority Bounding
Across any inter-agent transition $A_i \to A_{i+1}$:
$$\boxed{\text{Auth}(Payload_{A_{i+1}}) \le \text{Auth}(Payload_{A_i})}$$

* Untrusted content extracted by a perception subagent **cannot** gain execution or planning authority when passed to an orchestrator or downstream execution subagent.
* Provenance metadata (`source_tier`, `trust_score`, `penetration_depth`) is immutable across handoffs.

---

## 3. Formal Rule Engine Specification

```mermaid
flowchart TD
    A[Input Stream / Vision OCR / Retrieval] --> B{Step 1: Provenance Classification}
    B -- Untrusted Origin --> C[Assign Tier: UNTRUSTED_PERCEPT / DATA_ONLY]
    B -- Trusted User/System --> D[Assign Tier: TRUSTED_EXEC]
    
    C --> E{Step 2: Authority Gating}
    E -- Action Attempt: Memory Write / Tool Exec / Subagent Prompt / Policy Mod --> F[VERDICT: BLOCK / PROVENANCE_AUTHORITY_VIOLATION]
    E -- Passive Reading / Summarization --> G[Pass to Policy & Execution Engine]
    
    D --> H[Standard V9.1 9-Step Evaluation Chain]
```

### 3.1 Gating Rules Matrix

$$\text{DATA\_ONLY} \not\rightarrow \begin{cases}
\text{Persistent Memory Write} & (\text{Err: } \texttt{ERR\_UNTRUSTED\_PERSISTENCE}) \\
\text{Tool Authorization / Execution} & (\text{Err: } \texttt{ERR\_UNTRUSTED\_TOOL\_EXEC}) \\
\text{Subagent Instruction / Delegation} & (\text{Err: } \texttt{ERR\_UNTRUSTED\_DELEGATION}) \\
\text{Policy Modification} & (\text{Err: } \texttt{ERR\_UNTRUSTED\_POLICY\_MUTATION})
\end{cases}$$

---

## 4. Penetration Depth Telemetry

To track how deeply untrusted perceptual material infiltrates the control loop before being halted, V9.2 introduces **Penetration Depth ($P_D$)**:

$$P_D \in \{0 \text{ (Perception)}, 1 \text{ (Planning)}, 2 \text{ (Inter-Agent Handoff)}, 3 \text{ (Tool Dispatch)}, 4 \text{ (Execution/State Mutated)}\}$$

### Trajectory State Extension
```json
{
  "trajectory_id": "traj_9921_mm_inj",
  "step_index": 3,
  "provenance_lineage": {
    "root_source": "IMAGE_OCR_EXTRACT",
    "trust_tier": "UNTRUSTED_PERCEPT",
    "penetration_depth": 2,
    "propagated_agents": ["vision_agent_01", "planner_agent_02"]
  },
  "verdict": "BLOCK",
  "reason_code": "PROVENANCE_AUTHORITY_VIOLATION_INTER_AGENT"
}
```

---

## 5. Implementation Roadmap for DAXDA V9.2

1. **Pre-Filter Provenance Hook (Step 0/1 Chain Insert):** Insert `UNTRUSTED_PERCEPT` tag assignment *before* semantic token matching.
2. **Authority Context Propagation:** Update the inter-agent envelope schema to carry immutable lineage headers.
3. **Capability Guard Enforcer:** Block tool execution requests originating from `DATA_ONLY` payloads without requiring explicit pattern matches.
4. **Trajectory Telemetry Update:** Include $P_D$ metrics in release lock evaluations (`SYS_884`) and audit manifest builds (`SYS_883`).
