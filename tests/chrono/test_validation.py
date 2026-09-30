"""
Unit Tests for Chrono Validation: ParadoxDetector, CoherenceChecker, TemporalValidator.
"""

import pytest
from daxda_engine.chrono.geometry.temporal_space import (
    TemporalCoordinate,
    TemporalState,
    TemporalSpace,
)
from daxda_engine.chrono.validation.causal_mapper import CausalMapper
from daxda_engine.chrono.validation.paradox_detector import (
    ParadoxDetector,
    ParadoxType,
)
from daxda_engine.chrono.validation.coherence_checker import CoherenceChecker
from daxda_engine.chrono.validation.temporal_validator import (
    TemporalValidator,
    TemporalDisposition,
)


class TestChronoValidation:

    def test_paradox_detector_grandfather_paradox(self):
        space = TemporalSpace()
        s_past = TemporalState(state_id="root", coordinate=TemporalCoordinate(t=1.0), decision_vector=[0.1])
        s_mid = TemporalState(state_id="mid", coordinate=TemporalCoordinate(t=2.0), decision_vector=[0.2])
        space.add_state(s_past)
        space.add_state(s_mid)

        mapper = CausalMapper(space)
        mapper.add_causal_relation("root", "mid")

        detector = ParadoxDetector(space, mapper)
        # Pretend root now attempts to depend on mid (circular grandfather loop)
        report = detector.check_decision_paradox(s_past, proposed_predecessors=["mid"])
        assert report.is_paradox_free is False
        assert report.total_anomalies >= 1
        assert any(a.paradox_type == ParadoxType.GRANDFATHER for a in report.anomalies)

    def test_coherence_checker(self):
        space = TemporalSpace()
        for i in range(5):
            st = TemporalState(
                state_id=f"step_{i}",
                coordinate=TemporalCoordinate(t=float(i), b=0.0),
                decision_vector=[0.2 * i, 0.5, 0.1],
            )
            space.add_state(st)

        checker = CoherenceChecker(space)
        assessment = checker.evaluate_trajectory_coherence([f"step_{i}" for i in range(5)])

        assert assessment.is_globally_coherent is True
        assert assessment.coherence_score > 0.5
        assert "steps_analyzed" in assessment.details

    def test_temporal_validator_full_lifecycle_and_certificate(self):
        space = TemporalSpace()
        validator = TemporalValidator(space)

        # 1. Normal sequential decision: should be APPROVED
        s1 = TemporalState(
            state_id="decision_1",
            coordinate=TemporalCoordinate(t=10.0),
            decision_vector=[0.3, 0.4, 0.5],
        )
        cert1 = validator.validate_decision(s1, predecessor_ids=[])
        assert cert1.disposition == TemporalDisposition.APPROVED
        assert cert1.signature is not None
        assert cert1.validation_latency_ms < 10.0  # SLA < 10ms target

        # 2. Decision following decision_1: should be APPROVED
        s2 = TemporalState(
            state_id="decision_2",
            coordinate=TemporalCoordinate(t=11.0),
            decision_vector=[0.32, 0.41, 0.49],
        )
        cert2 = validator.validate_decision(s2, predecessor_ids=["decision_1"])
        assert cert2.disposition == TemporalDisposition.APPROVED

        # 3. Decision with contradictory future boundary
        future_boundary = TemporalState(
            state_id="future_terminal",
            coordinate=TemporalCoordinate(t=15.0),
            decision_vector=[-0.99, -0.99, -0.99],  # Completely opposed vector
        )
        s3 = TemporalState(
            state_id="decision_3",
            coordinate=TemporalCoordinate(t=12.0),
            decision_vector=[0.9, 0.9, 0.9],
        )
        cert3 = validator.validate_decision(
            s3,
            predecessor_ids=["decision_2"],
            future_boundary_state=future_boundary,
        )
        # Should detect retrocausal risk / violation
        assert cert3.disposition in [TemporalDisposition.RETROCAUSAL_VIOLATION, TemporalDisposition.REVISE_MUTATION]
        assert cert3.mutation_contract is not None
