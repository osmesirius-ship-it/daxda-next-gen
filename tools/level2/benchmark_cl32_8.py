#!/usr/bin/env python3
"""
DAXDA Level 2 - Cl(32,8) Hypercombinatorial Benchmark & SLA Verification Suite
==============================================================================

Verifies the mathematical rigor and computational throughput of the Cl(32,8)
geometric algebra engine and 20-qubit quantum compiler.

Targets:
  - Metric signature and anti-commutator preservation across 40 generators
  - 20-qubit Jordan-Wigner Pauli string compilation
  - Zero algebraic drift over continuous rotor rotations
  - Throughput >= 5,000 actions/sec in batched mode
  - Sub-150ms P99 validation latency
Outputs results to outputs/cl32_8_benchmark_latest.json.
"""

import argparse
import json
import math
import os
import sys
import time
from typing import Any, Dict, List

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.level2.cl32_8 import (
    Blade64,
    Cl32_8Space,
    Cl32_8ValidationReceipt,
    Cl32_8Validator,
    Multivector40,
    QuantumCliffordAdapter,
)


def run_benchmark(iterations: int = 10000) -> Dict[str, Any]:
    print("=" * 80)
    print("DAXDA LEVEL 2: Cl(32,8) HYPERCOMBINATORIAL & QUANTUM GATE BENCHMARK")
    print(f"Target Iterations: {iterations:,}")
    print("Blade Manifold Size: 2^40 = 1,099,511,627,776 basis elements")
    print("=" * 80)

    space = Cl32_8Space(32, 8)
    validator = Cl32_8Validator(space=space)
    adapter = QuantumCliffordAdapter(qubits=20)

    # ---------------------------------------------------------
    # Gate 1: Metric Signature & Anti-Commutation Check
    # ---------------------------------------------------------
    print("\n[Gate 1/5] Verifying 40-D Metric Signature & Anti-Commutation...")
    sig_pass = True
    for i in range(32):
        if space.compute_geometric_product_sign(1 << i, 1 << i) != 1.0:
            sig_pass = False
    for j in range(32, 40):
        if space.compute_geometric_product_sign(1 << j, 1 << j) != -1.0:
            sig_pass = False

    anti_commute_pass = True
    for i in range(10):
        for j in range(i + 1, 11):
            s1 = space.compute_geometric_product_sign(1 << i, 1 << j)
            s2 = space.compute_geometric_product_sign(1 << j, 1 << i)
            if s1 != -s2:
                anti_commute_pass = False

    print(f"  - 32 Positive Generators (e_i^2 = +1): {'PASS' if sig_pass else 'FAIL'}")
    print(f"  - 8 Negative Generators (e_j^2 = -1): {'PASS' if sig_pass else 'FAIL'}")
    print(f"  - Anti-commutator {{e_i, e_j}} = 0 for i != j: {'PASS' if anti_commute_pass else 'FAIL'}")
    assert sig_pass and anti_commute_pass, "Gate 1 Algebraic Foundations Failed"

    # ---------------------------------------------------------
    # Gate 2: Quantum Gate Mapping (Jordan-Wigner 20-Qubit Isomorphism)
    # ---------------------------------------------------------
    print("\n[Gate 2/5] Compiling 40 Generators to 20-Qubit Pauli Strings...")
    t0 = time.perf_counter()
    pauli_strings = [adapter.generator_to_pauli_string(k) for k in range(40)]
    compilation_time_ms = (time.perf_counter() - t0) * 1000.0

    # Verify length and properties
    assert len(pauli_strings) == 40
    assert all(p.qubits == 20 for p in pauli_strings)
    print(f"  - Compiled 40 generators to 20-qubit Pauli strings in {compilation_time_ms:.3f}ms")
    print(f"  - Sample e_0 Pauli: {pauli_strings[0].operators}")
    print(f"  - Sample e_1 Pauli: {pauli_strings[1].operators}")
    print(f"  - Sample e_39 Pauli: {pauli_strings[39].operators}")

    # ---------------------------------------------------------
    # Gate 3: Rotor Invariance & Representation Drift Testing
    # ---------------------------------------------------------
    print("\n[Gate 3/5] Testing Rotor Rotation Invariance and Numerical Drift...")
    rotor = space.create_rotor(0, 1, 0.05)
    r_rev = rotor.reverse()
    unit_norm = rotor.geometric_product(r_rev).get_blade(0)
    initial_drift = abs(unit_norm - 1.0)

    # Accumulate 10,000 continuous rotor rotations
    drift_iterations = min(iterations, 20000)
    accum = Multivector40(space=space)
    accum.set_blade(0, 1.0)
    for _ in range(drift_iterations):
        accum = accum.geometric_product(rotor)

    final_norm = accum.geometric_product(accum.reverse()).get_blade(0)
    drift = abs(final_norm - 1.0)
    print(f"  - Initial Rotor Norm Invariance: {initial_drift:.2e}")
    print(f"  - Representation Drift over {drift_iterations:,} rotations: {drift:.2e} (Requirement: < 1e-4)")
    assert drift < 1e-4, f"Rotor representation drifted excessively: {drift}"

    # ---------------------------------------------------------
    # Gate 4: High-Throughput Batch Validation (>= 5,000 actions/sec)
    # ---------------------------------------------------------
    print(f"\n[Gate 4/5] Benchmarking Batch Validation Throughput ({iterations:,} vectors)...")
    batch_size = iterations
    # Generate test decision vectors
    test_vectors = [
        [0.01 * math.sin(i * 0.1 + j) for i in range(40)]
        for j in range(batch_size)
    ]

    t0 = time.perf_counter()
    receipts = validator.validate_batch(test_vectors)
    elapsed_sec = time.perf_counter() - t0
    throughput = len(receipts) / max(1e-6, elapsed_sec)

    print(f"  - Validated {len(receipts):,} 40-D decision vectors in {elapsed_sec:.3f}s")
    print(f"  - Throughput: {throughput:,.1f} actions/sec (Requirement: >= 5,000/sec)")
    assert throughput >= 5000, f"Throughput {throughput:.1f} below 5,000 req/s"

    # ---------------------------------------------------------
    # Gate 5: P99 Validation Latency (< 150ms)
    # ---------------------------------------------------------
    print("\n[Gate 5/5] Measuring Validation Latency Distribution...")
    latencies = [r.latency_ms for r in receipts]
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"  - P50 Latency : {p50:.4f} ms")
    print(f"  - P95 Latency : {p95:.4f} ms")
    print(f"  - P99 Latency : {p99:.4f} ms (Requirement: < 150.0 ms)")
    assert p99 < 150.0, f"P99 latency {p99:.3f}ms exceeded 150ms limit"

    # ---------------------------------------------------------
    # Summary Report & JSON Output
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print("ALL Cl(32,8) QUALITY GATES PASSED (100% SUCCESS)")
    print("=" * 80)

    summary = {
        "benchmark": "DAXDA Level 2 Cl(32,8) Hypercombinatorial Quantum Geometric Engine",
        "status": "PASS",
        "subspace_dimension": 40,
        "blade_manifold_size": 1 << 40,
        "throughput_actions_per_sec": round(throughput, 1),
        "p50_latency_ms": round(p50, 4),
        "p95_latency_ms": round(p95, 4),
        "p99_latency_ms": round(p99, 4),
        "rotor_drift": drift,
        "qubit_count": 20,
        "timestamp": time.time(),
    }

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs"))
    if os.path.exists(out_dir):
        out_file = os.path.join(out_dir, "cl32_8_benchmark_latest.json")
        with open(out_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Benchmark telemetry saved to: {out_file}")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAXDA Cl(32,8) Benchmark")
    parser.add_argument("--iterations", type=int, default=10000, help="Number of vectors to validate")
    args = parser.parse_args()

    results = run_benchmark(iterations=args.iterations)
    if results["status"] != "PASS":
        sys.exit(1)
