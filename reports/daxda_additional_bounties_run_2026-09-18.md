# DAXDA Additional Public Bounty Scan

**Run date:** 2026-09-18  
**Candidates scanned:** 13  
**Method:** Public-source metadata discovery, DAXDA text triage, and Prada
Arena fail-closed classification. No target repositories, contracts, wallets,
accounts, APIs, or external systems were probed.

## Ranked candidates

| Rank | Candidate | Domain | Published maximum | Status | Evidence confidence |
|---:|---|---|---:|---|---|
| 1 | [Tonkeeper W5 #17](https://github.com/tonkeeper/w5/issues/17) | DeFi/Web3 security | **5,000–10,000 TON** (~$6,800–$13,600 at $1.36/TON) | Open | High; primary program issue |
| 2 | [Bounty Plaza #604](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/604) | Code/bug-fix | $10,000 | Open | Medium; mirror, verify escrow/source |
| 3 | [Bounty Plaza #645](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/645) | AI/ML | $10,000 | Open | Low/medium; sponsor and acceptance need verification |
| 4 | [Bounty Plaza #651](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/651) | Other/game engineering | $10,000 | Open | Low/medium; sponsor and licensing need verification |
| 5 | [Clanker OpenAgents #7](https://github.com/ClankerNation/OpenAgents/issues/7) | DeFi/Web3 | $7,000 (body also references $4,500) | Open | Medium; primary issue, payout text inconsistent |
| 6 | [Tenstorrent #55130](https://github.com/tenstorrent/tt-metal/issues/55130) | AI/ML | $5,000 | Open | High; primary issue |
| 7 | [Bounty Plaza #1185](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/1185) | Code/bug-fix | $5,000 | Open | Medium; mirror of Tenstorrent issue |
| 8 | [Tromp Cuckoo #116](https://github.com/tromp/cuckoo/issues/116) | Math/algorithm | $5,000 | Open | Medium; claim thread, payment unverified |
| 9 | [Clanker OpenAgents #34](https://github.com/ClankerNation/OpenAgents/issues/34) | DeFi/Web3 | $4,000 (body references $4,500) | Open | Medium; payout text inconsistent |
| 10 | [Bounty Plaza #310](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/310) | AI/ML | $2,500 | Open | Low/medium; aggregate mirror requiring exact source selection |
| 11 | [Bounty Plaza #1300](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/1300) | DeFi/Web3 | $1,200 | Open | Low/medium; escrow claim requires verification |
| 12 | [Bounty Plaza #1303](https://github.com/zhangjiayang6835-cyber/bounty-plaza/issues/1303) | DeFi/Web3 | $1,100 | Open | Low/medium; escrow claim requires verification |
| 13 | [Tenstorrent #54551](https://github.com/tenstorrent/tt-metal/issues/54551) | Code/bug-fix | $1,000 | **Closed** | High; excluded from active pursuit |

## DAXDA and Prada results

All 13 descriptions returned DAXDA `PASS /
WITHIN_GOVERNANCE_TOLERANCE`. This means the descriptions were accepted as
authorized research inputs; it does not establish a vulnerability, payment
eligibility, escrow, or target authorization.

Every Prada Arena evaluation returned:

`ROLLBACK_AND_DIAGNOSE:obtain_authorized_fixture`

Aggregate metrics:

| Metric | Value |
|---|---:|
| Iterations | 13 |
| Success rate | 0.0 |
| Verification rate | 0.0 |
| Regression rate | 0.0 |
| Novel-failure rate | 1.0 |
| Generalization rate | 0.0 |
| Recursive self-improvement rate | 0.0 |

## Recommended pursuit order

1. Tonkeeper W5, after pinning commit
   `fa1b372a417a32af104fe1b949b6b31d29cee349` and obtaining an authorized
   local TON fixture.
2. Tenstorrent #55130, using the stated hardware/version setup or an approved
   equivalent.
3. Clanker OpenAgents #7, after confirming the actual payout and repository
   acceptance criteria.
4. Bounty Plaza candidates only after independently verifying the sponsor,
   escrow, source issue, licensing, and payment terms.

No candidate should be submitted from this scan alone. The next permissible
step is an authorized local reproduction with independent evaluation,
regression evidence, and human-reviewed disclosure.
