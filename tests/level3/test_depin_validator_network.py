r"""
Tests for DePIN Validator Network Engine.
Verifies token staking, automated slashing for double-signing,
P2P epidemic gossip message propagation, and Merkle state receipts.
"""

import pytest

from daxda_engine.level3.depin_validator_network import (
    SlashingInfraction,
    DePINValidatorNode,
    SlashingEvent,
    DePINStakingEngine,
    GossipMessage,
    P2PGossipNetwork,
    StateValidationReceipt,
    DePINReceiptVerifier,
)


def test_validator_registration_and_staking():
    r"""Verify staking threshold enforcement and node registration."""
    staking = DePINStakingEngine(min_stake_threshold=1000.0)

    # Below minimum threshold should raise ValueError
    with pytest.raises(ValueError):
        staking.register_validator("val-under", "pubkey1", initial_stake=500.0)

    node = staking.register_validator("val-1", "pubkey1", initial_stake=5000.0)
    assert node.validator_id == "val-1"
    assert node.staked_tokens == 5000.0
    assert node.is_jailed is False
    assert node.is_slashed is False


def test_double_signing_automatic_100_percent_slashing():
    r"""Verify equivocation (double-signing at same height) triggers 100% slash and jail."""
    staking = DePINStakingEngine(min_stake_threshold=1000.0)
    staking.register_validator("val-byzantine", "pubkey-byz", initial_stake=10000.0)

    # First block proposal at height 100
    slash1 = staking.record_block_proposal("val-byzantine", height=100, block_hash="hash_alpha")
    assert slash1 is None

    # Equivocation: second different block proposal at height 100 by same validator
    slash2 = staking.record_block_proposal("val-byzantine", height=100, block_hash="hash_beta_fork")

    assert slash2 is not None
    assert slash2.infraction == SlashingInfraction.DOUBLE_SIGNING
    assert slash2.slashed_tokens == 10000.0
    assert slash2.remaining_tokens == 0.0
    assert slash2.is_jailed is True

    node = staking.validators["val-byzantine"]
    assert node.is_jailed is True
    assert node.is_slashed is True
    assert node.staked_tokens == 0.0


def test_invalid_state_proof_20_percent_slashing():
    r"""Verify submitting invalid state execution proof slashes 20% of stake."""
    staking = DePINStakingEngine(min_stake_threshold=1000.0)
    staking.register_validator("val-faulty", "pubkey-fault", initial_stake=10000.0)

    slash = staking.slash_validator(
        validator_id="val-faulty",
        infraction=SlashingInfraction.INVALID_STATE_PROOF,
        evidence_hash="fake_merkle_root_proof",
    )

    assert slash.slashed_tokens == 2000.0  # 20%
    assert slash.remaining_tokens == 8000.0
    assert slash.is_jailed is True


def test_p2p_gossip_dissemination():
    r"""Verify epidemic gossip spreads messages across P2P network peers."""
    p2p = P2PGossipNetwork(fanout=3)

    for i in range(5):
        p2p.add_node(f"node-{i}")

    # Connect in ring topology
    for i in range(5):
        p2p.connect_peers(f"node-{i}", f"node-{(i + 1) % 5}")

    msg, delivered = p2p.broadcast_message(
        origin_node_id="node-0",
        topic="consensus_proposals",
        payload="block_proposal_epoch_99",
    )

    assert delivered == 5  # All 5 nodes received message
    assert p2p.peer_scores["node-0"] > 50.0  # Reputation increased for forwarding


def test_cryptographic_state_receipt_verification():
    r"""Verify SHA-256 Merkle root calculation and receipt signature validation."""
    txs = ["tx_transfer_100_tokens", "tx_update_policy_alpha", "tx_burn_gas_50"]
    state_post = "state_hash_0x8899aabbcc"

    receipt = DePINReceiptVerifier.generate_receipt(
        validator_id="validator-prime",
        block_height=500,
        transactions=txs,
        state_post_hash=state_post,
    )

    assert receipt.is_valid_receipt is True
    assert len(receipt.merkle_root) == 64  # SHA-256 hex string

    # Verification with identical transactions
    is_valid = DePINReceiptVerifier.verify_receipt(receipt, txs)
    assert is_valid is True

    # Verification with tampered transaction must fail
    tampered_txs = ["tx_transfer_100_tokens", "tx_FRAUD_TRANSFER_1000000", "tx_burn_gas_50"]
    is_fraud_valid = DePINReceiptVerifier.verify_receipt(receipt, tampered_txs)
    assert is_fraud_valid is False
