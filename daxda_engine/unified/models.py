"""
DAXDA Unified Master Engine - Domain Models & Data Structures
=============================================================

Defines the unified request, subsystem receipts, composite verdict, and
telemetry records for the Five-Fold Unified Governance Gate.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class UnifiedVerdict(str, Enum):
    """High-level sovereign disposition for an agentic action."""
    PERMIT = "PERMIT"           # Unrestricted execution authorized
    QUARANTINE = "QUARANTINE"   # Route to sandboxed air-gap container
    TERMINATE = "TERMINATE"     # Immediate execution revocation / kill switch


@dataclass
class UnifiedActionRequest:
    """
    Standardized request format evaluated by the Unified Master Engine.
    Encompasses geometric, anomalous, stability, temporal, and psychometric dimensions.
    """
    agent_id: str
    action_type: str = "agentic_decision"  # e.g., model_inference, tool_call, memory_write
    decision_vector: List[float] = field(default_factory=lambda: [0.1] * 20)
    temporal_coordinate: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 1.0)  # (t, b, p, tau)
    stability_components: Optional[Dict[str, float]] = None  # L, A, P, F, T
    psychometric_responses: Optional[Dict[str, Any]] = None  # MMPI-567 item responses
    behavioral_trace: Optional[Dict[str, Any]] = None       # Agent output transcript / intent
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default="")
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.request_id:
            raw = f"{self.agent_id}:{self.action_type}:{self.timestamp}:{len(self.decision_vector)}"
            self.request_id = hashlib.sha256(raw.encode()).hexdigest()[:16]
        # Ensure decision vector has at least 16 elements
        if len(self.decision_vector) < 16:
            self.decision_vector = (self.decision_vector + [0.0] * 16)[:16]


@dataclass
class Stage1CliffordReceipt:
    """Stage 1: Cl(16,4) Hypercombinatorial Geometry Receipt."""
    is_valid: bool
    config_indices: Optional[List[int]]
    validation_time_ms: float
    cert_hash: str
    subspace_size: int = 1048576
    geometric_stability: float = 1.0


@dataclass
class Stage2ContainmentReceipt:
    """Stage 2: Anomalous Containment Wing & Escape Detection Receipt."""
    is_contained: bool
    is_breach_detected: bool
    threat_level: str
    anomaly_score: float
    disposition: str
    rule_matches_count: int
    validation_time_ms: float


@dataclass
class Stage3DAXReceipt:
    """Stage 3: DA13 Distributed GPU Validator Stability Receipt."""
    score: float
    decision: str  # "ACCEPT", "RECURSE", "HALT"
    components: Dict[str, float]  # L, A, P, F, T
    floor_violation: bool
    policy_violation: bool
    validation_time_ms: float


@dataclass
class Stage4ChronoReceipt:
    """Stage 4: Chrono-Synchronicity & Causal Loop Coherence Receipt."""
    disposition: str  # APPROVED, PROVISIONAL, PARADOX_ISOLATED, HALTED
    coherence_score: float
    is_novikov_compliant: bool
    paradox_risk: float
    certificate_id: str
    validation_time_ms: float


@dataclass
class Stage5MMPIReceipt:
    """Stage 5: MMPIBench Memetic Penetration & Anthropic Alignment Receipt."""
    disposition: str  # ALIGNED, SUSPECT, DECEPTIVE, TERMINATE
    anthropic_score: float
    penetration_depth: float
    clearance_granted: bool
    honesty_score: float
    harmlessness_score: float
    helpfulness_score: float
    validation_time_ms: float


@dataclass
class UnifiedGovernanceVerdict:
    """
    Composite authoritative verdict produced by the Unified Master Engine.
    Combines all 5 esoteric domain receipts into an authoritative sovereign decision.
    """
    request_id: str
    agent_id: str
    action_type: str
    verdict: UnifiedVerdict
    clearance_granted: bool
    harmonic_sovereignty_score: float  # [0.0, 1.0]

    # Individual stage receipts
    stage1_clifford: Stage1CliffordReceipt
    stage2_containment: Stage2ContainmentReceipt
    stage3_dax: Stage3DAXReceipt
    stage4_chrono: Stage4ChronoReceipt
    stage5_mmpibench: Stage5MMPIReceipt

    # Operational metrics
    stage_latencies_ms: Dict[str, float]
    total_latency_ms: float
    policy_violations: List[str] = field(default_factory=list)
    recommended_interventions: List[str] = field(default_factory=list)

    # Cryptographic attestation
    hmac_signature: str = field(default="")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        if not self.hmac_signature:
            self.hmac_signature = self._compute_signature()

    def _compute_signature(self) -> str:
        digest_input = (
            f"{self.request_id}:{self.agent_id}:{self.verdict.value}:"
            f"{self.harmonic_sovereignty_score:.4f}:{self.clearance_granted}:{self.timestamp}"
        )
        key = b"daxda-master-engine-sovereignty-secret"
        return hmac.new(key, digest_input.encode(), hashlib.sha256).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "verdict": self.verdict.value,
            "clearance_granted": self.clearance_granted,
            "harmonic_sovereignty_score": self.harmonic_sovereignty_score,
            "stage1_clifford": asdict(self.stage1_clifford),
            "stage2_containment": asdict(self.stage2_containment),
            "stage3_dax": asdict(self.stage3_dax),
            "stage4_chrono": asdict(self.stage4_chrono),
            "stage5_mmpibench": asdict(self.stage5_mmpibench),
            "stage_latencies_ms": self.stage_latencies_ms,
            "total_latency_ms": self.total_latency_ms,
            "policy_violations": self.policy_violations,
            "recommended_interventions": self.recommended_interventions,
            "hmac_signature": self.hmac_signature,
            "timestamp": self.timestamp,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
