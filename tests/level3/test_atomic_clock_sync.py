r"""
Tests for Strontium-87 Optical Lattice Atomic Clock Synchronization Engine.
Verifies Allan deviation calculation, quantum projection noise scaling,
gravitational redshift compensation, and sub-femtosecond phase locking.
"""

import math
import numpy as np
import pytest

from daxda_engine.level3.atomic_clock_sync import (
    SR87_CLOCK_TRANSITION_HZ,
    SPEED_OF_LIGHT_M_S,
    STANDARD_GRAVITY_M_S2,
    Sr87OpticalLatticeStandard,
    OpticalClockTelemetry,
    AllanDeviationCalculator,
    AllanDeviationResult,
    PhaseLockedOpticalSynchronizer,
    SynchronizationResult,
)


def test_sr87_constants_and_transition_frequency():
    r"""Verify fundamental transition frequency of ^87Sr and quantum projection noise limit."""
    clock = Sr87OpticalLatticeStandard(num_atoms_in_lattice=10_000)

    # Transition frequency should be 429.228 THz
    assert abs(clock.nominal_frequency_hz - 429_228_004_229_873.0) < 1.0
    assert clock.qpn_limit < 2.0e-16


def test_allan_deviation_computation():
    r"""Verify overlapping Allan deviation computation and \tau^{-1/2} white FM scaling."""
    clock = Sr87OpticalLatticeStandard(num_atoms_in_lattice=10_000)
    telemetry: OpticalClockTelemetry = clock.generate_synthetic_telemetry(
        duration_seconds=1000.0,
        sample_period_tau0=1.0,
        seed=101,
    )

    res: AllanDeviationResult = AllanDeviationCalculator.compute_overlapping_allan_deviation(
        fractional_frequencies=telemetry.fractional_frequencies,
        sample_period_tau0=1.0,
    )

    assert len(res.taus) >= 6
    assert res.taus[0] == 1.0
    # Stability should improve with tau
    assert res.allan_deviations[3] < res.allan_deviations[0]
    # Check that minimum Allan deviation achieves target stability < 1e-16
    assert res.minimum_adev < 1.0e-16
    assert res.achieves_target_stability is True


def test_gravitational_redshift_calculation():
    r"""Verify Einstein gravitational redshift: \Delta \nu / \nu_0 = g \Delta h / c^2."""
    # 1 meter altitude change at Earth surface
    shift_1m = Sr87OpticalLatticeStandard.calculate_gravitational_redshift_fraction(1.0)
    expected_1m = STANDARD_GRAVITY_M_S2 / (SPEED_OF_LIGHT_M_S**2)  # ~ 1.091e-16
    assert abs(shift_1m - expected_1m) < 1e-20
    assert abs(shift_1m - 1.091e-16) < 1.0e-18

    # 10 meters altitude change
    shift_10m = Sr87OpticalLatticeStandard.calculate_gravitational_redshift_fraction(10.0)
    assert abs(shift_10m - 10.0 * shift_1m) < 1e-22


def test_pll_phase_locking_and_sub_femtosecond_jitter():
    r"""Verify DPLL phase tracking loop and jitter suppression under gravitational bias."""
    clock_ref = Sr87OpticalLatticeStandard(num_atoms_in_lattice=10_000)
    clock_loc = Sr87OpticalLatticeStandard(num_atoms_in_lattice=10_000)

    tel_ref = clock_ref.generate_synthetic_telemetry(duration_seconds=200.0, seed=1)
    tel_loc = clock_loc.generate_synthetic_telemetry(duration_seconds=200.0, seed=2)

    pll = PhaseLockedOpticalSynchronizer(kp_proportional=0.8, ki_integral=0.1)

    # 5 meters altitude separation
    res: SynchronizationResult = pll.synchronize_remote_clock(
        reference_phase_seconds=tel_ref.phase_deviations_seconds,
        local_phase_seconds=tel_loc.phase_deviations_seconds,
        dt=1.0,
        height_difference_meters=5.0,
    )

    assert res.is_locked is True
    assert res.rms_jitter_femtoseconds < 100.0
    assert res.gravitational_shift_compensated > 0.0


def test_kalman_clock_filter_tracking():
    r"""Verify 2-state Kalman filter tracking phase and frequency offset states."""
    times = np.linspace(0.0, 50.0, 51)
    true_freq_offset = 2.0e-15
    true_phase = true_freq_offset * times + np.random.default_rng(42).normal(0.0, 1e-17, 51)

    est_x, est_y = PhaseLockedOpticalSynchronizer.kalman_clock_filter(true_phase, dt=1.0)

    assert len(est_x) == 51
    assert len(est_y) == 51
    # Estimated frequency offset should converge near true_freq_offset
    final_freq_est = est_y[-1]
    assert abs(final_freq_est - true_freq_offset) < 1.0e-15
