r"""
Strontium-87 (^87Sr) Optical Lattice Standard Simulation Engine.
Models the ultra-narrow optical clock transition ^1S_0 -> ^3P_0 at 429.228 THz,
generating realistic quantum projection noise and optical frequency comb telemetry.
"""

from dataclasses import dataclass
from typing import Dict, Tuple
import math
import numpy as np


# Fundamental physical constants for 87Sr clock
SR87_CLOCK_TRANSITION_HZ: float = 429_228_004_229_873.0  # 429.228 THz
SPEED_OF_LIGHT_M_S: float = 299_792_458.0                # m/s
STANDARD_GRAVITY_M_S2: float = 9.80665                   # m/s^2


@dataclass(frozen=True)
class OpticalClockTelemetry:
    """Telemetry stream from a Strontium-87 optical lattice clock."""
    timestamps_seconds: np.ndarray       # t_k
    fractional_frequencies: np.ndarray   # y_k = \Delta \nu / \nu_0
    phase_deviations_seconds: np.ndarray # x_k
    nominal_frequency_hz: float
    quantum_projection_noise_limit: float
    integrated_drift_rate_per_sec: float


class Sr87OpticalLatticeStandard:
    r"""
    Simulates a Strontium-87 optical lattice atomic clock standard.
    Transition: 5s^2 ^1S_0 \to 5s5p ^3P_0 at \lambda \approx 698 nm (\nu_0 \approx 429.228 THz).
    """

    def __init__(
        self,
        nominal_frequency_hz: float = SR87_CLOCK_TRANSITION_HZ,
        num_atoms_in_lattice: int = 10_000,
        cycle_time_seconds: float = 1.0,
    ):
        self.nominal_frequency_hz = nominal_frequency_hz
        self.num_atoms = num_atoms_in_lattice
        self.cycle_time = cycle_time_seconds
        
        # Quantum projection noise limit: \sigma_y(\tau) = \frac{1}{\pi Q \sqrt{N_{atoms}}} \tau^{-1/2}
        # Quality factor Q \approx 429e12 / 1.0 = 4.3e14 (for 1s Rabi pulse)
        # Typically gives ~ 1.5e-16 / \sqrt{\tau} for N=10,000
        self.qpn_limit = 1.5e-16 / math.sqrt(float(num_atoms_in_lattice) / 10_000.0)

    def generate_synthetic_telemetry(
        self,
        duration_seconds: float = 1000.0,
        sample_period_tau0: float = 1.0,
        linear_drift_rate: float = 5.0e-20,
        seed: int = 42,
    ) -> OpticalClockTelemetry:
        r"""
        Generates realistic fractional frequency noise time series:
        y(t) = y_{WFM}(t) + y_{FFM}(t) + D \cdot t
        where WFM scales as \sigma_y(\tau) \approx \text{qpn} \cdot \tau^{-1/2}.
        """
        rng = np.random.default_rng(seed)
        num_samples = int(duration_seconds / sample_period_tau0)
        times = np.arange(num_samples) * sample_period_tau0

        # White frequency noise with standard deviation = qpn_limit / sqrt(tau0)
        sigma_wfm = self.qpn_limit / math.sqrt(sample_period_tau0)
        y_wfm = rng.normal(0.0, sigma_wfm, size=num_samples)

        # Flicker frequency floor (~ 2e-18)
        y_flicker = rng.normal(0.0, 2.0e-18, size=num_samples)

        # Linear aging / thermal drift
        y_drift = linear_drift_rate * times

        y_total = y_wfm + y_flicker + y_drift

        # Phase deviation x_k = \int y(t) dt (discrete cumulative sum)
        x_phase = np.cumsum(y_total) * sample_period_tau0

        return OpticalClockTelemetry(
            timestamps_seconds=times,
            fractional_frequencies=y_total,
            phase_deviations_seconds=x_phase,
            nominal_frequency_hz=self.nominal_frequency_hz,
            quantum_projection_noise_limit=self.qpn_limit,
            integrated_drift_rate_per_sec=linear_drift_rate,
        )

    @staticmethod
    def calculate_gravitational_redshift_fraction(
        height_difference_meters: float,
        gravity_m_s2: float = STANDARD_GRAVITY_M_S2,
    ) -> float:
        r"""
        Calculates Einstein gravitational redshift fractional frequency shift:
        \Delta \nu / \nu_0 = \frac{g \Delta h}{c^2}.
        At Earth's surface, \approx 1.09 \times 10^{-16} per meter.
        """
        shift = (gravity_m_s2 * height_difference_meters) / (SPEED_OF_LIGHT_M_S**2)
        return float(shift)
