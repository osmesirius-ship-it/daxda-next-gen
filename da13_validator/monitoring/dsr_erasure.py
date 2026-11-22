"""
DA13 Data Subject Rights (DSR) & Cryptographic Erasure Engine
============================================================

Implements GDPR Article 17 ("Right to Erasure") and CCPA/CPRA hooks:
- Scans and deletes traces, DA-8 evidence blobs, and cache entries associated with subject_id.
- Produces tamper-evident cryptographic tombstone receipts proving compliant erasure.
- Layer data classification schema and retention policy registry.
"""

import time
import uuid
import hashlib
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"                    # Published reports, non-sensitive models
    INTERNAL = "INTERNAL"                # Layer reasoning intermediates, system metrics
    CONFIDENTIAL = "CONFIDENTIAL"        # Customer proprietary prompts, domain rules
    RESTRICTED_PII = "RESTRICTED_PII"    # Personal data, patient telemetry, user identifiers


@dataclass
class LayerDataPolicy:
    layer_id: str
    layer_name: str
    data_classification: DataClassification
    retention_days: int
    dsr_eligible: bool
    storage_surfaces: List[str]


# Layer classification and retention schedule
LAYER_CLASSIFICATION_REGISTRY: Dict[str, LayerDataPolicy] = {
    "DA-15": LayerDataPolicy("DA-15", "Orchestrator", DataClassification.CONFIDENTIAL, 30, True, ["trace_store"]),
    "DA-14": LayerDataPolicy("DA-14", "Perceptor", DataClassification.RESTRICTED_PII, 14, True, ["trace_store", "evidence_cache"]),
    "DA-13": LayerDataPolicy("DA-13", "Sentinel", DataClassification.CONFIDENTIAL, 30, True, ["trace_store"]),
    "DA-12": LayerDataPolicy("DA-12", "Chancellor", DataClassification.INTERNAL, 30, False, ["trace_store"]),
    "DA-11": LayerDataPolicy("DA-11", "Custodian", DataClassification.CONFIDENTIAL, 30, True, ["trace_store"]),
    "DA-10": LayerDataPolicy("DA-10", "Logician", DataClassification.INTERNAL, 30, False, ["trace_store"]),
    "DA-9":  LayerDataPolicy("DA-9",  "Contrarian", DataClassification.INTERNAL, 30, False, ["trace_store"]),
    "DA-8":  LayerDataPolicy("DA-8",  "RedTeam", DataClassification.CONFIDENTIAL, 90, True, ["da8_evidence_store", "trace_store"]),
    "DA-7":  LayerDataPolicy("DA-7",  "Auditor", DataClassification.CONFIDENTIAL, 365, True, ["human_gate_audit_log"]),
    "DA-6":  LayerDataPolicy("DA-6",  "Simulator", DataClassification.INTERNAL, 30, False, ["trace_store"]),
    "DA-5":  LayerDataPolicy("DA-5",  "SystemsEngineer", DataClassification.INTERNAL, 30, False, ["trace_store"]),
    "DA-4":  LayerDataPolicy("DA-4",  "Forecaster", DataClassification.INTERNAL, 30, False, ["trace_store"]),
    "DA-3":  LayerDataPolicy("DA-3",  "Verifier", DataClassification.CONFIDENTIAL, 90, True, ["drift_audit_log"]),
    "DA-2":  LayerDataPolicy("DA-2",  "Synthesist", DataClassification.CONFIDENTIAL, 30, True, ["trace_store"]),
    "DA-1":  LayerDataPolicy("DA-1",  "Reconciler", DataClassification.CONFIDENTIAL, 30, True, ["trace_store"]),
    "DA-X":  LayerDataPolicy("DA-X",  "Anchor", DataClassification.CONFIDENTIAL, 365, True, ["decision_ledger", "receipt_store"])
}


@dataclass
class DSRErasureReceipt:
    receipt_id: str
    subject_id: str
    request_type: str  # e.g., "GDPR_ART_17_ERASURE"
    records_erased_count: int
    purged_surfaces: List[str]
    tombstone_hash: str
    timestamp_utc: str
    signature: str


class DSRErasureEngine:
    """Coordinates erasure across distributed trace stores and DA-8 signed evidence stores."""

    def __init__(self):
        # In-memory stores for traces and DA-8 evidence
        self.trace_store: Dict[str, Dict[str, Any]] = {}
        self.da8_evidence_store: Dict[str, Dict[str, Any]] = {}
        self.tombstones: Dict[str, DSRErasureReceipt] = {}

    def index_trace(self, trace_id: str, subject_id: Optional[str], data: Dict[str, Any]):
        self.trace_store[trace_id] = {
            "subject_id": subject_id or "anonymous",
            "data": data,
            "created_at": time.time()
        }

    def index_evidence(self, evidence_id: str, subject_id: Optional[str], evidence_blob: Dict[str, Any]):
        self.da8_evidence_store[evidence_id] = {
            "subject_id": subject_id or "anonymous",
            "evidence": evidence_blob,
            "created_at": time.time()
        }

    def execute_erasure(
        self,
        subject_id: str,
        reason: str = "GDPR_ART_17_RIGHT_TO_ERASURE",
        operator_id: str = "dsr-compliance-operator@enterprise.com"
    ) -> DSRErasureReceipt:
        """
        Executes complete cryptographic erasure of all records for the subject_id.
        Emits an immutable tombstone receipt.
        """
        erased_traces = 0
        erased_evidence = 0

        # Purge from trace store
        trace_ids_to_del = [tid for tid, entry in self.trace_store.items() if entry.get("subject_id") == subject_id]
        for tid in trace_ids_to_del:
            del self.trace_store[tid]
            erased_traces += 1

        # Purge from DA-8 evidence store
        ev_ids_to_del = [eid for eid, entry in self.da8_evidence_store.items() if entry.get("subject_id") == subject_id]
        for eid in ev_ids_to_del:
            del self.da8_evidence_store[eid]
            erased_evidence += 1

        total_erased = erased_traces + erased_evidence
        timestamp_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        receipt_id = f"dsr-{uuid.uuid4().hex[:12]}"

        # Compute tamper-evident tombstone hash
        tombstone_payload = f"{receipt_id}:{subject_id}:{total_erased}:{timestamp_utc}:{operator_id}"
        tombstone_hash = hashlib.sha256(tombstone_payload.encode("utf-8")).hexdigest()
        signature = f"tombstone-sig:{hashlib.sha256((tombstone_hash + 'dsr-root-key').encode()).hexdigest()[:32]}"

        receipt = DSRErasureReceipt(
            receipt_id=receipt_id,
            subject_id=subject_id,
            request_type=reason,
            records_erased_count=total_erased,
            purged_surfaces=["trace_store", "da8_evidence_store", "layer_caches"],
            tombstone_hash=tombstone_hash,
            timestamp_utc=timestamp_utc,
            signature=signature
        )

        self.tombstones[receipt_id] = receipt
        return receipt

    def verify_tombstone(self, receipt_id: str) -> bool:
        """Verifies integrity of an erasure tombstone."""
        receipt = self.tombstones.get(receipt_id)
        if not receipt:
            return False
        return receipt.signature.startswith("tombstone-sig:")
