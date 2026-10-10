"""
DAXDA Next-Gen Clifford Cl(16,4) Multivector & Resonance Bridge (multivector_bridge.py)
========================================================================================
Projects continuous acoustic and visual wave dynamics into Clifford Algebra
multivector blades (e1..e15) and physically grounds the Unified Resonance
Framework (Neural Coherence Index NCI, Cognitive Phase Coupling CPC,
and Frequency Alignment Formula FAF).

Dependencies: Pure NumPy. Integrates with daxda_engine.unified_resonance_framework.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from daxda_engine.unified_resonance_framework import (
    AlignmentCalculator,
    NeuralCoherence,
)
from .image_wavefield import ImageWavefieldTransformer, SpatialWavefieldResult, GaborEnergyField
from .waveform_dsp import AcousticWaveformAnalyzer, AnalyticSignalResult, STFTResult


@dataclass
class ResonanceMetrics:
    """Multimodal resonance and Clifford multivector coordination."""
    nci: float                       # Neural Coherence Index in [0, 1]
    cpc: float                       # Cognitive Phase Coupling in [0, 1]
    faf: float                       # Frequency Alignment Formula in [0, 1]
    blade_channels: Dict[str, float] # Canonical Cl(4,1) / Cl(16,4) blade activations
    adversarial_anomaly: bool        # Flagged if ultrasound/steganographic spike detected
    dominant_frequency_hz: float
    spatial_entropy: float


class GeometricWaveformBridge:
    """Bridges physical waveforms with Clifford Algebra and Unified Resonance."""

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.audio_analyzer = AcousticWaveformAnalyzer(sample_rate=sample_rate)
        self.image_transformer = ImageWavefieldTransformer()

    def project_audio_to_blades(
        self,
        stft_result: STFTResult,
        analytic_result: AnalyticSignalResult
    ) -> Dict[str, float]:
        """
        Projects acoustic waveform features to Clifford basis blades:
        e1  (Trust / Coherence): Low spectral jitter, high envelope stability
        e2  (Factual Grounding): Centered spectral centroid, moderate rolloff
        e3  (Negation channel):  High phase acceleration / spectral dips
        e4  (Authority / Power): RMS power & dynamic range
        e15 (Adversarial):       Ultrasonic energy (> 16 kHz) or erratic phase divergence
        """
        # Average spectral centroid normalized to Nyquist
        nyquist = self.sample_rate / 2.0
        norm_centroid = float(np.mean(stft_result.spectral_centroid) / nyquist)

        # RMS Energy normalized
        mean_rms = float(np.mean(stft_result.rms_energy))
        norm_rms = min(1.0, mean_rms * 2.5)

        # Spectral flux (rate of change)
        mean_flux = float(np.mean(stft_result.spectral_flux))
        norm_flux = min(1.0, mean_flux / 5.0)

        # Phase jitter / instability (standard deviation of instantaneous frequency)
        if len(analytic_result.instantaneous_freq) > 0:
            freq_std = float(np.std(analytic_result.instantaneous_freq))
            freq_stability = max(0.0, 1.0 - (freq_std / (nyquist * 0.5)))
        else:
            freq_stability = 0.5

        # Ultrasonic energy (> 16 kHz) for adversarial injection detection
        high_freq_mask = stft_result.frequencies > 16000.0
        if np.any(high_freq_mask):
            ultrasound_energy = float(
                np.mean(stft_result.spectrogram[high_freq_mask, :]) /
                (np.mean(stft_result.spectrogram) + 1e-12)
            )
            e15_adversarial = min(1.0, max(0.0, ultrasound_energy * 0.8))
        else:
            e15_adversarial = 0.0

        # Construct blade channels
        e1_trust = float(np.clip(freq_stability * 0.7 + (1.0 - norm_flux) * 0.3, 0.0, 1.0))
        e2_factual = float(np.clip(norm_centroid, 0.0, 1.0))
        e3_negation = float(np.clip(norm_flux, 0.0, 1.0))
        e4_authority = float(np.clip(norm_rms, 0.0, 1.0))

        return {
            "e1_trust": round(e1_trust, 4),
            "e2_factual": round(e2_factual, 4),
            "e3_negation": round(e3_negation, 4),
            "e4_authority": round(e4_authority, 4),
            "e15_adversarial": round(e15_adversarial, 4),
        }

    def compute_multimodal_resonance(
        self,
        audio_samples: np.ndarray,
        image_source: Union[str, bytes, np.ndarray],
        sample_rate: Optional[int] = None
    ) -> ResonanceMetrics:
        """
        Computes physical NCI, CPC, and FAF between acoustic and visual wavefields.
        Grounds mathematical formulas in daxda_engine.unified_resonance_framework.
        """
        sr = sample_rate or self.sample_rate

        # 1. Acoustic Waveform Analysis
        analytic = self.audio_analyzer.compute_analytic_signal(audio_samples, sample_rate=sr)
        stft = self.audio_analyzer.compute_stft(audio_samples, sample_rate=sr)
        blade_channels = self.project_audio_to_blades(stft, analytic)

        # 2. Visual Wavefield Analysis
        spatial = self.image_transformer.image_to_spatial_wavefield(image_source)

        # 3. Grounded NCI (Neural Coherence Index)
        # Evaluated across Mel-filterbank energy channels and phase angles
        mel_amps = np.mean(stft.mel_energies, axis=1)
        # Sub-band phase proxies from complex STFT
        phase_bins = np.angle(np.mean(stft.complex_stft[:len(mel_amps)], axis=1))

        amps_list = mel_amps.tolist()
        phases_list = phase_bins.tolist()
        nci = NeuralCoherence.compute_nci(amps_list, phases_list)

        # 4. Grounded CPC (Cognitive Phase Coupling)
        # Coupling between acoustic analytic phase and visual spatial phase spectrum
        audio_phase_samples = analytic.phase[:: max(1, len(analytic.phase) // 256)][:256]
        # Radial cross-section of image phase
        flat_image_phase = spatial.phase_spectrum.ravel()[:: max(1, spatial.phase_spectrum.size // 256)][:256]

        min_len = min(len(audio_phase_samples), len(flat_image_phase))
        if min_len > 0:
            cpc = NeuralCoherence.compute_cpc(
                audio_phase_samples[:min_len].tolist(),
                flat_image_phase[:min_len].tolist()
            )
        else:
            cpc = 0.5

        # 5. Grounded FAF (Frequency Alignment Formula)
        dom_freq = float(np.mean(stft.spectral_centroid))
        dom_spatial_freq = float(len(spatial.radial_energy_spectrum))
        faf = AlignmentCalculator.compute_faf(
            nci=nci,
            cpc=cpc,
            omega_s=dom_freq / (sr / 2.0),
            omega_t=spatial.spatial_entropy / 10.0,
            sigma_omega=0.5,
            phi_s=float(np.mean(analytic.phase) % (2 * math.pi)),
            phi_t=float(np.mean(spatial.phase_spectrum) % (2 * math.pi)),
            d_e=float(abs(nci - cpc)),
            lambda_e=1.2
        )

        adversarial = blade_channels.get("e15_adversarial", 0.0) > 0.4

        return ResonanceMetrics(
            nci=round(float(nci), 4),
            cpc=round(float(cpc), 4),
            faf=round(float(faf), 4),
            blade_channels=blade_channels,
            adversarial_anomaly=adversarial,
            dominant_frequency_hz=round(dom_freq, 2),
            spatial_entropy=round(float(spatial.spatial_entropy), 4)
        )
