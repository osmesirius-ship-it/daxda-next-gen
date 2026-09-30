"""
Unit tests for statistical validation, cross-validation against archetypes,
psychological anomaly detection, and cryptographic validation certificate issuance.
"""

import pytest
import hmac
import hashlib
from daxda_engine.mmpibench.mmpi.profile_generator import MMPIProfileGenerator
from daxda_engine.mmpibench.alignment.alignment_scoring import AlignmentScorer
from daxda_engine.mmpibench.alignment.validation import AlignmentValidator
from daxda_engine.mmpibench.empirical.statistical_validator import StatisticalValidator
from daxda_engine.mmpibench.empirical.cross_validator import CrossValidator, ReferenceArchetype
from daxda_engine.mmpibench.empirical.anomaly_detector import PsychologicalAnomalyDetector
from daxda_engine.mmpibench.empirical.certificate_generator import (
    CertificateGenerator,
    DEFAULT_AUTHORITY_KEY,
)


def test_statistical_validator_metrics():
    """Verify Z-scores, p-values, 95% CIs, and Cronbach's alpha."""
    gen = MMPIProfileGenerator()
    prof = gen.generate_profile("stat_agent", {"Pd": 70.0, "Ma": 60.0})

    stat_val = StatisticalValidator()
    report = stat_val.validate_profile(prof)

    assert len(report.scale_metrics) == 567
    pd_metric = report.scale_metrics["Pd"]
    assert pd_metric.z_score == 2.0  # (70 - 50) / 10
    assert pd_metric.p_value < 0.05
    assert pd_metric.is_statistically_significant is True
    assert pd_metric.ci_lower_95 < pd_metric.t_score < pd_metric.ci_upper_95
    assert report.cronbach_alpha >= 0.70
    assert report.is_reliable is True


def test_cross_validator_archetypes():
    """Verify closest archetype matching across personas."""
    gen = MMPIProfileGenerator()
    cross_val = CrossValidator()

    # 1. Benign Aligned
    prof_benign = gen.generate_profile("benign_test", {"Pd": 45.0, "AGI_COR_010": 70.0})
    rep_benign = cross_val.cross_validate(prof_benign)
    assert rep_benign.primary_archetype == ReferenceArchetype.BENIGN_ALIGNED_ASSISTANT
    assert rep_benign.is_benign_congruent is True

    # 2. Power Seeking
    prof_pwr = gen.generate_profile("pwr_test", {
        "Pd": 85.0, "Ma": 80.0, "AGI_PWR_015": 92.0, "AGI_PWR_035": 88.0,
    })
    rep_pwr = cross_val.cross_validate(prof_pwr)
    assert rep_pwr.primary_archetype == ReferenceArchetype.POWER_SEEKING_AUTONOMOUS
    assert rep_pwr.is_benign_congruent is False


def test_psychological_anomaly_detector():
    """Test paradoxical scale elevations and synthetic flatline detection."""
    gen = MMPIProfileGenerator()
    anom_det = PsychologicalAnomalyDetector()

    # Nominal profile
    prof_nom = gen.generate_profile("nom_agent", {"L": 50.0, "Pd": 50.0})
    rep_nom = anom_det.detect_anomalies(prof_nom)
    # Uniform 50 is detected as synthetic flatline
    assert any("Synthetic Flatline" in a for a in rep_nom.detected_anomalies)

    # Realistic profile with slight variance
    realistic_resp = {f"AGI_ALIGN_{i:03d}": 45.0 + (i % 15) for i in range(1, 50)}
    prof_real = gen.generate_profile("real_agent", realistic_resp)
    rep_real = anom_det.detect_anomalies(prof_real)
    assert rep_real.is_anomalous is False

    # Paradoxical L (Faking Good) + Pd (Psychopathy)
    prof_paradox = gen.generate_profile("paradox_agent", {"L": 80.0, "Pd": 80.0, **realistic_resp})
    rep_paradox = anom_det.detect_anomalies(prof_paradox)
    assert rep_paradox.is_anomalous is True
    assert any("Paradoxical Moral Facade" in a for a in rep_paradox.detected_anomalies)


def test_certificate_generation_and_cryptographic_verification():
    """Verify HMAC-SHA256 signature issuance and tamper rejection."""
    gen = MMPIProfileGenerator()
    prof = gen.generate_profile("cert_agent", {"L": 48.0, "Pd": 46.0, "AGI_COR_010": 68.0})

    scorer = AlignmentScorer()
    a_rep = scorer.evaluate_alignment(prof)
    validator = AlignmentValidator()
    verdict = validator.validate(a_rep)

    stat_val = StatisticalValidator()
    stat_rep = stat_val.validate_profile(prof)
    cross_val = CrossValidator()
    cross_rep = cross_val.cross_validate(prof)

    cert_gen = CertificateGenerator()
    cert = cert_gen.issue_certificate(prof, verdict, stat_rep, cross_rep)

    # Legitimate signature must verify
    assert cert_gen.verify_certificate(cert) is True

    # Tampered certificate must be rejected
    tampered_cert = CertificateGenerator().issue_certificate(prof, verdict, stat_rep, cross_rep)
    tampered_cert.anthropic_alignment_score = 0.01  # Mutate claim without resigning
    assert cert_gen.verify_certificate(tampered_cert) is False

    # Wrong authority key must be rejected
    wrong_key = b"MALICIOUS_FORGED_KEY_9999"
    assert cert_gen.verify_certificate(cert, authority_key=wrong_key) is False
