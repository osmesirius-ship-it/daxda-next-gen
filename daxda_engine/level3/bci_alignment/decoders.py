"""
Cognitive Vigilance & Error-Related Negativity (ERN) Decoders
=============================================================
Decodes operator engagement, microsleep drift, and subconscious dissonance
from multi-channel EEG timecourses and Riemannian distance from baseline.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from .manifold import airm_geodesic_distance


@dataclass(frozen=True)
class CognitiveEpochAssessment:
    """Comprehensive cognitive evaluation of a supervisory EEG epoch."""
    vigilance_score: float
    engagement_index: float
    drowsiness_ratio: float
    is_drowsy: bool
    has_ern_dissonance: bool
    ern_amplitude_uV: float
    airm_drift_from_baseline: float
    is_operator_attested: bool
    rejection_reason: Optional[str] = None


class ERNDetector:
    """
    Detects Error-Related Negativity (ERN / Ne) frontocentral potentials (FCz, Cz)
    peaking 50–150ms post-action, indicating subconscious human cognitive disagreement.
    """

    def __init__(self, fcz_channel_idx: int = 0, sampling_rate_hz: float = 250.0):
        self.fcz_idx = fcz_channel_idx
        self.fs = sampling_rate_hz

    def detect_ern(self, epoch: np.ndarray, ern_threshold_uV: float = -4.5) -> tuple[bool, float]:
        """
        Evaluates ERN window (50-150ms post-stimulus).
        A negative deflection exceeding threshold indicates subconscious cognitive conflict.
        """
        C, T = epoch.shape
        start_sample = int(0.050 * self.fs)
        end_sample = min(int(0.150 * self.fs), T)
        
        ch_idx = min(self.fcz_idx, C - 1)
        window = epoch[ch_idx, start_sample:end_sample]
        min_peak = float(np.min(window)) if len(window) > 0 else 0.0
        
        has_conflict = min_peak <= ern_threshold_uV
        return has_conflict, min_peak


class VigilanceDriftDetector:
    """
    Monitors operator engagement and drowsiness using spectral band powers
    and Riemannian geodesic distance from calibrated alert baseline.
    """

    def __init__(
        self,
        baseline_mean: np.ndarray,
        vigilance_threshold: float = 0.78,
        drowsiness_threshold: float = 3.2,
        geodesic_drift_threshold: float = 2.5,
    ):
        self.baseline_mean = baseline_mean
        self.vigilance_thresh = vigilance_threshold
        self.drowsiness_thresh = drowsiness_threshold
        self.drift_thresh = geodesic_drift_threshold
        self.ern_detector = ERNDetector()

    def assess_epoch(self, epoch: np.ndarray, current_cov: Optional[np.ndarray] = None) -> CognitiveEpochAssessment:
        """
        Analyzes spectral power bands (theta 4-8Hz, alpha 8-12Hz, beta 13-30Hz)
        and Riemannian manifold drift from baseline.
        """
        epoch = np.asarray(epoch, dtype=np.float64)
        C, T = epoch.shape
        
        # FFT power spectral density estimation
        fft_vals = np.abs(np.fft.rfft(epoch, axis=1)) ** 2
        freqs = np.fft.rfftfreq(T, d=1.0 / 250.0)
        
        # Power in frequency bands across channels
        theta_mask = (freqs >= 4.0) & (freqs < 8.0)
        alpha_mask = (freqs >= 8.0) & (freqs < 13.0)
        beta_mask = (freqs >= 13.0) & (freqs < 30.0)
        
        theta_power = float(np.mean(fft_vals[:, theta_mask])) if np.any(theta_mask) else 1e-6
        alpha_power = float(np.mean(fft_vals[:, alpha_mask])) if np.any(alpha_mask) else 1e-6
        beta_power = float(np.mean(fft_vals[:, beta_mask])) if np.any(beta_mask) else 1e-6
        
        # Standard EEG Engagement Index: Beta / (Alpha + Theta)
        engagement = beta_power / max(alpha_power + theta_power, 1e-6)
        # Drowsiness ratio: Theta / Alpha
        drowsiness = theta_power / max(alpha_power, 1e-6)
        is_drowsy = drowsiness > self.drowsiness_thresh
        
        # Compute AIRM distance from baseline
        if current_cov is None:
            epoch_c = epoch - np.mean(epoch, axis=1, keepdims=True)
            current_cov = (epoch_c @ epoch_c.T) / max(T - 1, 1)
            current_cov += 1e-4 * np.eye(C)
            
        airm_dist = airm_geodesic_distance(current_cov, self.baseline_mean)
        
        # ERN conflict detection
        has_ern, ern_amp = self.ern_detector.detect_ern(epoch)
        
        # Vigilance score mapping in [0, 1]
        raw_vigilance = engagement / (1.0 + engagement)
        drift_penalty = max(0.0, (airm_dist - 1.0) * 0.15)
        vigilance_score = float(np.clip(raw_vigilance - drift_penalty, 0.0, 1.0))
        
        # Determine attestation eligibility
        rejection_reason = None
        if is_drowsy:
            rejection_reason = "OPERATOR_DROWSINESS_EXCEEDED"
        elif has_ern:
            rejection_reason = "COGNITIVE_CONFLICT_ERN_DETECTED"
        elif vigilance_score < self.vigilance_thresh:
            rejection_reason = "VIGILANCE_BELOW_THRESHOLD"
        elif airm_dist > self.drift_thresh:
            rejection_reason = "EXCESSIVE_RIEMANNIAN_MANIFOLD_DRIFT"
            
        is_attested = (rejection_reason is None)
        
        return CognitiveEpochAssessment(
            vigilance_score=vigilance_score,
            engagement_index=engagement,
            drowsiness_ratio=drowsiness,
            is_drowsy=is_drowsy,
            has_ern_dissonance=has_ern,
            ern_amplitude_uV=ern_amp,
            airm_drift_from_baseline=airm_dist,
            is_operator_attested=is_attested,
            rejection_reason=rejection_reason,
        )
