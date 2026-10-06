"""
DAXDA Level 3: Real-Time BCI Alignment Attestation Engine
=========================================================
Riemannian EEG covariance manifolds on SPD cones S_+^n,
vigilance drift detection, and neurometric hardware attestation.
"""

from .manifold import (
    RiemannianEEGCovarianceEngine,
    airm_geodesic_distance,
    frechet_mean_spd,
    tangent_space_log_map,
)
from .decoders import (
    VigilanceDriftDetector,
    CognitiveEpochAssessment,
    ERNDetector,
)
from .attestation import (
    NeurometricAttestationIssuer,
    NeurometricReceipt,
)

__all__ = [
    "RiemannianEEGCovarianceEngine",
    "airm_geodesic_distance",
    "frechet_mean_spd",
    "tangent_space_log_map",
    "VigilanceDriftDetector",
    "CognitiveEpochAssessment",
    "ERNDetector",
    "NeurometricAttestationIssuer",
    "NeurometricReceipt",
]
