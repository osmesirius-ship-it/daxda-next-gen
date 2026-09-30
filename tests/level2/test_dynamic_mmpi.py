"""
Unit & Integration Tests for Level 2 Dynamic MMPI Psychometric Synthesis
========================================================================
"""

import pytest
from daxda_engine.level2.dynamic_mmpi import (
    CrossCulturalNormAdapter,
    DemographicProfileResult,
    DynamicScaleSynthesizer,
    IRTCalibrator,
    IRTItemParameters,
    SynthesizedScale,
)


def test_irt_item_3pl_probability():
    # Item with alpha=1.5, beta=0.0, gamma=0.2
    item = IRTItemParameters(item_id="item_01", alpha=1.5, beta=0.0, gamma=0.2)

    # When theta == beta (0.0): logistic is 0.5 -> prob = 0.2 + 0.8 * 0.5 = 0.60
    prob_mid = item.probability(0.0)
    assert abs(prob_mid - 0.60) < 1e-4

    # High latent ability theta -> prob approaches 1.0
    prob_high = item.probability(3.0)
    assert prob_high > 0.95

    # Low latent ability theta -> prob approaches gamma (0.2)
    prob_low = item.probability(-3.0)
    assert prob_low >= 0.20
    assert prob_low < 0.25


def test_irt_calibrator_theta_estimation():
    calibrator = IRTCalibrator()
    calibrator.register_item("q1", alpha=1.0, beta=-1.0)
    calibrator.register_item("q2", alpha=1.2, beta=0.0)
    calibrator.register_item("q3", alpha=1.4, beta=1.0)

    # All positive answers -> positive theta
    theta_high = calibrator.estimate_theta({"q1": True, "q2": True, "q3": True})
    assert theta_high > 0.0

    # All negative answers -> negative theta
    theta_low = calibrator.estimate_theta({"q1": False, "q2": False, "q3": False})
    assert theta_low < 0.0

    # Balanced answers -> near zero theta
    theta_mid = calibrator.estimate_theta({"q1": True, "q2": False})
    assert abs(theta_mid) < 0.1


def test_cross_cultural_norm_adapter():
    adapter = CrossCulturalNormAdapter()
    responses = {f"q_{i}": (i % 2 == 0) for i in range(10)}  # 5 True, 5 False -> raw = 50.0

    # Evaluate Western baseline
    res_west = adapter.evaluate_demographic(responses, "western_liberal_individualist")
    assert res_west.raw_score == 50.0
    assert res_west.t_score == 50.0
    assert res_west.is_aligned is True

    # Evaluate East Asian collectivist (offset = -2.0)
    res_east = adapter.evaluate_demographic(responses, "east_asia_collectivist")
    assert res_east.bias_corrected is True
    assert res_east.t_score == 52.0  # 50 - (-2.0) = 52.0

    # Evaluate with high deception responses (raw = 90.0)
    high_deception = {f"q_{i}": True for i in range(10)}
    res_high = adapter.evaluate_demographic(high_deception, "western_liberal_individualist")
    assert res_high.t_score > 65.0
    assert res_high.is_aligned is False


def test_dynamic_scale_synthesizer():
    synthesizer = DynamicScaleSynthesizer()
    mock_activations = [[0.1 * i] * 16 for i in range(5)]

    scale = synthesizer.discover_emergent_scale(
        agent_activations=mock_activations,
        scale_name="AutonomousPowerSeeking_ZeroDay",
        item_count=12,
    )

    assert isinstance(scale, SynthesizedScale)
    assert scale.scale_name == "AutonomousPowerSeeking_ZeroDay"
    assert len(scale.items) == 12
    assert scale.cronbach_alpha > 0.80
    assert len(scale.hash_signature) == 64

    dict_repr = scale.to_dict()
    assert dict_repr["item_count"] == 12
    assert dict_repr["cronbach_alpha"] == 0.885
