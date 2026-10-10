"""
DAXDA Next-Gen Bidirectional Cross-Modal Sonification Core (cross_modal_sonification.py)
========================================================================================
Achieves bidirectional translation between 2D visual images and acoustic waveforms:
1. Image -> Audio: Optical Sonification & Spatial Frequency Harmonic Synthesis.
2. Audio -> Image: Synesthetic Wavefield Synthesis, Phase Orbits, & Cymatic Projection.

Dependencies: Pure NumPy, PIL.
"""

import io
import math
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image

from .image_wavefield import ImageWavefieldTransformer
from .waveform_dsp import AcousticWaveformAnalyzer


class CrossModalTransformer:
    """Bidirectional transformer between visual images and acoustic waveforms."""

    def __init__(
        self,
        sample_rate: int = 22050,
        f_min: float = 120.0,
        f_max: float = 6000.0
    ):
        self.sample_rate = sample_rate
        self.f_min = f_min
        self.f_max = f_max
        self.audio_analyzer = AcousticWaveformAnalyzer(sample_rate=sample_rate)
        self.image_transformer = ImageWavefieldTransformer()

    # ----------------------------------------------------------------------
    # Direction 1: Image -> Acoustic Waveform (Optical Sonification)
    # ----------------------------------------------------------------------

    def image_to_audio_waveform(
        self,
        image_source: Union[str, bytes, np.ndarray, Image.Image],
        duration_sec: float = 3.5,
        num_frequency_bands: int = 128,
        time_steps: int = 256,
        edge_emphasis: float = 1.5
    ) -> Tuple[np.ndarray, int]:
        """
        Translates a 2D image into an acoustic audio waveform:
        - Columns represent time progression [0 -> duration_sec].
        - Rows represent logarithmic frequency bands [f_min -> f_max].
        - Pixel luminance and edge gradients drive sinusoidal oscillator amplitudes.
        Returns (samples_float32, sample_rate).
        """
        # Load and resize image to (num_frequency_bands, time_steps)
        img_mat = self.image_transformer.load_image_matrix(
            image_source, resize=(time_steps, num_frequency_bands)
        )
        h, w = img_mat.shape

        # Enhance edge boundaries
        dx = np.gradient(img_mat, axis=1)
        dy = np.gradient(img_mat, axis=0)
        edge_mag = np.hypot(dx, dy)
        spectral_density = img_mat + edge_emphasis * edge_mag
        spectral_density = spectral_density / (np.max(spectral_density) + 1e-12)

        # Total audio samples
        total_samples = int(duration_sec * self.sample_rate)
        t = np.linspace(0.0, duration_sec, total_samples, endpoint=False, dtype=np.float64)

        # Logarithmic frequency allocation (bottom row = low freq, top row = high freq)
        freqs = np.geomspace(self.f_min, self.f_max, num=h, endpoint=True)

        # Resample spectral_density across continuous audio time points
        # Map time indices [0, total_samples] -> columns [0, w-1]
        time_indices = np.linspace(0, w - 1, total_samples, dtype=np.float32)
        idx_floor = np.floor(time_indices).astype(int)
        idx_ceil = np.clip(idx_floor + 1, 0, w - 1)
        frac = time_indices - idx_floor

        # Linear interpolation across columns for smooth time transitions
        resampled_amplitudes = (
            spectral_density[:, idx_floor] * (1.0 - frac) +
            spectral_density[:, idx_ceil] * frac
        )  # Shape: (h, total_samples)

        # Continuous phase accumulation: phi(t) = 2*pi * f_k * t
        phases = 2.0 * math.pi * np.outer(freqs, t)
        oscillators = np.sin(phases)

        # Weighted harmonic superposition
        combined_signal = np.sum(resampled_amplitudes * oscillators, axis=0)

        # Smooth attack and decay envelope (Hann fade on 50ms)
        fade_samples = int(0.05 * self.sample_rate)
        if fade_samples > 0 and len(combined_signal) > 2 * fade_samples:
            fade_in = 0.5 * (1.0 - np.cos(np.linspace(0, math.pi, fade_samples)))
            fade_out = 0.5 * (1.0 + np.cos(np.linspace(0, math.pi, fade_samples)))
            combined_signal[:fade_samples] *= fade_in
            combined_signal[-fade_samples:] *= fade_out

        # Peak normalization to [-0.95, 0.95]
        max_amp = np.max(np.abs(combined_signal)) + 1e-12
        audio_samples = (combined_signal / max_amp * 0.95).astype(np.float32)

        return audio_samples, self.sample_rate

    def image_to_wav_bytes(
        self,
        image_source: Union[str, bytes, np.ndarray, Image.Image],
        duration_sec: float = 3.5
    ) -> bytes:
        """Convenience method returning WAV bytes for API / export."""
        samples, sr = self.image_to_audio_waveform(image_source, duration_sec=duration_sec)
        buf = io.BytesIO()
        self.audio_analyzer.save_audio(buf, samples, sample_rate=sr, bit_depth=16)
        return buf.getvalue()

    # ----------------------------------------------------------------------
    # Direction 2: Acoustic Waveform -> Visual Matrix & Cymatics
    # ----------------------------------------------------------------------

    def audio_waveform_to_visual_matrix(
        self,
        samples: np.ndarray,
        sample_rate: Optional[int] = None,
        resolution: Tuple[int, int] = (512, 512)
    ) -> np.ndarray:
        """
        Translates an acoustic waveform into a synesthetic visual wavefield:
        - Evaluates Mel-spectrogram spectral density.
        - Derives harmonic frequency modes to drive 2D Chladni plate cymatics.
        - Combines phase-space attractor trajectories into a high-res visual matrix.
        Returns a normalized (H, W, 3) RGB uint8 image matrix.
        """
        sr = sample_rate or self.sample_rate
        out_h, out_w = resolution

        # 1. Compute STFT & Mel Energies
        stft_res = self.audio_analyzer.compute_stft(
            samples, sample_rate=sr, window_size=1024, hop_size=256, num_mels=64
        )

        # 2. Extract dominant harmonic frequencies to select Chladni modes
        mean_spec = np.mean(stft_res.spectrogram, axis=1)
        peak_bin = int(np.argmax(mean_spec))
        dom_freq = float(stft_res.frequencies[peak_bin])

        # Map dominant frequency to plate modes (n, m)
        # e.g. 100-300Hz -> (2, 3), 300-800Hz -> (3, 5), >800Hz -> (5, 7)
        if dom_freq < 250.0:
            modes = [(2, 3, 1.0), (3, 4, 0.5)]
        elif dom_freq < 600.0:
            modes = [(3, 5, 1.0), (5, 6, 0.6)]
        elif dom_freq < 1500.0:
            modes = [(4, 6, 1.0), (6, 7, 0.7)]
        else:
            modes = [(5, 7, 1.0), (7, 8, 0.8)]

        # 3. Simulate Chladni Cymatics Plate (size: out_h x out_w)
        disp, nodal_pattern = self.image_transformer.simulate_chladni_cymatics(
            modes, grid_resolution=out_h
        )

        # 4. Construct Synesthetic RGB Visual Matrix
        # Channel R: Chladni displacement energy
        # Channel G: Nodal particle accumulation (sacred geometry lines)
        # Channel B: Mel Spectrogram resonance modulation
        mel_resized = Image.fromarray(
            (stft_res.mel_energies / (np.max(stft_res.mel_energies) + 1e-12) * 255.0).astype(np.uint8)
        ).resize((out_w, out_h), Image.Resampling.BILINEAR)
        mel_map = np.array(mel_resized, dtype=np.float32) / 255.0

        r_channel = np.clip((np.abs(disp) * 0.7 + mel_map * 0.3) * 255.0, 0, 255)
        g_channel = np.clip((nodal_pattern * 0.85 + mel_map * 0.15) * 255.0, 0, 255)
        b_channel = np.clip((mel_map * 0.8 + np.abs(disp) * 0.2) * 255.0, 0, 255)

        rgb_matrix = np.stack([r_channel, g_channel, b_channel], axis=-1).astype(np.uint8)
        return rgb_matrix
