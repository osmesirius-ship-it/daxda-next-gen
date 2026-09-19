# Tonkeeper W5 — Candidate Hypothesis Gate Review

**Program:** [tonkeeper/w5#17](https://github.com/tonkeeper/w5/issues/17)  
**Pinned commit:** `fa1b372a417a32af104fe1b949b6b31d29cee349`  
**Review date:** 2026-09-19  
**Mode:** local sandbox only  

## Gate checklist (required before any disclosure)

| Gate | Status |
|---|---|
| Candidate hypothesis stated | **None credible / in-scope** |
| Failing Jest replay for unauthorized fund movement or auth bypass | **Not produced** (no such finding) |
| Independent confirmation (second evaluator / replay) | N/A — no claim |
| Human approval before public issue or `oleg@tonkeeper.com` | **Blocked** — nothing to disclose |

**Explicit non-actions:** No GitHub issue was opened. No email was sent.

## What was reviewed

- `contracts/wallet_v5.fc` auth paths (`sign` / `sint` / `extn`)
- Seqno/`commit` replay handling, signature-auth disable encoding
- Extension dict auth + anti-brick exits 42/44
- Action allowlist (`send_msg` + IGNORE_ERRORS bit)
- Upstream suites: external / internal / extensions / get
- Bounty out-of-scope rules (design choices, prior versions, docs-only)

## Coverage added (expected PASS, not a finding)

Local file (vendor fixture, gitignored tree):

`fixtures/authorized/tonkeeper-w5/tests/wallet-v5-security-coverage.spec.ts`

| Test | Result | Meaning |
|---|---|---|
| bounced=`1` extension body ignored | **PASS** | No outbound transfer / no state abuse |
| `send_msg` without IGNORE_ERRORS → exit 37 | **PASS** | Action allowlist enforced |

These close previously unasserted edges. Passing coverage ≠ vulnerability.

## Weak ideas rejected (not elevated)

1. Internal post-`commit` bounce economics for gasless relayers — owner funds not stolen; later upstream commit `2ba7fda` already changed external-only commit behavior (post-bounty pin).
2. Bounced-message auth bypass — coverage test confirms correct ignore.
3. Packed-address WC collision / malicious extension / disabled pubkey — documented design or bounty out-of-scope.

## Independent confirmation

- Upstream Jest baseline: 70 tests passed (prior fixture run).
- New coverage suite: 2/2 passed on the same pinned commit.
- DAXDA Cl(16,4)/Arena: fixture governance only; still `no_vulnerability_evidence_yet`.

## Human approval gate

Disclosure remains **forbidden** until all of the following are true:

1. A concrete in-scope hypothesis exists.
2. A **failing** Jest replay demonstrates unauthorized fund loss or auth bypass.
3. An independent second confirmation reproduces it.
4. A human reviewer approves the disclosure channel (public issue **or** private `oleg@tonkeeper.com`).

## Bottom line

At `fa1b372`, no candidate cleared the “failing Jest replay” bar for an in-scope bounty claim. Continue invariant research only inside the local sandbox; treat any new idea as unproven until it fails a deterministic test.
