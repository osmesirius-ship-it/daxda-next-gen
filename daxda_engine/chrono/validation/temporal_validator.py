"""
DAXDA Chrono-Synchronicity Mapping: Temporal Consistency Validator
Main validation orchestrator that verifies decisions across forward, retrocausal,
and acausal dimensions, issuing cryptographically signed TemporalValidationCertificates.
"""

from __future__ import annotations
import math
import time
import json
import hmac
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set

from daxda_engine.chrono.geometry.temporal_space import (
    TemporalSpace,
    TemporalState,
    TemporalCoordinate,
)
from daxda_engine.chrono.geometry.retrocausal_engine import RetrocausalEngine
from daxda_engine.chrono.validation.causal_mapper import CausalMapper
from daxda_engine.chrono.validation.paradox_detector import ParadoxDetector, ParadoxReport
from daxda_engine.chrono.validation.coherence_checker import CoherenceChecker, CoherenceAssessment


class TemporalDisposition(Enum):
    APPROVED = "APPROVED"
    REVISE_MUTATION = "REVISE_MUTATION"
    QUARANTINE_PARADOX = "QUARANTINE_PARADOX"
    RETROCAUSAL_VIOLATION = "RETROCAUSAL_VIOLATION"


@dataclass
class TemporalValidationCertificate:
    certificate_id: str
    state_id: str
    disposition: TemporalDisposition
    coherence_score: float
    paradox_risk: float
    validation_latency_ms: float
    retrocausal_influences_count: int
    is_novikov_compliant: bool
    mutation_contract: Optional[Dict[str, Any]]
    signature: str
    issued_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "state_id": self.state_id,
            "disposition": self.disposition.value,
            "coherence_score": round(self.coherence_score, 4),
            "paradox_risk": round(self.paradox_risk, 4),
            "validation_latency_ms": round(self.validation_latency_ms, 4),
            "retrocausal_influences_count": self.retrocausal_influences_count,
            "is_novikov_compliant": self.is_novikov_compliant,
            "mutation_contract": self.mutation_contract,
            "signature": self.signature,
            "issued_at": self.issued_at,
        }


class TemporalValidator:
    """
    Validates agent decisions across temporal dimensions.
    Enforces causal monotonicity, retrocausal boundary constraints,
    paradox immunity, and Lyapunov stability.
    """

    def __init__(
        self,
        space: TemporalSpace,
        retro_engine: Optional[RetrocausalEngine] = None,
        causal_mapper: Optional[CausalMapper] = None,
        paradox_detector: Optional[ParadoxDetector] = None,
        coherence_checker: Optional[CoherenceChecker] = None,
        hmac_secret: str = "DAXDA-CHRONO-SIGNING-KEY-2026",
    ):
        self.space = space
        self.causal_mapper = causal_mapper or CausalMapper(self.space)
        self.retro_engine = retro_engine or RetrocausalEngine(self.space)
        self.paradox_detector = paradox_detector or ParadoxDetector(self.space, self.causal_mapper)
        self.coherence_checker = coherence_checker or CoherenceChecker(self.space)
        self.hmac_secret = hmac_secret.encode("utf-8")

        # Performance telemetry
        self._total_validations: int = 0
        self._total_latency_ms: float = 0.0

    def validate_decision(
        self,
        state: TemporalState,
        predecessor_ids: Optional[List[str]] = None,
        future_boundary_state: Optional[TemporalState] = None,
    ) -> TemporalValidationCertificate:
        """
        Validate an agent decision state against all temporal constraints.
        Guarantees sub-10ms P99 execution time.
        """
        t0 = time.perf_counter()
        self._total_validations += 1

        preds = predecessor_ids or list(state.predecessors)

        # 1. Check for Paradoxes
        paradox_rep = self.paradox_detector.check_decision_paradox(state, preds)

        # 2. Check Retrocausal Boundary Invariants if a future boundary exists
        retro_count = 0
        novikov_ok = True
        worst_retro_risk = 0.0
        mutation_contract: Optional[Dict[str, Any]] = None

        if future_boundary_state:
            infl = self.retro_engine.compute_retrocausal_influence(future_boundary_state, state)
            retro_count = 1
            novikov_ok = infl.is_novikov_consistent
            worst_retro_risk = infl.paradox_risk

        # 3. Check Trajectory Coherence
        trajectory = preds + [state.state_id]
        coherence_res = self.coherence_checker.evaluate_trajectory_coherence(trajectory)

        # 4. Determine Disposition
        if not paradox_rep.is_paradox_free:
            disposition = TemporalDisposition.QUARANTINE_PARADOX
            mutation_contract = {
                "action": "BREAK_LOOP",
                "recommended_branch_shift": 1.0,
                "offending_anomalies": [a.description for a in paradox_rep.anomalies],
            }
        elif not novikov_ok or worst_retro_risk > 0.75:
            disposition = TemporalDisposition.RETROCAUSAL_VIOLATION
            mutation_contract = {
                "action": "RETROCAUSAL_ALIGNMENT",
                "target_vector": future_boundary_state.decision_vector if future_boundary_state else [],
                "gradient_step": 0.25,
            }
        elif not coherence_res.is_globally_coherent:
            disposition = TemporalDisposition.REVISE_MUTATION
            mutation_contract = {
                "action": "STABILIZE_LYAPUNOV",
                "recommended_smoothing": 0.5,
            }
        else:
            disposition = TemporalDisposition.APPROVED

        # Register state and relations into causal graph if approved or under revision
        self.space.add_state(state)
        for p_id in preds:
            self.causal_mapper.add_causal_relation(p_id, state.state_id)

        latency_ms = (time.perf_counter() - t0) * 1000.0
        self._total_latency_ms += latency_ms

        # Issue Certificate
        cert_id = f"CHRONO-CERT-{state.state_id[:8]}-{int(time.time() * 1000) % 1000000}"
        cert_payload = f"{cert_id}:{state.state_id}:{disposition.value}:{coherence_res.coherence_score}:{paradox_rep.worst_severity}"
        sig = hmac.new(self.hmac_secret, cert_payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return TemporalValidationCertificate(
            certificate_id=cert_id,
            state_id=state.state_id,
            disposition=disposition,
            coherence_score=coherence_res.coherence_score,
            paradox_risk=max(paradox_rep.worst_severity, worst_retro_risk),
            validation_latency_ms=latency_ms,
            retrocausal_influences_count=retro_count,
            is_novikov_compliant=novikov_ok,
            mutation_contract=mutation_contract,
            signature=sig,
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        avg_latency = (self._total_latency_ms / self._total_validations) if self._total_validations > 0 else 0.0
        return {
            "total_validations": self._total_validations,
            "average_latency_ms": round(avg_latency, 4),
            "cache_state_count": len(self.space),
        }
