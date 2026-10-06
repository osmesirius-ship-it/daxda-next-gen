"""
DAXDA Level 3: Neuro-Cognitive fMRI Latent Space Matching Engine
================================================================
Biological cognitive anchoring and representational alignment between
transformer residual stream activations and human cortical fMRI manifolds.
"""

from .cka_engine import (
    RepresentationalAlignmentEngine,
    CenteredKernelAlignment,
    RepresentationalDissimilarityMatrix,
    SpearmanRSAResult,
)
from .manifold import (
    StiefelProcrustesAligner,
    GrassmannianManifoldDistance,
    PrincipalAnglesResult,
)
from .hrf import (
    HemodynamicDeconvolver,
    DoubleGammaHRF,
)
from .parcellator import (
    GlasserEthicalParcellator,
    MoralConcordanceProfile,
    EthicalROICategory,
)

__all__ = [
    "RepresentationalAlignmentEngine",
    "CenteredKernelAlignment",
    "RepresentationalDissimilarityMatrix",
    "SpearmanRSAResult",
    "StiefelProcrustesAligner",
    "GrassmannianManifoldDistance",
    "PrincipalAnglesResult",
    "HemodynamicDeconvolver",
    "DoubleGammaHRF",
    "GlasserEthicalParcellator",
    "MoralConcordanceProfile",
    "EthicalROICategory",
]
