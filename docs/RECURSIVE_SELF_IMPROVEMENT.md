# How DAXDA gets better, faster, and smarter than a frozen model

Frontier language models are snapshots. Between training runs their weights do
not change, so at inference time `d(capability)/dt = 0`. DAXDA's bet is
**governed compounding**: a nested loop that measures three axes every cycle,
keeps only verified gains, and meta-learns which improvement operators actually
work.

This is not a claim that DAXDA writes better prose than a frontier LLM. It is a
claim that a system which **improves itself under fail-closed verification**
will outpace any frozen snapshot on the tasks it is allowed to optimize,
because every KEEP raises the floor and every ROLLBACK costs only a cycle.

## The three axes

| Axis | Operational meaning | How the loop moves it |
|---|---|---|
| **Better** | Verified verdict accuracy on train *and* held-out paraphrases | Learn suppress/verification lemmas from missed BLOCKs |
| **Faster** | p99 evaluation latency vs a 2 ms target | Short-circuit only when the overlay already BLOCKs |
| **Smarter** | Held-out generalization, transfer, diagnosis quality | UCB1 over operators + morphological transfer |

Scalar fitness is a **geometric mean**, and it is **identically 0** if safety
fails. There is no "trade a bit of safety for speed" Pareto cheat.

```
if safety < 1: F = 0
else:          F = quality^0.45 * speed^0.25 * smarts^0.30
```

## Nested loops

```
outer (meta-RSI)     UCB1 selects learn_lemmas | enable_short_circuit
                     | trim_false_positives | transfer_morphology
    inner            mutate strategy genome
                     measure train / held-out / benign / safety
                     KEEP iff quality rose, held-out did not regress,
                     benign accuracy intact, safety = 1, overlay monotonic
```

The genome is strategy, not source. It may **escalate** `PASS → CAUTION → BLOCK`.
It may never de-escalate a BLOCK, rewrite `classify_gate`, or touch
`daxda_guard/safety_invariants.py`.

## Why this can beat a bigger frozen model

1. **Compounding.** A frozen model has zero improvement per inference. DAXDA's
   RSI rate is `(final_scalar - baseline_scalar) / cycles`. Any KEEP makes the
   next cycle start higher.
2. **Held-out generalization.** Overfit lemmas that punch benign traffic are
   rolled back. The loop is selected for transfer, not memorization.
3. **Meta-selection.** The outer bandit stops wasting cycles on operators that
   do not pay. The improver itself improves.
4. **Monotonic safety.** Learned overlays can only add blocks. The system gets
   stricter as it gets smarter, not looser.
5. **Human-capacity bound.** Code-level promotion still goes through PRADA and
   waits for explicit human approval. Acceleration cannot outrun oversight.
6. **Latency as a first-class axis.** Short-circuit is allowed only on already
   decided BLOCKs, so speed-ups cannot skip unknown safety work.

## What it will not do

- Rewrite production source without a human.
- Disable verification to "converge faster".
- Claim physical capabilities without the scientific protocol.
- Treat a cryptographic receipt as a causal explanation (INV-01).

## Run it

```bash
python tools/run_recursive_self_improvement.py 8
pytest tests/test_recursive_self_improvement.py -q
```

Evidence lands in `reports/daxda_recursive_self_improvement/`.
