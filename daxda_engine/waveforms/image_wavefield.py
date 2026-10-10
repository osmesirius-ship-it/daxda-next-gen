"""
DAXDA Next-Gen 2D Image Wavefield & Cymatics Core (image_wavefield.py)
======================================================================
Transforms 2D images into continuous spatial wavefields, multi-orientation
2D Gabor wavelet energy tensors, and simulates 2D Chladni plate cymatic
nodal line resonance patterns driven by acoustic harmonic modes.

Dependencies: Pure NumPy, PIL (or pure NumPy array fallback).
"""

import io
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image


@dataclass
class SpatialWavefieldResult:
    """2D Spatial frequency wavefield decomposition."""
    magnitude_spectrum: np.ndarray      # 2D Centered log-magnitude spectrum
    phase_spectrum: np.ndarray          # 2D Centered phase spectrum [-pi, pi]
    radial_energy_spectrum: np.ndarray  # 1D Radial power distribution (DC to Nyquist)
    angular_energy_spectrum: np.ndarray # 1D Orientation distribution [0, pi]
    laplacian_wavefield: np.ndarray     # 2D High-pass spatial edge wavelets
    spatial_entropy: float              # Shannon entropy of spatial frequency distribution
    resolution: Tuple[int, int]         # (height, width)


@dataclass
class GaborEnergyField:
    """Multi-orientation 2D Gabor filterbank analysis."""
    orientation_energies: np.ndarray    # 1D energy per orientation angle
    orientations_rad: np.ndarray        # Angles in radians
    dominant_orientation_rad: float     # Dominant angle
    anisotropy_index: float             # Ratio of max to mean orientation energy
    filtered_wavefields: np.ndarray     # 3D Stack of filtered spatial wavefields


class ImageWavefieldTransformer:
    """Transforms 2D images into continuous spatial wavefields and cymatic resonance."""

    def __init__(self, target_resolution: Tuple[int, int] = (256, 256)):
        self.target_resolution = target_resolution

    # ----------------------------------------------------------------------
    # Image Loading & Preprocessing
    # ----------------------------------------------------------------------

    @staticmethod
    def load_image_matrix(
        source: Union[str, bytes, io.BytesIO, np.ndarray, Image.Image],
        resize: Optional[Tuple[int, int]] = None
    ) -> np.ndarray:
        """
        Loads an image source into normalized grayscale float32 matrix [0.0, 1.0].
        Shape: (H, W).
        """
        if isinstance(source, np.ndarray):
            if source.ndim == 3:
                # RGB / RGBA -> Grayscale luminosity
                img_gray = (
                    0.299 * source[:, :, 0] +
                    0.587 * source[:, :, 1] +
                    0.114 * source[:, :, 2]
                )
            else:
                img_gray = source.astype(np.float32)

            if img_gray.max() > 1.0:
                img_gray = img_gray / 255.0
            img_gray = np.clip(img_gray, 0.0, 1.0)

            if resize is not None:
                pil_img = Image.fromarray((img_gray * 255.0).astype(np.uint8))
                pil_img = pil_img.resize(resize, Image.Resampling.BILINEAR)
                return np.array(pil_img, dtype=np.float32) / 255.0
            return img_gray

        # From file path, bytes, or PIL Image
        if isinstance(source, Image.Image):
            pil_img = source.convert("L")
        elif isinstance(source, (bytes, io.BytesIO)):
            buf = io.BytesIO(source) if isinstance(source, bytes) else source
            pil_img = Image.open(buf).convert("L")
        else:
            pil_img = Image.open(source).convert("L")

        if resize is not None:
            pil_img = pil_img.resize(resize, Image.Resampling.BILINEAR)

        arr = np.array(pil_img, dtype=np.float32) / 255.0
        return arr

    # ----------------------------------------------------------------------
    # Mathematical Transformation 1: 2D Spatial Fourier Decomposition
    # ----------------------------------------------------------------------

    def image_to_spatial_wavefield(
        self,
        image_source: Union[str, bytes, np.ndarray, Image.Image]
    ) -> SpatialWavefieldResult:
        """
        Decomposes 2D image into 2D spatial frequency plane-waves:
        F(u, v) = FFT2{I(x, y)}.
        Extracts log-magnitude, phase spectrum, radial distribution, and angular distribution.
        """
        img = self.load_image_matrix(image_source, resize=self.target_resolution)
        h, w = img.shape

        # 2D Fast Fourier Transform
        f_transform = np.fft.fft2(img)
        f_shift = np.fft.fftshift(f_transform)

        # Log magnitude spectrum: log(1 + |F(u, v)|)
        magnitude = np.abs(f_shift)
        log_mag = np.log1p(magnitude)
        norm_mag = log_mag / (np.max(log_mag) + 1e-12)

        # Phase spectrum: angle(F(u, v))
        phase = np.angle(f_shift)

        # Radial Frequency Power Spectrum (DC center to Nyquist edge)
        cy, cx = h // 2, w // 2
        y, x = np.ogrid[:h, :w]
        r = np.hypot(x - cx, y - cy).astype(np.int32)
        max_r = min(cx, cy)

        # Radial binning
        radial_bins = np.bincount(r.ravel(), weights=magnitude.ravel())
        radial_counts = np.bincount(r.ravel())
        radial_counts[radial_counts == 0] = 1
        radial_energy = (radial_bins / radial_counts)[:max_r]

        # Angular Orientation Spectrum (0 to pi radians)
        angles = (np.arctan2(y - cy, x - cx) % math.pi)
        num_angular_bins = 36
        angle_bin_idx = np.clip(
            (angles / math.pi * num_angular_bins).astype(np.int32),
            0, num_angular_bins - 1
        )
        angular_bins = np.bincount(angle_bin_idx.ravel(), weights=magnitude.ravel(), minlength=num_angular_bins)
        angular_counts = np.bincount(angle_bin_idx.ravel(), minlength=num_angular_bins)
        angular_counts[angular_counts == 0] = 1
        angular_energy = angular_bins / angular_counts

        # Spatial Laplacian Wavefield (discrete 2nd derivative filter)
        laplacian_kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
        padded = np.pad(img, 1, mode="reflect")
        laplacian = (
            padded[:-2, 1:-1] * laplacian_kernel[0, 1] +
            padded[1:-1, :-2] * laplacian_kernel[1, 0] +
            padded[1:-1, 1:-1] * laplacian_kernel[1, 1] +
            padded[1:-1, 2:] * laplacian_kernel[1, 2] +
            padded[2:, 1:-1] * laplacian_kernel[2, 1]
        )

        # Shannon entropy of normalized spatial frequency distribution
        p = magnitude / (np.sum(magnitude) + 1e-12)
        p = p[p > 0]
        entropy = float(-np.sum(p * np.log2(p)))

        return SpatialWavefieldResult(
            magnitude_spectrum=norm_mag.astype(np.float32),
            phase_spectrum=phase.astype(np.float32),
            radial_energy_spectrum=radial_energy.astype(np.float32),
            angular_energy_spectrum=angular_energy.astype(np.float32),
            laplacian_wavefield=laplacian.astype(np.float32),
            spatial_entropy=entropy,
            resolution=(h, w)
        )

    # ----------------------------------------------------------------------
    # Mathematical Transformation 2: 2D Gabor Wavelet Filterbank
    # ----------------------------------------------------------------------

    def apply_gabor_filterbank(
        self,
        image_source: Union[str, bytes, np.ndarray, Image.Image],
        num_orientations: int = 8,
        wavelength: float = 8.0,
        sigma: float = 4.0,
        gamma: float = 0.5
    ) -> GaborEnergyField:
        """
        Decomposes image across multiple orientation angles theta:
        G(x', y') = exp(-(x'^2 + gamma^2 * y'^2) / (2 * sigma^2)) * cos(2 * pi * x' / lambda)
        Models primary visual cortex simple-cell receptive fields.
        """
        img = self.load_image_matrix(image_source, resize=self.target_resolution)
        h, w = img.shape

        angles = np.linspace(0, math.pi, num_orientations, endpoint=False)
        energies = np.zeros(num_orientations, dtype=np.float32)
        filtered_stack = np.zeros((num_orientations, h, w), dtype=np.float32)

        # Kernel size
        ksize = int(math.ceil(sigma * 6))
        if ksize % 2 == 0:
            ksize += 1
        half = ksize // 2
        y, x = np.mgrid[-half : half + 1, -half : half + 1]

        # FFT of image for fast frequency-domain filtering
        img_fft = np.fft.fft2(img, s=(h + ksize, w + ksize))

        for idx, theta in enumerate(angles):
            # Coordinate rotation
            x_theta = x * np.cos(theta) + y * np.sin(theta)
            y_theta = -x * np.sin(theta) + y * np.cos(theta)

            # Gabor kernel
            gaussian = np.exp(-(x_theta ** 2 + (gamma * y_theta) ** 2) / (2.0 * sigma ** 2))
            cos_wave = np.cos(2.0 * math.pi * x_theta / wavelength)
            kernel = (gaussian * cos_wave).astype(np.float32)
            kernel -= np.mean(kernel)  # Zero DC bias

            # 2D Convolution via FFT
            kernel_fft = np.fft.fft2(kernel, s=(h + ksize, w + ksize))
            filtered = np.real(np.fft.ifft2(img_fft * kernel_fft))
            # Crop valid interior
            cropped = filtered[half : half + h, half : half + w]
            filtered_stack[idx] = cropped

            # Energy in this orientation
            energies[idx] = float(np.sum(cropped ** 2))

        # Anisotropy index: max energy vs mean energy
        mean_e = np.mean(energies) + 1e-12
        max_e = np.max(energies)
        anisotropy = float(max_e / mean_e)

        dom_idx = int(np.argmax(energies))
        dom_angle = float(angles[dom_idx])

        return GaborEnergyField(
            orientation_energies=energies,
            orientations_rad=angles,
            dominant_orientation_rad=dom_angle,
            anisotropy_index=anisotropy,
            filtered_wavefields=filtered_stack
        )

    # ----------------------------------------------------------------------
    # Mathematical Transformation 3: 2D Chladni Plate Cymatics Simulator
    # ----------------------------------------------------------------------

    @staticmethod
    def simulate_chladni_cymatics(
        modal_modes: List[Tuple[int, int, float]],
        grid_resolution: int = 256,
        plate_size: float = 1.0,
        nodal_threshold: float = 0.08
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulates Chladni plate vibration displacement field:
        w_nm(x, y) = a * cos(n*pi*x/L)*cos(m*pi*y/L) - b * cos(m*pi*x/L)*cos(n*pi*x/L)
        Returns:
        - displacement_field: 2D continuous vibrating surface heightmap [-1.0, 1.0]
        - nodal_sand_pattern: 2D binary/soft mask of particle accumulation along zero-nodal lines.
        """
        x = np.linspace(-plate_size, plate_size, grid_resolution, dtype=np.float32)
        y = np.linspace(-plate_size, plate_size, grid_resolution, dtype=np.float32)
        X, Y = np.meshgrid(x, y)

        total_displacement = np.zeros((grid_resolution, grid_resolution), dtype=np.float32)

        for n, m, weight in modal_modes:
            # Symmetrical free-boundary 2D square plate wave equation
            phi_nm = (
                np.cos(n * math.pi * X / plate_size) * np.cos(m * math.pi * Y / plate_size) -
                np.cos(m * math.pi * X / plate_size) * np.cos(n * math.pi * Y / plate_size)
            )
            total_displacement += weight * phi_nm

        # Normalize displacement
        max_val = np.max(np.abs(total_displacement)) + 1e-12
        norm_displacement = total_displacement / max_val

        # Nodal lines: particles settle where displacement amplitude |w| approaches 0
        # Inverted exponential potential: high density at nodes
        nodal_density = np.exp(-((np.abs(norm_displacement)) ** 2) / (2.0 * (nodal_threshold ** 2)))

        return norm_displacement, nodal_density.astype(np.float32)
