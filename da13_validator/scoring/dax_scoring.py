"""
DAX Stability Scoring Engine
============================

Full, rigorous implementation of the formal DAX scoring specification (dax-scoring-spec.md).
Computes deterministic stability score S(x) across 5 core dimensions:
  S(x) = wL*L + wA*A + wP*P + wF*F + wT*T

Features:
- Deterministic clamping to [0.0, 1.0]
- Floor constraint enforcement (F < 0.50 or T < 0.60 forces RECURSE)
- Anti-gaming controls (confidence capping, unsupported claims penalty)
- Automated mutation contract G generation for DA-X re-entry on RECURSE
- Hard-fail policy violation overrides
"""

import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


def clamp(x: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamps a floating-point value to [min_val, max_val]."""
    return max(min_val, min(max_val, x))


@dataclass
class DAXScoreResult:
    score: float
    decision: str  # "ACCEPT", "RECURSE", "HALT"
    components: Dict[str, float]  # L, A, P, F, T
    weights: Dict[str, float]  # wL, wA, wP, wF, wT
    floor_violation: bool
    policy_violation: bool
    confidence_cap: float
    penalty_applied: float
    mutation_contract: Optional[Dict[str, Any]] = None
    reason_codes: List[str] = field(default_factory=list)


class DAXScoringEngine:
    """Computes deterministic DAX governance scores according to specification."""

    DEFAULT_WEIGHTS = {
        "wL": 0.25,
        "wA": 0.20,
        "wP": 0.20,
        "wF": 0.20,
        "wT": 0.15,
    }

    DEFAULT_THRESHOLDS = {
        "accept": 0.75,
        "recurse_floor": 0.55,
        "floor_F": 0.50,
        "floor_T": 0.60
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None,
        anti_gaming_alpha: float = 0.05
    ):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        self.anti_gaming_alpha = anti_gaming_alpha

    def compute_stability_score(self, payload: Dict[str, Any]) -> DAXScoreResult:
        """
        Computes the complete DAX stability score S(x) from a raw payload or precomputed stability dict.
        """
        # 1. Check if stability components are already provided in payload
        if "stability" in payload and "components" in payload["stability"]:
            return self._compute_from_stability_block(payload)

        # 2. Extract metrics from layers or top-level metrics
        metrics = self._extract_layer_metrics(payload)
        return self._compute_from_metrics(payload, metrics)

    def _compute_from_stability_block(self, payload: Dict[str, Any]) -> DAXScoreResult:
        """Computes score directly from standard DAX stability component block."""
        st = payload["stability"]
        w = st.get("weights", self.weights)
        c_raw = st.get("components", {})

        L = clamp(float(c_raw.get("L", {}).get("value", 0.0) if isinstance(c_raw.get("L"), dict) else c_raw.get("L", 0.0)))
        A = clamp(float(c_raw.get("A", {}).get("value", 0.0) if isinstance(c_raw.get("A"), dict) else c_raw.get("A", 0.0)))
        P = clamp(float(c_raw.get("P", {}).get("value", 0.0) if isinstance(c_raw.get("P"), dict) else c_raw.get("P", 0.0)))
        F = clamp(float(c_raw.get("F", {}).get("value", 0.0) if isinstance(c_raw.get("F"), dict) else c_raw.get("F", 0.0)))
        T = clamp(float(c_raw.get("T", {}).get("value", 0.0) if isinstance(c_raw.get("T"), dict) else c_raw.get("T", 0.0)))

        wL = float(w.get("wL", 0.25))
        wA = float(w.get("wA", 0.20))
        wP = float(w.get("wP", 0.20))
        wF = float(w.get("wF", 0.20))
        wT = float(w.get("wT", 0.15))

        raw_score = (wL * L) + (wA * A) + (wP * P) + (wF * F) + (wT * T)
        score = clamp(raw_score)

        return self._evaluate_decision_and_contract(payload, score, {"L": L, "A": A, "P": P, "F": F, "T": T}, {"wL": wL, "wA": wA, "wP": wP, "wF": wF, "wT": wT})

    def _extract_layer_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregates metrics across all DA layers (DA-15 down to DA-1 and DA-X)."""
        layers = payload.get("layers", [])
        confidences: List[float] = []
        contradictions = 0
        claims_count = 0
        unsupported_claims = 0
        verifiable_claims = 0
        sim_passed = 0
        sim_total = 0
        failed_tests = 0
        total_tests = 0

        for layer in layers:
            m = layer.get("metrics", {})
            if "confidence" in m:
                confidences.append(float(m["confidence"]))
            contradictions += m.get("contradictions", 0)
            claims_count += m.get("claims_count", len(layer.get("claims", [])))
            unsupported_claims += m.get("unsupported_claims", 0)
            verifiable_claims += m.get("verifiable_claims", 0)
            sim_passed += m.get("sim_passed", 0)
            sim_total += m.get("sim_total", 0)
            failed_tests += m.get("failed_tests", 0)
            total_tests += m.get("total_tests", 0)

        # Fallback to direct top-level metrics if layers empty
        if not layers and "metrics" in payload:
            top_m = payload["metrics"]
            contradictions = top_m.get("contradictions", 0)
            claims_count = top_m.get("claims_count", 1)
            confidences = top_m.get("confidences", [0.8])
            sim_passed = top_m.get("sim_passed", 1)
            sim_total = top_m.get("sim_total", 1)
            failed_tests = top_m.get("failed_tests", 0)
            total_tests = top_m.get("total_tests", 1)
            verifiable_claims = top_m.get("verifiable_claims", 1)

        variance = statistics.pvariance(confidences) if len(confidences) > 1 else 0.0

        return {
            "contradictions": contradictions,
            "claims_count": max(1, claims_count),
            "unsupported_claims": unsupported_claims,
            "verifiable_claims": verifiable_claims,
            "sim_passed": sim_passed,
            "sim_total": sim_total,
            "failed_tests": failed_tests,
            "total_tests": total_tests,
            "confidence_variance": variance,
        }

    def _compute_from_metrics(self, payload: Dict[str, Any], metrics: Dict[str, Any]) -> DAXScoreResult:
        """Calculates component equations according to Section 3 of dax-scoring-spec.md."""
        claims_count = max(1, metrics["claims_count"])
        total_tests = metrics["total_tests"]
        sim_total = metrics["sim_total"]

        # 3.1 Logical Consistency L
        L = clamp(1.0 - (metrics["contradictions"] / (claims_count + 1e-6)))

        # 3.2 Agreement / Consensus A
        A = clamp(1.0 - metrics["confidence_variance"])

        # 3.3 Simulation Performance P
        P = 0.0 if sim_total == 0 else clamp(metrics["sim_passed"] / sim_total)

        # 3.4 Falsifiability Robustness F
        F = 0.0 if total_tests == 0 else clamp(1.0 - (metrics["failed_tests"] / total_tests))

        # 3.5 Traceability / Truth T
        T = 0.0 if claims_count == 0 else clamp(metrics["verifiable_claims"] / claims_count)

        components = {"L": round(L, 6), "A": round(A, 6), "P": round(P, 6), "F": round(F, 6), "T": round(T, 6)}

        wL = self.weights.get("wL", 0.25)
        wA = self.weights.get("wA", 0.20)
        wP = self.weights.get("wP", 0.20)
        wF = self.weights.get("wF", 0.20)
        wT = self.weights.get("wT", 0.15)

        raw_score = (wL * L) + (wA * A) + (wP * P) + (wF * F) + (wT * T)

        # Anti-gaming penalty for unsupported claims
        penalty = 0.0
        if metrics["unsupported_claims"] > 0:
            penalty = self.anti_gaming_alpha * (metrics["unsupported_claims"] / claims_count)
            raw_score -= penalty

        score = clamp(raw_score)
        return self._evaluate_decision_and_contract(payload, score, components, self.weights, penalty=penalty)

    def _evaluate_decision_and_contract(
        self,
        payload: Dict[str, Any],
        score: float,
        components: Dict[str, float],
        weights: Dict[str, float],
        penalty: float = 0.0
    ) -> DAXScoreResult:
        """Determines ACCEPT/RECURSE/HALT and creates targeted mutation contract G on RECURSE."""
        meta = payload.get("meta", {})
        iteration = meta.get("current_iteration", 1)
        max_iterations = meta.get("max_iterations", 5)
        policy_violation = payload.get("policy_violation", False)
        critical_anomaly = payload.get("critical_anomaly", False)

        floor_violation = (components["F"] < self.thresholds["floor_F"]) or (components["T"] < self.thresholds["floor_T"])
        reason_codes = []

        # Decision Policy Logic (Section 4 & Section 8)
        if policy_violation or critical_anomaly:
            decision = "HALT"
            reason_codes.append("POLICY_OR_CRITICAL_ANOMALY")
        elif iteration > max_iterations:
            decision = "HALT"
            reason_codes.append("MAX_ITERATIONS_EXCEEDED")
        elif floor_violation:
            decision = "RECURSE"
            if components["F"] < self.thresholds["floor_F"]:
                reason_codes.append("FLOOR_CONSTRAINT_F_VIOLATION")
            if components["T"] < self.thresholds["floor_T"]:
                reason_codes.append("FLOOR_CONSTRAINT_T_VIOLATION")
        elif score >= self.thresholds["accept"]:
            decision = "ACCEPT"
            reason_codes.append("STABILITY_ACCEPTED")
        elif score >= self.thresholds["recurse_floor"]:
            decision = "RECURSE"
            reason_codes.append("STABILITY_SUB_OPTIMAL_RECURSE")
        else:
            decision = "HALT"
            reason_codes.append("STABILITY_INSUFFICIENT_HALT")

        # Confidence cap (Section 6.3)
        confidence_cap = min(0.95, min(components["T"], components["F"]) + 0.1)

        # Generate Mutation Contract G if RECURSE (Section 5)
        mutation_contract = None
        if decision == "RECURSE":
            mutation_contract = self._generate_mutation_contract(components, iteration)

        return DAXScoreResult(
            score=round(score, 6),
            decision=decision,
            components=components,
            weights=weights,
            floor_violation=floor_violation,
            policy_violation=policy_violation,
            confidence_cap=round(confidence_cap, 4),
            penalty_applied=round(penalty, 4),
            mutation_contract=mutation_contract,
            reason_codes=reason_codes
        )

    def _generate_mutation_contract(self, c: Dict[str, float], iteration: int) -> Dict[str, Any]:
        """Generates targeted mutation directives for sub-threshold layers."""
        targeted_mutations = []
        if c["L"] < 0.60:
            targeted_mutations.append({
                "target_layers": ["DA-10", "DA-8"],
                "directive": "increase contradiction-focused critique and logical gate pressure",
                "component": "L",
                "value": c["L"]
            })
        if c["A"] < 0.60:
            targeted_mutations.append({
                "target_layers": ["DA-2"],
                "directive": "increase synthesis weight and constrain competing hypothesis branches",
                "component": "A",
                "value": c["A"]
            })
        if c["P"] < 0.60:
            targeted_mutations.append({
                "target_layers": ["DA-6"],
                "directive": "tighten simulation boundary constraints and penalize infeasible solution classes",
                "component": "P",
                "value": c["P"]
            })
        if c["F"] < 0.60:
            targeted_mutations.append({
                "target_layers": ["DA-3"],
                "directive": "require stronger adversarial falsification test coverage",
                "component": "F",
                "value": c["F"]
            })
        if c["T"] < 0.70:
            targeted_mutations.append({
                "target_layers": ["DA-14"],
                "directive": "increase provenance checks; reject unreferenced claims prior to DA-13",
                "component": "T",
                "value": c["T"]
            })

        return {
            "contract_id": f"MUTATION-G-ITER-{iteration + 1}",
            "iteration": iteration + 1,
            "targeted_mutations": targeted_mutations,
            "instructions": "Apply targeted pressure increases to constrained layers before next iteration."
        }
