#!/usr/bin/env bash
"""True""" # Shell polyglot wrapper to run with python3
""":"
exec python3 "$0" "$@"
":"""

"""
DAXDA Level 3: Multiversal Social Choice & Consensus SLA Benchmark
==================================================================
Measures execution latency and throughput for Generalized Nash Bargaining,
Byzantine-robust Huber-Weiszfeld geometric median, and (epsilon, delta)-DP receipts.
"""

import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from daxda_engine.level3.multiversal_consensus import (
    NashBargainingSolver,
    WeiszfeldGeometricMedian,
    CardinalWelfareOptimizer,
    DifferentialPrivacyAggregator,
    MultiversalConsensusManager,
)


def run_benchmark(agents: int = 50, candidates: int = 20, iterations: int = 10):
    print("=" * 78)
    print("DAXDA LEVEL 3 MULTIVERSAL SOCIAL CHOICE & VALUE ALIGNMENT BENCHMARK")
    print(f"Swarm Agents M: {agents} | Candidates K: {candidates} | Iterations: {iterations}")
    print("=" * 78)

    rng = np.random.default_rng(42)
    # Generate random utility matrix (K, M) and threat point (M,)
    util_matrix = rng.uniform(2.0, 10.0, size=(candidates, agents))
    threat_pt = np.full(agents, 1.0)

    # 1. Benchmark Generalized Nash Bargaining Solver
    nash_latencies = []
    for _ in range(iterations * 10):
        t0 = time.perf_counter()
        _best_k, _u, _obj = NashBargainingSolver.solve_discrete(util_matrix, threat_pt)
        nash_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 2. Benchmark Pareto Frontier Extraction
    pareto_latencies = []
    for _ in range(iterations * 5):
        t0 = time.perf_counter()
        _frontier = NashBargainingSolver.extract_pareto_frontier(util_matrix)
        pareto_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 3. Benchmark Weiszfeld Geometric Median
    pts = rng.normal(loc=0.0, scale=1.0, size=(agents, 16))
    median_latencies = []
    for _ in range(iterations * 5):
        t0 = time.perf_counter()
        _med = WeiszfeldGeometricMedian.compute_median(pts, max_iter=50)
        median_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 4. Benchmark Byzantine Outlier Detection
    byz_latencies = []
    for _ in range(iterations * 5):
        t0 = time.perf_counter()
        _outliers = WeiszfeldGeometricMedian.detect_byzantine_outliers(pts)
        byz_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 5. Benchmark End-to-End Consensus Manager with DP & Signing
    manager = MultiversalConsensusManager()
    e2e_latencies = []
    for _ in range(iterations * 5):
        t0 = time.perf_counter()
        _receipt, _dp_u = manager.reach_consensus(
            candidate_utilities=util_matrix,
            threat_point=threat_pt,
            epsilon=1.0,
            delta=1e-5,
            filter_byzantine=True,
        )
        e2e_latencies.append((time.perf_counter() - t0) * 1000.0)

    results = {
        "agents": agents,
        "candidates": candidates,
        "nash_solver_mean_ms": float(np.mean(nash_latencies)),
        "nash_solver_p99_ms": float(np.percentile(nash_latencies, 99)),
        "pareto_frontier_mean_ms": float(np.mean(pareto_latencies)),
        "geometric_median_mean_ms": float(np.mean(median_latencies)),
        "geometric_median_p99_ms": float(np.percentile(median_latencies, 99)),
        "byzantine_detector_mean_ms": float(np.mean(byz_latencies)),
        "e2e_consensus_mean_ms": float(np.mean(e2e_latencies)),
        "e2e_consensus_p99_ms": float(np.percentile(e2e_latencies, 99)),
    }

    print(f"Nash Bargaining Latency:   {results['nash_solver_mean_ms']:.4f} ms (p99: {results['nash_solver_p99_ms']:.4f} ms) [SLA < 1.0 ms]")
    print(f"Pareto Frontier Extraction:{results['pareto_frontier_mean_ms']:.4f} ms [SLA < 2.0 ms]")
    print(f"Huber-Weiszfeld Median:    {results['geometric_median_mean_ms']:.4f} ms (p99: {results['geometric_median_p99_ms']:.4f} ms) [SLA < 5.0 ms]")
    print(f"Byzantine Outlier Filter:  {results['byzantine_detector_mean_ms']:.4f} ms [SLA < 5.0 ms]")
    print(f"End-to-End DP Consensus:   {results['e2e_consensus_mean_ms']:.4f} ms (p99: {results['e2e_consensus_p99_ms']:.4f} ms) [SLA < 10.0 ms]")
    print("=" * 78)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAXDA Level 3 Multiversal Consensus Benchmark")
    parser.add_argument("--agents", type=int, default=50, help="Number of swarm agents")
    parser.add_argument("--candidates", type=int, default=20, help="Number of proposal candidates")
    parser.add_argument("--out", type=str, default="", help="Path to write JSON output")
    args = parser.parse_args()

    bench_res = run_benchmark(agents=args.agents, candidates=args.candidates)
    if args.out:
        Path(args.out).write_text(json.dumps(bench_res, indent=2))
        print(f"Saved benchmark results to {args.out}")
