"""
Unit tests for Photonic Clifford Accelerator & MZI Mesh.
"""

import numpy as np
import pytest
from daxda_engine.level3.photonic_clifford import (
    ClementsMZIMesh,
    MZIEelement,
    PhotonicSimulator,
)


def test_single_mzi_unitarity():
    """Verify 2x2 MZI transfer matrix is unitary: T^dag T = I."""
    elem = MZIEelement(port_m=0, port_n=1, theta=0.45, phi=1.2)
    T = elem.transfer_matrix(total_modes=2)

    diff = np.dot(T.conj().T, T) - np.eye(2)
    assert np.linalg.norm(diff) < 1e-12


def test_clements_decomposition_roundtrip():
    """Verify random unitary decomposition into Clements MZI mesh has fidelity > 0.9999."""
    n = 4
    # Generate random Haar-distributed unitary matrix
    np.random.seed(42)
    X = (np.random.randn(n, n) + 1j * np.random.randn(n, n)) / np.sqrt(2.0)
    Q, R = np.linalg.qr(X)
    target_U = Q

    mesh = ClementsMZIMesh.decompose_unitary(target_U)
    recon_U = mesh.reconstruct_unitary()

    # Check unitarity
    diff = np.dot(recon_U.conj().T, recon_U) - np.eye(n)
    assert np.linalg.norm(diff) < 1e-10

    # Check fidelity
    fidelity = mesh.compute_fidelity(target_U)
    assert fidelity > 0.9999, f"Fidelity too low: {fidelity}"


def test_optical_simulator_propagation():
    """Verify optical field propagation through MZI mesh."""
    n = 4
    np.random.seed(123)
    X = (np.random.randn(n, n) + 1j * np.random.randn(n, n)) / np.sqrt(2.0)
    Q, _ = np.linalg.qr(X)

    mesh = ClementsMZIMesh.decompose_unitary(Q)
    sim = PhotonicSimulator(waveguide_loss_db=0.12, phase_noise_std=0.001)

    # Input field with unit power on port 0
    e_in = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.complex128)
    res = sim.propagate_field(mesh, e_in, apply_noise=True)

    assert len(res.output_fields) == n
    assert len(res.photodiode_currents) == n
    assert res.total_transmitted_power > 0.9  # Mild attenuation
    assert res.fidelity > 0.995
