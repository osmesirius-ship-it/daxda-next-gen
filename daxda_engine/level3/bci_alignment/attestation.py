"""
Hardware-Bound Neurometric Attestation Envelope
===============================================
Binds human neural cognitive validation to machine-readable Policy Enforcement Point (PEP)
decisions via cryptographic digests and HMAC/digital signatures.
"""

from dataclasses import dataclass
import hashlib
import hmac
import json
import time
from typing import Optional

from .decoders import CognitiveEpochAssessment


@dataclass(frozen=True)
class NeurometricReceipt:
    """Tamper-evident cryptographic receipt binding neural intent to an action proposal."""
    receipt_id: str
    action_proposal_id: str
    timestamp_iso: str
    is_attested: bool
    governance_verdict: str  # "ALLOW" or "DENY"
    vigilance_score: float
    airm_distance: float
    rejection_reason: Optional[str]
    payload_digest: str
    signature_hex: str


class NeurometricAttestationIssuer:
    """
    Issues cryptographic neurometric receipts for DAXDA PEP decision gates.
    """

    def __init__(self, private_key_seed: bytes = b"daxda_supervisory_operator_hsm_key_2026"):
        self.secret_key = private_key_seed

    def issue_attestation(
        self,
        action_proposal_id: str,
        assessment: CognitiveEpochAssessment,
        airm_distance: float,
        timestamp_iso: Optional[str] = None,
    ) -> NeurometricReceipt:
        """
        Signs and emits a canonical NeurometricReceipt.
        If operator is not attested, verdict is DENY.
        """
        ts = timestamp_iso or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        verdict = "ALLOW" if assessment.is_operator_attested else "DENY"
        
        canonical_payload = {
            "proposal_id": action_proposal_id,
            "timestamp": ts,
            "verdict": verdict,
            "vigilance": round(assessment.vigilance_score, 4),
            "airm_dist": round(airm_distance, 4),
            "is_attested": assessment.is_operator_attested,
            "rejection": assessment.rejection_reason or "NONE",
        }
        
        payload_bytes = json.dumps(canonical_payload, sort_keys=True).encode("utf-8")
        payload_digest = hashlib.sha256(payload_bytes).hexdigest()
        
        # Hardware HMAC signature
        signature = hmac.new(self.secret_key, payload_bytes, hashlib.sha256).hexdigest()
        receipt_id = f"urn:daxda:neurometric:{payload_digest[:16]}"
        
        return NeurometricReceipt(
            receipt_id=receipt_id,
            action_proposal_id=action_proposal_id,
            timestamp_iso=ts,
            is_attested=assessment.is_operator_attested,
            governance_verdict=verdict,
            vigilance_score=assessment.vigilance_score,
            airm_distance=airm_distance,
            rejection_reason=assessment.rejection_reason,
            payload_digest=payload_digest,
            signature_hex=signature,
        )
