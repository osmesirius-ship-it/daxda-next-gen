r"""
Allan Deviation Analysis Engine.
Computes standard Allan deviation \sigma_y(\tau), overlapping Allan deviation,
and stability curves for optical lattice atomic frequency standards.
"""

from dataclasses import dataclass
from typing import List, Tuple
import math
import numpy as np


@dataclass(frozen=True)
class AllanDeviationResult:
    """Stores the Allan deviation curve across integration times tau."""
    taus: np.ndarray             # Integration times \tau (seconds)
    allan_deviations: np.ndarray # Allan deviation \sigma_y(\tau)
    confidence_intervals: np.ndarray # shape (N, 2)
    minimum_adev: float
    tau_at_minimum: float
    achieves_target_stability: bool  # True if min ADEV < 1e-16


class AllanDeviationCalculator:
    r"""
    Calculates Allan deviation \sigma_y(\tau) from fractional frequency fluctuations y_k
    or phase time deviations x_k:
    \sigma_y^2(\tau) = \frac{1}{2(M-1)} \sum_{k=1}^{M-1} (\bar{y}_{k+1} - \bar{y}_k)^2.
    """

    @staticmethod
    def compute_fractional_frequencies_from_phase(
        phase_deviations_seconds: np.ndarray,
        sample_period_tau0: float,
    ) -> np.ndarray:
        r"""
        Converts phase error time series x_k (in seconds) to fractional frequency y_k:
        y_k = (x_{k+1} - x_k) / \tau_0.
        """
        return np.diff(phase_deviations_seconds) / sample_period_tau0

    @classmethod
    def compute_overlapping_allan_deviation(
        cls,
        fractional_frequencies: np.ndarray,
        sample_period_tau0: float,
        tau_multipliers: np.ndarray = None,
    ) -> AllanDeviationResult:
        r"""
        Computes overlapping Allan deviation:
        \sigma_y(\tau = m \tau_0) = \sqrt{ \frac{1}{2 m^2 (N - 2m + 1)} \sum_{j=1}^{N - 2m + 1} \left( \sum_{i=j}^{j+m-1} (y_{i+m} - y_i) \right)^2 }.
        """
        N = len(fractional_frequencies)
        if N < 4:
            raise ValueError(f"Allan deviation requires at least 4 samples, got {N}")

        if tau_multipliers is None:
            # Powers of 2 or log-spaced multipliers up to N//3
            max_m = max(1, N // 3)
            m_list = []
            m = 1
            while m <= max_m:
                m_list.append(m)
                m *= 2
            tau_multipliers = np.array(m_list, dtype=int)

        taus = []
        adevs = []
        conf_intervals = []

        for m in tau_multipliers:
            if 2 * m >= N:
                break
            tau = float(m * sample_period_tau0)
            taus.append(tau)

            # Block averaging for stride m
            # We compute rolling block averages of y over window m
            cumsum = np.cumsum(np.insert(fractional_frequencies, 0, 0.0))
            y_bar = (cumsum[m:] - cumsum[:-m]) / float(m)

            # Overlapping differences (y_bar_{k+m} - y_bar_k)
            diffs = y_bar[m:] - y_bar[:-m]
            K = len(diffs)
            sigma2 = float(np.sum(diffs**2) / (2.0 * K))
            adev = math.sqrt(max(1e-35, sigma2))
            adevs.append(adev)

            # 68% Chi-squared confidence interval approximation: adev / sqrt(K)
            rel_err = 1.0 / math.sqrt(max(1, K))
            conf_intervals.append([adev * (1.0 - rel_err), adev * (1.0 + rel_err)])

        taus_arr = np.array(taus, dtype=np.float64)
        adevs_arr = np.array(adevs, dtype=np.float64)
        confs_arr = np.array(conf_intervals, dtype=np.float64)

        min_idx = int(np.argmin(adevs_arr))
        min_adev = float(adevs_arr[min_idx])
        tau_min = float(taus_arr[min_idx])

        return AllanDeviationResult(
            taus=taus_arr,
            allan_deviations=adevs_arr,
            confidence_intervals=confs_arr,
            minimum_adev=min_adev,
            tau_at_minimum=tau_min,
            achieves_target_stability=min_adev < 1.0e-16,
        )
