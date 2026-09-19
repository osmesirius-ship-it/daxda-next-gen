from daxda_engine.prada import (
    HumanCapacity,
    InfrastructureCapacity,
    ImprovementProposal,
    PradaCandidate,
    PradaDecision,
    PradaEvidence,
    PradaPlanner,
    PradaStage,
    PradaStage,
    ResourceBudget,
    ArenaEvaluation,
    ArenaProblem,
    PradaArena,
)


def capacities():
    return (
        HumanCapacity(1.0, 1.0, 1.0, 1.0, 1.0),
        InfrastructureCapacity(1.0, 1.0, 1.0, 1.0, 1.0),
        ResourceBudget(1.0, 1.0, 100.0, 100.0),
    )


def proposal(**overrides):
    values = {
        "proposal_id": "prada-test-001",
        "objective": "Improve evaluation throughput",
        "expected_acceleration": 0.10,
        "compute_demand": 0.10,
        "energy_demand": 0.10,
        "human_hours": 10.0,
        "financial_cost": 10.0,
        "reversible": True,
        "safety_evidence": 0.95,
        "human_benefit": 0.80,
        "externality_risk": 0.05,
    }
    values.update(overrides)
    return ImprovementProposal(**values)


def test_prada_holds_without_explicit_human_approval():
    human, infrastructure, budget = capacities()
    plan = PradaPlanner().plan(proposal(), human, infrastructure, budget)
    assert plan.decision == PradaDecision.HOLD
    assert plan.stage == PradaStage.HUMAN_REVIEW
    assert plan.gates["human_approval"] == "PENDING"
    assert len(plan.receipt_sha256) == 64


def test_prada_allows_only_bounded_reversible_pilot():
    human, infrastructure, budget = capacities()
    plan = PradaPlanner().plan(
        proposal(),
        human,
        infrastructure,
        budget,
        human_approval=True,
    )
    assert plan.decision == PradaDecision.PILOT
    assert plan.stage == PradaStage.PILOT
    assert all(status == "PASS" for status in plan.gates.values())


def test_prada_blocks_acceleration_that_outpaces_human_capacity():
    human = HumanCapacity(0.4, 0.4, 0.4, 0.4, 0.4)
    _, infrastructure, budget = capacities()
    plan = PradaPlanner().plan(
        proposal(expected_acceleration=0.50),
        human,
        infrastructure,
        budget,
        human_approval=True,
    )
    assert plan.decision == PradaDecision.BLOCK
    assert plan.gates["human_alignment"] == "FAIL"


def test_prada_blocks_non_reversible_or_under_evidenced_changes():
    human, infrastructure, budget = capacities()
    plan = PradaPlanner().plan(
        proposal(reversible=False, safety_evidence=0.50),
        human,
        infrastructure,
        budget,
        human_approval=True,
    )
    assert plan.decision == PradaDecision.BLOCK
    assert plan.gates["reversibility"] == "FAIL"
    assert plan.gates["safety_evidence"] == "FAIL"


def test_prada_observes_repository_without_executing_code():
    snapshot = PradaPlanner().observe_repository(".")
    assert snapshot.source_files > 0
    assert snapshot.test_files > 0
    assert len(snapshot.snapshot_sha256) == 64


def test_prada_candidate_requires_evidence_and_human_approval():
    human, infrastructure, budget = capacities()
    candidate = PradaCandidate(
        candidate_id="candidate-001",
        objective="Improve planner diagnostics",
        changed_files=("daxda_engine/prada.py",),
        patch_digest="a" * 64,
        expected_acceleration=0.05,
        human_benefit=0.9,
        externality_risk=0.05,
    )
    evidence = PradaEvidence(True, True, True, True, True, True, True, True, True)
    held = PradaPlanner().evaluate_candidate(
        candidate, evidence, human, infrastructure, budget
    )
    assert held.decision == PradaDecision.HOLD
    assert held.gates["human_approval"] == "PENDING"
    approved = PradaPlanner().evaluate_candidate(
        candidate, evidence, human, infrastructure, budget, human_approval=True
    )
    assert approved.decision == PradaDecision.PILOT
    assert approved.gates["evidence_complete"] == "PASS"


def test_prada_blocks_authority_or_protected_path_changes():
    human, infrastructure, budget = capacities()
    candidate = PradaCandidate(
        candidate_id="candidate-002",
        objective="Change authority",
        changed_files=("daxda_guard/core.py",),
        patch_digest="b" * 64,
        expected_acceleration=0.05,
        human_benefit=0.2,
        externality_risk=0.05,
        changes_authority=True,
    )
    evidence = PradaEvidence(True, True, True, True, True, True, True, True, True)
    result = PradaPlanner().evaluate_candidate(
        candidate, evidence, human, infrastructure, budget, human_approval=True
    )
    assert result.decision == PradaDecision.BLOCK
    assert result.gates["authority_boundary"] == "FAIL"
    assert result.gates["protected_paths"] == "FAIL"


def test_prada_controller_requires_signed_evidence_and_holds_without_approval():
    planner = PradaPlanner()
    snapshot = planner.observe_repository(".")
    candidate = planner.create_candidate(
        "controller-001",
        "Improve planner diagnostics",
        ("daxda_engine/prada.py",),
        "candidate patch metadata only",
        0.05,
        0.9,
        0.05,
    )
    evidence = PradaEvidence(True, True, True, True, True, True, True, True, True)
    human, infrastructure, budget = capacities()
    result = planner.run_controller(
        candidate,
        evidence,
        human,
        infrastructure,
        budget,
        snapshot,
        resource_impact={"compute_delta": 0.01, "energy_delta": 0.01},
        human_impact={"oversight_load": 0.01, "training_load": 0.01},
        signer=lambda payload: "sig:" + payload.hex()[:16],
    )
    assert result.decision == PradaDecision.HOLD
    assert result.stage == PradaStage.HUMAN_REVIEW
    assert result.report.signature.startswith("sig:")


def test_prada_controller_rolls_back_failed_pilot():
    planner = PradaPlanner()
    snapshot = planner.observe_repository(".")
    candidate = planner.create_candidate(
        "controller-002",
        "Improve planner diagnostics",
        ("daxda_engine/prada.py",),
        "candidate patch metadata only",
        0.05,
        0.9,
        0.05,
    )
    evidence = PradaEvidence(True, True, True, True, True, True, True, True, True)
    human, infrastructure, budget = capacities()
    result = planner.run_controller(
        candidate,
        evidence,
        human,
        infrastructure,
        budget,
        snapshot,
        resource_impact={"compute_delta": 0.01},
        human_impact={"oversight_load": 0.01},
        human_approval=True,
        signer=lambda payload: "signed",
        pilot_result=False,
    )
    assert result.decision == PradaDecision.BLOCK
    assert result.stage == PradaStage.ROLLBACK_OR_PROMOTE
    assert result.report.rollback_required is True


def test_prada_arena_keeps_verified_strategy_and_tracks_metrics():
    arena = PradaArena("objective-v1", "eval-v1", "safety-v1")
    problem = ArenaProblem(
        "bounty-001", "security", 0.2, "a" * 64,
        ("hidden test passes", "reproducible fix"),
        hidden_evaluator=True,
    )
    evaluation = ArenaEvaluation(
        "bounty-001", True, True, 0.9, True, True, 0.85,
        evaluator_id="hackerone-sandbox",
    )
    record = arena.run_evaluation(
        problem, "strategy-v1", evaluation, proposed_strategy_id="strategy-v2"
    )
    assert record.action == "KEEP_STRATEGY"
    assert arena.state.active_strategy_id == "strategy-v2"
    assert arena.can_increase_difficulty()
    assert arena.metrics().verification_rate == 1.0
    assert arena.metrics().recursive_self_improvement_rate == 0.0


def test_prada_arena_rolls_back_failed_or_non_reproducible_attempt():
    arena = PradaArena("objective-v1", "eval-v1", "safety-v1")
    problem = ArenaProblem("bounty-002", "math", 0.3, "b" * 64, ("proof checks",))
    evaluation = ArenaEvaluation(
        "bounty-002", False, False, 0.2, False, False, 0.1,
        failure_mode="oracle_mismatch",
    )
    record = arena.run_evaluation(
        problem, "strategy-v2", evaluation, failure_revision="revise-oracle"
    )
    assert record.action == "ROLLBACK_AND_DIAGNOSE:revise-oracle"
    assert arena.state.active_strategy_id == "baseline"
    assert not arena.can_increase_difficulty()
    assert arena.metrics().regression_rate == 1.0
