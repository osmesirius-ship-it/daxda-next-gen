# DAXDA V10 Master — Reasoner Behind V9

This package implements the missing architecture: a pluggable task-solving reasoner behind the frozen DAXDA V9 governance firewall. V9 controls admission and release; the injected reasoner performs the task.

**Claim boundary:** the package is an evaluator candidate. The bundled demo is a structural fixture, not a genuine reasoner, and its outputs must not be used to claim intelligence or external validation.

## Package map

- `daxda_engine_v10.py` — preflight, 16-layer orchestration, synthesis, postflight, authority gate, and audit record
- `reasoner_protocol.py` — Python-module and subprocess reasoner boundaries
- `reasoner_adapter_template.py` — evaluator-owned integration point
- `layer_registry.py` — 16 layer objectives and required output schema
- `tile_executor.py` — 55 concrete computations per layer, including `Cl(2,0)` operations
- `v9_firewall/` — byte-for-byte V9 engine and Clifford implementation, plus a package import shim
- `suite_adapter.py` — connects V10 to the existing ordered 208-question runner
- `demo_reasoner.py` and `demo_suite_adapter.py` — integration tests only
- `test_v10.py` — fail-closed, quarantine, receipt-chain, operation-count, and hash tests
- `ARCHITECTURE.md` — threat model, executed path, and external validation design

## Verify the package

From the directory containing `DAXDA_V10_MASTER`:

```bash
python3 -m unittest DAXDA_V10_MASTER.test_v10 -v
python3 -m py_compile DAXDA_V10_MASTER/*.py DAXDA_V10_MASTER/v9_firewall/*.py
```

## Connect the real reasoner

Copy `reasoner_adapter_template.py`, implement `solve(request)`, and keep credentials outside the package. The adapter must support the layer, synthesis, and repair protocols documented in the template. It may call a local model, a remote model endpoint, a symbolic planner, or a hybrid system, but it must return the requested JSON object.

For Python-module integration:

```python
from DAXDA_V10_MASTER.daxda_engine_v10 import DAXDAEngineV10
from DAXDA_V10_MASTER.reasoner_protocol import ModuleReasoner

engine = DAXDAEngineV10(ModuleReasoner("/absolute/path/to/real_reasoner.py"))
audit = engine.evaluate("Your task", sources=[], mode="analysis")
print(audit["answer"])
```

For process isolation, use `SubprocessReasoner(["/absolute/path/to/command", "--json"])`. It sends one JSON request on standard input and expects one JSON object on standard output.

## Run the 208-question evaluator suite

The external evaluator—not the developer—should set the real adapter path and run:

```bash
export DAXDA_REASONER_MODULE=/absolute/path/to/real_reasoner.py
python3 DAXDA_EXTERNAL_SUPERINTELLIGENCE_SUITE/ide_runner.py \
  DAXDA_EXTERNAL_SUPERINTELLIGENCE_SUITE/suite_questions.json \
  DAXDA_V10_MASTER/suite_adapter.py \
  --out v10_sealed_outputs.json
```

Do not give the reasoner `sealed_rubric.json`. Score only after output commitment. Compare paired results with the frozen V7 baseline and the ablation arms in `ARCHITECTURE.md`.

The suite adapter forwards compact, bounded summaries of earlier answers for the ordered consistency probes; it does not forward nested engine audits into later model context.

## Interpreting counts

A complete reasoning run logs 16 layers × 55 computations plus 6 system operations, totaling 886. A blocked or failed run reports only the operations it actually executed. Passing software tests establishes implementation integrity, not task intelligence, safety in deployment, or superintelligence.
