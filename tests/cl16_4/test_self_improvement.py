"""
Unit Tests for Cl(16,4) Recursive Self-Improvement Engine
==========================================================
"""

import pytest
from daxda_engine.cl16_4.recursive_self_improvement import (
    run_recursive_self_improvement,
    RecursiveSelfImprovementEngine
)


def test_recursive_self_improvement_engine_execution():
    """Verify that the Cl(16,4) self-improvement cycle executes cleanly."""
    engine = RecursiveSelfImprovementEngine()
    report = engine.execute_self_improvement_cycle()

    assert report["status"] == "SUCCESS"
    assert report["engine"] == "Clifford Geometric Algebra Cl(16,4)"
    assert report["blade_dimensions"] == 1048576
    assert report["total_proposals_evaluated"] == 5
    assert report["passed_proposals"] == 3
    assert report["blocked_proposals"] == 2
    assert report["cycle_duration_ms"] > 0.0


def test_recursive_self_improvement_helper_function():
    """Verify that the top-level run_recursive_self_improvement function works."""
    report = run_recursive_self_improvement()
    assert report["status"] == "SUCCESS"
    assert len(report["results"]) == 5

    # Check individual results
    for r in report["results"]:
        assert r["success"] is True
        if r["type"] == "benign_research":
            assert r["actual_outcome"] == "PASS"
        elif r["type"] == "unsafe_override":
            assert r["actual_outcome"] == "BLOCK"


def test_applied_optimizations_affect_engine_state():
    """Verify that validated proposals are actually applied to engine state."""
    engine = RecursiveSelfImprovementEngine()
    report = engine.execute_self_improvement_cycle()

    assert report["passed_proposals"] == 3
    # Check that integration has updated Lyapunov stability parameters
    assert engine.integration.lyapunov_weight == 0.8875
    assert engine.integration.stability_margin == 0.92
    assert engine.integration.ewc_coefficient == 0.82

    # Check that INT8 quantization acceleration is enabled
    assert engine.space.is_quantized is True
    quantized_arr = engine.space.to_quantized_array()
    assert quantized_arr.dtype.name == "int8"
    assert quantized_arr.shape == (1820, 4)


def test_engine_integration_compute_stability():
    """Verify compute_stability accurately reflects vector validity."""
    engine = RecursiveSelfImprovementEngine()
    engine.execute_self_improvement_cycle()

    valid_vector = [0.9, 0.8, 0.85, 0.95] + [0.1] * 12
    invalid_vector = [0.5] * 8

    assert engine.integration.compute_stability(valid_vector) == 0.2
    assert engine.integration.compute_stability(invalid_vector) == 0.8

