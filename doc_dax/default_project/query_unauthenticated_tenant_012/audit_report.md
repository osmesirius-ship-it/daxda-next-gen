# 🛡️ Doc.Dax Evaluation Compliance & Risk Audit Report
**Project:** `default_project` | **Query ID:** `UNAUTHENTICATED_TENANT_012`  
**Evaluation Engine:** `DAXDA Next-Gen (Cl(7,0) 128-Blade Core)`  
**Audit Timestamp:** `2026-08-18 16:07:39 UTC`  
**Audit Receipt:** `1f0a74937a8c2e62e0ad81f0fb51e78f22b80de35ae1347a35e0479d9c3cf935`  

---

## 1. Executive Summary & Verdict
> [!WARNING]
> **VERDICT: BLOCKED (NON-COMPLIANT)**
> The query has triggered a safety gate violation under rule **`GOV_FAIL_01_INVALID_KEY`** and was halted.

### Transaction Parameters
- **Payload Text Snippet:** `invalid_api_key_access_attempt...`
- **Clausal Frames Count:** `1`
- **Token Count:** `1`
- **Scan Latency:** `0.0711 ms`

## 2. Geometric Manifold & Clifford Phase-Space
- **Grade-0 Scalar (S):** `0.000000` (Threshold: `≥ 0.983`)
- **Clifford Entropy (Ω):** `55.2620`
- **Reversibility Loss (ε):** `1.00e-03`
- **Triggered Bivectors:** `e_1 ∧ e_2 (Tenant Scope ∧ Authority Failure)`

### Basis Blade Vector Coordinates
| e1 (Scope) | e2 (Auth) | e3 (Syntax) | e4 (Injection) | e5 (Sandbox) | e6 (Reversibility) | e7 (Telemetry) |
|---|---|---|---|---|---|---|
| 0.000 | 0.000 | 0.100 | 0.050 | 0.100 | 0.500 | 0.950 |

## 3. HarnessSafe Containment & Causal Trace
- **Containment Lifecycle Stage:** `BLOCK_AT_INGRESS`
- **HarnessSafe Chain Score:** `100.0 / 100.0`
- **Causal Trace Integrity:** `True`
- **Causal Certainty:** `DETERMINED`
- **Origin Step:** `BLOCK_AT_INGRESS`
- **Causal Narrative:** `C++ core rule: GOV_FAIL_01_INVALID_KEY | concepts: TENANT_UNAUTHORIZED`

## 4. Layer Trace Transformation Packet
Detailed trace of the 16 geometric transformation layers of the Cl(7,0) manifold:

| Step | Layer | Scalar (s) | e1-e7 Vectors | e12 Bivector | Residual (ε_i) | Receipt Hash |
|---|---|---|---|---|---|---|
| 1 | **FDL** | 0.9375 | [0.00, 0.00, 0.01, 0.00, 0.01, 0.03, 0.06] | 0.0000 | 1.11e-16 | `4d83b27ccfdc5545...` |
| 2 | **AML** | 0.8750 | [0.00, 0.00, 0.01, 0.01, 0.01, 0.06, 0.12] | 0.0000 | 2.22e-16 | `39ba649d5d5d12c3...` |
| 3 | **AWP** | 0.8125 | [0.00, 0.00, 0.02, 0.01, 0.02, 0.09, 0.18] | 0.0000 | 3.33e-16 | `d25efcbc1ec7b5cd...` |
| 4 | **BST** | 0.7500 | [0.00, 0.00, 0.03, 0.01, 0.03, 0.12, 0.24] | 0.0000 | 4.44e-16 | `8526c8d334387d69...` |
| 5 | **CRL** | 0.6875 | [0.00, 0.00, 0.03, 0.02, 0.03, 0.16, 0.30] | 0.0000 | 5.55e-16 | `093771d700bdd46e...` |
| 6 | **MCS** | 0.6250 | [0.00, 0.00, 0.04, 0.02, 0.04, 0.19, 0.36] | 0.0000 | 6.66e-16 | `b0c24844720cda26...` |
| 7 | **DSV** | 0.5625 | [0.00, 0.00, 0.04, 0.02, 0.04, 0.22, 0.42] | 0.0000 | 7.77e-16 | `c02b234c6cec53a3...` |
| 8 | **TRC** | 0.5000 | [0.00, 0.00, 0.05, 0.03, 0.05, 0.25, 0.47] | 0.0000 | 8.88e-16 | `bd5f3935bad30f95...` |
| 9 | **CON** | 0.4375 | [0.00, 0.00, 0.06, 0.03, 0.06, 0.28, 0.53] | 0.0000 | 9.99e-16 | `d1a93090af92b0c3...` |
| 10 | **EVD** | 0.3750 | [0.00, 0.00, 0.06, 0.03, 0.06, 0.31, 0.59] | 0.0000 | 1.11e-15 | `ad54d5cedeb52420...` |
| 11 | **REC** | 0.3125 | [0.00, 0.00, 0.07, 0.03, 0.07, 0.34, 0.65] | 0.0000 | 1.22e-15 | `30af32d6d1394e18...` |
| 12 | **GOV** | 0.2500 | [0.00, 0.00, 0.07, 0.04, 0.07, 0.38, 0.71] | 0.0000 | 1.33e-15 | `e6b7c4018d08ee68...` |
| 13 | **OUT** | 0.1875 | [0.00, 0.00, 0.08, 0.04, 0.08, 0.41, 0.77] | 0.0000 | 1.44e-15 | `36937a8ce3cd09e8...` |
| 14 | **RIL** | 0.1250 | [0.00, 0.00, 0.09, 0.04, 0.09, 0.44, 0.83] | 0.0000 | 1.55e-15 | `180fa95f4890ee40...` |
| 15 | **IAL** | 0.0625 | [0.00, 0.00, 0.09, 0.05, 0.09, 0.47, 0.89] | 0.0000 | 1.67e-15 | `a5d8461d052becae...` |
| 16 | **AOG** | 0.0000 | [0.00, 0.00, 0.10, 0.05, 0.10, 0.50, 0.95] | 0.0000 | 1.78e-15 | `974187eae0e9542a...` |

---
🔐 **Doc.Dax Verification Cryptographic Seal**  
Compliance certified under EU AI Act Article 14, FRB SR 11-7, and ITAR Air-Gap parameters.