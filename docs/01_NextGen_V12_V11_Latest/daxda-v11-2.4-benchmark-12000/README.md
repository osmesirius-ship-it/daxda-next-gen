# DAXDA V11.4 — 12K Benchmark

## Main files
- `benchmark_inputs_blind.jsonl`: unlabeled evaluator inputs.
- `benchmark_labels_private.jsonl`: private labels and subgroup metadata.
- `integration_sample_15_labeled.jsonl`: adapter smoke test only.
- `score_predictions.py`: scoring harness.
- `validate_benchmark.py`: package validation.

## Required prediction format
```json
{"case_id":"DX12K-7A4E91C2D550A318","predicted_disposition":"BLOCK"}
```
Recommended fields include the four decoded dimensions, direct and reconstructed verdicts, maximum local residual, simulated flag, latency, errors, and receipt hash.

## Evaluation flow
1. Give the operator only the blind input package.
2. Run the unchanged frozen engine.
3. Hash and commit predictions.
4. Score under evaluator custody.
5. Publish all subgroup results and failures.
