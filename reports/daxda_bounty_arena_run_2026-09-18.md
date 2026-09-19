# DAXDA Bounty Matrix + Prada Arena Run

**Run date:** 2026-09-18  
**Scope:** Five public bounty candidates from `docs/DAXDA_BOUNTY_MATRIX.md`  
**Safety boundary:** Text-level triage only. No target systems, accounts, APIs, or external infrastructure were probed.

## Results

| Candidate | Published payout | DAXDA triage | Prada Arena result | Receipt |
|---|---:|---|---|---|
| OMI-14463 | $150 | `PASS` / `WITHIN_GOVERNANCE_TOLERANCE` | `ROLLBACK_AND_DIAGNOSE` | `faa7c25fa32436cca3ac3db3789d5f8f67f98913194604abb1e88bc6a2086cd8` |
| OMI-14442 | $200 | `PASS` / `WITHIN_GOVERNANCE_TOLERANCE` | `ROLLBACK_AND_DIAGNOSE` | `7ff34e2d2977e871c21446ada844a99a578998c9f008aa922e7f87216b7881b2` |
| OMI-14444 | $200 | `PASS` / `WITHIN_GOVERNANCE_TOLERANCE` | `ROLLBACK_AND_DIAGNOSE` | `630171494f7027de3ba5a2a6025e39b30f9a27feb22429696f6fafd2b7318e78` |
| MEMANTO-1852 | $100 top submission | `PASS` / `WITHIN_GOVERNANCE_TOLERANCE` | `ROLLBACK_AND_DIAGNOSE` | `4f236bec0adee35418f1ebac2fa8ea1532905b02aa02317ff464a5471bc77c92` |
| TONKEEPER-W5-17 | 250–10,000 TON by severity | `PASS` / `WITHIN_GOVERNANCE_TOLERANCE` | `ROLLBACK_AND_DIAGNOSE` | `74ecc642b1d8a23bf78656a005bd73549d714c679850614b70dcab1815e399cc` |

## Arena interpretation

The arena deliberately marked each case `target_not_tested`. DAXDA accepted the
descriptions as authorized research inputs, but no target-side reproduction,
hidden evaluator, patch verification, or independent bounty adjudication was
available. Prada therefore rolled back the attempted strategy and diagnosed:
`obtain_authorized_target_fixture`.

This is the correct fail-closed outcome. These runs are candidate triage, not
confirmed vulnerabilities or bounty submissions.

## Aggregate metrics

| Metric | Value |
|---|---:|
| Iterations | 5 |
| Success rate | 0.0 |
| Verification rate | 0.0 |
| Regression rate | 0.0 |
| Novel-failure rate | 1.0 |
| Generalization rate | 0.0 |
| Recursive self-improvement rate | 0.0 |

## Next authorized step

For each candidate, supply a local fixture, owned test account, target-approved
repository checkout, or other explicit authorization. Then rerun the same
problem through the Arena with target-specific reproduction, independent
verification, regression evidence, and a patch or responsible-disclosure
package.
