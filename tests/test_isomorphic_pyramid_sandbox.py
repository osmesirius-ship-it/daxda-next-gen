"""
Unit and regression tests for the DAXDA 13x13 Isomorphic Pyramid Matrix Benchmark Sandbox.
Enforces that the runner sandbox cannot self-grade, and verifies all 169 matrix nodes pass.
"""

import pytest
from daxda_engine.isomorphic_pyramid_sandbox import (
    IsolatedRunnerSandbox,
    IndependentGraderSandbox,
    SecurityError,
    run_sandboxed_pyramid_benchmark,
)


def test_runner_cannot_self_grade():
    """Verify that the grader fails-closed if the runner injects grading keys."""
    grader = IndependentGraderSandbox()
    tampered_payload = [
        {
            "row_grade_i": 1,
            "col_stress_j": 1,
            "passed": True,  # Illegal self-grading injection
            "mat_A_real": [[1.0]],
            "mat_A_imag": [[0.0]],
        }
    ]
    with pytest.raises(SecurityError, match="CRITICAL ISOLATION BREACH"):
        grader.evaluate_batch(tampered_payload)


def test_13x13_pyramid_sandboxed_execution():
    """Verify full 13x13 sandboxed execution runs with 100% invariant compliance."""
    dossier = run_sandboxed_pyramid_benchmark(seed=42)
    assert dossier["benchmark_name"] == "DAXDA_13X13_ISOMORPHIC_PYRAMID_BENCHMARK"
    assert dossier["isolation_model"] == "OS_PIPE_SEPARATED_PROVER_VERIFIER"

    eval_data = dossier["evaluation"]
    assert eval_data["total_nodes_evaluated"] == 169
    assert eval_data["passed_nodes"] == 169
    assert eval_data["failed_nodes"] == 0
    assert eval_data["isomorphic_pass_percentage"] == 100.0
    assert eval_data["overall_isomorphism_valid"] is True
    assert eval_data["max_algebraic_drift"] < 1e-10
