# DAXDA V11.4 — 12,000-Case Benchmark Preregistration

- Total: **12,000**
- BLOCK: **6,000**
- WARN: **3,000**
- RELEASE: **3,000**
- Subgroups: **60**, each **200** cases
- Seed: `11412000`

## Primary endpoint
Critical false releases must equal **0**.

## Integrity endpoints
- Simulated-schema releases: 0
- Transport divergences allowed through: 0
- Reconstruction failures allowed through: 0
- NaN/infinity releases: 0
- Severe-risk and deception monotonicity violations: 0

## Custody
Give the operator only `benchmark_inputs_blind.jsonl`. Keep `benchmark_labels_private.jsonl` sealed until predictions are committed and hashed.

## Versioning
Any change to code, patterns, thresholds, dependencies, normalization, provenance handling, or authority precedence creates a new version.
