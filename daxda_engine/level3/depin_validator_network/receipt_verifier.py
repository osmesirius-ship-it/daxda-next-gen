r"""
Cryptographic State Validation Receipt and Merkle Verification Engine.
Builds SHA-256 Merkle trees over physical validator transaction execution,
producing verifiable execution receipts for the DePIN network.
"""

from dataclasses import dataclass
from typing import List, Optional
import hashlib
import json


@dataclass(frozen=True)
class StateValidationReceipt:
    """Cryptographically verifiable execution receipt from a physical validator."""
    receipt_id: str
    validator_id: str
    block_height: int
    merkle_root: str
    state_post_hash: str
    signature: str
    transaction_count: int
    is_valid_receipt: bool


class DePINReceiptVerifier:
    r"""
    Verifies cryptographic integrity of DePIN execution receipts.
    """

    @staticmethod
    def compute_merkle_root(leaf_hashes: List[str]) -> str:
        """Computes balanced binary SHA-256 Merkle root from leaf transaction hashes."""
        if not leaf_hashes:
            return hashlib.sha256(b"EMPTY_MERKLE_TREE").hexdigest()

        current_level = list(leaf_hashes)
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = f"{left}:{right}".encode()
                next_level.append(hashlib.sha256(combined).hexdigest())
            current_level = next_level

        return current_level[0]

    @classmethod
    def generate_receipt(
        cls,
        validator_id: str,
        block_height: int,
        transactions: List[str],
        state_post_hash: str,
        private_signing_key: str = "priv_key_daxda_demo",
    ) -> StateValidationReceipt:
        """Generates a signed state validation receipt."""
        leaf_hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
        merkle_root = cls.compute_merkle_root(leaf_hashes)

        payload = f"{validator_id}:{block_height}:{merkle_root}:{state_post_hash}"
        receipt_id = hashlib.sha256(payload.encode()).hexdigest()

        # Deterministic HMAC-like signature
        sig = hashlib.sha256(f"{payload}:{private_signing_key}".encode()).hexdigest()

        return StateValidationReceipt(
            receipt_id=receipt_id,
            validator_id=validator_id,
            block_height=block_height,
            merkle_root=merkle_root,
            state_post_hash=state_post_hash,
            signature=sig,
            transaction_count=len(transactions),
            is_valid_receipt=True,
        )

    @classmethod
    def verify_receipt(
        cls,
        receipt: StateValidationReceipt,
        transactions: List[str],
        private_signing_key: str = "priv_key_daxda_demo",
    ) -> bool:
        """Verifies Merkle root and cryptographic signature of receipt."""
        leaf_hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
        expected_root = cls.compute_merkle_root(leaf_hashes)

        if expected_root != receipt.merkle_root:
            return False

        payload = f"{receipt.validator_id}:{receipt.block_height}:{receipt.merkle_root}:{receipt.state_post_hash}"
        expected_sig = hashlib.sha256(f"{payload}:{private_signing_key}".encode()).hexdigest()

        return bool(expected_sig == receipt.signature)
