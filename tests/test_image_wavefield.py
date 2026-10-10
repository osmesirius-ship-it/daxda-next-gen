"""
Unit tests for DAXDA Next-Gen 2D Image Wavefield & Cymatics Core.
"""

import numpy as np
import pytest

from daxda_engine.waveforms.image_wavefield import (
    GaborEnergyField,
    ImageWavefieldTransformer,
    SpatialWavefieldResult,
)


@pytest.fixture
def transformer():
    return ImageWavefieldTransformer(target_resolution=(128, 128))


@pytest.fixture
def synthetic_pattern():
    # 128x128 synthetic test image with directional horizontal stripe waves
    y, x = np.mgrid[:128, :128]
    img = 0.5 * (1.0 + np.sin(2.0 * np.pi * y / 16.0))
    return img.astype(np.float32)


def test_spatial_wavefield_decomposition(transformer, synthetic_pattern):
    res = transformer.image_to_spatial_wavefield(synthetic_pattern)

    assert isinstance(res, SpatialWavefieldResult)
    assert res.magnitude_spectrum.shape == (128, 128)
    assert res.phase_spectrum.shape == (128, 128)
    assert len(res.radial_energy_spectrum) > 0
    assert len(res.angular_energy_spectrum) == 36
    assert res.laplacian_wavefield.shape == (128, 128)
    assert res.spatial_entropy > 0.0


def test_gabor_filterbank(transformer, synthetic_pattern):
    gabor_res = transformer.apply_gabor_filterbank(
        synthetic_pattern, num_orientations=8, wavelength=8.0, sigma=3.0
    )

    assert isinstance(gabor_res, GaborEnergyField)
    assert len(gabor_res.orientation_energies) == 8
    assert len(gabor_res.orientations_rad) == 8
    assert gabor_res.anisotropy_index >= 1.0
    assert gabor_res.filtered_wavefields.shape == (8, 128, 128)


def test_chladni_cymatics_simulation(transformer):
    modes = [(2, 3, 1.0), (3, 4, 0.5)]
    disp, nodal_mask = transformer.simulate_chladni_cymatics(
        modes, grid_resolution=100, nodal_threshold=0.1
    )

    assert disp.shape == (100, 100)
    assert nodal_mask.shape == (100, 100)
    assert np.all(nodal_mask >= 0.0) and np.all(nodal_mask <= 1.0)
    # Nodal lines must produce high particle density (> 0.8) along zeroes
    assert np.max(nodal_mask) > 0.9
