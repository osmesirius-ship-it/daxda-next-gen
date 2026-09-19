# DAXDA Submission Package

**Snapshot date:** 2026-09-18  
**Repository:** `osmesirius-ship-it/daxda-next-gen`  
**Current HEAD inspected:** `3b6eb81`

## 1. Executive brief

DAXDA is a bounded governance, verification, and bounty-triage architecture
for externally evaluated tasks. Its Prada controller and Arena keep candidate
improvements reversible, require independent evaluator evidence, preserve
provenance, and fail closed when authorization or target-side evidence is
missing.

The strongest near-term submission areas are:

1. security and authorization-boundary verification;
2. reproducible code and numerical bug fixes;
3. smart-contract and DeFi/Web3 testing in local fixtures;
4. AI/ML evaluator, provenance, and tool-use integrity.

DAXDA should present evidence as `implemented -> tested -> reproducible ->
externally verifiable`. Existing artifacts support the first three levels for
several capabilities. No current artifact proves a live third-party
vulnerability or a paid bounty.

## 2. Evidence ledger

| Capability | Repository evidence | Verification level | External-verification gap |
|---|---|---|---|
| Governance decisions and authority receipts | `daxda_guard/`, `tests/test_governed_authority_gate.py`, `tests/test_advisory_mode_and_pilots.py` | Implemented + test-defined | Run the focused suite in an environment with declared dev dependencies |
| Safety-critical fail-closed behavior | `tests/test_safety_critical.py` | Test-defined | Capture a clean CI run and artifact manifest |
| Prada bounded improvement controller | `daxda_engine/prada.py`, `tests/test_prada.py` | Implemented + compiled + direct smoke evidence | Execute the full focused pytest suite |
| External-evaluator Arena | `PradaArena` in `daxda_engine/prada.py`, `tests/test_prada.py` | Implemented + test-defined | Attach a real independent evaluator and target fixture |
| Audit/report receipts | `daxda_guard/audit_generator.py`, `tests/test_audit_generator.py` | Implemented + test-defined | Re-run report generation and archive hashes |
| 12,000-case benchmark | `docs/01_NextGen_V12_V11_Latest/daxda-v11.4-benchmark-12000/benchmark_manifest.json` | Artifact present; manifest states 12,000 cases and seed `11412000` | Re-run from the pinned benchmark inputs and publish command/output |
| Runtime provenance | `audit_reports/runtime_provenance_manifest.json` | Manifest present with hashes, seed, hardware, and backend | Refresh timestamp and tie it to a reproducible run |
| Public bounty triage | `reports/daxda_bounty_arena_run_2026-09-18.md`, `reports/daxda_additional_bounties_run_2026-09-18.md` | Reproducible local triage records | Target-side authorization, reproduction, independent evaluation, and submission |

## 3. Bounty coverage matrix

| Requirement class | DAXDA capability | Evidence | Fit | Cost/risk |
|---|---|---|---|---|
| Deterministic code fix | Patch metadata, regression gates, rollback | `PradaCandidate`, `PradaEvidence`, `tests/test_prada.py` | Strong | Low in local checkout |
| Numerical correctness | Benchmark fixtures and reproducibility manifests | V11.4 benchmark artifacts; Tenstorrent candidates | Strong-to-medium | Hardware/version dependent |
| Security reproduction | Authorization gates, isolated fixtures, receipts | safety tests and Arena | Medium | Requires explicit target authorization |
| Smart-contract exploit proof | Arena evaluator contract and rollback | Tonkeeper selection report | Potentially strong, unproven | Requires local TON harness and domain expertise |
| AI/ML evaluation | Provenance, held-out evaluator, composition metrics | Arena metrics and benchmark artifacts | Medium | Evaluator quality is decisive |
| Research synthesis | Evidence mapping and review packets | positioning and bounty reports | Medium | Human adjudication required |

## 4. Target shortlist

| Priority | Target | Published maximum | Selection status |
|---:|---|---:|---|
| 1 | [Tonkeeper W5 #17](https://github.com/tonkeeper/w5/issues/17) | 5,000–10,000 TON | Selected; pinned commit and local-only plan documented |
| 2 | [Tenstorrent #55130](https://github.com/tenstorrent/tt-metal/issues/55130) | $5,000 | Candidate; hardware/version reproduction required |
| 3 | [Clanker OpenAgents #7](https://github.com/ClankerNation/OpenAgents/issues/7) | $7,000 stated, conflicting body text | Candidate; payout and sponsor must be confirmed |
| 4 | [Bounty Plaza #604](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/604) | $10,000 | Candidate only; mirror/escrow/source verification required |
| 5 | [Bounty Plaza #645](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/645) | $10,000 | Candidate only; sponsor and acceptance verification required |

The Bounty Plaza entries are discovery leads, not equivalent to primary
program commitments. They must not outrank a primary-source program until
escrow, sponsor identity, source issue, licensing, and settlement terms are
verified.

## 5. Eligibility and requirements matrix

| Target | Required deliverable | Independent judge | Current blocker |
|---|---|---|---|
| Tonkeeper W5 | Reproducible vulnerability report against commit `fa1b372a417a32af104fe1b949b6b31d29cee349` | Maintainer review plus deterministic replay | No authorized local fixture |
| Tenstorrent #55130 | Correctness fix and hardware/version validation | Maintainer tests and benchmark comparison | Required device/runtime not available |
| Clanker #7 | Solidity fix, tests, and impact proof | Repository maintainer | Payout text conflict and no authorized checkout |
| Bounty Plaza #604 | Performance implementation, accuracy tests, benchmark data | Sponsor/source maintainer | Mirror and escrow unverified |
| Bounty Plaza #645 | Five detailed subsystem bounty specifications | Sponsor/board acceptance | Sponsor and settlement unverified |

## 6. Reproduction instructions

### Repository evidence

```bash
.venv/bin/python -m py_compile daxda_engine/prada.py tests/test_prada.py
.venv/bin/pytest tests/test_prada.py tests/test_safety_critical.py \
  tests/test_governed_authority_gate.py tests/test_integration_hardened.py
```

The second command is the intended verification command; this environment
currently lacks `.venv/bin/pytest`, so no pytest result is claimed here.

### Bounty evidence

1. Confirm the program rules and exact target revision.
2. Obtain explicit authorization or use a local owned fixture.
3. Record the baseline behavior and source hash.
4. Reproduce deterministically with generated identities and non-valuable
   assets.
5. Apply a reversible candidate change in an isolated checkout.
6. Run static, unit, integration, security, regression, resource, and
   reproducibility checks as applicable.
7. Attach independent evaluator output and a signed provenance report.
8. Obtain human approval before disclosure or submission.

## 7. Submission checklist

- [ ] Primary source and rules captured with date.
- [ ] Eligibility, geography, licensing, duplicate policy, and deadline checked.
- [ ] Exact revision pinned.
- [ ] Authorization recorded.
- [ ] Baseline and reproduction fixture archived.
- [ ] Impact mapped to the program's payout category.
- [ ] Independent verification complete.
- [ ] Regression and rollback evidence complete.
- [ ] Provenance hashes and command logs attached.
- [ ] Human reviewer approves the final brief.

## 8. Known gaps and failure conditions

- No GitHub Actions workflow files are present in the inspected checkout; CI
  evidence must be obtained from repository-hosted workflows or a new
  explicitly authorized run.
- `pytest` is declared as a development dependency but is not installed in the
  current virtual environment.
- Public bounty triage is not target verification.
- A DAXDA `PASS` is an input-governance result, not a vulnerability finding.
- Payment amounts, escrow, deadlines, eligibility, and duplicate status must
  be checked again immediately before submission.
- Missing authorization, evaluator access, reproducibility, safety evidence, or
  capacity causes a fail-closed review packet rather than execution.

## 9. Tool sequence

`GitHub repository -> web/program discovery -> workflow verification -> local
files -> Python comparison -> human-reviewed submission package`

Do not run every discovered bounty. Select representative targets, verify them
properly, and upgrade the matrix only when externally verifiable evidence
exists.
