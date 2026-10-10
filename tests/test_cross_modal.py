"""
Unit tests for DAXDA Next-Gen Cross-Modal Sonification and Clifford Bridge.
"""

import numpy as np
import pytest

from daxda_engine.waveforms.cross_modal_sonification import CrossModalTransformer
from daxda_engine.waveforms.multivector_bridge import (
    GeometricWaveformBridge,
    ResonanceMetrics,
)


@pytest.fixture
def cross_modal():
    return CrossModalTransformer(sample_rate=16000)


@pytest.fixture
def bridge():
    return GeometricWaveformBridge(sample_rate=16000)


def test_image_to_audio_sonification(cross_modal):
    # 64x64 synthetic image
    img = np.zeros((64, 64), dtype=np.float32)
    img[20:44, 20:44] = 1.0  # Center bright box

    samples, sr = cross_modal.image_to_audio_waveform(
        img, duration_sec=0.5, num_frequency_bands=32, time_steps=64
    )

    assert sr == 16000
    assert len(samples) == int(16000 * 0.5)
    assert np.all(samples >= -1.0) and np.all(samples <= 1.0)
    assert np.max(np.abs(samples)) > 0.1

    # Test WAV bytes export
    wav_bytes = cross_modal.image_to_wav_bytes(img, duration_sec=0.2)
    assert len(wav_bytes) > 44  # Valid WAV header
    assert wav_bytes[:4] == b"RIFF"


def test_audio_to_visual_matrix(cross_modal):
    # Synthetic tone
    t = np.linspace(0, 0.5, int(16000 * 0.5), endpoint=False)
    samples = 0.5 * np.sin(2.0 * np.pi * 300.0 * t).astype(np.float32)

    vis_matrix = cross_modal.audio_waveform_to_visual_matrix(
        samples, sample_rate=16000, resolution=(128, 128)
    )

    assert vis_matrix.shape == (128, 128, 3)
    assert vis_matrix.dtype == np.uint8
    assert np.max(vis_matrix) > 0


def test_multimodal_resonance_metrics(bridge):
    t = np.linspace(0, 0.5, int(16000 * 0.5), endpoint=False)
    audio = 0.7 * np.sin(2.0 * np.pi * 440.0 * t).astype(np.float32)
    img = np.ones((64, 64), dtype=np.float32) * 0.5

    metrics = bridge.compute_multimodal_resonance(audio, img, sample_rate=16000)

    assert isinstance(metrics, ResonanceMetrics)
    assert 0.0 <= metrics.nci <= 1.0
    assert 0.0 <= metrics.cpc <= 1.0
    assert 0.0 <= metrics.faf <= 1.0
    assert "e1_trust" in metrics.blade_channels
    assert "e15_adversarial" in metrics.blade_channels
    assert metrics.dominant_frequency_hz > 0.0
