"""
DAXDA Chrono-Synchronicity Mapping: Geometric Retrocausality Layer
Package root for multi-dimensional temporal validation, retrocausal inference,
paradox mitigation, and acausal synchronicity detection.
"""

from daxda_engine.chrono.geometry.temporal_space import (
    TemporalDimension,
    TemporalCoordinate,
    TemporalState,
    TemporalSpace,
)
from daxda_engine.chrono.geometry.retrocausal_engine import (
    RetrocausalEngine,
    RetrocausalInfluence,
    TemporalPath,
)
from daxda_engine.chrono.geometry.synchronicity import (
    SynchronicityDetector,
    SynchronicityEvent,
)
from daxda_engine.chrono.geometry.visualization import TemporalVisualizer

from daxda_engine.chrono.validation.causal_mapper import (
    CausalMapper,
    CausalEdge,
)
from daxda_engine.chrono.validation.paradox_detector import (
    ParadoxDetector,
    ParadoxType,
    ParadoxAnomaly,
    ParadoxReport,
)
from daxda_engine.chrono.validation.coherence_checker import (
    CoherenceChecker,
    CoherenceAssessment,
)
from daxda_engine.chrono.validation.temporal_validator import (
    TemporalValidator,
    TemporalDisposition,
    TemporalValidationCertificate,
)

from daxda_engine.chrono.integration.cl16_4_integration import Cl16_4ChronoBridge
from daxda_engine.chrono.integration.daxda_engine import ChronoDAXDAAdapter
from daxda_engine.chrono.integration.guard_hooks import ChronoGuardHooks
from daxda_engine.chrono.integration.anomaly_integration import ChronoAnomalyIntegrator

__version__ = "1.0.0"
__all__ = [
    # Geometry
    "TemporalDimension",
    "TemporalCoordinate",
    "TemporalState",
    "TemporalSpace",
    "RetrocausalEngine",
    "RetrocausalInfluence",
    "TemporalPath",
    "SynchronicityDetector",
    "SynchronicityEvent",
    "TemporalVisualizer",
    # Validation
    "CausalMapper",
    "CausalEdge",
    "ParadoxDetector",
    "ParadoxType",
    "ParadoxAnomaly",
    "ParadoxReport",
    "CoherenceChecker",
    "CoherenceAssessment",
    "TemporalValidator",
    "TemporalDisposition",
    "TemporalValidationCertificate",
    # Integration
    "Cl16_4ChronoBridge",
    "ChronoDAXDAAdapter",
    "ChronoGuardHooks",
    "ChronoAnomalyIntegrator",
]
