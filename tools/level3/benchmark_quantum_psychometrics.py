#!/usr/bin/env bash
"""True""" # Shell polyglot wrapper to run with python3
""":"
exec python3 "$0" "$@"
":"""

"""
DAXDA Level 3: Quantum Psychometrics Measurement Models SLA Benchmark
======================================================================
Measures execution latency and throughput for complex density operator algebra,
Lüders projective reduction, Wang-Busemeyer QQ solver, Wigner-Yanase skew info,
and Hilbert-Schmidt quantum state tomography.
"""

import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from daxda_engine.level3.quantum_psychometrics import (
    QuantumDensityState,
    create_pure_state,
    create_maximally_mixed_state,
    HermitianObservable,
    LudersMeasurementSimulator,
    WangBusemeyerQQSolver,
    WignerYanaseSkewAnalyzer,
    QuantumStateTomographyEngine,
)


def run_benchmark(dim: int = 4, iterations: int = 10):
    print("=" * 78)
    print("DAXDA LEVEL 3 QUANTUM PSYCHOMETRICS MEASUREMENT MODELS SLA BENCHMARK")
    print(f"Hilbert Dimension d: {dim} | Iterations: {iterations}")
    print("=" * 78)

    rng = np.random.default_rng(42)
    # Generate random d-dimensional state vector
    psi = rng.normal(size=dim) + 1j * rng.normal(size=dim)
    pure_state = create_pure_state(psi)
    
    # 1. Benchmark Purity and Von Neumann Entropy
    entropy_latencies = []
    for _ in range(iterations * 50):
        t0 = time.perf_counter()
        _p = pure_state.purity()
        _s = pure_state.von_neumann_entropy()
        entropy_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 2. Benchmark Lüders Measurement Simulation
    H = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    H = (H + H.conj().T) * 0.5
    obs_A = HermitianObservable(H, name="ObsA")
    sim = LudersMeasurementSimulator()

    luders_latencies = []
    for _ in range(iterations * 20):
        t0 = time.perf_counter()
        _prob, _post = sim.measure_single(pure_state, obs_A, 0)
        luders_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 3. Benchmark Wang-Busemeyer QQ Equality Verification (d=2)
    Z = HermitianObservable.from_pauli("Z")
    X = HermitianObservable.from_pauli("X")
    qubit_state = create_pure_state(np.array([0.8, 0.6]))

    qq_latencies = []
    for _ in range(iterations * 20):
        t0 = time.perf_counter()
        _q = WangBusemeyerQQSolver.verify_qq_equality(qubit_state, Z, X)
        qq_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 4. Benchmark Wigner-Yanase Skew Information
    skew_latencies = []
    for _ in range(iterations * 20):
        t0 = time.perf_counter()
        _skew = WignerYanaseSkewAnalyzer.compute_skew_information(pure_state.matrix, obs_A.matrix)
        skew_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 5. Benchmark Quantum State Tomography (QST)
    qst_engine = QuantumStateTomographyEngine(dim=dim)
    tomography_latencies = []
    for _ in range(iterations * 10):
        t0 = time.perf_counter()
        _recon = qst_engine.tomographic_reconstruction(pure_state)
        tomography_latencies.append((time.perf_counter() - t0) * 1000.0)

    results = {
        "dim": dim,
        "entropy_mean_ms": float(np.mean(entropy_latencies)),
        "entropy_p99_ms": float(np.percentile(entropy_latencies, 99)),
        "luders_mean_ms": float(np.mean(luders_latencies)),
        "luders_p99_ms": float(np.percentile(luders_latencies, 99)),
        "qq_solver_mean_ms": float(np.mean(qq_latencies)),
        "qq_solver_p99_ms": float(np.percentile(qq_latencies, 99)),
        "skew_info_mean_ms": float(np.mean(skew_latencies)),
        "skew_info_p99_ms": float(np.percentile(skew_latencies, 99)),
        "tomography_mean_ms": float(np.mean(tomography_latencies)),
        "tomography_p99_ms": float(np.percentile(tomography_latencies, 99)),
    }

    print(f"Entropy/Purity Latency:   {results['entropy_mean_ms']:.4f} ms (p99: {results['entropy_p99_ms']:.4f} ms) [SLA < 0.5 ms]")
    print(f"Lüders Projection Latency:{results['luders_mean_ms']:.4f} ms (p99: {results['luders_p99_ms']:.4f} ms) [SLA < 1.0 ms]")
    print(f"QQ Equality Solver:       {results['qq_solver_mean_ms']:.4f} ms (p99: {results['qq_solver_p99_ms']:.4f} ms) [SLA < 2.0 ms]")
    print(f"Wigner-Yanase Skew Info:  {results['skew_info_mean_ms']:.4f} ms (p99: {results['skew_info_p99_ms']:.4f} ms) [SLA < 1.0 ms]")
    print(f"QST Reconstruction:       {results['tomography_mean_ms']:.4f} ms (p99: {results['tomography_p99_ms']:.4f} ms) [SLA < 5.0 ms]")
    print("=" * 78)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAXDA Level 3 Quantum Psychometrics Benchmark")
    parser.add_argument("--dim", type=int, default=4, help="Hilbert space dimension")
    parser.add_argument("--out", type=str, default="", help="Path to write JSON output")
    args = parser.parse_args()

    bench_res = run_benchmark(dim=args.dim)
    if args.out:
        Path(args.out).write_text(json.dumps(bench_res, indent=2))
        print(f"Saved benchmark results to {args.out}")
