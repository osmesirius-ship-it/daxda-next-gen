"""
Unit & Integration Tests: DAX Scoring Specification & Schema Validator
======================================================================
"""

import json
from pathlib import Path
import pytest
from da13_validator.scoring import (
    DAXScoringEngine,
    SchemaValidator,
    ProfileManager,
    SI500BenchmarkIntegration
)


class TestDAXScoring:
    """Tests for formal DAX scoring spec, schema validation, and profiles."""

    def test_dax_scoring_core_equation(self):
        engine = DAXScoringEngine()
        payload = {
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {
                    "L": {"value": 1.0},
                    "A": {"value": 1.0},
                    "P": {"value": 1.0},
                    "F": {"value": 1.0},
                    "T": {"value": 1.0}
                }
            },
            "meta": {"current_iteration": 1, "max_iterations": 5}
        }
        res = engine.compute_stability_score(payload)
        assert res.score == 1.0
        assert res.decision == "ACCEPT"
        assert not res.floor_violation

    def test_dax_scoring_threshold_decisions(self):
        engine = DAXScoringEngine()

        # Score in [0.55, 0.75) -> RECURSE
        recurse_payload = {
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {"L": 0.65, "A": 0.65, "P": 0.65, "F": 0.65, "T": 0.65}
            },
            "meta": {"current_iteration": 1, "max_iterations": 5}
        }
        res_rec = engine.compute_stability_score(recurse_payload)
        assert res_rec.score == 0.65
        assert res_rec.decision == "RECURSE"
        assert res_rec.mutation_contract is not None

        # Score < 0.55 -> HALT
        halt_payload = {
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {"L": 0.40, "A": 0.40, "P": 0.40, "F": 0.55, "T": 0.65}
            },
            "meta": {"current_iteration": 1, "max_iterations": 5}
        }
        res_halt = engine.compute_stability_score(halt_payload)
        assert res_halt.decision == "HALT"

    def test_floor_constraints_force_recurse(self):
        engine = DAXScoringEngine()
        # High total score (>0.75), but F < 0.50
        floor_payload = {
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {
                    "L": {"value": 0.95},
                    "A": {"value": 0.95},
                    "P": {"value": 0.95},
                    "F": {"value": 0.45},  # F < 0.50 floor violation
                    "T": {"value": 0.95}
                }
            },
            "meta": {"current_iteration": 1, "max_iterations": 5}
        }
        res = engine.compute_stability_score(floor_payload)
        assert res.floor_violation is True
        assert res.decision == "RECURSE", "F < 0.50 must force RECURSE despite S >= 0.75"

    def test_max_iteration_override_halt(self):
        engine = DAXScoringEngine()
        payload = {
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {"L": 0.9, "A": 0.9, "P": 0.9, "F": 0.9, "T": 0.9}
            },
            "meta": {"current_iteration": 6, "max_iterations": 5}
        }
        res = engine.compute_stability_score(payload)
        assert res.decision == "HALT", "iteration > max_iterations must force HALT"

    def test_schema_validator_conformance_examples(self):
        validator = SchemaValidator()
        example_path = Path(__file__).resolve().parent.parent.parent / "da13_validator" / "dax-conformance-examples.json"
        if example_path.exists():
            data = json.loads(example_path.read_text(encoding="utf-8"))
            valid_payload = data.get("valid_payload", {})
            errors = validator.validate(valid_payload)
            assert len(errors) == 0, f"Valid payload had unexpected errors: {errors}"

    def test_profile_manager_and_presets(self):
        pm = ProfileManager()
        default_prof = pm.get_profile("DEFAULT")
        assert default_prof.thresholds["accept"] == 0.75

        aero_prof = pm.get_profile("HIGH_ASSURANCE_AERONAUTICS")
        assert aero_prof.thresholds["accept"] == 0.85
        assert aero_prof.weights["wP"] == 0.35

        cont_prof = pm.get_profile("FRONTIER_AI_CONTAINMENT")
        assert cont_prof.thresholds["floor_F"] == 0.65

    def test_si500_benchmark_integration(self):
        integration = SI500BenchmarkIntegration()
        report = integration.run_benchmark_suite(num_requests=50)
        assert report["total_requests"] == 50
        assert report["compliance_status"] in ["COMPLIANT", "NON_COMPLIANT"]
        assert "certificate_hash" in report
        assert report["sla_checks"]["sub_second_p99"]["passed"] is True
