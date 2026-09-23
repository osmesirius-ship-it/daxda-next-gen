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
