r"""
DePIN Validator Staking, Slashing, and Reputation Engine.
Enforces economic security for physical validator nodes with automated slashing
for equivocation (double-signing) and invalid state execution proofs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import hashlib


class SlashingInfraction(str, Enum):
    DOUBLE_SIGNING = "DOUBLE_SIGNING"           # 100% slash and permanent jail
    INVALID_STATE_PROOF = "INVALID_STATE_PROOF" # 20% slash
    UNRESPONSIVE_DOWNTIME = "UNRESPONSIVE"     # 1% slash and temporary jail


@dataclass
class DePINValidatorNode:
    """Represents an active validator in the physical DePIN network."""
    validator_id: str
    public_key: str
    staked_tokens: float
    reputation_score: float = 1.0  # In [0.0, 1.0]
    is_jailed: bool = False
    is_slashed: bool = False
    slashed_amount: float = 0.0


@dataclass(frozen=True)
class SlashingEvent:
    """Record of an automated slashing action."""
    validator_id: str
    infraction: SlashingInfraction
    slashed_tokens: float
    remaining_tokens: float
    is_jailed: bool
    evidence_hash: str


class DePINStakingEngine:
    r"""
    Manages token staking and automated smart slashing rules.
    """

    SLASHING_PENALTIES: Dict[SlashingInfraction, float] = {
        SlashingInfraction.DOUBLE_SIGNING: 1.00,        # 100% penalty
        SlashingInfraction.INVALID_STATE_PROOF: 0.20,   # 20% penalty
        SlashingInfraction.UNRESPONSIVE_DOWNTIME: 0.01, # 1% penalty
    }

    def __init__(self, min_stake_threshold: float = 1000.0):
        self.min_stake = min_stake_threshold
        self.validators: Dict[str, DePINValidatorNode] = {}
        self.signed_blocks: Dict[Tuple[str, int], str] = {}  # (validator_id, height) -> block_hash
        self.slashing_history: List[SlashingEvent] = []

    def register_validator(
        self,
        validator_id: str,
        public_key: str,
        initial_stake: float,
    ) -> DePINValidatorNode:
        """Registers and stakes tokens for a new validator node."""
        if initial_stake < self.min_stake:
            raise ValueError(f"Stake {initial_stake} below minimum threshold {self.min_stake}")
        if validator_id in self.validators:
            raise ValueError(f"Validator {validator_id} already registered")

        node = DePINValidatorNode(
            validator_id=validator_id,
            public_key=public_key,
            staked_tokens=initial_stake,
        )
        self.validators[validator_id] = node
        return node

    def record_block_proposal(
        self,
        validator_id: str,
        height: int,
        block_hash: str,
    ) -> Optional[SlashingEvent]:
        """
        Records a signed block proposal. Detects equivocation (double-signing)
        if validator signed two different hashes at the same height.
        """
        node = self.validators.get(validator_id)
        if not node:
            raise KeyError(f"Unknown validator {validator_id}")

        key = (validator_id, height)
        if key in self.signed_blocks:
            prev_hash = self.signed_blocks[key]
            if prev_hash != block_hash:
                # Double signing detected! Immediate 100% slash
                evidence = hashlib.sha256(f"{prev_hash}:{block_hash}".encode()).hexdigest()
                return self.slash_validator(
                    validator_id=validator_id,
                    infraction=SlashingInfraction.DOUBLE_SIGNING,
                    evidence_hash=evidence,
                )
        else:
            self.signed_blocks[key] = block_hash

        return None

    def slash_validator(
        self,
        validator_id: str,
        infraction: SlashingInfraction,
        evidence_hash: str,
    ) -> SlashingEvent:
        """Executes smart slashing penalty on a misbehaving validator."""
        node = self.validators[validator_id]
        fraction = self.SLASHING_PENALTIES[infraction]
        penalty = node.staked_tokens * fraction

        node.staked_tokens -= penalty
        node.slashed_amount += penalty
        node.is_slashed = True
        node.reputation_score = max(0.0, node.reputation_score - fraction)

        if infraction in (SlashingInfraction.DOUBLE_SIGNING, SlashingInfraction.INVALID_STATE_PROOF):
            node.is_jailed = True

        event = SlashingEvent(
            validator_id=validator_id,
            infraction=infraction,
            slashed_tokens=penalty,
            remaining_tokens=node.staked_tokens,
            is_jailed=node.is_jailed,
            evidence_hash=evidence_hash,
        )
        self.slashing_history.append(event)
        return event
