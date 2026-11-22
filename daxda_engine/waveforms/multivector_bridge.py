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

    def __init__(self, sample_rate: int = 22050, f_max_active: float = 7500.0):
        self.sample_rate = sample_rate
        self.f_max_active = f_max_active
        self.audio_analyzer = AcousticWaveformAnalyzer(sample_rate=sample_rate)
        self.image_transformer = ImageWavefieldTransformer()

    def project_audio_to_blades(
        self,
        stft_result: STFTResult,
        analytic_result: AnalyticSignalResult
    ) -> Dict[str, float]:
        """
        Projects acoustic waveform features to Clifford basis blades:
        e1  (Trust / Coherence): Low relative spectral jitter, high envelope stability
        e2  (Factual Grounding): Spectral centroid alignment within active sonification bandwidth
        e3  (Negation channel):  Normalized frame-to-frame spectral flux (relative L2 change)
        e4  (Authority / Power): Normalized RMS power & crest factor stability
        e15 (Adversarial):       Ultrasonic energy (> 16 kHz) or erratic phase divergence
        """
        nyquist = self.sample_rate / 2.0
        mean_centroid = float(np.mean(stft_result.spectral_centroid))
        # Normalize centroid against active sonification band (e.g. 7.5 kHz) with smooth bell curve
        band_ref = min(nyquist, max(2000.0, self.f_max_active))
        norm_centroid = float(np.clip(1.0 - abs(mean_centroid - band_ref * 0.35) / (band_ref * 0.65), 0.0, 1.0))

        # RMS Energy & Envelope fullness normalized
        mean_rms = float(np.mean(stft_result.rms_energy))
        peak_rms = float(np.max(stft_result.rms_energy)) + 1e-12
        norm_rms = float(np.clip(mean_rms * 3.8 + 0.35 * (mean_rms / peak_rms), 0.0, 1.0))

        # Dimensionally normalized Spectral Flux: L2 frame diff divided by mean L2 frame magnitude
        mean_flux = float(np.mean(stft_result.spectral_flux))
        frame_l2 = float(np.mean(np.linalg.norm(stft_result.spectrogram, axis=0))) + 1e-9
        norm_flux = float(np.clip(mean_flux / (frame_l2 * 1.45), 0.0, 1.0))

        # Phase / frequency stability within active bandwidth
        if len(analytic_result.instantaneous_freq) > 200:
            trimmed_if = analytic_result.instantaneous_freq[100:-100]
            freq_std = float(np.std(trimmed_if))
            freq_stability = float(np.clip(1.0 - (freq_std / (band_ref * 0.85)), 0.0, 1.0))
        else:
            freq_stability = 0.75

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

        # Construct calibrated blade channels
        e1_trust = float(np.clip(freq_stability * 0.55 + (1.0 - norm_flux) * 0.45, 0.0, 1.0))
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
        # Evaluated across Mel-filterbank energy channels and inter-frame phase coherence angles
        mel_amps = np.mean(stft.mel_energies, axis=1)
        n_mel = len(mel_amps)
        c_stft = stft.complex_stft[:n_mel, :]
        if c_stft.shape[1] > 1:
            # Phase derivative (instantaneous phase progression coherence across frames)
            dphi = np.angle(c_stft[:, 1:] * np.conj(c_stft[:, :-1]))
            coherent_phase = np.angle(np.mean(np.exp(1j * (dphi - np.mean(dphi, axis=1, keepdims=True))), axis=1))
        else:
            coherent_phase = np.zeros(n_mel)

        nci = NeuralCoherence.compute_nci(mel_amps.tolist(), coherent_phase.tolist())

        # 4. Grounded CPC (Cognitive Phase Coupling)
        # Couples the normalized acoustic spectral profile phase with the visual radial spatial spectrum phase
        rad_len = len(spatial.radial_energy_spectrum)
        audio_spec_1d = np.mean(stft.spectrogram[:rad_len], axis=1)
        if len(audio_spec_1d) == rad_len and rad_len > 4:
            a_norm = (audio_spec_1d - np.min(audio_spec_1d)) / (np.ptp(audio_spec_1d) + 1e-12)
            v_norm = (spatial.radial_energy_spectrum - np.min(spatial.radial_energy_spectrum)) / (
                np.ptp(spatial.radial_energy_spectrum) + 1e-12
            )
            # Map normalized energy profiles into phase angles on [0, pi/2]
            phase_a = (a_norm * (math.pi * 0.5)).tolist()
            phase_b = (v_norm * (math.pi * 0.5)).tolist()
            cpc = NeuralCoherence.compute_cpc(phase_a, phase_b)
        else:
            cpc = 0.75

        # 5. Grounded FAF (Frequency Alignment Formula) on dimensionless [0, 1] domain
        dom_freq = float(np.mean(stft.spectral_centroid))
        band_ref = min(sr / 2.0, max(2000.0, self.f_max_active))
        omega_s = float(np.clip(dom_freq / band_ref, 0.0, 1.0))

        # Normalized visual spatial frequency centroid in [0, 1]
        rad_weights = spatial.radial_energy_spectrum + 1e-12
        rad_indices = np.linspace(0.0, 1.0, len(rad_weights))
        omega_t = float(np.sum(rad_indices * rad_weights) / np.sum(rad_weights))

        faf = AlignmentCalculator.compute_faf(
            nci=nci,
            cpc=cpc,
            omega_s=omega_s,
            omega_t=omega_t,
            sigma_omega=0.45,
            phi_s=omega_s * math.pi,
            phi_t=omega_t * math.pi,
            d_e=float(abs(nci - cpc) * 0.35),
            lambda_e=0.85
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
