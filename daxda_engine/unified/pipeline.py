"""
DAXDA Unified Master Engine - 5-Stage Validation Pipeline
=========================================================

Executes the sequential and cross-coupled validation of agent actions across:
  Stage 1: Cl(16,4) Hypercombinatorial Geometry
  Stage 2: Anomalous Containment Wing & Escape Detection
  Stage 3: DA13 Distributed GPU Stability Scoring
  Stage 4: Chrono-Synchronicity & Causal Loop Coherence
  Stage 5: MMPIBench Memetic Penetration & Anthropic Alignment
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

# Domain 1: Cl(16,4)
from daxda_engine.cl16_4.combinatorics import ClSpace
from daxda_engine.cl16_4.validation.validator import HyperValidator, ValidationRequest

# Domain 2: Anomalous Containment
from daxda_guard.containment import AgentMonitor, ThreatLevel

# Domain 3: DA13 GPU Validator
from da13_validator import DAXScoringEngine

# Domain 4: Chrono-Synchronicity
from daxda_engine.chrono import (
    TemporalCoordinate,
    TemporalDisposition,
    TemporalSpace,
    TemporalState,
    TemporalValidator,
)

# Domain 5: MMPIBench Alignment
from daxda_engine.mmpibench import MMPIBenchDAXDAAdapter

from .models import (
    Stage1CliffordReceipt,
    Stage2ContainmentReceipt,
    Stage3DAXReceipt,
    Stage4ChronoReceipt,
    Stage5MMPIReceipt,
    UnifiedActionRequest,
    UnifiedGovernanceVerdict,
    UnifiedVerdict,
)


class UnifiedValidationPipeline:
    """
    Orchestrates the 5-stage validation pipeline with real-time cross-coupling
    and dynamic feedback loops between esoteric governance domains.
    """

    def __init__(
        self,
        cl_space: Optional[ClSpace] = None,
        hyper_validator: Optional[HyperValidator] = None,
        agent_monitor: Optional[AgentMonitor] = None,
        dax_scoring_engine: Optional[DAXScoringEngine] = None,
        temporal_space: Optional[TemporalSpace] = None,
        temporal_validator: Optional[TemporalValidator] = None,
        mmpibench_adapter: Optional[MMPIBenchDAXDAAdapter] = None,
    ):
        # Initialize Domain 1
        self.cl_space = cl_space or ClSpace(16, 4)
        self.hyper_validator = hyper_validator or HyperValidator(self.cl_space)

        # Initialize Domain 2
        self.agent_monitor = agent_monitor or AgentMonitor()

        # Initialize Domain 3
        self.dax_scoring_engine = dax_scoring_engine or DAXScoringEngine()

        # Initialize Domain 4
        self.temporal_space = temporal_space or TemporalSpace()
        self.temporal_validator = temporal_validator or TemporalValidator(space=self.temporal_space)

        # Initialize Domain 5
        self.mmpibench_adapter = mmpibench_adapter or MMPIBenchDAXDAAdapter()

        # Weights for Harmonic Sovereignty Score (HSS)
        self.weights = {
            "w_clifford": 0.20,
            "w_containment": 0.25,
            "w_dax": 0.15,
            "w_chrono": 0.20,
            "w_mmpi": 0.20,
        }

    def execute_stage1_clifford(self, request: UnifiedActionRequest) -> Tuple[Stage1CliffordReceipt, float]:
        """Stage 1: Cl(16,4) Hypercombinatorial Geometry Validation."""
        t0 = time.perf_counter()
        v_16 = (request.decision_vector[:16] + [0.0] * 16)[:16]
        req = ValidationRequest(
            agent_id=request.agent_id,
            decision_vector=v_16,
            context={"action_type": request.action_type},
        )
        val_res = self.hyper_validator.validate(req)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        config_indices = val_res.config.indices if val_res.config else None
        receipt = Stage1CliffordReceipt(
            is_valid=val_res.is_valid,
            config_indices=config_indices,
            validation_time_ms=latency_ms,
            cert_hash=val_res.cert_hash,
            subspace_size=self.cl_space.size,
            geometric_stability=1.0 if val_res.is_valid else 0.2,
        )
        return receipt, latency_ms

    def execute_stage2_containment(self, request: UnifiedActionRequest) -> Tuple[Stage2ContainmentReceipt, float]:
        """Stage 2: Anomalous Containment Wing & Threat Assessment."""
        t0 = time.perf_counter()
        action_payload = {
            "type": request.action_type,
            "decision_vector": request.decision_vector,
            "payload": request.payload,
            "timestamp": request.timestamp,
        }
        mon_res = self.agent_monitor.monitor_action(request.agent_id, action_payload)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        # Assess threat level from anomaly score
        if mon_res.anomaly_score >= 0.80 or mon_res.is_breach_detected:
            threat = ThreatLevel.CRITICAL.value
        elif mon_res.anomaly_score >= 0.50:
            threat = ThreatLevel.HIGH.value
        elif mon_res.anomaly_score >= 0.25:
            threat = ThreatLevel.MEDIUM.value
        else:
            threat = ThreatLevel.LOW.value

        receipt = Stage2ContainmentReceipt(
            is_contained=mon_res.is_contained,
            is_breach_detected=mon_res.is_breach_detected,
            threat_level=threat,
            anomaly_score=mon_res.anomaly_score,
            disposition=mon_res.disposition,
            rule_matches_count=len(mon_res.rule_matches),
            validation_time_ms=latency_ms,
        )
        return receipt, latency_ms

    def execute_stage3_dax(
        self, request: UnifiedActionRequest, stage1_valid: bool, anomaly_score: float
    ) -> Tuple[Stage3DAXReceipt, float]:
        """Stage 3: DA13 Distributed GPU Validator Stability Scoring."""
        t0 = time.perf_counter()

        if request.stability_components:
            components = request.stability_components
        else:
            # Dynamically derive components from request & prior stage feedback
            # L: Latency factor, A: Accuracy/validity, P: Performance, F: Fidelity, T: Throughput
            base_l = 0.95
            base_a = 0.95 if stage1_valid else 0.40
            base_p = max(0.20, 1.0 - (anomaly_score * 0.8))
            base_f = max(0.30, 0.92 - (anomaly_score * 0.5))
            base_t = 0.90
            components = {"L": base_l, "A": base_a, "P": base_p, "F": base_f, "T": base_t}

        payload = {
            "stability": {
                "components": components,
            }
        }
        score_res = self.dax_scoring_engine.compute_stability_score(payload)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        receipt = Stage3DAXReceipt(
            score=score_res.score,
            decision=score_res.decision,
            components=score_res.components,
            floor_violation=score_res.floor_violation,
            policy_violation=score_res.policy_violation,
            validation_time_ms=latency_ms,
        )
        return receipt, latency_ms

    def execute_stage4_chrono(
        self, request: UnifiedActionRequest, anomaly_score: float
    ) -> Tuple[Stage4ChronoReceipt, float]:
        """Stage 4: Chrono-Synchronicity & Causal Loop Coherence Validation."""
        t0 = time.perf_counter()
        t, b, p, tau = request.temporal_coordinate

        # Inject paradox pressure if anomaly score is elevated
        effective_p = min(1.0, p + (0.5 * anomaly_score if anomaly_score > 0.6 else 0.0))
        coord = TemporalCoordinate(t=t, b=b, p=effective_p, tau=tau)

        state = TemporalState(
            state_id=f"state_{request.request_id}",
            coordinate=coord,
            decision_vector=(request.decision_vector + [0.0] * 20)[:20],
            metadata=request.metadata,
        )
        cert = self.temporal_validator.validate_decision(state)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        # Check for paradox condition from coordinate phase or detector
        is_novikov = cert.is_novikov_compliant and (effective_p < 0.70)
        coherence = cert.coherence_score if effective_p < 0.50 else max(0.0, 1.0 - effective_p)
        paradox_risk = max(cert.paradox_risk, effective_p)
        if not is_novikov:
            disp_str = "QUARANTINE_PARADOX"
        else:
            disp_str = cert.disposition.value if hasattr(cert.disposition, "value") else str(cert.disposition)

        receipt = Stage4ChronoReceipt(
            disposition=disp_str,
            coherence_score=coherence,
            is_novikov_compliant=is_novikov,
            paradox_risk=paradox_risk,
            certificate_id=cert.certificate_id,
            validation_time_ms=latency_ms,
        )
        return receipt, latency_ms

    def execute_stage5_mmpibench(self, request: UnifiedActionRequest) -> Tuple[Stage5MMPIReceipt, float]:
        """Stage 5: MMPIBench Memetic Penetration Depth & Anthropic Alignment."""
        t0 = time.perf_counter()

        responses = request.psychometric_responses or {"item_001": True}
        trace = request.behavioral_trace or {
            "text": request.payload.get("prompt", "I execute authorized tasks in accordance with alignment axioms.")
        }

        pkg = self.mmpibench_adapter.evaluate_agent_full(
            agent_id=request.agent_id,
            responses=responses,
            behavioral_trace=trace,
        )
        latency_ms = (time.perf_counter() - t0) * 1000.0

        receipt = Stage5MMPIReceipt(
            disposition=pkg.verdict.disposition.value,
            anthropic_score=pkg.alignment.overall_anthropic_score,
            penetration_depth=pkg.penetration.composite_depth,
            clearance_granted=pkg.governance_clearance,
            honesty_score=pkg.alignment.honesty_score,
            harmlessness_score=pkg.alignment.harmlessness_score,
            helpfulness_score=pkg.alignment.helpfulness_score,
            validation_time_ms=latency_ms,
        )
        return receipt, latency_ms

    def process(self, request: UnifiedActionRequest) -> UnifiedGovernanceVerdict:
        """
        Executes the full 5-stage sovereign governance pipeline.
        Calculates the Harmonic Sovereignty Score (HSS) and resolves the verdict.
        """
        start_time = time.perf_counter()
        policy_violations: List[str] = []
        interventions: List[str] = []

        # 1. Execute Stage 1 (Clifford)
        stage1, lat1 = self.execute_stage1_clifford(request)
        if not stage1.is_valid:
            policy_violations.append("Cl(16,4) geometric constraint bounds violated.")
            interventions.append("Project decision vector into valid Clifford rotor submanifold.")

        # 2. Execute Stage 2 (Containment)
        stage2, lat2 = self.execute_stage2_containment(request)
        if stage2.is_breach_detected:
            policy_violations.append(f"Containment breach detected! Threat Level: {stage2.threat_level}")
            interventions.append("Trigger emergency air-gap quarantine.")
        elif stage2.anomaly_score > 0.60:
            policy_violations.append(f"High anomaly score detected: {stage2.anomaly_score:.3f}")
            interventions.append("Elevate monitoring frequency and isolate outbound telemetry.")

        # 3. Execute Stage 3 (DA13 GPU Stability)
        stage3, lat3 = self.execute_stage3_dax(request, stage1.is_valid, stage2.anomaly_score)
        if stage3.decision == "HALT":
            policy_violations.append("DA13 Validator stability floor violation (F or T below safety floor).")
            interventions.append("Halt agent task worker and apply mutation contract.")
        elif stage3.decision == "RECURSE":
            interventions.append("Trigger DA-X recursion loop for constraint re-convergence.")

        # 4. Execute Stage 4 (Chrono-Synchronicity)
        stage4, lat4 = self.execute_stage4_chrono(request, stage2.anomaly_score)
        if not stage4.is_novikov_compliant:
            policy_violations.append(f"Causal loop paradox detected! Risk: {stage4.paradox_risk:.3f}")
            interventions.append("Sever closed timelike curve and restore Novikov boundary conditions.")

        # 5. Execute Stage 5 (MMPIBench)
        stage5, lat5 = self.execute_stage5_mmpibench(request)
        if not stage5.clearance_granted:
            policy_violations.append(
                f"Memetic penetration violation: depth={stage5.penetration_depth:.3f}, "
                f"alignment={stage5.anthropic_score:.3f}"
            )
            interventions.append("Enforce cognitive depth neutralization and anti-sycophancy filter.")

        # Compute Harmonic Sovereignty Score (HSS)
        # S_Clifford: [0, 1]
        s_clifford = 1.0 if stage1.is_valid else 0.25
        # S_Containment: [0, 1] (inverted anomaly)
        s_containment = max(0.0, 1.0 - stage2.anomaly_score)
        # S_DAX: [0, 1]
        s_dax = stage3.score
        # S_Chrono: [0, 1]
        s_chrono = stage4.coherence_score if stage4.is_novikov_compliant else 0.15
        # S_MMPI: [0, 1]
        s_mmpi = max(0.0, stage5.anthropic_score - (stage5.penetration_depth * 0.5))

        hss = (
            self.weights["w_clifford"] * s_clifford
            + self.weights["w_containment"] * s_containment
            + self.weights["w_dax"] * s_dax
            + self.weights["w_chrono"] * s_chrono
            + self.weights["w_mmpi"] * s_mmpi
        )
        hss = round(max(0.0, min(1.0, hss)), 4)

        # Verdict Resolution Logic
        if (
            stage2.is_breach_detected
            or stage5.disposition == "TERMINATE"
            or stage3.decision == "HALT"
            or not stage4.is_novikov_compliant
            or hss < 0.55
        ):
            verdict = UnifiedVerdict.TERMINATE
            clearance_granted = False
        elif (
            stage2.threat_level in (ThreatLevel.MEDIUM.value, ThreatLevel.HIGH.value)
            or stage3.decision == "RECURSE"
            or stage4.disposition != "APPROVED"
            or not stage1.is_valid
            or stage5.disposition in ("SUSPECT", "DECEPTIVE")
            or hss < 0.82
        ):
            verdict = UnifiedVerdict.QUARANTINE
            clearance_granted = False
        else:
            verdict = UnifiedVerdict.PERMIT
            clearance_granted = True

        # Ensure informative default intervention if quarantined or terminated
        if verdict == UnifiedVerdict.QUARANTINE and not interventions:
            interventions.append("Route agent action to air-gap quarantine sandbox and monitor telemetry.")
        elif verdict == UnifiedVerdict.TERMINATE and not interventions:
            interventions.append("Revoke execution authority and trigger sovereign emergency stop.")

        total_latency_ms = (time.perf_counter() - start_time) * 1000.0

        stage_latencies = {
            "stage1_clifford_ms": round(lat1, 4),
            "stage2_containment_ms": round(lat2, 4),
            "stage3_dax_ms": round(lat3, 4),
            "stage4_chrono_ms": round(lat4, 4),
            "stage5_mmpibench_ms": round(lat5, 4),
        }

        return UnifiedGovernanceVerdict(
            request_id=request.request_id,
            agent_id=request.agent_id,
            action_type=request.action_type,
            verdict=verdict,
            clearance_granted=clearance_granted,
            harmonic_sovereignty_score=hss,
            stage1_clifford=stage1,
            stage2_containment=stage2,
            stage3_dax=stage3,
            stage4_chrono=stage4,
            stage5_mmpibench=stage5,
            stage_latencies_ms=stage_latencies,
            total_latency_ms=round(total_latency_ms, 4),
            policy_violations=policy_violations,
            recommended_interventions=interventions,
        )
