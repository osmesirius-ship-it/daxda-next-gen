"""
Double-Gamma Hemodynamic Response Function (HRF) Convolution & Deconvolution
=============================================================================
Mathematical modeling of neurovascular coupling and BOLD timecourses
using the canonical Friston & Glover double-gamma probability density function.
Pure NumPy and standard library implementation.
"""

from dataclasses import dataclass
import math
from typing import Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class HRFParameters:
    """Canonical parameters for double-gamma hemodynamic response function."""
    a1: float = 6.0       # Response delay (shape param 1)
    b1: float = 1.0       # Response dispersion (scale param 1)
    a2: float = 16.0      # Undershoot delay (shape param 2)
    b2: float = 1.0       # Undershoot dispersion (scale param 2)
    c: float = 0.1667     # Undershoot to peak amplitude ratio
    duration_sec: float = 32.0  # Total kernel window length in seconds


class DoubleGammaHRF:
    """
    Continuous and discretized double-gamma Hemodynamic Response Function:
    h(t) = [t^{a_1 - 1} * b_1^{a_1} * e^{-b_1 * t} / Gamma(a_1)] - 
           c * [t^{a_2 - 1} * b_2^{a_2} * e^{-b_2 * t} / Gamma(a_2)]
    """

    def __init__(self, params: Optional[HRFParameters] = None):
        self.params = params or HRFParameters()

    def evaluate(self, t: np.ndarray) -> np.ndarray:
        """Evaluates continuous h(t) at time points t (seconds)."""
        t = np.asarray(t, dtype=np.float64)
        h = np.zeros_like(t)
        pos_mask = t > 0.0
        t_pos = t[pos_mask]
        
        p = self.params
        gamma_a1 = math.gamma(p.a1)
        gamma_a2 = math.gamma(p.a2)
        
        term1 = (t_pos ** (p.a1 - 1.0)) * (p.b1 ** p.a1) * np.exp(-p.b1 * t_pos) / gamma_a1
        term2 = p.c * (t_pos ** (p.a2 - 1.0)) * (p.b2 ** p.a2) * np.exp(-p.b2 * t_pos) / gamma_a2
        h[pos_mask] = term1 - term2
        return h

    def generate_discrete_kernel(self, tr_seconds: float = 1.5, oversampling: int = 16) -> np.ndarray:
        """
        Discretizes the HRF kernel sampled at high-resolution dt = tr / oversampling
        and downsampled to TR (Repetition Time). Normalized to peak amplitude = 1.0.
        """
        dt = tr_seconds / oversampling
        timepoints = np.arange(0.0, self.params.duration_sec, dt)
        fine_kernel = self.evaluate(timepoints)
        
        # Subsample at TR indices
        kernel_len = int(np.ceil(self.params.duration_sec / tr_seconds))
        tr_kernel = np.zeros(kernel_len, dtype=np.float64)
        for i in range(kernel_len):
            idx = i * oversampling
            if idx < len(fine_kernel):
                tr_kernel[i] = fine_kernel[idx]
                
        # Normalize peak to 1.0
        max_val = np.max(np.abs(tr_kernel))
        if max_val > 0.0:
            tr_kernel = tr_kernel / max_val
        return tr_kernel


class HemodynamicDeconvolver:
    """
    Convolution and regularized Wiener/Tikhonov deconvolution
    between token activation sequences and BOLD timecourses.
    """

    def __init__(self, tr_seconds: float = 1.5, oversampling: int = 16):
        self.tr_seconds = tr_seconds
        self.oversampling = oversampling
        self.hrf_model = DoubleGammaHRF()
        self.kernel = self.hrf_model.generate_discrete_kernel(
            tr_seconds=tr_seconds, oversampling=oversampling
        )

    def convolve_events(
        self,
        event_amplitudes: np.ndarray,
        event_onsets_sec: Optional[np.ndarray] = None,
        total_duration_sec: Optional[float] = None,
    ) -> np.ndarray:
        """
        Convolves token activation event stream with the discrete HRF kernel.
        Returns predicted BOLD timecourse y(t).
        """
        event_amplitudes = np.asarray(event_amplitudes, dtype=np.float64)
        if event_onsets_sec is None:
            # Assume uniformly spaced events sampled at TR
            return np.convolve(event_amplitudes, self.kernel, mode="full")[:len(event_amplitudes)]
        
        # Non-uniform discrete onsets placed into TR time bins
        assert len(event_amplitudes) == len(event_onsets_sec)
        max_time = total_duration_sec or (np.max(event_onsets_sec) + self.hrf_model.params.duration_sec)
        bin_count = int(np.ceil(max_time / self.tr_seconds))
        binned_events = np.zeros(bin_count, dtype=np.float64)
        
        for amp, onset in zip(event_amplitudes, event_onsets_sec):
            bin_idx = int(round(onset / self.tr_seconds))
            if 0 <= bin_idx < bin_count:
                binned_events[bin_idx] += amp
                
        bold_pred = np.convolve(binned_events, self.kernel, mode="full")[:bin_count]
        return bold_pred

    def deconvolve_bold(
        self,
        bold_timecourse: np.ndarray,
        regularization_lambda: float = 1e-3,
    ) -> np.ndarray:
        """
        Tikhonov regularized frequency-domain Wiener deconvolution:
        X_hat(f) = [ H*(f) / (|H(f)|^2 + lambda) ] * Y(f)
        Recovers latent neural activation drive.
        """
        y = np.asarray(bold_timecourse, dtype=np.float64)
        N = len(y)
        kernel_padded = np.zeros(N, dtype=np.float64)
        k_len = min(len(self.kernel), N)
        kernel_padded[:k_len] = self.kernel[:k_len]
        
        Y_fft = np.fft.rfft(y)
        H_fft = np.fft.rfft(kernel_padded)
        
        # Wiener filter transfer function
        H_conj = np.conj(H_fft)
        H_sq = np.abs(H_fft) ** 2
        filter_tf = H_conj / (H_sq + regularization_lambda)
        
        X_hat_fft = Y_fft * filter_tf
        x_recovered = np.fft.irfft(X_hat_fft, n=N)
        return x_recovered
