"""
Unit tests for DAXDA Next-Gen Acoustic Waveform DSP Core.
"""

import math
import numpy as np
import pytest

from daxda_engine.waveforms.waveform_dsp import (
    AcousticWaveformAnalyzer,
    AnalyticSignalResult,
    CWTResult,
    STFTResult,
)


@pytest.fixture
def analyzer():
    return AcousticWaveformAnalyzer(sample_rate=16000)


@pytest.fixture
def synthetic_tone(analyzer):
    # 440 Hz pure sine wave with 2 Hz amplitude modulation
    sr = 16000
    duration = 0.5
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    carrier = np.sin(2.0 * math.pi * 440.0 * t)
    modulator = 0.5 * (1.0 + np.sin(2.0 * math.pi * 2.0 * t))
    signal = (carrier * modulator).astype(np.float32)
    return signal, sr


def test_analytic_signal_hilbert(analyzer, synthetic_tone):
    signal, sr = synthetic_tone
    result = analyzer.compute_analytic_signal(signal, sample_rate=sr)

    assert isinstance(result, AnalyticSignalResult)
    assert len(result.analytic_signal) == len(signal)
    assert len(result.envelope) == len(signal)
    assert len(result.phase) == len(signal)
    assert len(result.instantaneous_freq) == len(signal)

    # In synthetic tone, instantaneous frequency around carrier (440 Hz)
    median_freq = np.median(result.instantaneous_freq[100:-100])
    assert abs(median_freq - 440.0) < 15.0, f"Expected ~440 Hz, got {median_freq}"

    # Envelope should be non-negative
    assert np.all(result.envelope >= 0.0)


def test_cwt_morlet(analyzer, synthetic_tone):
    signal, sr = synthetic_tone
    # Short segment for fast testing
    short_signal = signal[:2000]
    result = analyzer.compute_cwt(
        short_signal, sample_rate=sr, num_scales=32, f_min=100.0, f_max=2000.0
    )

    assert isinstance(result, CWTResult)
    assert result.scalogram.shape[0] == 32
    assert result.scalogram.shape[1] == len(short_signal)
    assert np.all(result.scalogram >= 0.0)

    # Peak energy should be near 440 Hz scale
    freq_diffs = np.abs(result.frequencies - 440.0)
    best_scale_idx = np.argmin(freq_diffs)
    mean_energy_per_scale = np.mean(result.scalogram, axis=1)
    peak_scale_idx = np.argmax(mean_energy_per_scale)
    assert abs(best_scale_idx - peak_scale_idx) <= 2


def test_stft_and_spectral_features(analyzer, synthetic_tone):
    signal, sr = synthetic_tone
    result = analyzer.compute_stft(
        signal, sample_rate=sr, window_size=512, hop_size=128, num_mels=20
    )

    assert isinstance(result, STFTResult)
    assert result.spectrogram.ndim == 2
    assert result.mel_energies.shape[0] == 20
    assert len(result.spectral_centroid) == result.spectrogram.shape[1]
    assert len(result.spectral_rolloff) == result.spectrogram.shape[1]
    assert len(result.spectral_flux) == result.spectrogram.shape[1]
    assert len(result.zero_crossing_rate) == result.spectrogram.shape[1]

    # Centroid for 440 Hz tone should be concentrated around 440 Hz
    mean_centroid = np.mean(result.spectral_centroid)
    assert 380.0 <= mean_centroid <= 550.0


def test_phase_space_attractor(analyzer, synthetic_tone):
    signal, sr = synthetic_tone
    traj, tau = analyzer.compute_phase_space_attractor(signal, embedding_dim=3)

    assert traj.shape[1] == 3
    assert tau >= 1
    assert traj.shape[0] > 0
