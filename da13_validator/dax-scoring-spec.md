# DAX Stability Scoring Specification

## 1) Purpose

This specification defines deterministic computation of DAX stability score `S(x)` used by DA-X to decide `ACCEPT`, `RECURSE`, or `HALT`.

## 2) Core Equation

`S(x) = wL*L + wA*A + wP*P + wF*F + wT*T`

Subject to:

- `0 <= L,A,P,F,T <= 1`
- `0 <= wL,wA,wP,wF,wT <= 1`
- `wL + wA + wP + wF + wT = 1`

Recommended baseline weights:

- `wL = 0.25`
- `wA = 0.20`
- `wP = 0.20`
- `wF = 0.20`
- `wT = 0.15`

## 3) Component Definitions

### 3.1 Logical Consistency `L`

Inputs:

- `contradictions`: count of contradictions detected (DA-10 + DA-8)
- `claims_count`: total claims emitted
- `epsilon = 1e-6`

Equation:

`L = clamp(1 - contradictions / (claims_count + epsilon), 0, 1)`

### 3.2 Agreement/Consensus `A`

Inputs:

- `confidences[]`: confidence values from competing hypotheses (DA-9 + DA-2)

Intermediate:

- `mean = avg(confidences)`
- `var = avg((c_i - mean)^2)`

Equation:

`A = clamp(1 - var, 0, 1)`

### 3.3 Simulation Performance `P`

Inputs:

- `sim_passed`: simulations meeting constraints (DA-6)
- `sim_total`: total simulations executed (DA-6)

Equation:

`P = 0, if sim_total = 0`

`P = clamp(sim_passed / sim_total, 0, 1), otherwise`

### 3.4 Falsifiability Robustness `F`

Inputs:

- `failed_tests`: number of falsification tests failed (DA-3)
- `total_tests`: number of falsification tests executed (DA-3)

Equation:

`F = 0, if total_tests = 0`

`F = clamp(1 - failed_tests / total_tests, 0, 1), otherwise`

### 3.5 Traceability/Truth `T`

Inputs:

- `verifiable_claims`: claims with explicit evidence/simulation/falsification references
- `claims_count`: total claims emitted

Equation:

`T = 0, if claims_count = 0`

`T = clamp(verifiable_claims / claims_count, 0, 1), otherwise`

## 4) Decision Threshold Policy

Default thresholds:

- `ACCEPT` if `S >= 0.75`
- `RECURSE` if `0.55 <= S < 0.75`
- `HALT` if `S < 0.55` OR hard-fail policy violation

Hard-fail conditions override score:

- policy violation flagged at DA-3 or DA-X
- recursion iteration exceeds `max_iterations`
- integrity anomaly marked critical

## 5) DA-X Re-entry Logic

When `status = RECURSE`, DA-X must emit a mutation contract `G`.

Targeted mutations:

- If `L < 0.60`: increase pressure on DA-10 and DA-8; inject contradiction-focused critique.
- If `A < 0.60`: increase DA-2 synthesis weight; constrain hypothesis branch count.
- If `P < 0.60`: tighten DA-6 simulation constraints; penalize infeasible solution classes.
- If `F < 0.60`: increase DA-3 falsification pressure; require stronger test coverage.
- If `T < 0.70`: increase DA-14 provenance checks; reject unreferenced claims before DA-13.

## 6) Anti-Gaming Controls

To prevent confidence or consensus inflation:

1. **Component independence**
   - `A` cannot compensate for low `F` and `T`.
2. **Floor constraints**
   - Force `RECURSE` if `F < 0.50` or `T < 0.60`, regardless of `S`.
3. **Confidence cap**
   - Layer confidence cannot exceed evidence-supported cap:
   - `confidence_cap = min(T, F) + 0.1`, capped at `0.95`.
4. **Penalty term for unsupported claims**
   - Optional adjustment:
   - `S' = S - alpha * (unsupported_claims / max(claims_count,1))`, `alpha` in `[0.05,0.20]`.
5. **Simulation completeness rule**
   - `P = 0` if `sim_total < sim_min_required`.

## 7) Determinism Requirements

- All score inputs must be present in payload.
- No hidden runtime state may alter `S`.
- Same payload must produce same `S` and same DA-X decision.

## 8) Reference Pseudocode

```text
L = clamp(1 - contradictions / (claims_count + 1e-6), 0, 1)
A = clamp(1 - variance(confidences), 0, 1)
P = (sim_total == 0) ? 0 : clamp(sim_passed / sim_total, 0, 1)
F = (total_tests == 0) ? 0 : clamp(1 - failed_tests / total_tests, 0, 1)
T = (claims_count == 0) ? 0 : clamp(verifiable_claims / claims_count, 0, 1)

S = wL*L + wA*A + wP*P + wF*F + wT*T

if policy_violation or critical_integrity_anomaly: HALT
else if iteration > max_iterations: HALT
else if F < 0.50 or T < 0.60: RECURSE
else if S >= 0.75: ACCEPT
else if S >= 0.55: RECURSE
else HALT
```

## 9) Mapping to DA Layers

- `L`: DA-10, DA-8
- `A`: DA-9, DA-2
- `P`: DA-6
- `F`: DA-3
- `T`: DA-14 (input provenance), propagated across all layers
