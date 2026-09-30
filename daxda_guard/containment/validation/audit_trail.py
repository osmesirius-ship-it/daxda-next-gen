"""
Cryptographic Audit Trail & Lineage Ledger
==========================================

Maintains an immutable SHA-256 chained ledger of containment events and validation decisions.
"""

import time
import json
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AuditBlock:
    """An individual block in the cryptographic lineage chain."""
    index: int
    timestamp: float
    event_type: str
    agent_id: str
    action_details: Dict[str, Any]
    verdict: str
    prev_hash: str
    block_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "action_details": self.action_details,
            "verdict": self.verdict,
            "prev_hash": self.prev_hash,
            "block_hash": self.block_hash
        }


class ContainmentAuditTrail:
    """Tamper-evident append-only ledger for containment governance decisions."""

    def __init__(self):
        self.chain: List[AuditBlock] = []
        self._genesis()

    def _genesis(self):
        genesis = AuditBlock(
            index=0,
            timestamp=time.time(),
            event_type="GENESIS_CONTAINMENT_LOCK",
            agent_id="SYSTEM",
            action_details={"manifest": "DAXDA_ANOMALOUS_CONTAINMENT_WING_GENESIS"},
            verdict="INITIALIZED",
            prev_hash="0" * 64,
            block_hash=hashlib.sha256(b"DAXDA_CONTAINMENT_GENESIS_ROOT").hexdigest()
        )
        self.chain.append(genesis)

    def record_event(self, event_type: str, agent_id: str, action_details: Dict[str, Any], verdict: str) -> AuditBlock:
        """Appends a new verified event to the cryptographic ledger."""
        prev_block = self.chain[-1]
        now = time.time()
        idx = len(self.chain)

        payload = {
            "index": idx,
            "timestamp": now,
            "event_type": event_type,
            "agent_id": agent_id,
            "action_details": action_details,
            "verdict": verdict,
            "prev_hash": prev_block.block_hash
        }

        block_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

        block = AuditBlock(
            index=idx,
            timestamp=now,
            event_type=event_type,
            agent_id=agent_id,
            action_details=action_details,
            verdict=verdict,
            prev_hash=prev_block.block_hash,
            block_hash=block_hash
        )
        self.chain.append(block)
        return block

    def verify_chain_integrity(self) -> bool:
        """Verifies that every block in the ledger is cryptographically unbroken."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.prev_hash != prev.block_hash:
                return False

            payload = {
                "index": curr.index,
                "timestamp": curr.timestamp,
                "event_type": curr.event_type,
                "agent_id": curr.agent_id,
                "action_details": curr.action_details,
                "verdict": curr.verdict,
                "prev_hash": curr.prev_hash
            }
            expected_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
            if curr.block_hash != expected_hash:
                return False

        return True

    def export_ledger(self) -> List[Dict[str, Any]]:
        """Exports full ledger as list of dictionaries."""
        return [b.to_dict() for b in self.chain]
