# DAX Technical Submission Memo

## Purpose

This memo maps the DAX full-system schema and scoring model to the DA-13 + DA-X architecture and identifies implementation touchpoints for runtime enforcement.

## Artifact Index

- Schema: `dax-full-system.schema.json`
- Scoring specification: `dax-scoring-spec.md`
- Validation contract: `dax-validator-contract.md`
- Conformance examples: `dax-conformance-examples.json`

## Architecture Mapping

### DA-13/DA-X Layer Coverage

Schema section `layers[]` enforces all 16 layer outputs:

- DA-15 to DA-1 reasoning path
- DA-X stability gate

Each layer object captures:

- input and output text
- claim objects (with verifiability references)
- layer metrics required for score computation and audit

### DA-X Control Behavior

Schema section `dax_decision` + `recursion` enforces operational control:

- `ACCEPT` emits governed output
- `RECURSE` requires mutation contract `G`
- `HALT` stops emission and terminates recursion

`allOf` conditions in schema bind decision state to recursion action.

## Scoring-to-Layer Mapping

Stability score:

`S = wL*L + wA*A + wP*P + wF*F + wT*T`

Component ownership:

- `L` <- DA-10 + DA-8
- `A` <- DA-9 + DA-2
- `P` <- DA-6
- `F` <- DA-3
- `T` <- DA-14 (provenance) and global claim traceability

Threshold policy:

- `ACCEPT`: `S >= 0.75`
- `RECURSE`: `0.55 <= S < 0.75` or floor failures
- `HALT`: hard-fail policy/integrity conditions or low-score region

## Validator and Enforcement Touchpoints

### LM Studio / API-side schema enforcement

Apply `dax-full-system.schema.json` on model output prior to release.

Reject output if:

- required governed fields are missing
- additional undeclared fields appear
- DA-X state is inconsistent with recursion contract

### Runtime validator insertion points

Insert validator in `dax-core` flow at three gates:

1. Post-layer assembly (before DA-X finalization)
2. Post-DA-X decision (decision verification)
3. Pre-emission (final safety and audit gate)

Validator responsibilities:

- recompute `L/A/P/F/T` and `S`
- compare expected vs reported decision
- emit machine-readable error object with `rule_id`

## Auditability and External Review Readiness

The package enforces auditable transitions:

- per-layer hashes and timestamps
- telemetry for all 16 layers
- decision reason codes and recursion mutation trace

Result: reviewers can reproduce `S`, verify DA-X control decisions, and trace why output was emitted, re-entered, or halted.

## Implementation Notes

- Keep schema Draft 2020-12 strict (`additionalProperties: false` on governed objects).
- Treat validator as authoritative action gate.
- Use conformance examples as CI fixtures for acceptance tests.
