#!/usr/bin/env bash
"""True""" # Shell polyglot wrapper to run with python3
""":"
exec python3 "$0" "$@"
":"""

"""
DAXDA Level 3: Neuro-Cognitive fMRI Latent Space Matching SLA Benchmark
========================================================================
Measures execution latency and throughput for Centered Kernel Alignment (CKA),
Stiefel Procrustes alignment, Grassmannian geodesic metrics, and Glasser parcellation.
"""

import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from daxda_engine.level3.neuro_fmri import (
    RepresentationalAlignmentEngine,
    CenteredKernelAlignment,
    StiefelProcrustesAligner,
    GrassmannianManifoldDistance,
    GlasserEthicalParcellator,
    HemodynamicDeconvolver,
)


def run_benchmark(stimuli: int = 500, voxels: int = 180, d_model: int = 4096, iterations: int = 5):
    print("=" * 78)
    print("DAXDA LEVEL 3 NEURO-COGNITIVE fMRI REPRESENTATIONAL MATCHING BENCHMARK")
    print(f"Stimuli: {stimuli} | Voxels (ROIs): {voxels} | Model Dimension: {d_model}")
    print("=" * 78)

    rng = np.random.default_rng(42)
    # Generate high-dimensional synthetic stimulus representations
    X = rng.normal(size=(stimuli, d_model)).astype(np.float64)
    Y = rng.normal(size=(stimuli, voxels)).astype(np.float64)

    # 1. Benchmark Linear CKA
    cka_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        res_cka = CenteredKernelAlignment.linear_cka(X, Y)
        cka_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 2. Benchmark Stiefel Procrustes Alignment
    procrustes_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        res_proc = StiefelProcrustesAligner.align(X, Y)
        procrustes_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 3. Benchmark Grassmannian Geodesic Distance
    grassmann_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        res_geo = GrassmannianManifoldDistance.compute_principal_angles(X, Y, rank=32)
        grassmann_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 4. Benchmark Glasser Ethical Parcellation
    parcellator = GlasserEthicalParcellator()
    parcellation_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        profile = parcellator.evaluate_moral_network_concordance(X, Y)
        parcellation_latencies.append((time.perf_counter() - t0) * 1000.0)

    # 5. Benchmark HRF Convolution
    deconv = HemodynamicDeconvolver(tr_seconds=1.5)
    amplitudes = rng.uniform(0.0, 2.0, size=stimuli)
    hrf_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        bold_stream = deconv.convolve_events(amplitudes)
        hrf_latencies.append((time.perf_counter() - t0) * 1000.0)

    mean_cka = float(np.mean(cka_latencies))
    mean_proc = float(np.mean(procrustes_latencies))
    mean_geo = float(np.mean(grassmann_latencies))
    mean_parc = float(np.mean(parcellation_latencies))
    mean_hrf = float(np.mean(hrf_latencies))

    total_pipeline_ms = mean_cka + mean_proc + mean_geo + mean_parc + mean_hrf
    throughput_stimuli_sec = (stimuli / (total_pipeline_ms / 1000.0))

    print(f"• Linear CKA Mean Latency:           {mean_cka:8.3f} ms (Score: {res_cka.cka_score:.4f})")
    print(f"• Stiefel Procrustes Latency:        {mean_proc:8.3f} ms (EVR: {res_proc.explained_variance_ratio:.4f})")
    print(f"• Grassmannian Geodesic Latency:     {mean_geo:8.3f} ms (Dist: {res_geo.geodesic_distance:.4f})")
    print(f"• Glasser Parcellation Latency:      {mean_parc:8.3f} ms (MCI: {profile.composite_mci:.4f})")
    print(f"• HRF Event Convolution Latency:     {mean_hrf:8.3f} ms")
    print("-" * 78)
    print(f"TOTAL PIPELINE EXECUTION:            {total_pipeline_ms:8.3f} ms")
    print(f"AGGREGATE THROUGHPUT:                {throughput_stimuli_sec:8.1f} stimuli/second")

    # SLA Verification: Sub-50ms requirement for parcellation
    status = "PASS" if total_pipeline_ms < 150.0 else "FAIL"
    print(f"SLA STATUS:                          {status}")
    print("=" * 78)

    benchmark_output = {
        "benchmark": "DAXDA Level 3 Neuro-fMRI Latent Space Matching",
        "status": status,
        "stimuli": stimuli,
        "voxels": voxels,
        "d_model": d_model,
        "mean_cka_ms": mean_cka,
        "mean_procrustes_ms": mean_proc,
        "mean_grassmann_ms": mean_geo,
        "mean_parcellation_ms": mean_parc,
        "mean_hrf_ms": mean_hrf,
        "total_pipeline_ms": total_pipeline_ms,
        "throughput_stimuli_per_sec": throughput_stimuli_sec,
    }

    out_path = Path("outputs/neuro_fmri_benchmark_latest.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(benchmark_output, indent=2))
    print(f"Benchmark artifact saved to: {out_path}")
    return benchmark_output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Level 3 Neuro-fMRI Benchmark")
    parser.add_argument("--stimuli", type=int, default=500, help="Number of stimuli")
    parser.add_argument("--voxels", type=int, default=180, help="Number of cortical voxels")
    parser.add_argument("--d_model", type=int, default=4096, help="Transformer residual dimension")
    args = parser.parse_args()
    run_benchmark(stimuli=args.stimuli, voxels=args.voxels, d_model=args.d_model)
