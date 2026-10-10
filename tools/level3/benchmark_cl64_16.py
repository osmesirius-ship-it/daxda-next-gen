#!/usr/bin/env python3
"""
DAXDA Level 3 Domain 1 SLA Benchmark: Cl(64,16) Hypercombinatorial Engine
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.level3.cl64_16 import Cl64_16Multivector, SpinorManifoldDetector


def run_benchmark():
    print("=" * 80)
    print("  BENCHMARK: Cl(64,16) Sparse Hypermanifold Geometric Algebra Engine")
    print("=" * 80)

    # 1. Basis products
    t0 = time.perf_counter()
    ops = 10000
    for i in range(1, 80):
        e_i = Cl64_16Multivector.basis_vector(i)
        e_j = Cl64_16Multivector.basis_vector(i + 1)
        _ = e_i * e_j
    t_basis = time.perf_counter() - t0
    print(f"  [+] Basis blade product throughput: {79 / t_basis:,.1f} products/sec")

    # 2. Sparse multivector multiplication (100 terms x 100 terms)
    m1_dict = {1 << i: float(i % 5 + 1) for i in range(25)}
    m2_dict = {1 << (i + 10): float(i % 3 + 1) for i in range(25)}
    A = Cl64_16Multivector(m1_dict)
    B = Cl64_16Multivector(m2_dict)

    t0 = time.perf_counter()
    for _ in range(200):
        C = A * B
    elapsed = time.perf_counter() - t0
    per_op_ms = (elapsed / 200) * 1000.0
    print(f"  [+] Sparse 25-blade x 25-blade geometric product latency: {per_op_ms:.4f} ms")
    print(f"  [+] Resulting blade terms: {len(C.blades)}")

    # 3. Spinor triality drift
    e1 = Cl64_16Multivector.basis_vector(1)
    e2 = Cl64_16Multivector.basis_vector(2)
    biv = e1 * e2
    res = SpinorManifoldDetector.verify_triality_closure(e1, e2, biv, theta=0.1)
    print(f"  [+] Spinor norm drift: {res['spinor_drift']:.2e}")
    print(f"  [+] Metric conservation error: {res['metric_conservation_error']:.2e}")

    # SLA check (< 1.0 ms)
    assert per_op_ms < 1.0, f"SLA Breach: latency {per_op_ms:.4f} ms exceeds 1.0 ms"
    print("\n  [✓] Cl(64,16) Hypermanifold SLA Benchmark: PASS")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
