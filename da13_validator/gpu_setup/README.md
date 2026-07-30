# DAX 17-GPU Setup (NVIDIA)

This package provides a practical Ray-based setup for a 17-GPU DAX run.

## GPU Role Map

- `GPU 0`: orchestrator/control
- `GPU 1-6`: reasoning pool
- `GPU 7-12`: simulation pool
- `GPU 13-15`: validation pool
- `GPU 16`: shadow verifier

## Files

- `requirements.txt`: Python dependencies
- `cluster_config.py`: role map, model names, thresholds, weights
- `ray_workers.py`: one Ray actor per GPU
- `run_dax_17gpu.py`: orchestration loop with DA-X style stability gating
- `validator.py`: Draft 2020-12 schema + semantic decision validation

## 1) Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Start Ray

Single-node (17 GPUs):

```bash
ray start --head --num-gpus=17
```

Cluster:

```bash
ray start --head --port=6379 --num-gpus=<head_gpu_count>
# on worker nodes:
ray start --address='<HEAD_IP>:6379' --num-gpus=<worker_gpu_count>
```

## 3) Run

```bash
python run_dax_17gpu.py \
  --objective "What portfolio of carbon removal technologies can remove 10 gigatons CO2/year by 2045 while minimizing cost and energy use?" \
  --max-iterations 5 \
  --schema /Users/user/Documents/da13/dax-full-system.schema.json \
  --out dax_run_output.json \
  --ray-address auto
```

## 4) Output

`dax_run_output.json` includes:

- stability history (`L/A/P/F/T/S`)
- iteration decisions (`ACCEPT/RECURSE/HALT`)
- audit records
- validator gate result on each iteration

## 5) Production Notes

- Replace heuristic metric extraction with domain parsers for production.
- Keep model names in `cluster_config.py`; start with smaller models to validate scheduling.
- Add schema validation (`dax-full-system.schema.json`) before emitting final output.
- Add timeout and retry guards per role for failure isolation.
