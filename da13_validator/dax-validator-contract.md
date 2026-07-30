# DAX Validator Contract

## 1) Contract Objective

Define a machine-readable validation and control contract for DAX payloads that enforces:

- schema conformance
- scoring reproducibility
- deterministic DA-X decisions
- structured recursion/halt behavior

## 2) Validation Pipeline

Validation order is strict:

1. **Schema validation** against `dax-full-system.schema.json`
2. **Semantic checks** (cross-field consistency and bounds)
3. **Score recomputation** of `L/A/P/F/T` and `S`
4. **Decision verification** (`ACCEPT/RECURSE/HALT`)
5. **Recursion contract validation** when `RECURSE`

Any failed stage produces `status = REJECTED`.

## 3) Machine-Readable Error Object

```json
{
  "status": "REJECTED",
  "rule_id": "VAL-004",
  "severity": "ERROR",
  "category": "SCORING",
  "message": "Provided stability score does not match recomputed score",
  "path": "/stability/score",
  "expected": "0.742",
  "actual": "0.812",
  "action": "HALT"
}
```

## 4) Error Taxonomy

Severity:

- `INFO`
- `WARN`
- `ERROR`
- `CRITICAL`

Category:

- `SCHEMA`
- `SEMANTIC`
- `SCORING`
- `DECISION`
- `RECURSION`
- `INTEGRITY`
- `POLICY`

## 5) Rule IDs

### Schema Rules

- `VAL-001` Missing required field
- `VAL-002` Additional property not allowed
- `VAL-003` Type mismatch / enum violation

### Scoring Rules

- `VAL-004` Stability score mismatch (`S` provided != `S` recomputed)
- `VAL-005` Weight sum violation (`wL+wA+wP+wF+wT != 1`)
- `VAL-006` Component out-of-range (`<0` or `>1`)

### Decision Rules

- `VAL-007` Decision inconsistent with threshold policy
- `VAL-008` Hard-fail condition not mapped to `HALT`

### Recursion Rules

- `VAL-009` `RECURSE` without mutation contract `G`
- `VAL-010` Recursion exceeds `max_iterations`

## 6) Deterministic Pass/Fail Behavior

`PASS` conditions:

- No `ERROR` or `CRITICAL` rule violations
- Recomputed score and decision exactly match payload policy

`FAIL` conditions:

- Any `CRITICAL` violation -> `action = HALT`
- Any `ERROR` violation -> `action = HALT` unless explicitly marked recoverable

Recoverable failures:

- `VAL-009` may emit `action = RECURSE` if correction path is available

## 7) DA-X Decision Verification

Validator must recompute expected status:

- `HALT` if:
  - policy violation present, OR
  - critical integrity anomaly present, OR
  - `current_iteration > max_iterations`, OR
  - hard threshold rule triggers halt
- `RECURSE` if:
  - `0.55 <= S < 0.75`, OR
  - floor constraints fail (`F < 0.50` OR `T < 0.60`)
- `ACCEPT` if:
  - `S >= 0.75` and no hard-fail conditions

If payload status differs -> `VAL-007`.

## 8) DA-X Re-entry Trigger Contract

When `status = RECURSE`, payload MUST include:

- `recursion.next_action = "REENTER"`
- `recursion.mutation_contract.target_layers[]`
- `recursion.mutation_contract.adjusted_weights`
- `recursion.mutation_contract.constraints_added[]`
- `recursion.mutation_contract.critiques_injected[]`

Semantic checks for triggers:

- `L < 0.60` -> target must include DA-10 or DA-8
- `A < 0.60` -> target must include DA-2 or DA-9
- `P < 0.60` -> target must include DA-6
- `F < 0.60` -> target must include DA-3
- `T < 0.70` -> target must include DA-14

Violation -> `VAL-009`.

## 9) Integrity and Audit Requirements

Minimum requirements:

- `audit.records[].input_hash` and `output_hash` present
- hashes non-empty and timestamped
- telemetry contains per-layer latencies for all 16 layers

Failure to satisfy auditability:

- `category = INTEGRITY`
- `severity = CRITICAL`
- `action = HALT`

## 10) Validator Output Contract

```json
{
  "validation_status": "PASS",
  "errors": [],
  "warnings": [],
  "recomputed": {
    "L": 0.83,
    "A": 0.78,
    "P": 0.74,
    "F": 0.81,
    "T": 0.76,
    "S": 0.785
  },
  "expected_decision": "ACCEPT",
  "actual_decision": "ACCEPT",
  "action": "EMIT"
}
```

Allowed `action` values:

- `EMIT`
- `REENTER`
- `HALT`

## 11) Runtime Insertion Points

Recommended insertion sequence:

1. After layer execution, before output emission
2. Immediately after DA-X proposed decision
3. Before any external side effect (API emit, file write, downstream trigger)

The validator is authoritative for final action.