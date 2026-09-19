# Selected Bounty: Tonkeeper W5

**Selected program:** [tonkeeper/w5#17](https://github.com/tonkeeper/w5/issues/17)  
**Target repository:** `https://github.com/tonkeeper/w5`  
**Target commit:** `fa1b372a417a32af104fe1b949b6b31d29cee349`  
**Selection date:** 2026-09-18  
**Status:** `selected_pending_authorized_local_fixture`

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

## Prada Arena classification

The existing DAXDA run classified `TONKEEPER-W5-17` as text-level triage only.
Because no authorized target fixture was available, the Arena correctly
returned `ROLLBACK_AND_DIAGNOSE` with the diagnosis
`obtain_authorized_target_fixture`. This selection does not claim a
vulnerability or bounty eligibility.

## Acceptance gates

- [ ] Exact commit is locally pinned and hash recorded.
- [ ] Test harness is isolated and uses non-valuable funds.
- [ ] Reproduction is deterministic and independently replayable.
- [ ] Impact is within the published bounty scope.
- [ ] No duplicate or previously reported root cause.
- [ ] Fix or mitigation passes regression testing.
- [ ] Human reviewer approves disclosure before submission.
