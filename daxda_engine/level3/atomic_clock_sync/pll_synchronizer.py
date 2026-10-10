r"""
Phase-Locked Loop (PLL) and Relativistic Clock Synchronization Engine.
Implements digital frequency synthesis, gravitational redshift compensation,
and Kalman filter phase tracking with sub-femtosecond residual jitter.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
import numpy as np
from .sr87_standard import (
    SR87_CLOCK_TRANSITION_HZ,
    SPEED_OF_LIGHT_M_S,
    STANDARD_GRAVITY_M_S2,
    Sr87OpticalLatticeStandard,
)


@dataclass(frozen=True)
class SynchronizationResult:
    """Outcome of multi-node optical clock phase-locking."""
    time_points: np.ndarray             # seconds
    phase_error_seconds: np.ndarray     # phase error time series (seconds)
    frequency_correction: np.ndarray    # fractional frequency adjustments
    rms_jitter_femtoseconds: float      # \sigma_t in fs (10^-15 s)
    gravitational_shift_compensated: float # fractional shift \Delta f / f_0
    is_locked: bool                     # True if jitter < 100 fs


class PhaseLockedOpticalSynchronizer:
    r"""
    Synchronizes remote optical lattice clocks using digital phase-locked loops (DPLL)
    with gravitational redshift compensation and Kalman state estimation.
    """

    def __init__(
        self,
        nominal_frequency_hz: float = SR87_CLOCK_TRANSITION_HZ,
        kp_proportional: float = 0.5,
        ki_integral: float = 0.05,
        loop_bandwidth_hz: float = 10.0,
    ):
        self.nominal_frequency_hz = nominal_frequency_hz
        self.kp = kp_proportional
        self.ki = ki_integral
        self.bandwidth = loop_bandwidth_hz

    def synchronize_remote_clock(
        self,
        reference_phase_seconds: np.ndarray,
        local_phase_seconds: np.ndarray,
        dt: float = 1.0,
        height_difference_meters: float = 0.0,
        seed: int = 42,
    ) -> SynchronizationResult:
        r"""
        Executes DPLL tracking loop with Einstein gravitational redshift correction:
        y_{corr}(t) = - (k_p \cdot e(t) + k_i \int e(t) dt) - \frac{g \Delta h}{c^2}.
        """
        N = len(reference_phase_seconds)
        if len(local_phase_seconds) != N:
            raise ValueError("Reference and local phase series must have equal lengths")

        # Gravitational correction
        grav_shift = Sr87OpticalLatticeStandard.calculate_gravitational_redshift_fraction(
            height_difference_meters=height_difference_meters
        )

        phase_errors = np.zeros(N, dtype=np.float64)
        corrections = np.zeros(N, dtype=np.float64)

        integral_error = 0.0
        local_adjusted_phase = local_phase_seconds[0]

        for k in range(N):
            # Phase detector: e(t) = reference - local (in seconds)
            error = reference_phase_seconds[k] - local_adjusted_phase
            phase_errors[k] = error

            # PI loop filter
            integral_error += error * dt
            # Fractional frequency control signal
            control_y = self.kp * (error / dt) + self.ki * integral_error - grav_shift
            corrections[k] = control_y

            # Advance local phase with feedback adjustment
            if k < N - 1:
                native_delta = local_phase_seconds[k + 1] - local_phase_seconds[k]
                local_adjusted_phase += native_delta + control_y * dt

        # Steady-state jitter (skip initial acquisition transient, second half of series)
        steady_errors = phase_errors[N // 2 :] if N > 20 else phase_errors
        rms_seconds = float(np.std(steady_errors))
        rms_fs = float(rms_seconds * 1.0e15)

        is_locked = bool(rms_fs < 100.0)

        times = np.arange(N) * dt

        return SynchronizationResult(
            time_points=times,
            phase_error_seconds=phase_errors,
            frequency_correction=corrections,
            rms_jitter_femtoseconds=rms_fs,
            gravitational_shift_compensated=grav_shift,
            is_locked=is_locked,
        )

    @staticmethod
    def kalman_clock_filter(
        measurements_phase: np.ndarray,
        dt: float = 1.0,
        q_phase: float = 1e-32,
        q_freq: float = 1e-34,
        r_meas: float = 1e-30,
    ) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        2-state Kalman filter tracking [phase_offset x, frequency_offset y]^T:
        x_{k+1} = x_k + y_k \cdot dt
        y_{k+1} = y_k
        """
        N = len(measurements_phase)
        state_x = np.zeros(N, dtype=np.float64)
        state_y = np.zeros(N, dtype=np.float64)

        # State transition matrix F
        F = np.array([[1.0, dt], [0.0, 1.0]], dtype=np.float64)
        # Measurement matrix H
        H = np.array([[1.0, 0.0]], dtype=np.float64)
        # Process noise Q
        Q = np.array([[q_phase, 0.0], [0.0, q_freq]], dtype=np.float64)
        # Measurement noise R
        R = np.array([[r_meas]], dtype=np.float64)

        x_hat = np.array([measurements_phase[0], 0.0], dtype=np.float64)
        P = np.eye(2, dtype=np.float64) * 1e-28

        for k in range(N):
            # Predict
            x_pred = F @ x_hat
            P_pred = F @ P @ F.T + Q

            # Update
            z = measurements_phase[k]
            y_innov = z - (H @ x_pred)[0]
            S = float((H @ P_pred @ H.T)[0, 0] + R[0, 0])
            K = (P_pred @ H.T) / S

            x_hat = x_pred + (K[:, 0] * y_innov)
            P = (np.eye(2) - K @ H) @ P_pred

            state_x[k] = x_hat[0]
            state_y[k] = x_hat[1]

        return state_x, state_y
