# Selected Bounty: Tonkeeper W5

**Selected program:** [tonkeeper/w5#17](https://github.com/tonkeeper/w5/issues/17)  
**Target repository:** `https://github.com/tonkeeper/w5`  
**Target commit:** `fa1b372a417a32af104fe1b949b6b31d29cee349`  
**Selection date:** 2026-09-18  
**Fixture run date:** 2026-09-19  
**Status:** `authorized_local_fixture_ready__no_finding_claimed`

## Payment

| Severity category | Published reward |
|---|---:|
| Low | 250–500 TON |
| Medium | 1,000–2,500 TON |
| Top | **5,000–10,000 TON** |

The top category requires reliable loss of funds with little or no user
interaction. Payment is discretionary and the program states that the offer
may be amended or terminated.

## Scope

The selected target is the W5 smart contract at the pinned commit above.
Prior contract versions, documentation-only issues, failures outside the
wallet contract and immediate toolchain, and explicit design choices are out
of scope.

## Safe execution plan

1. Obtain the pinned source into a local, isolated checkout.
2. Build a local TON emulator or test harness with generated test keys and
   non-valuable test funds.
3. Establish baseline behavior and deterministic replay fixtures.
4. Test only locally owned contracts, keys, messages, and accounts.
5. Require an independent evaluator to confirm any claimed unauthorized state
   transition or fund movement.
6. Run regression, reproducibility, and impact checks.
7. Produce a responsible-disclosure report only if the evidence passes every
   gate and does not duplicate a known report.

No live wallet, production contract, external endpoint, or real funds were
accessed for this selection.

## Local fixture evidence (2026-09-19)

| Gate | Result |
|---|---|
| Pinned commit checkout | `fa1b372a417a32af104fe1b949b6b31d29cee349` confirmed |
| Fixture path | `fixtures/authorized/tonkeeper-w5` (gitignored vendor tree) |
| Independent evaluator | Upstream Jest: **4 suites / 70 tests passed** |
| Ephemeral test keys | Generated via `ton-crypto`; **secret not persisted** |
| Live probing | **False** |
| DAXDA Cl(16,4) fixture authorization | Valid (governance of local research mode) |
| Prada Arena | `ROLLBACK_AND_DIAGNOSE:begin_scoped_invariant_review` |
| Vulnerability / bounty claim | **None** — fixture PASS ≠ finding |

Machine receipt: `reports/tonkeeper_w5_local_fixture_receipt.json`  
Runner: `tools/run_tonkeeper_w5_local_fixture.py`  
Re-clone notes: `fixtures/authorized/README.md`

## Prada Arena classification

Text-only triage previously returned `obtain_authorized_target_fixture`.
That gate is now satisfied locally. The Arena still correctly refuses to
promote a bounty solve because no independently verified unauthorized fund
movement or auth bypass was demonstrated.

## Acceptance gates

- [x] Exact commit is locally pinned and hash recorded.
- [x] Test harness is isolated and uses non-valuable funds / ephemeral keys.
- [x] Baseline suite is deterministic and independently replayable (`npm test`).
- [ ] Impact is within the published bounty scope (no finding yet).
- [ ] No duplicate or previously reported root cause.
- [ ] Fix or mitigation passes regression testing.
- [ ] Human reviewer approves disclosure before submission.

## Hypothesis gate (2026-09-19)

See `reports/tonkeeper_w5_hypothesis_gate_2026-09-19.md`.

- Scoped review of `wallet_v5.fc` + existing Jest suites completed locally.
- **No in-scope candidate produced a failing Jest replay** for fund loss / auth bypass.
- Added passing coverage guards for bounced extension msgs and send_mode bit-2
  (fixture path only; not a finding).
- **No disclosure** to the public tracker or `oleg@tonkeeper.com`.

## Next authorized step

Only if a new in-scope hypothesis appears: add a **failing** Jest replay,
get independent confirmation, then obtain **human approval** before any
disclosure to the public issue tracker or `oleg@tonkeeper.com`.
