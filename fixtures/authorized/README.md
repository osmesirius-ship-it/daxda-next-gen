# Authorized local bounty fixtures

Isolated checkouts for published bounty programs. These are **not** findings.

## Tonkeeper W5 (`tonkeeper/w5` issue #17)

```bash
git clone https://github.com/tonkeeper/w5.git fixtures/authorized/tonkeeper-w5
cd fixtures/authorized/tonkeeper-w5
git checkout fa1b372a417a32af104fe1b949b6b31d29cee349
npm ci
npm test
cd ../../..
python tools/run_tonkeeper_w5_local_fixture.py
```

Rules:
- Pinned commit only: `fa1b372a417a32af104fe1b949b6b31d29cee349`
- Test keys / local sandbox only — no live network probing, no real funds
- Jest is the independent baseline evaluator
- DAXDA Cl(16,4) / Arena fixture PASS ≠ vulnerability finding
- Submit only after independent proof + human review under the program ROE
