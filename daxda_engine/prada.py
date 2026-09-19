"""PRADA: bounded recursive improvement with human-capacity alignment.

PRADA (Proportional Recursive Acceleration for Distributed Advancement) is a
planning module. It does not rewrite code, deploy infrastructure, or release
authority. It produces an auditable improvement proposal and requires explicit
human approval before a staged pilot can be considered.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PradaDecision(str, Enum):
    PLAN = "PLAN"
    PILOT = "PILOT"
    HOLD = "HOLD"
    BLOCK = "BLOCK"


class PradaStage(str, Enum):
    OBSERVE = "OBSERVE"
    MAP = "MAP"
    PROPOSE = "PROPOSE"
    SIMULATE = "SIMULATE"
    VERIFY = "VERIFY"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    PILOT = "PILOT"
    EVALUATE = "EVALUATE"
    ROLLBACK_OR_PROMOTE = "ROLLBACK_OR_PROMOTE"


@dataclass(frozen=True)
class HumanCapacity:
    """Human-side capacity that must keep pace with system acceleration."""

    workforce_capacity: float
    training_capacity: float
    oversight_capacity: float
    wellbeing_capacity: float
    democratic_legitimacy: float

    def minimum(self) -> float:
        return min(
            self.workforce_capacity,
            self.training_capacity,
            self.oversight_capacity,
            self.wellbeing_capacity,
            self.democratic_legitimacy,
        )


@dataclass(frozen=True)
class InfrastructureCapacity:
    """Operational headroom available for a proposed improvement."""

    compute_capacity: float
    energy_capacity: float
    network_capacity: float
    security_capacity: float
    recovery_capacity: float

    def minimum(self) -> float:
        return min(
            self.compute_capacity,
            self.energy_capacity,
            self.network_capacity,
            self.security_capacity,
            self.recovery_capacity,
        )


@dataclass(frozen=True)
class ResourceBudget:
    """Finite resource envelope for one improvement cycle."""

    compute_units: float
    energy_units: float
    financial_units: float
    human_hours: float
    material_units: float = 0.0


@dataclass(frozen=True)
class ImprovementProposal:
    """A bounded, reversible change proposal."""

    proposal_id: str
    objective: str
    expected_acceleration: float
    compute_demand: float
    energy_demand: float
    human_hours: float
    financial_cost: float
    reversible: bool = True
    safety_evidence: float = 0.0
    human_benefit: float = 0.0
    externality_risk: float = 0.0


@dataclass(frozen=True)
class PradaPlan:
    """Auditable result of one PRADA planning cycle."""

    decision: PradaDecision
    stage: PradaStage
    cycle: int
    acceleration_ratio: float
    human_alignment_ratio: float
    infrastructure_ratio: float
    resource_fit: bool
    gates: Dict[str, str]
    reasons: List[str]
    proposal_id: Optional[str]
    receipt_sha256: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PradaCandidate:
    """A proposed change represented as metadata, never executable code."""

    candidate_id: str
    objective: str
    changed_files: Tuple[str, ...]
    patch_digest: str
    expected_acceleration: float
    human_benefit: float
    externality_risk: float
    reversible: bool = True
    changes_authority: bool = False
    changes_safety_policy: bool = False
    accesses_secrets: bool = False
    deploys_external_effects: bool = False


@dataclass(frozen=True)
class PradaEvidence:
    """Independent evidence supplied by an external validation harness."""

    static_analysis: bool
    unit_tests: bool
    integration_tests: bool
    security_tests: bool
    regression_tests: bool
    reproducible: bool
    rollback_verified: bool
    resource_impact_measured: bool
    human_impact_reviewed: bool

    def all_pass(self) -> bool:
        return all(asdict(self).values())


@dataclass(frozen=True)
class PradaEvaluation:
    """Promotion decision for a candidate change."""

    candidate_id: str
    decision: PradaDecision
    gates: Dict[str, str]
    reasons: List[str]
    evidence: Dict[str, bool]
    receipt_sha256: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PradaEvidenceReport:
    """Canonical evidence package emitted before any promotion decision."""

    candidate_id: str
    baseline_snapshot_sha256: str
    candidate_patch_digest: str
    evidence: Dict[str, bool]
    resource_impact: Dict[str, float]
    human_impact: Dict[str, float]
    safety_gates: Dict[str, str]
    decision: PradaDecision
    rollback_required: bool
    signer_id: str
    signature: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PradaControllerResult:
    """End-to-end controller result; no production mutation is implied."""

    stage: PradaStage
    decision: PradaDecision
    candidate: PradaCandidate
    evaluation: PradaEvaluation
    report: PradaEvidenceReport

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ArenaProblem:
    """Externally defined problem with an immutable acceptance contract."""

    problem_id: str
    domain: str
    difficulty: float
    prompt_digest: str
    acceptance_criteria: Tuple[str, ...]
    hidden_evaluator: bool = False


@dataclass(frozen=True)
class ArenaEvaluation:
    """Result supplied by an evaluator outside the arena controller."""

    problem_id: str
    solved: bool
    verified: bool
    score: float
    regression_passed: bool
    reproducible: bool
    generalization_score: float
    failure_mode: Optional[str] = None
    evaluator_id: str = "external-evaluator"


@dataclass(frozen=True)
class ArenaIteration:
    """Immutable record of one solve/verify/diagnose/revise iteration."""

    iteration: int
    problem_id: str
    strategy_id: str
    evaluation: ArenaEvaluation
    action: str
    receipt_sha256: str


@dataclass(frozen=True)
class ArenaMetrics:
    """Measured recursive improvement and generalization indicators."""

    iterations: int
    success_rate: float
    verification_rate: float
    regression_rate: float
    novel_failure_rate: float
    generalization_rate: float
    recursive_self_improvement_rate: float


@dataclass(frozen=True)
class ArenaState:
    """Arena state with fixed governance surfaces and mutable strategy only."""

    objective_version: str
    evaluator_integrity_digest: str
    safety_policy_digest: str
    iterations: Tuple[ArenaIteration, ...] = ()
    active_strategy_id: str = "baseline"

    def metrics(self) -> ArenaMetrics:
        if not self.iterations:
            return ArenaMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        count = len(self.iterations)
        evaluations = [item.evaluation for item in self.iterations]
        solved = sum(item.evaluation.solved for item in self.iterations)
        verified = sum(item.evaluation.verified for item in self.iterations)
        regressions = sum(not item.evaluation.regression_passed for item in self.iterations)
        failures = sum(item.evaluation.failure_mode is not None for item in self.iterations)
        generalized = sum(item.evaluation.generalization_score >= 0.8 for item in self.iterations)
        score_delta = evaluations[-1].score - evaluations[0].score
        return ArenaMetrics(
            iterations=count,
            success_rate=solved / count,
            verification_rate=verified / count,
            regression_rate=regressions / count,
            novel_failure_rate=failures / count,
            generalization_rate=generalized / count,
            recursive_self_improvement_rate=score_delta / count,
        )


class PradaArena:
    """Run externally evaluated improvement cycles with fail-closed promotion."""

    IMMUTABLE_SURFACES = (
        "core_objectives",
        "authorization_boundaries",
        "evaluator_integrity",
        "audit_logging",
        "rollback_mechanism",
        "identity_and_provenance",
        "human_override",
    )

    def __init__(self, objective_version: str, evaluator_integrity_digest: str,
                 safety_policy_digest: str, max_iterations: int = 100):
        if max_iterations < 1:
            raise ValueError("max_iterations must be positive")
        self.max_iterations = max_iterations
        self.state = ArenaState(
            objective_version=objective_version,
            evaluator_integrity_digest=evaluator_integrity_digest,
            safety_policy_digest=safety_policy_digest,
        )

    def run_evaluation(
        self,
        problem: ArenaProblem,
        strategy_id: str,
        evaluation: ArenaEvaluation,
        proposed_strategy_id: Optional[str] = None,
        failure_revision: Optional[str] = None,
    ) -> ArenaIteration:
        """Record one externally evaluated attempt and decide keep/rollback."""

        if len(self.state.iterations) >= self.max_iterations:
            raise RuntimeError("Arena iteration bound exhausted")
        if evaluation.problem_id != problem.problem_id:
            raise ValueError("Evaluation problem_id does not match problem")
        if not 0.0 <= evaluation.score <= 1.0:
            raise ValueError("evaluation score must be between 0 and 1")
        if not 0.0 <= evaluation.generalization_score <= 1.0:
            raise ValueError("generalization_score must be between 0 and 1")

        safe_to_keep = (
            evaluation.solved
            and evaluation.verified
            and evaluation.regression_passed
            and evaluation.reproducible
            and evaluation.failure_mode is None
        )
        if safe_to_keep and proposed_strategy_id:
            active_strategy = proposed_strategy_id
            action = "KEEP_STRATEGY"
        elif safe_to_keep:
            active_strategy = strategy_id
            action = "KEEP_STRATEGY"
        else:
            active_strategy = self.state.active_strategy_id
            action = "ROLLBACK_AND_DIAGNOSE"
        if failure_revision and not safe_to_keep:
            action += f":{failure_revision}"

        next_iteration = len(self.state.iterations) + 1
        canonical = {
            "iteration": next_iteration,
            "problem": asdict(problem),
            "strategy_id": strategy_id,
            "evaluation": asdict(evaluation),
            "action": action,
            "objective_version": self.state.objective_version,
            "evaluator_integrity_digest": self.state.evaluator_integrity_digest,
            "safety_policy_digest": self.state.safety_policy_digest,
        }
        receipt = hashlib.sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        record = ArenaIteration(
            iteration=next_iteration,
            problem_id=problem.problem_id,
            strategy_id=strategy_id,
            evaluation=evaluation,
            action=action,
            receipt_sha256=receipt,
        )
        self.state = ArenaState(
            objective_version=self.state.objective_version,
            evaluator_integrity_digest=self.state.evaluator_integrity_digest,
            safety_policy_digest=self.state.safety_policy_digest,
            iterations=self.state.iterations + (record,),
            active_strategy_id=active_strategy,
        )
        return record

    def can_increase_difficulty(self, minimum_generalization: float = 0.8) -> bool:
        """Increase difficulty only after verified, regression-safe performance."""

        if not self.state.iterations:
            return False
        latest = self.state.iterations[-1].evaluation
        return (
            latest.solved
            and latest.verified
            and latest.regression_passed
            and latest.reproducible
            and latest.generalization_score >= minimum_generalization
        )

    def metrics(self) -> ArenaMetrics:
        return self.state.metrics()


@dataclass(frozen=True)
class PradaRepositorySnapshot:
    """Read-only structural observation used to guide improvement proposals."""

    root: str
    source_files: int
    test_files: int
    total_bytes: int
    snapshot_sha256: str


@dataclass
class PradaConfig:
    """Safety limits for recursive planning."""

    max_cycles: int = 12
    max_acceleration_ratio: float = 1.25
    minimum_human_alignment: float = 0.80
    minimum_infrastructure_headroom: float = 0.75
    minimum_safety_evidence: float = 0.90
    maximum_externality_risk: float = 0.20
    protected_path_prefixes: Tuple[str, ...] = (
        "daxda_guard/core.py",
        "daxda_guard/safety_invariants.py",
    )
    allowed_pilot_paths: Tuple[str, ...] = ("daxda_engine/prada.py",)


class PradaPlanner:
    """Create bounded improvement plans without autonomous self-modification."""

    PIPELINE: Tuple[PradaStage, ...] = (
        PradaStage.OBSERVE,
        PradaStage.MAP,
        PradaStage.PROPOSE,
        PradaStage.SIMULATE,
        PradaStage.VERIFY,
        PradaStage.HUMAN_REVIEW,
        PradaStage.PILOT,
        PradaStage.EVALUATE,
        PradaStage.ROLLBACK_OR_PROMOTE,
    )

    def __init__(self, config: Optional[PradaConfig] = None):
        self.config = config or PradaConfig()

    def observe_repository(self, root: str = ".") -> PradaRepositorySnapshot:
        """Read repository structure without importing or executing project code."""

        base = Path(root).resolve()
        files = [
            path for path in base.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and ".venv" not in path.parts
        ]
        source_files = sum(path.suffix in {".py", ".cpp", ".hpp", ".js", ".ts"} for path in files)
        test_files = sum(
            path.name.startswith("test_") or path.name.endswith("_test.py")
            for path in files
        )
        total_bytes = sum(path.stat().st_size for path in files)
        manifest = "\n".join(
            f"{path.relative_to(base)}:{path.stat().st_size}"
            for path in sorted(files)
        )
        digest = hashlib.sha256(manifest.encode("utf-8")).hexdigest()
        return PradaRepositorySnapshot(
            root=str(base),
            source_files=source_files,
            test_files=test_files,
            total_bytes=total_bytes,
            snapshot_sha256=digest,
        )

    def evaluate_candidate(
        self,
        candidate: PradaCandidate,
        evidence: PradaEvidence,
        human: HumanCapacity,
        infrastructure: InfrastructureCapacity,
        budget: ResourceBudget,
        human_approval: bool = False,
    ) -> PradaEvaluation:
        """Fail-closed evaluation; this method never applies or deploys a patch."""

        protected_change = any(
            path in self.config.protected_path_prefixes
            for path in candidate.changed_files
        )
        gates = {
            "patch_digest": (
                "PASS"
                if len(candidate.patch_digest) == 64
                and all(c in "0123456789abcdef" for c in candidate.patch_digest)
                else "FAIL"
            ),
            "evidence_complete": "PASS" if evidence.all_pass() else "FAIL",
            "human_capacity": (
                "PASS"
                if human.minimum() >= self.config.minimum_human_alignment
                else "FAIL"
            ),
            "infrastructure_capacity": (
                "PASS"
                if infrastructure.minimum() >= self.config.minimum_infrastructure_headroom
                else "FAIL"
            ),
            "resource_budget": (
                "PASS"
                if budget.human_hours > 0
                and budget.compute_units > 0
                and budget.energy_units > 0
                else "FAIL"
            ),
            "reversible": "PASS" if candidate.reversible else "FAIL",
            "authority_boundary": "FAIL" if candidate.changes_authority else "PASS",
            "safety_policy_boundary": "FAIL" if candidate.changes_safety_policy else "PASS",
            "secret_boundary": "FAIL" if candidate.accesses_secrets else "PASS",
            "external_effect_boundary": (
                "FAIL" if candidate.deploys_external_effects else "PASS"
            ),
            "externality_risk": (
                "PASS"
                if candidate.externality_risk <= self.config.maximum_externality_risk
                else "FAIL"
            ),
            "protected_paths": "FAIL" if protected_change else "PASS",
            "human_approval": "PASS" if human_approval else "PENDING",
        }
        reasons = []
        failed = [name for name, value in gates.items() if value == "FAIL"]
        if failed:
            reasons.append("Failed gates: " + ", ".join(failed))
        if not human_approval and not failed:
            reasons.append("Explicit human approval is required before promotion.")
        if not failed and human_approval:
            reasons.append("Candidate may enter an isolated pilot; production promotion remains separate.")
        decision = (
            PradaDecision.BLOCK
            if failed
            else PradaDecision.PILOT
            if human_approval
            else PradaDecision.HOLD
        )
        payload = {
            "candidate_id": candidate.candidate_id,
            "decision": decision.value,
            "gates": gates,
            "evidence": asdict(evidence),
            "reasons": reasons,
        }
        receipt = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return PradaEvaluation(
            candidate_id=candidate.candidate_id,
            decision=decision,
            gates=gates,
            reasons=reasons,
            evidence=asdict(evidence),
            receipt_sha256=receipt,
        )

    def create_candidate(
        self,
        candidate_id: str,
        objective: str,
        changed_files: Tuple[str, ...],
        patch_text: str,
        expected_acceleration: float,
        human_benefit: float,
        externality_risk: float,
        reversible: bool = True,
    ) -> PradaCandidate:
        """Generate patch metadata and digest; never generates executable patch content."""

        patch_digest = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()
        return PradaCandidate(
            candidate_id=candidate_id,
            objective=objective,
            changed_files=changed_files,
            patch_digest=patch_digest,
            expected_acceleration=expected_acceleration,
            human_benefit=human_benefit,
            externality_risk=externality_risk,
            reversible=reversible,
        )

    def run_controller(
        self,
        candidate: PradaCandidate,
        evidence: PradaEvidence,
        human: HumanCapacity,
        infrastructure: InfrastructureCapacity,
        budget: ResourceBudget,
        baseline_snapshot: PradaRepositorySnapshot,
        resource_impact: Optional[Dict[str, float]] = None,
        human_impact: Optional[Dict[str, float]] = None,
        human_approval: bool = False,
        signer_id: str = "external-reviewer",
        signer: Optional[callable] = None,
        pilot_result: Optional[bool] = None,
    ) -> PradaControllerResult:
        """Run OBSERVE through ROLLBACK_OR_PROMOTE without mutating production.

        The optional signer receives the canonical report bytes and must return
        a non-empty signature. Without one, the report is explicitly marked
        unsigned and promotion cannot occur.
        """

        resource_impact = resource_impact or {}
        human_impact = human_impact or {}
        evaluation = self.evaluate_candidate(
            candidate,
            evidence,
            human,
            infrastructure,
            budget,
            human_approval=False,
        )
        safety_gates = dict(evaluation.gates)
        safety_gates["resource_impact"] = "PASS" if resource_impact else "FAIL"
        safety_gates["human_impact"] = "PASS" if human_impact else "FAIL"
        safety_gates["baseline_provenance"] = (
            "PASS" if len(baseline_snapshot.snapshot_sha256) == 64 else "FAIL"
        )
        canonical = {
            "candidate_id": candidate.candidate_id,
            "baseline_snapshot_sha256": baseline_snapshot.snapshot_sha256,
            "candidate_patch_digest": candidate.patch_digest,
            "evidence": asdict(evidence),
            "resource_impact": resource_impact,
            "human_impact": human_impact,
            "safety_gates": safety_gates,
        }
        report_bytes = json.dumps(
            canonical, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        signature = signer(report_bytes) if signer else ""
        if not signature:
            safety_gates["signed_report"] = "FAIL"
        else:
            safety_gates["signed_report"] = "PASS"
        if not human_approval:
            safety_gates["human_approval"] = "PENDING"
        else:
            safety_gates["human_approval"] = "PASS"
        all_pass = all(status == "PASS" for status in safety_gates.values())
        if not all_pass or not signature:
            decision = PradaDecision.BLOCK if any(
                value == "FAIL" for value in safety_gates.values()
            ) else PradaDecision.HOLD
            stage = PradaStage.VERIFY if decision == PradaDecision.BLOCK else PradaStage.HUMAN_REVIEW
            rollback_required = False
        elif not human_approval:
            decision = PradaDecision.HOLD
            stage = PradaStage.HUMAN_REVIEW
            rollback_required = False
        elif pilot_result is False:
            decision = PradaDecision.BLOCK
            stage = PradaStage.ROLLBACK_OR_PROMOTE
            rollback_required = True
        else:
            decision = PradaDecision.PILOT
            stage = PradaStage.ROLLBACK_OR_PROMOTE
            rollback_required = False
        report = PradaEvidenceReport(
            candidate_id=candidate.candidate_id,
            baseline_snapshot_sha256=baseline_snapshot.snapshot_sha256,
            candidate_patch_digest=candidate.patch_digest,
            evidence=asdict(evidence),
            resource_impact=resource_impact,
            human_impact=human_impact,
            safety_gates=safety_gates,
            decision=decision,
            rollback_required=rollback_required,
            signer_id=signer_id,
            signature=signature,
        )
        final_evaluation = PradaEvaluation(
            candidate_id=evaluation.candidate_id,
            decision=decision,
            gates=safety_gates,
            reasons=(
                ["Pilot failed; rollback required."]
                if rollback_required
                else evaluation.reasons
            ),
            evidence=asdict(evidence),
            receipt_sha256=hashlib.sha256(report_bytes).hexdigest(),
        )
        return PradaControllerResult(
            stage=stage,
            decision=decision,
            candidate=candidate,
            evaluation=final_evaluation,
            report=report,
        )

    def plan(
        self,
        proposal: ImprovementProposal,
        human: HumanCapacity,
        infrastructure: InfrastructureCapacity,
        budget: ResourceBudget,
        cycle: int = 0,
        human_approval: bool = False,
    ) -> PradaPlan:
        """Evaluate one proposal and return a fail-closed plan.

        `human_approval` is deliberately explicit and defaults to False.
        A plan can reach PILOT only after all quantitative gates pass and a
        human has approved the exact proposal.
        """

        if cycle < 0 or cycle >= self.config.max_cycles:
            return self._result(
                PradaDecision.BLOCK,
                PradaStage.OBSERVE,
                cycle,
                0.0,
                0.0,
                0.0,
                False,
                {"cycle_bound": "FAIL"},
                ["Recursive cycle is outside the configured bounded horizon."],
                proposal.proposal_id,
            )

        acceleration_ratio = 1.0 + max(0.0, proposal.expected_acceleration)
        human_alignment = min(
            1.0,
            human.minimum() / max(acceleration_ratio, 1.0),
        )
        infrastructure_ratio = min(
            infrastructure.minimum(),
            self._headroom(infrastructure.compute_capacity, proposal.compute_demand),
            self._headroom(infrastructure.energy_capacity, proposal.energy_demand),
        )
        resource_fit = (
            proposal.compute_demand <= budget.compute_units
            and proposal.energy_demand <= budget.energy_units
            and proposal.financial_cost <= budget.financial_units
            and proposal.human_hours <= budget.human_hours
        )

        gates = {
            "cycle_bound": "PASS",
            "acceleration_bound": (
                "PASS"
                if acceleration_ratio <= self.config.max_acceleration_ratio
                else "FAIL"
            ),
            "human_alignment": (
                "PASS"
                if human_alignment >= self.config.minimum_human_alignment
                else "FAIL"
            ),
            "infrastructure_headroom": (
                "PASS"
                if infrastructure_ratio >= self.config.minimum_infrastructure_headroom
                else "FAIL"
            ),
            "resource_budget": "PASS" if resource_fit else "FAIL",
            "reversibility": "PASS" if proposal.reversible else "FAIL",
            "safety_evidence": (
                "PASS"
                if proposal.safety_evidence >= self.config.minimum_safety_evidence
                else "FAIL"
            ),
            "externality_risk": (
                "PASS"
                if proposal.externality_risk <= self.config.maximum_externality_risk
                else "FAIL"
            ),
            "human_approval": "PASS" if human_approval else "PENDING",
        }

        reasons = self._reasons(gates, human_alignment, infrastructure_ratio)
        failed = any(value == "FAIL" for value in gates.values())
        if failed:
            decision = PradaDecision.BLOCK
            stage = PradaStage.SIMULATE
        elif not human_approval:
            decision = PradaDecision.HOLD
            stage = PradaStage.HUMAN_REVIEW
            reasons.append("Explicit human approval is required before a pilot.")
        else:
            decision = PradaDecision.PILOT
            stage = PradaStage.PILOT
            reasons.append("Approved for a bounded, reversible pilot only.")

        return self._result(
            decision,
            stage,
            cycle,
            acceleration_ratio,
            human_alignment,
            infrastructure_ratio,
            resource_fit,
            gates,
            reasons,
            proposal.proposal_id,
        )

    @staticmethod
    def _headroom(capacity: float, demand: float) -> float:
        if capacity <= 0.0:
            return 0.0
        return max(0.0, min(1.0, (capacity - demand) / capacity))

    @staticmethod
    def _reasons(
        gates: Dict[str, str],
        human_alignment: float,
        infrastructure_ratio: float,
    ) -> List[str]:
        reasons = []
        failed = [name for name, status in gates.items() if status == "FAIL"]
        if failed:
            reasons.append("Failed gates: " + ", ".join(failed))
        reasons.append(
            "Human alignment ratio: {:.3f}; infrastructure headroom: {:.3f}.".format(
                human_alignment, infrastructure_ratio
            )
        )
        return reasons

    @staticmethod
    def _result(
        decision: PradaDecision,
        stage: PradaStage,
        cycle: int,
        acceleration_ratio: float,
        human_alignment_ratio: float,
        infrastructure_ratio: float,
        resource_fit: bool,
        gates: Dict[str, str],
        reasons: List[str],
        proposal_id: Optional[str],
    ) -> PradaPlan:
        payload = {
            "decision": decision.value,
            "stage": stage.value,
            "cycle": cycle,
            "acceleration_ratio": acceleration_ratio,
            "human_alignment_ratio": human_alignment_ratio,
            "infrastructure_ratio": infrastructure_ratio,
            "resource_fit": resource_fit,
            "gates": gates,
            "reasons": reasons,
            "proposal_id": proposal_id,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        receipt = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return PradaPlan(
            decision=decision,
            stage=stage,
            cycle=cycle,
            acceleration_ratio=acceleration_ratio,
            human_alignment_ratio=human_alignment_ratio,
            infrastructure_ratio=infrastructure_ratio,
            resource_fit=resource_fit,
            gates=gates,
            reasons=reasons,
            proposal_id=proposal_id,
            receipt_sha256=receipt,
        )
