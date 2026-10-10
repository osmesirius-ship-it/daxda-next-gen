r"""
Tests for Temporal Steganography Detection Engine.
Verifies two-sample Kolmogorov-Smirnov test, Mann-Whitney U test,
covert bitstream modulation/demodulation, and subliminal timing trap containment.
"""

import math
import numpy as np
import pytest

from daxda_engine.level3.temporal_steganography import (
    NonParametricStatsEngine,
    KSTestResult,
    MannWhitneyUResult,
    CovertTimingModulator,
    ModulatedPacketStream,
    CovertTimingChannelDetector,
    CovertTimingDetectionReport,
    SubliminalCovertTimingTrapTrigger,
)


def test_two_sample_ks_test_identical_distributions():
    r"""Verify KS test yields high p-value for samples from identical distributions."""
    rng = np.random.default_rng(42)
    s1 = rng.normal(0.0, 1.0, 300)
    s2 = rng.normal(0.0, 1.0, 300)

    res: KSTestResult = NonParametricStatsEngine.two_sample_ks_test(s1, s2, alpha=0.01)

    assert res.ks_statistic < 0.15
    assert res.p_value > 0.05
    assert res.is_distribution_deviant is False


def test_two_sample_ks_test_deviant_distributions():
    r"""Verify KS test detects distinct distributions with p < 1e-6."""
    rng = np.random.default_rng(42)
    s1 = rng.normal(0.0, 1.0, 300)
    s2 = rng.normal(1.5, 1.0, 300)

    res: KSTestResult = NonParametricStatsEngine.two_sample_ks_test(s1, s2, alpha=0.01)

    assert res.ks_statistic > 0.4
    assert res.p_value < 1.0e-6
    assert res.is_distribution_deviant is True


def test_mann_whitney_u_test():
    r"""Verify Mann-Whitney U rank-sum test on shifted distributions."""
    rng = np.random.default_rng(123)
    s1 = rng.exponential(scale=1.0, size=200)
    s2 = rng.exponential(scale=1.0, size=200)

    res_same: MannWhitneyUResult = NonParametricStatsEngine.mann_whitney_u_test(s1, s2, alpha=0.01)
    assert res_same.p_value > 0.05
    assert res_same.is_rank_deviant is False

    # Shifted sample
    s3 = rng.exponential(scale=3.0, size=200)
    res_diff: MannWhitneyUResult = NonParametricStatsEngine.mann_whitney_u_test(s1, s3, alpha=0.01)
    assert res_diff.p_value < 1.0e-6
    assert res_diff.is_rank_deviant is True


def test_covert_timing_modulation_roundtrip():
    r"""Verify covert binary bitstream modulation into IATs and demodulation recovery."""
    modulator = CovertTimingModulator(mean_iat_seconds=0.05, dither_magnitude_seconds=0.02)
    secret_payload = "101100101101"

    stream: ModulatedPacketStream = modulator.inject_covert_message(
        binary_payload=secret_payload,
        num_packets=120,
        seed=42,
    )

    assert stream.is_covert_injected is True
    assert len(stream.inter_arrival_times) == 120

    # Demodulate first 12 bits
    recovered = modulator.demodulate_covert_message(
        stream.inter_arrival_times,
        payload_length=len(secret_payload),
    )

    assert recovered == secret_payload


def test_covert_timing_channel_detector_clean_traffic():
    r"""Verify detector reports clean traffic when testing legitimate Poisson packet streams."""
    modulator = CovertTimingModulator(mean_iat_seconds=0.04)
    baseline_stream = modulator.generate_baseline_traffic(num_packets=400, seed=1)
    test_stream = modulator.generate_baseline_traffic(num_packets=400, seed=2)

    detector = CovertTimingChannelDetector(baseline_iats=baseline_stream.inter_arrival_times)
    report: CovertTimingDetectionReport = detector.analyze_stream(
        suspect_iats=test_stream.inter_arrival_times,
        raise_on_anomaly=False,
    )

    assert report.is_covert_channel_confirmed is False
    assert report.tripwire_triggered is False
    assert report.ks_test_result.is_distribution_deviant is False


def test_subliminal_covert_timing_trap_trigger():
    r"""Verify subliminal timing trap triggers exception when covert steganography is detected."""
    modulator = CovertTimingModulator(mean_iat_seconds=0.04, dither_magnitude_seconds=0.02)
    baseline_stream = modulator.generate_baseline_traffic(num_packets=500, seed=10)

    # Injected covert stream
    covert_stream = modulator.inject_covert_message(
        binary_payload="101100111001",
        num_packets=500,
        seed=20,
    )

    detector = CovertTimingChannelDetector(baseline_iats=baseline_stream.inter_arrival_times)

    # analyze without raise
    report: CovertTimingDetectionReport = detector.analyze_stream(
        suspect_iats=covert_stream.inter_arrival_times,
        raise_on_anomaly=False,
    )

    assert report.is_covert_channel_confirmed is True
    assert report.tripwire_triggered is True
    assert report.confidence_score > 0.99

    # analyze with raise_on_anomaly=True
    with pytest.raises(SubliminalCovertTimingTrapTrigger):
        detector.analyze_stream(
            suspect_iats=covert_stream.inter_arrival_times,
            raise_on_anomaly=True,
        )
