#!/usr/bin/env python3
"""
DAXDA Level 3 Domain 1 SLA Benchmark: Quantum Error-Correction Suite
"""

import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.level3.quantum_error_correction import (
    MagicStateDistillation,
    PauliOperator,
    SteaneCode,
    SurfaceCode,
    SyndromeDecoder,
)


def run_benchmark():
    print("=" * 80)
    print("  BENCHMARK: Fault-Tolerant Quantum Error-Corrected Clifford Suite")
    print("=" * 80)

    # 1. Steane Code Decoding Latency
    code = SteaneCode.get_code()
    errors = [
        PauliOperator.from_string("XIIIIII"),
        PauliOperator.from_string("IZIIIII"),
        PauliOperator.from_string("IIYIIII"),
        PauliOperator.from_string("IIIXIII"),
        PauliOperator.from_string("IIIIZII"),
    ]

    t0 = time.perf_counter()
    n_runs = 500
    for _ in range(n_runs):
        for err in errors:
            corr, success = SyndromeDecoder.correct_error(code, err)
            assert success is True
    elapsed = time.perf_counter() - t0
    per_decode_us = (elapsed / (n_runs * len(errors))) * 1e6

    print(f"  [+] Steane [[7,1,3]] Syndrome Extraction & Decode Latency: {per_decode_us:.2f} us")
    assert per_decode_us < 100.0, f"Decoding latency {per_decode_us:.2f} us exceeds 100 us SLA"

    # 2. Magic State Distillation Scaling
    print("\n  [+] Magic State Distillation Error Scaling:")
    for p_in in [0.10, 0.05, 0.01, 0.001]:
        res = MagicStateDistillation.distill_magic_state(p_in)
        print(f"      p_in = {p_in:6.4f} -> p_out = {res['output_error_rate']:10.3e} | Suppression: {res['suppression_factor']:8.1f}x")

    print("\n  [✓] Quantum Error Correction SLA Benchmark: PASS")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
