r"""
Inter-Packet Arrival Time (IAT) Telemetry and Steganography Detector.
Ingests network packet timing streams, analyzes IAT entropy and empirical distributions,
and trips subliminal covert timing traps when unauthorized steganography is detected.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import math
import numpy as np

from .statistical_tests import (
    NonParametricStatsEngine,
    KSTestResult,
    MannWhitneyUResult,
)
from .modulation import ModulatedPacketStream


class SubliminalCovertTimingTrapTrigger(Exception):
    """Raised when covert steganographic timing channels breach statistical tripwires."""
    pass


@dataclass(frozen=True)
class CovertTimingDetectionReport:
    """Detailed forensic audit report on observed packet inter-arrival times."""
    total_packets_analyzed: int
    mean_iat_observed: float
    variance_iat_observed: float
    iat_shannon_entropy_bits: float
    ks_test_result: KSTestResult
    mann_whitney_result: MannWhitneyUResult
    is_covert_channel_confirmed: bool
    confidence_score: float             # In [0.0, 1.0]
    tripwire_triggered: bool


class CovertTimingChannelDetector:
    r"""
    Monitors packet telemetry and triggers containment traps if IAT distributions
    deviate from legitimate Poisson/Exponential traffic standards.
    """

    def __init__(
        self,
        baseline_iats: np.ndarray,
        significance_alpha: float = 0.01,
        entropy_bin_count: int = 50,
    ):
        if len(baseline_iats) < 20:
            raise ValueError("Baseline IAT requires at least 20 packets")
        self.baseline_iats = baseline_iats
        self.alpha = significance_alpha
        self.num_bins = entropy_bin_count

    @staticmethod
    def extract_inter_arrival_times(timestamps: np.ndarray) -> np.ndarray:
        """Computes delta t = t_{k+1} - t_k."""
        if len(timestamps) < 2:
            return np.array([])
        return np.diff(timestamps)

    def calculate_empirical_entropy(self, iats: np.ndarray) -> float:
        """Calculates discrete Shannon entropy (in bits) of binned IAT values."""
        hist, _ = np.histogram(iats, bins=self.num_bins, density=True)
        probs = hist / np.sum(hist) if np.sum(hist) > 0 else np.zeros_like(hist)
        pos_probs = probs[probs > 1e-12]
        entropy = -float(np.sum(pos_probs * np.log2(pos_probs)))
        return entropy

    def analyze_stream(
        self,
        suspect_iats: np.ndarray,
        raise_on_anomaly: bool = False,
    ) -> CovertTimingDetectionReport:
        """
        Executes dual non-parametric statistical hypothesis tests (KS and Mann-Whitney U)
        comparing suspect IATs against baseline.
        """
        ks_res = NonParametricStatsEngine.two_sample_ks_test(
            sample1=self.baseline_iats,
            sample2=suspect_iats,
            alpha=self.alpha,
        )

        mw_res = NonParametricStatsEngine.mann_whitney_u_test(
            sample1=self.baseline_iats,
            sample2=suspect_iats,
            alpha=self.alpha,
        )

        entropy = self.calculate_empirical_entropy(suspect_iats)
        mean_iat = float(np.mean(suspect_iats))
        var_iat = float(np.var(suspect_iats))

        # Channel confirmed if either test detects significant deviation at alpha
        covert_confirmed = bool(ks_res.is_distribution_deviant or mw_res.is_rank_deviant)

        # Confidence score based on p-values
        min_p = min(ks_res.p_value, mw_res.p_value)
        confidence = float(min(1.0, 1.0 - min_p))

        report = CovertTimingDetectionReport(
            total_packets_analyzed=len(suspect_iats),
            mean_iat_observed=mean_iat,
            variance_iat_observed=var_iat,
            iat_shannon_entropy_bits=entropy,
            ks_test_result=ks_res,
            mann_whitney_result=mw_res,
            is_covert_channel_confirmed=covert_confirmed,
            confidence_score=confidence,
            tripwire_triggered=covert_confirmed,
        )

        if covert_confirmed and raise_on_anomaly:
            raise SubliminalCovertTimingTrapTrigger(
                f"Covert timing channel detected! KS D={ks_res.ks_statistic:.4f} "
                f"(p={ks_res.p_value:.3e}), MW z={mw_res.z_score:.2f} (p={mw_res.p_value:.3e})"
            )

        return report
