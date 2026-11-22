#!/usr/bin/env python3
"""
DAXDA Next-Gen — DePIN Validator Network CLI & Cluster Runner
=============================================================
Deploys, monitors, and runs the Decentralized Physical Infrastructure (DePIN)
Validator Network with P2P epidemic gossip, Merkle receipts, and automated slashing.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from daxda_engine.level3.depin_validator_network import (
    DePINClusterManager,
    get_depin_cluster,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("daxda.depin_cli")


def print_depin_summary(cluster: DePINClusterManager):
    """Renders formatted CLI dashboard for the DePIN network."""
    t = cluster.get_telemetry()
    print("\n" + "=" * 80)
    print(" 🌐 DAXDA DECENTRALIZED PHYSICAL INFRASTRUCTURE NETWORK (DePIN)")
    print(" Consensus: Proof-of-Execution | P2P Epidemic Mesh | Merkle State Receipts")
    print("=" * 80)
    print(f"  Network Status           : 🟢 {t['depin_status']}")
    print(f"  Protocol Version         : {t['protocol_version']}")
    print(f"  Current Block Height     : {t['current_block_height']}")
    print(f"  Blocks Sealed            : {t['total_blocks_sealed']}")
    print(f"  Transactions Verified    : {t['total_transactions_verified']}")
    print(f"  Active Validator Nodes   : {t['active_validator_nodes']} / {t['total_network_nodes']}")
    print(f"  Jailed / Slashed Nodes   : ⚠️  {t['jailed_validator_nodes']} Jailed | 🚨 {t['slashed_validator_nodes']} Slashed")
    print(f"  Total Network Stake      : {t['total_network_stake_dax']:,.2f} DAX Tokens")
    print(f"  Slashing Invariant Events: {t['slashing_events_count']}")
    print(f"  Latest Merkle Root       : {t['latest_merkle_root'][:32]}...")
    print("-" * 80)

    print("  ACTIVE VALIDATOR FLEET SAMPLE:")
    print("  " + f"{'Validator Node ID':<28} {'Region':<16} {'Hardware':<24} {'Stake (DAX)':<12} {'Status'}")
    print("  " + "-" * 88)
    for v in t["recent_validators"][:8]:
        status_str = "🚨 SLASHED" if v["is_slashed"] else ("⚠️ JAILED" if v["is_jailed"] else "✅ ACTIVE")
        print(f"  {v['validator_id']:<28} {v['region']:<16} {v['hardware']:<24} {v['staked_tokens']:<12.1f} {status_str}")

    if t["recent_slashing_history"]:
        print("-" * 80)
        print("  RECENT AUTOMATED SLASHING RECEIPTS:")
        for s in t["recent_slashing_history"]:
            print(f"  ⚡ Node: {s['validator_id']} | Infraction: {s['infraction']} | Slashed: {s['slashed_tokens']:.1f} DAX | Jailed: {s['is_jailed']}")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="DAXDA DePIN Validator Cluster Runner")
    parser.add_argument("--nodes", type=int, default=50, help="Total nodes in validator mesh")
    parser.add_argument("--rounds", type=int, default=10, help="Number of block validation rounds to execute")
    parser.add_argument("--byzantine-round", type=int, default=3, help="Round in which to inject Byzantine double-signing")
    parser.add_argument("--continuous", action="store_true", help="Run continuous block production loop")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between rounds in seconds")
    args = parser.parse_args()

    cluster = DePINClusterManager(node_count=args.nodes)

    if args.continuous:
        logger.info(f"Starting continuous DePIN block validation loop (interval={args.interval}s)...")
        try:
            r = 0
            while True:
                r += 1
                fault = "DOUBLE_SIGNING" if (r == args.byzantine_round) else None
                summary = cluster.execute_validation_round(simulate_byzantine_fault=fault)
                print(f"Block #{summary['block_height']} sealed by {summary['proposer_id']} | Merkle: {summary['merkle_root'][:16]}... | Mesh Coverage: {summary['p2p_mesh_coverage_pct']}%")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("DePIN continuous loop terminated by user.")
    else:
        logger.info(f"Executing {args.rounds} validation rounds on DePIN cluster...")
        for r in range(1, args.rounds + 1):
            fault = "DOUBLE_SIGNING" if (r == args.byzantine_round) else None
            summary = cluster.execute_validation_round(simulate_byzantine_fault=fault)
            verif_icon = "✅" if summary["is_cryptographically_verified"] else "❌"
            print(f"[{r}/{args.rounds}] Block #{summary['block_height']:03d} Proposer: {summary['proposer_id']:<26} Merkle: {summary['merkle_root'][:16]}... {verif_icon} Mesh: {summary['p2p_mesh_coverage_pct']}%")

    print_depin_summary(cluster)


if __name__ == "__main__":
    main()
