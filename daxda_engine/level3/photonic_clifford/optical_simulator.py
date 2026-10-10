"""
DAXDA Next-Gen Optical Coherent Field & Homodyne Simulator (optical_simulator.py)
=================================================================================
Simulates optical field propagation through integrated photonic MZI meshes,
including waveguide attenuation loss (dB), thermal phase drift noise,
and balanced homodyne coherent photodiode detection.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np

from .mzi_mesh import ClementsMZIMesh


@dataclass
class OpticalDetectionResult:
    """Detection metrics at photodiode output array."""
    output_fields: np.ndarray        # Complex electric field amplitudes (N modes)
    photodiode_currents: np.ndarray  # Optical power / detector currents |E_k|^2
    total_transmitted_power: float   # Sum of detected powers
    waveguide_loss_db: float         # Simulated waveguide insertion loss
    phase_drift_rad: float           # Thermal noise deviation applied
    fidelity: float                  # Unitary fidelity compared to ideal matrix


class PhotonicSimulator:
    """Coherent optical propagation simulator for Clifford accelerators."""

    def __init__(
        self,
        waveguide_loss_db: float = 0.12,
        phase_noise_std: float = 0.0015
    ):
        self.waveguide_loss_db = waveguide_loss_db
        self.phase_noise_std = phase_noise_std

    def propagate_field(
        self,
        mesh: ClementsMZIMesh,
        input_field: np.ndarray,
        apply_noise: bool = True
    ) -> OpticalDetectionResult:
        """
        Propagates complex electric field vector E_in through MZI mesh:
        E_out = alpha * (U + delta_U) * E_in
        where alpha = 10^(-loss_db / 20).
        """
        n = mesh.num_modes
        if len(input_field) != n:
            raise ValueError(f"Input field mode count {len(input_field)} != mesh modes {n}")

        # Check if mesh has precompiled cached unitary
        if not hasattr(mesh, "_cached_unitary") or mesh._cached_unitary is None:
            mesh._cached_unitary = mesh.reconstruct_unitary()
        ideal_U = mesh._cached_unitary

        # Attenuation factor
        alpha = 10.0 ** (-self.waveguide_loss_db / 20.0)

        # Thermal phase drift on mesh elements
        if apply_noise and self.phase_noise_std > 0:
            perturbed_mesh = ClementsMZIMesh(num_modes=n)
            perturbed_mesh.output_phases = mesh.output_phases + np.random.normal(
                0, self.phase_noise_std, size=n
            )
            perturbed_elements = []
            for elem in mesh.elements:
                d_theta = np.random.normal(0, self.phase_noise_std)
                d_phi = np.random.normal(0, self.phase_noise_std)
                from .mzi_mesh import MZIEelement
                perturbed_elements.append(
                    MZIEelement(
                        port_m=elem.port_m,
                        port_n=elem.port_n,
                        theta=elem.theta + d_theta,
                        phi=elem.phi + d_phi
                    )
                )
            perturbed_mesh.elements = perturbed_elements
            sim_U = perturbed_mesh.reconstruct_unitary()
            phase_drift = float(self.phase_noise_std)
        else:
            sim_U = ideal_U
            phase_drift = 0.0

        # Propagate optical electric field
        e_out = alpha * np.dot(sim_U, input_field.astype(np.complex128))

        # Photodiode optical power / currents: I_k = |E_out,k|^2
        currents = np.abs(e_out) ** 2
        total_power = float(np.sum(currents))

        # Fidelity between ideal and noisy execution
        if apply_noise:
            fidelity = mesh.compute_fidelity(sim_U)
        else:
            fidelity = 1.0

        return OpticalDetectionResult(
            output_fields=e_out,
            photodiode_currents=currents.astype(np.float64),
            total_transmitted_power=total_power,
            waveguide_loss_db=self.waveguide_loss_db,
            phase_drift_rad=phase_drift,
            fidelity=fidelity
        )
