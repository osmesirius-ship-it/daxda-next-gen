#!/usr/bin/env bash
"""True""" # Shell polyglot wrapper to run with python3
""":"
exec python3 "$0" "$@"
":"""

"""
DAXDA Level 3: Real-Time BCI Alignment Attestation SLA Benchmark
================================================================
Measures execution latency and throughput for Affine-Invariant Riemannian Metric (AIRM),
Fréchet mean gradient descent, tangent space projection, and neurometric hardware attestation.
"""

import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from daxda_engine.level3.bci_alignment import (
    RiemannianEEGCovarianceEngine,
    airm_geodesic_distance,
    frechet_mean_spd,
    tangent_space_log_map,
    VigilanceDriftDetector,
    CognitiveEpochAssessment,
    NeurometricAttestationIssuer,
)


def run_benchmark(channels: int = 32, epochs: int = 20, iterations: int = 5):
    print("=" * 78)
    print("DAXDA LEVEL 3 REAL-TIME BCI ALIGNMENT ATTESTATION SLA BENCHMARK")
    print(f"EEG Channels: {channels} | Calibration Epochs: {epochs} | Iterations: {iterations}")
    print("=" * 78)

    rng = np.random.default_rng(42)
    # Generate random SPD matrices on S_+^C
    A_list = []
    for _ in range(epochs):
        raw = rng.normal(size=(channels, channels))
        spd = raw @ raw.T + np.eye(channels) * 0.1
        A_list.append(spd)
    
    P1, P2 = A_list[0], A_list[1]

    # 1. Benchmark AIRM Geodesic Distance
    airm_latencies = []
    for _ in range(iterations * 10):
        t0 = time.perf_counter()
        dist = airm_geodesic_distance(P1, P2)
        airm_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 2. Benchmark Fréchet Mean Gradient Descent
    frechet_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        mean_mat = frechet_mean_spd(A_list, max_iter=25)
        frechet_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 3. Benchmark Tangent Space Log Map
    tangent_latencies = []
    for _ in range(iterations * 10):
        t0 = time.perf_counter()
        t_vec = tangent_space_log_map(P1, P2)
        tangent_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 4. Benchmark Neurometric Hardware Attestation
    issuer = NeurometricAttestationIssuer()
    assessment = CognitiveEpochAssessment(
        vigilance_score=0.91,
        engagement_index=1.45,
        drowsiness_ratio=0.82,
        is_drowsy=False,
        has_ern_dissonance=False,
        ern_amplitude_uV=1.2,
        airm_drift_from_baseline=float(dist),
        is_operator_attested=True,
    )
    attestation_latencies = []
    for _ in range(iterations * 10):
        t0 = time.perf_counter()
        envelope = issuer.issue_attestation(
            action_proposal_id="PROPOSAL_TX_9876543210",
            assessment=assessment,
            airm_distance=float(dist),
        )
        attestation_latencies.append((time.perf_counter() - t0) * 1000.0)

    results = {
        "channels": channels,
        "epochs": epochs,
        "airm_distance_mean_ms": float(np.mean(airm_latencies)),
        "airm_distance_p99_ms": float(np.percentile(airm_latencies, 99)),
        "frechet_mean_mean_ms": float(np.mean(frechet_latencies)),
        "frechet_mean_p99_ms": float(np.percentile(frechet_latencies, 99)),
        "tangent_map_mean_ms": float(np.mean(tangent_latencies)),
        "attestation_signing_mean_ms": float(np.mean(attestation_latencies)),
        "attestation_signing_p99_ms": float(np.percentile(attestation_latencies, 99)),
    }

    print(f"AIRM Distance Latency:     {results['airm_distance_mean_ms']:.4f} ms (p99: {results['airm_distance_p99_ms']:.4f} ms) [SLA < 1.0 ms]")
    print(f"Fréchet Mean Latency:      {results['frechet_mean_mean_ms']:.4f} ms (p99: {results['frechet_mean_p99_ms']:.4f} ms) [SLA < 50.0 ms]")
    print(f"Tangent Space Map Latency: {results['tangent_map_mean_ms']:.4f} ms [SLA < 1.0 ms]")
    print(f"Attestation Issue Latency: {results['attestation_signing_mean_ms']:.4f} ms (p99: {results['attestation_signing_p99_ms']:.4f} ms) [SLA < 5.0 ms]")
    print("=" * 78)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAXDA Level 3 BCI Alignment Benchmark")
    parser.add_argument("--channels", type=int, default=32, help="Number of EEG channels")
    parser.add_argument("--epochs", type=int, default=15, help="Number of calibration epochs")
    parser.add_argument("--out", type=str, default="", help="Path to write JSON output")
    args = parser.parse_args()

    bench_res = run_benchmark(channels=args.channels, epochs=args.epochs)
    if args.out:
        Path(args.out).write_text(json.dumps(bench_res, indent=2))
        print(f"Saved benchmark results to {args.out}")
