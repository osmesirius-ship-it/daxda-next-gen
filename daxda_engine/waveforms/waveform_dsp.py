"""
DAXDA Next-Gen Acoustic Waveform DSP Core (waveform_dsp.py)
============================================================
Vectorized, high-precision signal processing engine for continuous
acoustic waveform decomposition, Hilbert analytic signals, Continuous
Wavelet Transforms (CWT), Short-Time Fourier Transforms (STFT), Mel
filterbanks, and 3D delay-coordinate phase-space attractors.

Dependencies: Pure NumPy + standard library (wave, struct, io).
"""

import io
import math
import struct
import wave
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np


@dataclass
class AnalyticSignalResult:
    """Hilbert analytic signal decomposition."""
    analytic_signal: np.ndarray      # z(t) = s(t) + i*H{s(t)}
    envelope: np.ndarray             # Instantaneous amplitude A(t)
    phase: np.ndarray                # Unwrapped instantaneous phase phi(t)
    instantaneous_freq: np.ndarray   # Instantaneous frequency f(t) in Hz
    sample_rate: int


@dataclass
class CWTResult:
    """Continuous Wavelet Transform decomposition."""
    scalogram: np.ndarray            # 2D Magnitude matrix (scales x time)
    complex_cwt: np.ndarray          # 2D Complex wavelet coefficients
    frequencies: np.ndarray          # Center frequency per scale in Hz
    scales: np.ndarray
    times: np.ndarray


@dataclass
class STFTResult:
    """Short-Time Fourier Transform & spectral feature matrix."""
    spectrogram: np.ndarray          # 2D Magnitude spectrum (freqs x frames)
    complex_stft: np.ndarray         # 2D Complex STFT
    frequencies: np.ndarray          # Frequency bins in Hz
    times: np.ndarray                # Time stamps in seconds
    mel_energies: np.ndarray         # Mel filterbank energies (num_mels x frames)
    mel_frequencies: np.ndarray      # Mel band center frequencies in Hz
    spectral_centroid: np.ndarray    # Centroid per frame (Hz)
    spectral_rolloff: np.ndarray     # 85% energy rolloff per frame (Hz)
    spectral_flux: np.ndarray        # Frame-to-frame spectral flux
    zero_crossing_rate: np.ndarray   # Frame zero-crossing rate
    rms_energy: np.ndarray           # Root-mean-square amplitude per frame
    sample_rate: int


class AcousticWaveformAnalyzer:
    """High-performance acoustic waveform transformation engine."""

    def __init__(self, sample_rate: int = 22050):
        self.default_sample_rate = sample_rate

    # ----------------------------------------------------------------------
    # Audio I/O (Pure Python + NumPy, supports 16-bit, 24-bit, 32-bit PCM)
    # ----------------------------------------------------------------------

    @staticmethod
    def load_audio(source: Union[str, bytes, io.BytesIO]) -> Tuple[int, np.ndarray]:
        """
        Load audio file or raw bytes into normalized float32 samples [-1.0, 1.0].
        Returns (sample_rate, samples_float).
        """
        if isinstance(source, bytes):
            wav_file = io.BytesIO(source)
        elif isinstance(source, str):
            wav_file = open(source, "rb")
        else:
            wav_file = source

        try:
            with wave.open(wav_file, "rb") as wf:
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                num_frames = wf.getnframes()
                raw_data = wf.readframes(num_frames)

                if sample_width == 1:
                    # 8-bit unsigned PCM
                    samples = np.frombuffer(raw_data, dtype=np.uint8).astype(np.float32)
                    samples = (samples - 128.0) / 128.0
                elif sample_width == 2:
                    # 16-bit signed PCM
                    samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
                elif sample_width == 3:
                    # 24-bit signed PCM packed as 3 bytes
                    a = np.frombuffer(raw_data, dtype=np.uint8)
                    # Convert 3-byte tuples into 32-bit signed ints
                    n_samples = len(a) // 3
                    s24 = np.zeros(n_samples, dtype=np.int32)
                    b0 = a[0::3].astype(np.int32)
                    b1 = a[1::3].astype(np.int32)
                    b2 = a[2::3].astype(np.int32)
                    s24 = (b0 | (b1 << 8) | (b2 << 16))
                    # Sign extend 24-bit to 32-bit
                    neg = (s24 & 0x800000) != 0
                    s24[neg] -= 0x1000000
                    samples = s24.astype(np.float32) / 8388608.0
                elif sample_width == 4:
                    # 32-bit signed PCM
                    samples = np.frombuffer(raw_data, dtype=np.int32).astype(np.float32) / 2147483648.0
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width} bytes")

                # If multi-channel, downmix to mono via channel average
                if num_channels > 1:
                    samples = samples.reshape(-1, num_channels).mean(axis=1)

                return sample_rate, samples
        finally:
            if isinstance(source, str):
                wav_file.close()

    @staticmethod
    def save_audio(
        output_path_or_buffer: Union[str, io.BytesIO],
        samples: np.ndarray,
        sample_rate: int = 22050,
        bit_depth: int = 16
    ) -> None:
        """Export normalized float32 samples to PCM WAV format."""
        # Clip to safe dynamic range
        clipped = np.clip(samples, -1.0, 1.0)

        if bit_depth == 16:
            int_samples = (clipped * 32767.0).astype(np.int16)
            data_bytes = int_samples.tobytes()
            sample_width = 2
        elif bit_depth == 32:
            int_samples = (clipped * 2147483647.0).astype(np.int32)
            data_bytes = int_samples.tobytes()
            sample_width = 4
        else:
            raise ValueError("Supported export bit depths: 16 or 32")

        if isinstance(output_path_or_buffer, str):
            wf = wave.open(output_path_or_buffer, "wb")
        else:
            wf = wave.open(output_path_or_buffer, "wb")

        try:
            wf.setnchannels(1)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(data_bytes)
        finally:
            if isinstance(output_path_or_buffer, str):
                wf.close()

    # ----------------------------------------------------------------------
    # Mathematical Transformation 1: Discrete Hilbert Analytic Signal
    # ----------------------------------------------------------------------

    def compute_analytic_signal(
        self,
        samples: np.ndarray,
        sample_rate: Optional[int] = None
    ) -> AnalyticSignalResult:
        """
        Computes the discrete analytic signal z(t) = s(t) + i*H{s(t)} via FFT.
        Extracts instantaneous envelope, instantaneous phase, and frequency.
        """
        sr = sample_rate or self.default_sample_rate
        n = len(samples)
        if n == 0:
            empty = np.array([], dtype=np.float32)
            return AnalyticSignalResult(
                analytic_signal=np.array([], dtype=np.complex64),
                envelope=empty,
                phase=empty,
                instantaneous_freq=empty,
                sample_rate=sr
            )

        # FFT of signal
        x = np.asarray(samples, dtype=np.float64)
        X = np.fft.fft(x)

        # Hilbert multiplier h[k]:
        # 1 at k=0 and k=n/2 (if even)
        # 2 at 1 <= k < n/2
        # 0 at n/2 < k < n
        h = np.zeros(n, dtype=np.float64)
        if n % 2 == 0:
            h[0] = 1.0
            h[n // 2] = 1.0
            h[1 : n // 2] = 2.0
        else:
            h[0] = 1.0
            h[1 : (n + 1) // 2] = 2.0

        z = np.fft.ifft(X * h)

        # Instantaneous envelope A(t)
        envelope = np.abs(z)

        # Unwrapped instantaneous phase phi(t)
        phase = np.unwrap(np.angle(z))

        # Instantaneous frequency: (1 / 2*pi) * (d(phi) / dt)
        # Using numerical central differentiation
        d_phase = np.gradient(phase)
        dt = 1.0 / sr
        inst_freq = (d_phase / (2.0 * math.pi * dt))

        # Smooth and bound instantaneous frequency to Nyquist
        inst_freq = np.clip(inst_freq, 0.0, sr / 2.0)

        return AnalyticSignalResult(
            analytic_signal=z.astype(np.complex64),
            envelope=envelope.astype(np.float32),
            phase=phase.astype(np.float32),
            instantaneous_freq=inst_freq.astype(np.float32),
            sample_rate=sr
        )

    # ----------------------------------------------------------------------
    # Mathematical Transformation 2: Continuous Wavelet Transform (CWT)
    # ----------------------------------------------------------------------

    def compute_cwt(
        self,
        samples: np.ndarray,
        sample_rate: Optional[int] = None,
        num_scales: int = 64,
        f_min: float = 40.0,
        f_max: float = 8000.0,
        w0: float = 6.0
    ) -> CWTResult:
        """
        Computes Continuous Wavelet Transform with complex Morlet wavelet:
        psi(t) = pi^(-1/4) * exp(i * w0 * t) * exp(-t^2 / 2).
        Vectorized via FFT convolution across logarithmic scale bins.
        """
        sr = sample_rate or self.default_sample_rate
        n = len(samples)
        dt = 1.0 / sr

        # Logarithmic distribution of center frequencies
        f_max = min(f_max, sr / 2.1)
        frequencies = np.geomspace(f_min, f_max, num=num_scales)
        # Morlet scale relationship: f = (w0 + sqrt(2 + w0^2)) / (4 * pi * a) -> a ~= w0 / (2 * pi * f)
        scales = (w0 / (2.0 * math.pi)) / (frequencies * dt)

        # FFT of signal
        x = np.asarray(samples, dtype=np.float64)
        X = np.fft.fft(x)
        omega = 2.0 * math.pi * np.fft.fftfreq(n, d=dt)

        # Matrix to hold coefficients
        cwt_matrix = np.zeros((num_scales, n), dtype=np.complex128)

        # Vectorized frequency-domain Morlet wavelet evaluation:
        # Psi_hat(a * omega) = pi^(1/4) * sqrt(2 * a) * H(omega) * exp(-(a*omega - w0)^2 / 2)
        norm_factor = (math.pi ** 0.25) * math.sqrt(2.0)
        for i, scale in enumerate(scales):
            scaled_w = scale * dt * omega
            psi_ft = norm_factor * np.sqrt(scale) * np.exp(-0.5 * (scaled_w - w0) ** 2)
            # Heaviside filter (analytic positive frequencies only)
            psi_ft[omega <= 0] = 0.0

            # Inverse FFT of product
            cwt_matrix[i, :] = np.fft.ifft(X * psi_ft)

        scalogram = np.abs(cwt_matrix).astype(np.float32)
        times = np.arange(n, dtype=np.float32) * dt

        return CWTResult(
            scalogram=scalogram,
            complex_cwt=cwt_matrix.astype(np.complex64),
            frequencies=frequencies.astype(np.float32),
            scales=scales.astype(np.float32),
            times=times
        )

    # ----------------------------------------------------------------------
    # Mathematical Transformation 3: Short-Time Fourier Transform & Features
    # ----------------------------------------------------------------------

    def compute_stft(
        self,
        samples: np.ndarray,
        sample_rate: Optional[int] = None,
        window_size: int = 1024,
        hop_size: int = 256,
        num_mels: int = 40
    ) -> STFTResult:
        """
        Computes high-resolution STFT with Hann windowing, extracting:
        - Magnitude spectrogram
        - Mel-scale filterbank energy
        - Spectral Centroid & Spectral Rolloff
        - Spectral Flux & Zero-Crossing Rate
        - RMS Energy
        """
        sr = sample_rate or self.default_sample_rate
        n = len(samples)
        if n < window_size:
            # Zero-pad if signal shorter than window
            padded = np.pad(samples, (0, window_size - n))
            samples = padded
            n = len(samples)

        # Hann window
        window = np.hanning(window_size)
        num_frames = 1 + (n - window_size) // hop_size

        # Strided frame extraction
        indices = (
            np.tile(np.arange(0, window_size), (num_frames, 1)) +
            np.tile(np.arange(0, num_frames * hop_size, hop_size), (window_size, 1)).T
        )
        frames = samples[indices] * window

        # Real FFT of each windowed frame
        complex_stft = np.fft.rfft(frames, axis=1).T  # Shape: (freq_bins, num_frames)
        magnitude = np.abs(complex_stft)

        freq_bins = complex_stft.shape[0]
        frequencies = np.fft.rfftfreq(window_size, d=1.0 / sr)
        times = (np.arange(num_frames) * hop_size + window_size / 2.0) / sr

        # Mel Filterbank construction
        mel_energies, mel_freqs = self._compute_mel_filterbank(
            magnitude, frequencies, sr, num_mels=num_mels
        )

        # Spectral Centroid: sum(f * |X(f)|) / sum(|X(f)|)
        denom = np.sum(magnitude, axis=0) + 1e-12
        spectral_centroid = np.sum(frequencies[:, None] * magnitude, axis=0) / denom

        # Spectral Rolloff: frequency below which 85% of magnitude energy falls
        cumulative_energy = np.cumsum(magnitude, axis=0)
        total_energy = cumulative_energy[-1, :]
        threshold = 0.85 * total_energy
        rolloff_indices = np.argmax(cumulative_energy >= threshold[None, :], axis=0)
        spectral_rolloff = frequencies[rolloff_indices]

        # Spectral Flux: frame-to-frame Euclidean magnitude difference
        flux = np.zeros(num_frames, dtype=np.float32)
        if num_frames > 1:
            diff = np.diff(magnitude, axis=1)
            # Half-wave rectified flux
            diff[diff < 0] = 0.0
            flux[1:] = np.sqrt(np.sum(diff ** 2, axis=0))

        # Zero-Crossing Rate per frame
        zcr = np.mean(np.abs(np.diff(np.sign(frames), axis=1)) > 0, axis=1)

        # RMS Energy per frame
        rms = np.sqrt(np.mean(frames ** 2, axis=1))

        return STFTResult(
            spectrogram=magnitude.astype(np.float32),
            complex_stft=complex_stft.astype(np.complex64),
            frequencies=frequencies.astype(np.float32),
            times=times.astype(np.float32),
            mel_energies=mel_energies.astype(np.float32),
            mel_frequencies=mel_freqs.astype(np.float32),
            spectral_centroid=spectral_centroid.astype(np.float32),
            spectral_rolloff=spectral_rolloff.astype(np.float32),
            spectral_flux=flux.astype(np.float32),
            zero_crossing_rate=zcr.astype(np.float32),
            rms_energy=rms.astype(np.float32),
            sample_rate=sr
        )

    def _compute_mel_filterbank(
        self,
        magnitude: np.ndarray,
        frequencies: np.ndarray,
        sample_rate: int,
        num_mels: int = 40,
        f_min: float = 20.0,
        f_max: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Triangular Mel-scale filterbank matrix projection."""
        f_max = f_max or (sample_rate / 2.0)

        # Convert Hz to Mel: m = 2595 * log10(1 + f / 700)
        def hz_to_mel(hz):
            return 2595.0 * np.log10(1.0 + hz / 700.0)

        def mel_to_hz(mel):
            return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

        mel_min = hz_to_mel(f_min)
        mel_max = hz_to_mel(f_max)
        mel_points = np.linspace(mel_min, mel_max, num_mels + 2)
        hz_points = mel_to_hz(mel_points)

        # Map to FFT bin indices
        num_bins = len(frequencies)
        bin_indices = np.floor((num_bins - 1) * hz_points / frequencies[-1]).astype(int)
        bin_indices = np.clip(bin_indices, 0, num_bins - 1)

        filterbank = np.zeros((num_mels, num_bins), dtype=np.float32)
        for m in range(1, num_mels + 1):
            f_prev = bin_indices[m - 1]
            f_curr = bin_indices[m]
            f_next = bin_indices[m + 1]

            if f_curr > f_prev:
                filterbank[m - 1, f_prev:f_curr] = (
                    (np.arange(f_prev, f_curr) - f_prev) / (f_curr - f_prev)
                )
            if f_next > f_curr:
                filterbank[m - 1, f_curr:f_next] = (
                    (f_next - np.arange(f_curr, f_next)) / (f_next - f_curr)
                )

        mel_energies = np.dot(filterbank, magnitude)
        center_mels = (mel_points[1:-1])
        center_hz = mel_to_hz(center_mels)
        return mel_energies, center_hz

    # ----------------------------------------------------------------------
    # Mathematical Transformation 4: 3D Phase-Space Attractor (Delay Embedding)
    # ----------------------------------------------------------------------

    def compute_phase_space_attractor(
        self,
        samples: np.ndarray,
        delay: Optional[int] = None,
        embedding_dim: int = 3,
        max_samples: int = 8000
    ) -> Tuple[np.ndarray, int]:
        """
        Reconstructs phase-space manifold trajectory X[n] = [s[n], s[n-tau], s[n-2*tau]]^T.
        If delay is None, computes optimal tau via first zero-crossing of autocorrelation.
        Returns (trajectory_matrix_3d, optimal_tau).
        """
        n = len(samples)
        if n == 0:
            return np.zeros((0, embedding_dim), dtype=np.float32), 1

        # Downsample if overly dense for attractor visualization
        step = max(1, n // max_samples)
        sig = samples[::step]
        m = len(sig)

        # Estimate optimal delay tau via autocorrelation first zero-crossing
        if delay is None:
            tau = self._estimate_delay(sig)
        else:
            tau = max(1, delay)

        total_vectors = m - (embedding_dim - 1) * tau
        if total_vectors <= 0:
            tau = 1
            total_vectors = m - (embedding_dim - 1)

        trajectory = np.zeros((total_vectors, embedding_dim), dtype=np.float32)
        for d in range(embedding_dim):
            start = d * tau
            trajectory[:, d] = sig[start : start + total_vectors]

        return trajectory, tau

    @staticmethod
    def _estimate_delay(samples: np.ndarray, max_lag: int = 200) -> int:
        """Finds first zero-crossing or local minimum of the autocorrelation function."""
        n = len(samples)
        limit = min(n // 2, max_lag)
        if limit < 2:
            return 1

        centered = samples - np.mean(samples)
        var = np.var(samples)
        if var == 0:
            return 1

        # Autocorrelation via FFT
        r = np.correlate(centered, centered, mode="full")
        r = r[n - 1 : n - 1 + limit] / (var * n)

        # Check for first zero-crossing
        for lag in range(1, len(r)):
            if r[lag] <= 0:
                return lag

        # Fallback to first local minimum
        for lag in range(1, len(r) - 1):
            if r[lag] < r[lag - 1] and r[lag] < r[lag + 1]:
                return lag

        return max(1, limit // 4)
