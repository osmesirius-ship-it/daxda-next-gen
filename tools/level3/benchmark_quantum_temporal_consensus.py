#!/usr/bin/env python3
"""
Benchmark Runner: Quantum Temporal Consensus Engine (Domain 2).
Measures execution latency and numerical precision across 64-branch Novikov fixed point loops,
Mermin-Peres pseudo-telepathy games, and Bell-CHSH Tsirelson bound verification.
"""

import time
import math
import numpy as np

from daxda_engine.level3.quantum_temporal_consensus import (
    GHZStateRouter,
    MerminPseudoTelepathyEngine,
    NovikovCausalLoopHarmonizer,
    ByzantineEntanglementFilter,
    QuantumTemporalConsensusEngine,
    TSIRELSON_BOUND,
)


def run_benchmark():
    print("=" * 70)
    print("DAXDA Level 3: Quantum Temporal Consensus Engine Benchmark")
    print("=" * 70)

    # 1. GHZ State Router
    t0 = time.perf_counter()
    router = GHZStateRouter(num_qubits=3)
    purity, entropy = router.reduced_density_matrix_and_entropy(target_qubits=[0])
    t_ghz = (time.perf_counter() - t0) * 1000.0
    print(f"[1/4] GHZ State Router: {t_ghz:.3f} ms | Purity: {purity:.4f} | Entropy: {entropy:.4f} nats")

    # 2. Mermin Pseudo-Telepathy Game (500 rounds)
    t0 = time.perf_counter()
    game_engine = MerminPseudoTelepathyEngine()
    suite_res = game_engine.benchmark_game_suite(rounds_per_query=250, seed=42)
    t_game = (time.perf_counter() - t0) * 1000.0
    print(f"[2/4] Mermin Game Suite (1000 rounds): {t_game:.3f} ms | Win Rate: {suite_res['quantum_win_rate'] * 100:.1f}%")

    # 3. 64-Branch Novikov Causal Loop Harmonizer
    t0 = time.perf_counter()
    harmonizer = NovikovCausalLoopHarmonizer(num_branches=64)
    results = harmonizer.harmonize_all_64_branches()
    t_novikov = (time.perf_counter() - t0) * 1000.0
    avg_iters = np.mean([r.iterations for r in results])
    max_err = np.max([r.final_frobenius_error for r in results])
    print(f"[3/4] Novikov 64-Branch Solver: {t_novikov:.3f} ms | Avg Iters: {avg_iters:.1f} | Max Error: {max_err:.2e}")

    # 4. End-to-End Quantum Temporal Consensus Engine
    t0 = time.perf_counter()
    engine = QuantumTemporalConsensusEngine(num_branches=64, num_agents=3)
    outcome = engine.run_temporal_consensus_cycle(
        epoch=1,
        agent_ids=["alpha", "beta", "gamma"],
        sybil_candidates={"sybil-1": 1.95, "sybil-2": 2.10},
        game_rounds=50,
        seed=42,
    )
    t_e2e = (time.perf_counter() - t0) * 1000.0
    print(f"[4/4] End-to-End Consensus Cycle: {t_e2e:.3f} ms")
    print(f"      Status: {outcome.status} | Bell Parameter: {outcome.bell_parameter:.4f} / {TSIRELSON_BOUND:.4f}")
    print(f"      Sybil Nodes Isolated: {outcome.sybil_nodes_isolated}")
    print(f"      Consensus Receipt Hash: {outcome.consensus_receipt_hash[:16]}...")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
