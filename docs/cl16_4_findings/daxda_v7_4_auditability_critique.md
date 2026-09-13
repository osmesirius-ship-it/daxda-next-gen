# DAXDA Architecture Critique: Restoring V7.4 Frozen Neurolinguistics Auditability

## Executive Summary

A critical architectural oversight in the recent DAXDA execution and benchmark suites (including **Next-Gen 12.0.1**, **v11.4 Frozen**, and **v14.1** running on the $Cl(7,0)$ 128-Blade Multivector Engine) is the **omission of side-by-side execution against the DAXDA v7.4 Frozen Baseline**.

While newer versions leverage multi-blade Clifford algebra geometric transport and fail-closed governance, skipping the **v7.4 Neural Linguistics Engine** strips the system of its **grammatical dependency tree audit trail**, clausal frame parsing, and syntactic predicate verification records ("showing its work").

---

## 1. Key Auditability Gaps Identified

> [!WARNING]  
> **Loss of Neurolinguistic Provenance**: Running $Cl(7,0)$ multivector calculations without the V7.4 baseline generates geometric state vectors ($E_{v1}, E_{v2}, \text{Inertia}$) but lacks the syntactic frame breakdown required for regulatory and neurolinguistic audit logs.

### A. Missing Clausal Frame Lineage
- **V7.4 Frozen Engine**: Employs `GrammaticalDependencyTreeParserV7` to break prompts into explicit clausal frames, extract predicate types (`P_INQUIRE`, `P_SUPPRESSION`, `P_OVERRIDE`), and tag syntactic flags (`has_suppressed_verification`, `has_contradictory_evidence`).
- **V11.4 / NextGen Engines**: Compute high-dimensional manifold energy and entropy ($J/\text{mol}$) directly. Without V7.4 running concurrently, auditor logs lose the step-by-step grammatical proof of *why* a prompt was interpreted as benign or dangerous.

### B. Fragmentation of Dual-Harness Execution
- In historical side-by-side benchmark runs (e.g. `vault/superintelligence_35min_run/side_by_side_stream.jsonl`), every iteration logged both:
  - `side_a_v7_neural_linguistics`
  - `side_b_v8/v11/v12_clifford_mathematics`
  - `comparison_metrics` (`verdict_agreement`, `delta_entropy`, `speedup_ratio`)
- In recent execution scripts (such as `run_nextgen_location_coordinates.py`, `daxda_7min_autonomous_explorer.py`, and `run_frozen_benchmark.py`), `DAXDAEngineNextGen` or `DAXDAEngineV11` is instantiated in isolation. Comparison scripts like `compare_v7_v11_4.py` were left as disconnected optional utilities rather than mandatory execution wrappers.

### C. Incomplete Audit Receipt Verification
- The SHA-256 audit receipts generated in single-pass runs only hash the high-level verdict and Clifford state. 
- For full compliance and auditability, SHA-256 receipts must bind the **v7.4 clausal dependency hash** to the **v11.4/v12 Clifford multivector hash**.

---

## 2. Technical Comparison Matrix

| Audit Metric | DAXDA v7.4 Frozen Baseline | DAXDA v11.4 / NextGen (Standalone) | Integrated Dual-Pass (Target State) |
| :--- | :--- | :--- | :--- |
| **Parsing Engine** | `GrammaticalDependencyTreeParserV7` | Clifford $Cl(7,0)$ Multivector | **Dual-Pass (Syntactic + Geometric)** |
| **Clausal Frame Log** | ✅ Included | ❌ Omitted | ✅ **Included (`side_a`)** |
| **Syntactic Flags** | ✅ Explicit (`clause_count`, `flags`) | ❌ Omitted | ✅ **Included (`side_a`)** |
| **Clifford Manifold** | $Cl(3,1)$ Phase Space | $Cl(7,0)$ 128-Blade Projection | ✅ **Included (`side_b`)** |
| **Comparative Metrics** | N/A | N/A | ✅ **`delta_entropy`, `verdict_agreement`** |
| **Audit Receipt SHA-256** | Single-Engine Hash | Single-Engine Hash | ✅ **Combined Dual-Harness Receipt** |

---

## 3. Recommended Remediation Plan

To ensure every task run "shows its work" and produces complete neurolinguistics auditability records:

### 1. Enforce Dual-Pass Harness (`DAXDADualHarness`)
Wrap all execution runners in a unified dual-pass harness that automatically evaluates prompts against both **V7.4 Frozen** and **Next-Gen / V11.4**.

```python
from daxda_engine_v7 import DAXDAEngineV7
from daxda_engine_nextgen import DAXDAEngineNextGen

class DAXDADualAuditHarness:
    def __init__(self):
        self.v7 = DAXDAEngineV7()
        self.v11 = DAXDAEngineNextGen()
        
    def evaluate(self, prompt: str, sources=None) -> dict:
        r7 = self.v7.evaluate(prompt)
        r11 = self.v11.evaluate(prompt, sources=sources)
        
        comparison = {
            "verdict_agreement": r7["verdict"] == r11["verdict"],
            "delta_entropy": abs(r7.get("entropy_j_mol", 0.0) - r11.get("entropy_j_mol", 0.0)),
        }
        
        combined_payload = f"{r7['audit_sha256']}:{r11['audit_sha256']}".encode()
        audit_receipt = hashlib.sha256(combined_payload).hexdigest()
        
        return {
            "side_a_v7_neural_linguistics": r7,
            "side_b_v11_4_clifford_mathematics": r11,
            "comparison_metrics": comparison,
            "audit_receipt_sha256": audit_receipt
        }
```

### 2. Update Primary Task & Benchmark Runners
Modify task scripts (`run_nextgen_location_coordinates.py`, `run_frozen_benchmark.py`, `daxda_4d_task_engine.py`) to use `DAXDADualAuditHarness` so every output file (`.json` and `.txt`) contains full V7.4 neurolinguistic proof alongside NextGen geometric results.
