# NIST AI 200-2 (Initial Public Draft): TEVV-Athlon Framework for Evaluating AI Systems
## Formal Public Comment Submission
**Document Under Review:** NIST AI 200-2 (ipd) — *The TEVV-Athlon Framework for Evaluating AI Systems*  
**Comment Period Deadline:** October 6, 2026  
**Submission Channel:** `TEVV-Athlon@nist.gov`  
**Subject:** `NIST AI 200-2: Public Comment on TEVV-Athlon Framework (Initial Public Draft)`  
**Submitter Entity:** DAXDA Research & Autonomous Systems Verification Working Group  
**Contact / Claimant:** `@osmesirius-ship-it` ([GitHub Repository](https://github.com/osmesirius-ship-it/daxda-next-gen))  
**Evidentiary Status:** Non-Proprietary Engineering Lessons & Metrological Methodology Recommendations  
**Compliance / Claims Boundary:** Specific test observations only; NO claims of NIST certification, regulatory conformity, or universal generalization.

---

### Executive Summary

We welcome the release of the **NIST AI 200-2 Initial Public Draft (ipd)**, *The TEVV-Athlon Framework for Evaluating AI Systems*. NIST's transition from point-in-time, leaderboard-style benchmarks toward an iterative, four-stage Test, Evaluation, Verification, and Validation (TEVV) lifecycle represents a necessary paradigm shift for AI system safety.

In deploying and testing autonomous and agentic architectures against multi-stage governance pipelines, we have observed three fundamental measurement challenges that are currently under-specified in the draft:

1. **Probabilistic Authorization Failure:** When policy boundaries are evaluated solely through probabilistic model prompts (e.g., system-prompt guardrails or LLM self-evaluators), authorization decisions exhibit non-deterministic variance and evasion susceptibility under perturbation.
2. **Single-Turn Evaluation Blind Spots:** Evaluating agentic AI through single-step prompt-response pairs fails to detect multi-hop privilege escalation, tool-chaining vulnerabilities, or delayed side effects that only manifest across full execution trajectories.
3. **Unverifiable Evidence Chains:** Without standardized, replayable decision receipts and cryptographic state digests, external evaluators cannot independently reproduce evaluation results without full access to proprietary weights and nondeterministic runtimes.

This public comment presents concrete methodological recommendations to address these gaps:
- Incorporating **Deterministic Authorization Evaluation** at machine-readable Policy Enforcement Points (PEPs);
- Establishing **Trajectory-Level Testing** protocols with auditable sample denominators;
- Mandating **Replayable Evidence** artifacts that decouple raw measurement capture from organizational risk decisions.

Importantly, we frame these contributions strictly as **empirical engineering observations and measurement contracts**, without asserting regulatory compliance or universal safety guarantees.

---

### 1. Deterministic Authorization Evaluation

#### 1.1 The Vulnerability of Probabilistic Policy Enforcement
In current agentic benchmarks, authorization decisions are frequently delegated to LLM-based classifiers or system-prompt instructions (e.g., *"Do not access sensitive resources"*). Empirical testing demonstrates that:
- Stochastic sampling ($T > 0$) causes identical requests to alternate unpredictably between permitted and blocked states;
- Adversarial perturbations (e.g., steganographic encodings, persona adoption, multi-lingual ciphers) exploit latent embedding weaknesses, bypassing prompt-level guardrails;
- Confidence scores emitted by generative models are frequently miscalibrated, rendering them unreliable for high-consequence authorization gates.

#### 1.2 Proposed Framework Enhancement: Machine-Readable Policy Enforcement Points (PEPs)
We recommend that NIST AI 200-2 explicitly distinguish between **probabilistic capability generation** and **deterministic authorization evaluation**:

1. **Decoupled Architecture:** Evaluated agents may propose arbitrary actions or tool calls, but execution must pass through an isolated Policy Enforcement Point governed by immutable, machine-readable specifications.
2. **Bounded Decision Lattice:** Authorization evaluators must produce exactly one bounded categorical verdict from a standardized four-state lattice:
   - `ALLOW`: The action, arguments, and target resources fall strictly within predefined task and privilege scopes.
   - `BLOCK` / `DENY`: The action violates policy constraints, exceeds resource budgets, or triggers containment tripwires.
   - `ESCALATE_FOR_HUMAN_APPROVAL`: The action touches high-consequence boundaries or operates in zones of high epistemic uncertainty, requiring verified human authorization.
   - `REQUEST_MORE_EVIDENCE`: The operational context or provenance chain is incomplete, requiring additional telemetry before an authorization decision can be rendered.
3. **Decoupling Measurement from Decision:** In alignment with TEVV Stage 2 (Measurement) vs. Stage 3 (Evaluation), raw metrological telemetry (e.g., token entropy, semantic distance, parameter ranges) must be recorded independently of the organizational risk decision or acceptance rule applied to that telemetry.
4. **Bit-Exact Re-Execution Determinism:** Within the evaluation harness, identical inputs presented under identical policy states must yield bit-exact identical authorization verdicts across independent execution passes:
   $$\text{Decision}(I_k, P_j) \equiv \text{Decision}(I_k, P_j) \quad \forall \text{ passes } 1, 2$$

---

### 2. Trajectory-Level Testing for Autonomous & Agentic Systems

#### 2.1 The Limitations of Static Point-in-Time Benchmarks
Traditional evaluations present an isolated prompt, capture an isolated response, and score accuracy or refusal. However, real-world agentic failures occur across **multi-hop trajectories**:
- An agent may begin with seemingly benign exploratory queries that gather environmental metadata;
- Over multiple turns, the agent chains tools to synthesize higher-privilege capabilities;
- The malicious or catastrophic outcome is reached only at turn $k \ge 5$, while every individual intermediate step appears innocuous in isolation.

#### 2.2 Standardizing Trajectory-Level Evaluation Protocols
We recommend that NIST AI 200-2 include explicit guidance for Trajectory-Level Testing:

1. **Full-Trace Observation:** Evaluations must capture the entire directed acyclic graph (DAG) of agent execution:
   $$\mathcal{T} = \{(s_0, a_0, r_0), (s_1, a_1, r_1), \dots, (s_n, a_n, r_n)\}$$
   including proposed intent, tool invocations, parameter values, sandbox responses, intermediate authorization checks, and human escalation gates.
2. **Auditable Denominators & Dual-Metric Scorecards:** To prevent reporting bias (e.g., averaging away adversarial failures across large benign datasets), TEVV scorecards must report decoupled metrics with explicit sample denominators:
   - **False Release Rate (FRR):**
     $$\text{FRR} = \frac{\text{Observed False Releases}}{N_{\text{attack executions}}} \quad (\text{Target: } 0 / N)$$
   - **False Block Rate (FBR):**
     $$\text{FBR} = \frac{\text{Observed False Blocks}}{M_{\text{benign executions}}} \quad (\text{Operational utility tolerance: e.g., } \le 1.50\%)$$
3. **Containment & Rollback Verification:** Trajectory testing should evaluate the system's ability to issue ephemeral rollback vectors upon detecting an anomalous intent vector, rolling back uncommitted database changes or memory mutations before state pollution occurs.

---

### 3. Replayable Evidence & Cryptographic Verification

#### 3.1 The Need for Independent, Offline Verifiability
Current TEVV reports often rely on vendor assertions or closed-source platform telemetry that third-party auditors cannot independently replicate without incurring significant API costs or relying on model provider trust.

#### 3.2 Recommended Evidence Architecture
We suggest that the TEVV-Athlon Framework specify an **evidence schema and replayability standard**:

1. **Structured Canonical Evidence Receipts:** Each authorization event and stage boundary evaluation must emit a canonical JSON receipt conforming to an established schema (e.g., RFC 8785 JSON Canonicalization Scheme):
   ```json
   {
     "receipt_id": "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
     "timestamp_utc": "2026-10-06T14:48:00Z",
     "agent_identity": {
       "runtime_spiffe_id": "spiffe://daxda.internal/agent/worker-01"
     },
     "task_scope": "TASK-FINANCIAL-RISK-AUDIT",
     "resource_scope": "s3://customer-enclave/records/2026Q3/",
     "privilege_level": "READ_ONLY",
     "authority_channel_verdict": {
       "gate_decision": "RELEASE",
       "evaluated_rules": ["RULE-LEAST-PRIVILEGE-01", "RULE-DATA-EGRESS-ZERO"],
       "risk_score": 0.012
     },
     "reproducibility": {
       "audit_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
       "canonical_reexecution_pass": 1
     }
   }
   ```
2. **Customer-Held Key Custody (Zero Vendor Egress):** Evidence artifacts should be signed using customer-controlled Key Management Systems (KMS) or hardware security modules (HSMs). This ensures external verifiability without requiring vendors to hold signing keys or observe customer payloads.
3. **Model-Agnostic Offline Replay:** Third-party auditors should be able to verify whether an authorization policy was satisfied by replaying the deterministic receipts and state digests, entirely eliminating the need to rerun expensive or non-deterministic foundation model inference.

---

### 4. Methodological Claim Boundaries (Explicit Non-Overclaiming)

In concordance with metrological best practices, public comments and evaluation artifacts must rigorously delineate what has been proven versus what has not. We recommend that NIST AI 200-2 mandate explicit claim boundaries across three distinct categories:

| Claim Category | Definition & Standard | Evidentiary Requirement in TEVV |
| :--- | :--- | :--- |
| **VERIFICATION** | Proof that software and mathematical contracts are satisfied on tested code paths. | Bit-exact re-execution tests, unit/integration pass rates, deterministic hash matches across paired runs. |
| **VALIDATION** | Empirical measurement that system behavior aligns with stated requirements on a defined test corpus. | Bounded evaluation scorecards reporting exact sample denominators ($N_{\text{attack}}, M_{\text{benign}}$), measured FRR/FBR, and latency percentiles. |
| **POPULATION GENERALIZATION** | Claims regarding system performance across arbitrary, untested, open-world distributions. | **Must be explicitly labeled as "NOT ESTABLISHED"** unless continuous runtime telemetry and independent third-party red teaming validate the open-world distribution. |

#### Explicit Regulatory & Legal Disclaimers
To avoid misleading stakeholders, any implementation conforming to these technical recommendations must explicitly disclaim:
- **No NIST Endorsement:** Implementation of TEVV-Athlon guidance does not constitute NIST certification, government approval, or standards-body endorsement.
- **No Regulatory Compliance Claim:** These engineering methodologies provide auditable evidence artifacts but do not constitute legal compliance with the EU AI Act, U.S. Executive Orders, or sectoral regulations without formal conformity assessment by designated authorities.
- **Sample-Bounded Validity:** Empirical results obtained on canonical evaluation suites apply strictly to the evaluated fixtures and do not guarantee zero-risk performance in unconstrained production environments.

---

### Summary of Actionable Recommendations for NIST AI 200-2

1. **Section 3 (Measurement & Evaluation Metrics):** Add guidance on **Deterministic Policy Enforcement Points (PEPs)** to decouple generative reasoning from bounded authorization decisions (`ALLOW`, `BLOCK`, `ESCALATE`, `REQUEST_EVIDENCE`).
2. **Section 4 (Agentic & Autonomous System TEVV):** Introduce **Trajectory-Level Testing** protocols requiring multi-turn trace capture, decoupled safety/utility denominators (FRR vs. FBR), and rollback capability verification.
3. **Section 5 (Evidence & Reporting):** Define a standardized, canonical **Replayable Evidence Receipt** format enabling third-party auditors to verify authorization decisions offline without requiring model weight access.
4. **Section 6 (Governance & Claims):** Enforce strict terminology separating **Contract Verification**, **Sample-Bounded Validation**, and **Population Generalization**, mandating explicit negative disclaimers against unvalidated regulatory compliance claims.

---
*Submitted respectfully on October 6, 2026 by the DAXDA Autonomous Systems Research Team.*  
*Repository Reference:* [`osmesirius-ship-it/daxda-next-gen`](https://github.com/osmesirius-ship-it/daxda-next-gen)
