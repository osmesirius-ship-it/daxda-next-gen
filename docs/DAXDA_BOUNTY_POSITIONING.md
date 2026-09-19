# DAXDA Bounty Positioning and Submission Strategy

## Project profile

**Project name:** DAXDA with Prada Recursive Improvement Arena

**Main claim:** DAXDA is a bounded bounty-solving and verification architecture
for externally evaluated, machine-checkable tasks. Prada can triage problems,
record evaluator results, diagnose failure modes, retain only verified
improvements, and fail closed when target evidence or authorization is missing.

## Target domains

| Priority | Domain | Appropriate DAXDA role |
|---|---|---|
| 1 | Security | Authorization-boundary analysis, reproducible local fixtures, regression evidence, disclosure packaging |
| 2 | Code/bug-fix | Candidate patch generation metadata, static/test evidence, rollback and regression tracking |
| 3 | DeFi/Web3 | Smart-contract and transaction-state verification in isolated local harnesses |
| 4 | AI/ML | Evaluator integrity, prompt-injection resistance, provenance, tool-schema and composition testing |
| 5 | Math | Machine-checkable solutions with independent proof or oracle validation |
| 6 | Data science | Reproducible pipelines, held-out evaluation, data lineage, and resource-impact reporting |
| 7 | Research synthesis | Source provenance, claim/evidence mapping, contradiction detection, and reviewer packets |
| 8 | Other | Only when acceptance criteria and an independent evaluator are explicit |

## Bounty sources and boards

- GitHub bounties and open-source issue boards
- Security bug-bounty programs with explicit rules of engagement
- Research challenge boards with machine-checkable evaluation
- DeFi/Web3 grant and bounty portals, including Immunefi-style programs
- Maintainer-approved local reproductions and responsible-disclosure channels

Public listings are discovery inputs, not authorization to probe live systems.

## Submission model

The recommended model is a **benchmark matrix plus submission documents**:

1. Maintain a ranked shortlist of eligible opportunities.
2. Map each opportunity to DAXDA vectors, tools, evaluator, difficulty, and payout.
3. Reproduce only in an authorized local fixture, owned account, or approved
   checkout.
4. Submit only after independent verification, regression testing,
   reproducibility checks, and human review.

This produces a general DAXDA capability statement while retaining a
submission-ready brief for a specific bounty.

## Existing evidence

- `daxda_engine/prada.py`
  - bounded planner
  - human/infrastructure/resource mapping
  - candidate evidence and signed reports
  - fail-closed controller
  - `PradaArena` external-evaluator loop
- `tests/test_prada.py`
  - planner, controller, rollback, evidence, and arena coverage
- `docs/DAXDA_BOUNTY_MATRIX.md`
  - 13 operational vectors, tools, verification methods, difficulty, payouts,
    and public candidates
- `reports/daxda_bounty_arena_run_2026-09-18.md`
  - five public candidates processed as text-level triage
  - five explicit `target_not_tested` diagnoses
  - per-case receipts and aggregate metrics
- `reports/selected_bounty_tonkeeper_w5_2026-09-18.md`
  - selected highest-payment candidate
  - exact Tonkeeper W5 commit and local-only execution plan
- `doc_dax/default_project/query_*/`
  - DAXDA audit reports and layer-trace packets for each candidate

## Strongest demonstrated capabilities

| Capability | Evidence standard |
|---|---|
| Governance triage | Scanner verdict, decision rule, containment stage, and receipt |
| External evaluation | Arena accepts evaluator-supplied results rather than self-certifying |
| Safe failure handling | Missing target evidence produces `ROLLBACK_AND_DIAGNOSE` |
| Recursive improvement bookkeeping | Success, verification, regression, novelty, generalization, and improvement metrics |
| Reversibility | Candidate changes remain metadata-only; failed pilots roll back |
| Provenance | SHA-256 digests, baseline provenance, signed evidence reports, immutable receipts |
| Human control | Production, authority, safety-policy, high-impact, and external-effect changes require approval |

These demonstrate verification architecture and bounded orchestration. They do
not establish that any listed target is vulnerable or that a bounty will be
paid.

## Ranked bounty strategy

| Rank | Candidate class | Example | Why pursue | Required proof |
|---:|---|---|---|---|
| 1 | Smart-contract loss-of-funds security | [tonkeeper/w5#17](https://github.com/tonkeeper/w5/issues/17) | Highest documented ceiling: 5,000–10,000 TON | Pinned-commit local replay, independent evaluator, scope and duplicate checks |
| 2 | Memory-layer and agent security | [moorcheh-ai/memanto#1852](https://github.com/moorcheh-ai/memanto/issues/1852) | Strongest DAXDA thematic fit | Owned fixtures, minimal failing test, fix, regression suite, one compliant PR |
| 3 | OAuth authorization-boundary bugs | [BasedHardware/omi#14442](https://github.com/BasedHardware/omi/issues/14442) | Concrete local callback reproduction | Forged state/signature fixtures and verified account-binding failure |
| 4 | OAuth multi-provider state bugs | [BasedHardware/omi#14444](https://github.com/BasedHardware/omi/issues/14444) | Same reusable harness as #14442 | Duplicate/root-cause screening and provider-specific regression tests |
| 5 | Webhook/principal rebinding | [BasedHardware/omi#14463](https://github.com/BasedHardware/omi/issues/14463) | Clear execution-boundary fit | Local Redis and fake-client reproduction on every mutating route |

## Constraints

- Public, low-risk work only unless explicit authorization is obtained.
- No live probing, real funds, production accounts, secret access, or external
  deployment.
- Use isolated sandboxes, generated credentials, non-valuable test assets, and
  pinned source revisions.
- Do not modify production or safety gates through Prada.
- Do not claim a vulnerability from a DAXDA `PASS`; it means only that the
  description passed local governance triage.
- Human approval is required for disclosure, submission, deployment, authority
  changes, safety-policy changes, or high-impact findings.
- Respect each program's scope, duplicate policy, disclosure process, licensing,
  jurisdiction, and deadlines.

## Submission checklist

- [ ] Program rules and scope captured with retrieval date.
- [ ] Exact target revision or challenge version pinned.
- [ ] Authorization and permitted test surface recorded.
- [ ] Local fixture uses generated identities and non-valuable assets.
- [ ] Baseline behavior recorded before the candidate change.
- [ ] Reproduction is deterministic and independently replayable.
- [ ] Impact is tied to the program's payout category.
- [ ] Static, unit, integration, security, regression, resource, and
      reproducibility checks pass as applicable.
- [ ] Duplicate and known-issue screening complete.
- [ ] Evidence report is signed and provenance-tracked.
- [ ] Human reviewer approves the final submission.

## Recommended workflow

`DISCOVER -> SCOPE -> AUTHORIZE -> REPRODUCE LOCALLY -> VERIFY INDEPENDENTLY ->
REGRESSION TEST -> PACKAGE EVIDENCE -> HUMAN REVIEW -> SUBMIT`

If authorization, evaluator access, reproducibility, or safety evidence is
missing, stop at triage and produce a review packet instead of acting.
