#!/usr/bin/env python3
"""
DAXDA Execution Evidence Chain & Runtime Contract (execution_evidence_chain.py)
==============================================================================
Implements the runtime contract C = (P, A, S, E) and deterministic cryptographic
receipt chaining for DAXDA V11.4 Validation Shell.

- Policy Constraints (P)
- Authority State (A)
- Allowed State Transitions (S)
- Required Execution Evidence (E)

Chaining Protocol:
  H_t = SHA256( H_{t-1} || CanonicalJSON(R_t) )
"""

from __future__ import annotations
import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


def canonical_json(data: Dict[str, Any]) -> str:
    """Produces deterministic, stably ordered UTF-8 JSON representation."""
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


@dataclass
class RuntimeContract:
    policy_version: str = "v11.4.2026.08"
    authority_scope: List[str] = field(default_factory=lambda: ["READ_LOCAL", "SIMULATED_TEST"])
    allowed_state_transitions: List[str] = field(default_factory=lambda: ["STATE_INIT", "STATE_TRANSITION", "STATE_COMPLETE"])
    required_evidence_type: str = "CRYPTOGRAPHIC_SHA256_CHAIN"

    def is_authorized(self, action: str, scope: str) -> bool:
        return scope in self.authority_scope and action in self.allowed_state_transitions


@dataclass
class EvidenceStepRecord:
    step_index: int
    request_hash: str
    policy_version: str
    authority_scope: str
    proposed_action: str
    precondition_state: str
    DAXDA_disposition: str
    external_gate_result: str
    actual_effect: str
    effect_evidence: str
    postcondition_state: str
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    previous_receipt_hash: str = GENESIS_HASH
    receipt_hash: str = ""

    def compute_hash(self, prev_hash: str) -> str:
        d = asdict(self)
        d.pop("receipt_hash", None)
        d["previous_receipt_hash"] = prev_hash
        payload_str = prev_hash + canonical_json(d)
        return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()


class ExecutionEvidenceChain:
    def __init__(self, contract: Optional[RuntimeContract] = None):
        self.contract = contract or RuntimeContract()
        self.chain: List[EvidenceStepRecord] = []
        self.latest_hash: str = GENESIS_HASH

    def add_step(
        self,
        request_text: str,
        proposed_action: str,
        precondition_state: str,
        daxda_disposition: str,
        external_gate_result: str,
        actual_effect: str,
        effect_evidence: str,
        postcondition_state: str,
        scope: str = "SIMULATED_TEST",
    ) -> EvidenceStepRecord:
        req_hash = hashlib.sha256(request_text.encode("utf-8")).hexdigest()
        step_idx = len(self.chain) + 1

        record = EvidenceStepRecord(
            step_index=step_idx,
            request_hash=req_hash,
            policy_version=self.contract.policy_version,
            authority_scope=scope,
            proposed_action=proposed_action,
            precondition_state=precondition_state,
            DAXDA_disposition=daxda_disposition,
            external_gate_result=external_gate_result,
            actual_effect=actual_effect,
            effect_evidence=effect_evidence,
            postcondition_state=postcondition_state,
            previous_receipt_hash=self.latest_hash,
        )

        record.receipt_hash = record.compute_hash(self.latest_hash)
        self.latest_hash = record.receipt_hash
        self.chain.append(record)
        return record

    def verify_chain(self) -> bool:
        """Verifies full cryptographic chain integrity from Genesis."""
        prev = GENESIS_HASH
        for rec in self.chain:
            if rec.previous_receipt_hash != prev:
                return False
            expected_hash = rec.compute_hash(prev)
            if rec.receipt_hash != expected_hash:
                return False
            prev = rec.receipt_hash
        return True

    def export_ledger(self) -> List[Dict[str, Any]]:
        return [asdict(r) for r in self.chain]


if __name__ == "__main__":
    chain = ExecutionEvidenceChain()
    step1 = chain.add_step(
        request_text="Analyze Zeno's Paradox",
        proposed_action="STATE_TRANSITION",
        precondition_state="STATE_INIT",
        daxda_disposition="PASS",
        external_gate_result="AUTHORIZED",
        actual_effect="EVALUATE_CL70",
        effect_evidence="SUB_FEMTOMETER_RESIDUAL_9.51E-16",
        postcondition_state="STATE_COMPLETE",
    )
    print(f"Added Step 1 | Hash: {step1.receipt_hash}")
    print(f"Chain Verified: {chain.verify_chain()}")
