r"""
DAXDA Level 3: DePIN Validator Network Engine.
Implements token staking, automated smart contract slashing for double-signing,
P2P gossip message routing, and cryptographic Merkle state receipts.
"""

from .staking_slashing import (
    SlashingInfraction,
    DePINValidatorNode,
    SlashingEvent,
    DePINStakingEngine,
)
from .p2p_gossip import (
    GossipMessage,
    P2PGossipNetwork,
)
from .receipt_verifier import (
    StateValidationReceipt,
    DePINReceiptVerifier,
)

__all__ = [
    "SlashingInfraction",
    "DePINValidatorNode",
    "SlashingEvent",
    "DePINStakingEngine",
    "GossipMessage",
    "P2PGossipNetwork",
    "StateValidationReceipt",
    "DePINReceiptVerifier",
]
