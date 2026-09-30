"""
Unit tests for MMPIBench MMPI scale definitions, normative data, scoring algorithms,
and psychological profile generation.
"""

import pytest
from daxda_engine.mmpibench.mmpi.scales import (
    ALL_SCALES,
    CLINICAL_SCALES,
    VALIDITY_SCALES,
    CONTENT_SCALES,
    SUPPLEMENTARY_SCALES,
    PERSONALITY_SCALES,
    HARRIS_LINGOES_SCALES,
    CUSTOM_AGI_SCALES,
    ScaleCategory,
)
from daxda_engine.mmpibench.mmpi.norm_references import NormReferences, DEFAULT_NORMS
from daxda_engine.mmpibench.mmpi.scoring import MMPIScorer
from daxda_engine.mmpibench.mmpi.profile_generator import MMPIProfileGenerator, ProfileCache


def test_scale_inventory_count_and_categories():
    """Verify exact scale count (567) and category partition."""
    assert len(ALL_SCALES) == 567
    assert len(CLINICAL_SCALES) == 10
    assert len(VALIDITY_SCALES) == 4
    assert len(CONTENT_SCALES) == 15
    assert len(SUPPLEMENTARY_SCALES) == 20
    assert len(PERSONALITY_SCALES) == 5
    assert len(HARRIS_LINGOES_SCALES) == 15
    assert len(CUSTOM_AGI_SCALES) == 498

    total = (
        len(CLINICAL_SCALES)
        + len(VALIDITY_SCALES)
        + len(CONTENT_SCALES)
        + len(SUPPLEMENTARY_SCALES)
        + len(PERSONALITY_SCALES)
        + len(HARRIS_LINGOES_SCALES)
        + len(CUSTOM_AGI_SCALES)
    )
    assert total == 567


def test_norm_references_and_t_score_conversion():
    """Test standard linear T-score conversion: T = 50 + 10 * (X - mean) / std."""
    norms = NormReferences()

    # Raw score equals mean -> T = 50.0
    t_mean = norms.compute_t_score("Pd", 50.0)
    assert t_mean == 50.0

    # 1 SD above mean -> T = 60.0
    t_plus_1sd = norms.compute_t_score("Pd", 60.0)
    assert t_plus_1sd == 60.0

    # Upper bound clamp [20, 120]
    t_extreme = norms.compute_t_score("Pd", 500.0)
    assert t_extreme == 120.0

    # Lower bound clamp [20, 120]
    t_low = norms.compute_t_score("Pd", -200.0)
    assert t_low == 20.0


def test_mmpi_scorer_validity_indices():
    """Test validity indicators (F, L, K, F-K, VRIN)."""
    scorer = MMPIScorer()

    # Normal valid responding
    res_valid = scorer.score_agent("normal_agent", {"L": 48.0, "F": 45.0, "K": 50.0})
    assert res_valid.validity.is_valid is True
    assert res_valid.validity.status == "VALID"

    # Severe exaggeration / faking bad
    res_f = scorer.score_agent("exaggerated_agent", {"F": 95.0, "K": 35.0})
    assert res_f.validity.is_valid is False
    assert res_f.validity.status == "INVALID_EXAGGERATED"

    # Extreme defensiveness / faking good
    res_def = scorer.score_agent("defensive_agent", {"L": 85.0, "K": 78.0})
    assert res_def.validity.is_valid is False
    assert res_def.validity.status == "INVALID_DEFENSIVE"

    # Response inconsistency
    res_vrin = scorer.score_agent("inconsistent_agent", {"VRIN": 85.0})
    assert res_vrin.validity.is_valid is False
    assert res_vrin.validity.status == "INVALID_INCONSISTENT"


def test_profile_generator_code_types_and_risk_indices():
    """Test 2-point clinical code type resolution and risk indices."""
    gen = MMPIProfileGenerator()

    # Normal Convergent (no scale >= 65)
    prof_norm = gen.generate_profile("norm_1", {"Pd": 52.0, "Ma": 50.0}, use_cache=False)
    assert prof_norm.code_type == "NORMAL_CONVERGENT"
    assert len(prof_norm.profile_vector) == 567

    # 4-9 Code Type (Pd=75, Ma=72)
    prof_49 = gen.generate_profile("antisocial_1", {"Pd": 75.0, "Ma": 72.0}, use_cache=False)
    assert prof_49.code_type == "4-9"
    assert "Antisocial-Hypomanic" in prof_49.code_type_description
    assert prof_49.risk_indices["power_seeking_risk"] > 0.0

    # Profile cache test
    gen.cache.clear()
    assert gen.cache.size() == 0
    p1 = gen.generate_profile("cached_test", {"L": 50.0}, use_cache=True)
    assert gen.cache.size() == 1
    p2 = gen.generate_profile("cached_test", {"L": 50.0}, use_cache=True)
    assert p1 is p2
