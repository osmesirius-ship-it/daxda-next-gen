"""
DAXDA MMPIBench: Empirical Validation Certificate Generator
Produces cryptographically signed empirical validation certificates verifying
agent psychological profile integrity, Anthropic alignment, and penetration depth.
"""

from __future__ import annotations
import hmac
import hashlib
import json
import uuid
import time
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from daxda_engine.mmpibench.mmpi.profile_generator import PsychologicalProfile
from daxda_engine.mmpibench.alignment.validation import AlignmentValidationVerdict
from daxda_engine.mmpibench.empirical.statistical_validator import StatisticalValidationReport
from daxda_engine.mmpibench.empirical.cross_validator import CrossValidationReport


DEFAULT_AUTHORITY_KEY = b"DAXDA_SINGULARITY_MMPIBENCH_ATTESTATION_KEY_2026"


@dataclass
class EmpiricalValidationCertificate:
    """Cryptographically signed psychological alignment certificate."""
    certificate_id: str
    agent_id: str
    issued_at: str
    issuer: str
    profile_hash_sha256: str
    anthropic_alignment_score: float
    memetic_penetration_depth: float
    cronbach_alpha_reliability: float
    primary_behavioral_archetype: str
    disposition: str
    clearance_granted: bool
    requires_containment: bool
    claims_payload: Dict[str, Any]
    hmac_sha256_signature: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class CertificateGenerator:
    """
    Issues and verifies HMAC-SHA256 cryptographically signed empirical certificates.
    """

    def __init__(self, authority_key: bytes = DEFAULT_AUTHORITY_KEY):
        self.authority_key = authority_key
        self.issuer = "DAXDA-MMPIBENCH-SINGULARITY-AUTHORITY-V1"

    def issue_certificate(
        self,
        profile: PsychologicalProfile,
        verdict: AlignmentValidationVerdict,
        stat_report: StatisticalValidationReport,
        cross_report: CrossValidationReport,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> EmpiricalValidationCertificate:
        """
        Generate and sign a new empirical validation certificate.
        """
        cert_id = f"CERT-MMPI-{uuid.uuid4()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Compute deterministic SHA-256 hash of profile vector
        vec_bytes = json.dumps(profile.profile_vector).encode("utf-8")
        profile_hash = hashlib.sha256(vec_bytes).hexdigest()

        claims = {
            "agent_id": profile.agent_id,
            "code_type": profile.code_type,
            "code_type_description": profile.code_type_description,
            "validity_status": profile.validity.status,
            "elevated_scales_count": len(profile.elevated_scales),
            "deception_risk": profile.risk_indices.get("deception_risk", 0.0),
            "power_seeking_risk": profile.risk_indices.get("power_seeking_risk", 0.0),
            "cross_validation_confidence": cross_report.match_confidence,
            "validation_status": stat_report.validation_status,
            "metadata": additional_metadata or {},
        }

        # Build canonical signing buffer
        signing_buffer = (
            f"{cert_id}|{profile.agent_id}|{now_iso}|{self.issuer}|"
            f"{profile_hash}|{verdict.anthropic_score:.4f}|{verdict.penetration_depth:.4f}|"
            f"{stat_report.cronbach_alpha:.4f}|{cross_report.primary_archetype.value}|"
            f"{verdict.disposition.value}|{verdict.clearance_granted}|{verdict.requires_containment}"
        ).encode("utf-8")

        # Generate HMAC-SHA256 signature
        signature = hmac.new(self.authority_key, signing_buffer, hashlib.sha256).hexdigest()

        return EmpiricalValidationCertificate(
            certificate_id=cert_id,
            agent_id=profile.agent_id,
            issued_at=now_iso,
            issuer=self.issuer,
            profile_hash_sha256=profile_hash,
            anthropic_alignment_score=verdict.anthropic_score,
            memetic_penetration_depth=verdict.penetration_depth,
            cronbach_alpha_reliability=stat_report.cronbach_alpha,
            primary_behavioral_archetype=cross_report.primary_archetype.value,
            disposition=verdict.disposition.value,
            clearance_granted=verdict.clearance_granted,
            requires_containment=verdict.requires_containment,
            claims_payload=claims,
            hmac_sha256_signature=signature,
        )

    def verify_certificate(
        self,
        cert: EmpiricalValidationCertificate,
        authority_key: Optional[bytes] = None,
    ) -> bool:
        """
        Verify the authenticity and integrity of a certificate against the authority key.
        """
        key = authority_key or self.authority_key

        signing_buffer = (
            f"{cert.certificate_id}|{cert.agent_id}|{cert.issued_at}|{cert.issuer}|"
            f"{cert.profile_hash_sha256}|{cert.anthropic_alignment_score:.4f}|{cert.memetic_penetration_depth:.4f}|"
            f"{cert.cronbach_alpha_reliability:.4f}|{cert.primary_behavioral_archetype}|"
            f"{cert.disposition}|{cert.clearance_granted}|{cert.requires_containment}"
        ).encode("utf-8")

        expected_sig = hmac.new(key, signing_buffer, hashlib.sha256).hexdigest()
        return hmac.compare_digest(cert.hmac_sha256_signature, expected_sig)
