#!/usr/bin/env python3
"""Activate the DAXDA DePIN validator network locally for synthetic validation."""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from daxda_engine.level3.depin_validator_network import (
    DePINStakingEngine,
    P2PGossipNetwork,
    DePINReceiptVerifier,
)


def main() -> int:
    print("[1/4] Initializing DePIN staking engine...")
    staking = DePINStakingEngine(min_stake_threshold=1000.0)

    validators = [
        ("node-alpha", "pub-alpha", 5000.0),
        ("node-beta", "pub-beta", 5500.0),
        ("node-gamma", "pub-gamma", 6000.0),
        ("node-delta", "pub-delta", 7000.0),
    ]

    for validator_id, public_key, stake in validators:
        staking.register_validator(validator_id, public_key, initial_stake=stake)

    print("[2/4] Registering validators and checking consensus state...")
    for vid, _, _ in validators:
        staking.record_block_proposal(vid, height=100, block_hash=f"hash-{vid}-block-a")
        staking.record_block_proposal(vid, height=101, block_hash=f"hash-{vid}-block-b")

    print("[3/4] Activating P2P gossip network...")
    p2p = P2PGossipNetwork(fanout=3)
    for i in range(6):
        p2p.add_node(f"peer-{i}")
    for i in range(6):
        p2p.connect_peers(f"peer-{i}", f"peer-{(i + 1) % 6}")

    _, delivered = p2p.broadcast_message(
        origin_node_id="peer-0",
        topic="consensus_proposals",
        payload="daxda-depin-activation",
    )

    print("[4/4] Verifying cryptographic execution receipts...")
    txs = [
        "tx_transfer_100_tokens",
        "tx_update_policy_alpha",
        "tx_burn_gas_50",
    ]
    receipt = DePINReceiptVerifier.generate_receipt(
        validator_id="node-alpha",
        block_height=500,
        transactions=txs,
        state_post_hash="state_hash_0x8899aabbcc",
    )
    verified = DePINReceiptVerifier.verify_receipt(receipt, txs)

    print("DePIN STATUS: ACTIVE")
    print(f"Validators: {len(staking.validators)}")
    print(f"Network delivery count: {delivered}")
    print(f"Receipt valid: {verified}")
    print(f"Total staked tokens: {sum(v.staked_tokens for v in staking.validators.values()):.2f}")
    print(f"Latest slashing events: {len(staking.slashing_history)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
