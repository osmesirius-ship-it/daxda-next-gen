import importlib
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Locate the existing worker without changing its implementation.
GPUValidationWorker = None
for module_name in (
    "da13_validator.workers.gpu_worker",
    "da13_validator.gpu_worker",
    "da13_validator.workers",
):
    try:
        module = importlib.import_module(module_name)
        GPUValidationWorker = getattr(module, "GPUValidationWorker", None)
        if GPUValidationWorker:
            break
    except ImportError:
        pass

if GPUValidationWorker is None:
    raise ImportError(
        "Could not locate GPUValidationWorker. "
        "Check the import path in tests/da13_validator/test_workers.py."
    )

worker = GPUValidationWorker(worker_id="geometry-benchmark", gpu_id=0)

print("\n========== DA13 GEOMETRY TEST ==========")
print(f"Repository: {ROOT}")
print(f"CUDA available: {worker.cuda_available}")
print(f"GPU ID: {worker.gpu_id}")

def cpu_run(vectors):
    return [worker._evaluate_geometric_bounds(v) for v in vectors]

def batch_run(vectors):
    return worker._evaluate_geometric_bounds_batch(vectors)

# Correctness: exact boundary and values immediately around it.
boundary_vectors = [
    [4.0] + [0.0] * 15,
    [4.0 + 1e-10] + [0.0] * 15,
    [4.0 - 1e-10] + [0.0] * 15,
    [0.0] * 16,
    [1.0] * 16,
]

cpu_boundary = cpu_run(boundary_vectors)
batch_boundary = batch_run(boundary_vectors)

print("\n========== BOUNDARY CHECK ==========")
boundary_ok = True
for i, (cpu_result, batch_result) in enumerate(
    zip(cpu_boundary, batch_boundary)
):
    same_decision = cpu_result[0] == batch_result[0]
    same_confidence = abs(cpu_result[1] - batch_result[1]) <= 1e-12
    passed = same_decision and same_confidence
    boundary_ok = boundary_ok and passed
    print(
        f"Case {i + 1}: CPU={cpu_result} "
        f"GPU/batch={batch_result} "
        f"{'PASS' if passed else 'FAIL'}"
    )

# Throughput: input generation stays outside the timed section.
print("\n========== THROUGHPUT BENCHMARK ==========")
print("Batch size | CPU items/sec | GPU/batch items/sec | Match")

all_correct = boundary_ok

for size in (1, 8, 32, 128, 512, 2048):
    vectors = [
        [0.05 + ((i + j) % 17) * 0.001 for j in range(16)]
        for i in range(size)
    ]

    cpu_results = cpu_run(vectors)
    batch_results = batch_run(vectors)

    matches = all(
        a[0] == b[0] and abs(a[1] - b[1]) <= 1e-12
        for a, b in zip(cpu_results, batch_results)
    )
    all_correct = all_correct and matches

    # Warm-up before timing.
    for _ in range(2):
        cpu_run(vectors)
        batch_run(vectors)

    cpu_times = []
    batch_times = []

    for _ in range(5):
        start = time.perf_counter()
        cpu_run(vectors)
        cpu_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        batch_run(vectors)
        batch_times.append(time.perf_counter() - start)

    cpu_median = statistics.median(cpu_times)
    batch_median = statistics.median(batch_times)

    cpu_rate = size / cpu_median if cpu_median else 0
    batch_rate = size / batch_median if batch_median else 0

    print(
        f"{size:10d} | {cpu_rate:13.1f} | "
        f"{batch_rate:19.1f} | "
        f"{'PASS' if matches else 'FAIL'}"
    )

print("\n========== FINAL RESULT ==========")
print(f"Boundary checks: {'PASS' if boundary_ok else 'FAIL'}")
print(f"CPU/batch numerical agreement: {'PASS' if all_correct else 'FAIL'}")
print("Measurement scope: geometric-bound calculation only.")
print("Not measured: full scoring, network dispatch, or cluster scaling.")

if not worker.cuda_available:
    print("WARNING: CUDA unavailable; batch method may be using CPU fallback.")

worker.stop()

if not all_correct:
    raise SystemExit("TEST FAILED: CPU and batch results differ.")

print("\nTEST PASSED")
