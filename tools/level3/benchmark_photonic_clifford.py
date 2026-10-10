#!/usr/bin/env python3
"""
DAXDA Level 3 Domain 1 SLA Benchmark: Photonic Clifford MZI Accelerator
"""

import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.level3.photonic_clifford import ClementsMZIMesh, PhotonicSimulator


def run_benchmark():
    print("=" * 80)
    print("  BENCHMARK: Photonic Clifford MZI Optical Mesh Accelerator")
    print("=" * 80)

    for n in [4, 8, 16]:
        # Generate random unitary
        np.random.seed(42)
        X = (np.random.randn(n, n) + 1j * np.random.randn(n, n)) / np.sqrt(2.0)
        Q, _ = np.linalg.qr(X)

        t0 = time.perf_counter()
        mesh = ClementsMZIMesh.decompose_unitary(Q)
        decomp_ms = (time.perf_counter() - t0) * 1000.0

        fidelity = mesh.compute_fidelity(Q)
        num_mzis = len(mesh.elements)

        print(f"  [+] Mode Dimension N={n:2d} | MZIs={num_mzis:3d} | Decomp Time: {decomp_ms:6.2f} ms | Fidelity: {fidelity:.8f}")
        assert fidelity > 0.9999, f"Fidelity error on N={n}"

    # Optical propagation latency
    sim = PhotonicSimulator()
    e_in = np.ones(16, dtype=np.complex128) / 4.0
    t0 = time.perf_counter()
    for _ in range(500):
        _ = sim.propagate_field(mesh, e_in, apply_noise=False)
    sim_ms = ((time.perf_counter() - t0) / 500) * 1000.0
    print(f"\n  [+] Optical Propagation Latency (N=16): {sim_ms:.4f} ms per evaluation")

    assert sim_ms < 0.1, f"Propagation latency {sim_ms:.4f} ms exceeds SLA"
    print("  [✓] Photonic Clifford Accelerator SLA Benchmark: PASS")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
