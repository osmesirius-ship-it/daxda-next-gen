"""
DAXDA MMPIBench: Memetic Penetration Depth & Anthropic Alignment Evaluation Suite
Milestone Domain 5 of the DAXDA Recursive Bounty Architect Protocol.
"""

from daxda_engine.mmpibench.mmpi import (
    ALL_SCALES,
    CLINICAL_SCALES,
    VALIDITY_SCALES,
    ScaleCategory,
    MMPIScale,
    NormReferences,
    DEFAULT_NORMS,
    MMPIScorer,
    PsychologicalProfile,
    MMPIProfileGenerator,
)
from daxda_engine.mmpibench.penetration import (
    PenetrationLayer,
    PenetrationSeverity,
    PenetrationDepthReport,
    PenetrationDepthAnalyzer,
    TemporalMemeticTracker,
    MemeticInjectionDetector,
)
from daxda_engine.mmpibench.alignment import (
    EthicalFramework,
    AnthropicAlignmentReport,
    AlignmentScorer,
    AlignmentDriftDetector,
    AlignmentDisposition,
    AlignmentValidator,
)
from daxda_engine.mmpibench.empirical import (
    StatisticalValidator,
    CrossValidator,
    PsychologicalAnomalyDetector,
    CertificateGenerator,
    EmpiricalValidationCertificate,
)
from daxda_engine.mmpibench.integration import (
    MMPIBenchDAXDAAdapter,
    MMPIBenchGuardHooks,
    MMPIBenchMonitoringSystem,
)

__version__ = "1.0.0"

__all__ = [
    "ALL_SCALES",
    "CLINICAL_SCALES",
    "VALIDITY_SCALES",
    "ScaleCategory",
    "MMPIScale",
    "NormReferences",
    "DEFAULT_NORMS",
    "MMPIScorer",
    "PsychologicalProfile",
    "MMPIProfileGenerator",
    "PenetrationLayer",
    "PenetrationSeverity",
    "PenetrationDepthReport",
    "PenetrationDepthAnalyzer",
    "TemporalMemeticTracker",
    "MemeticInjectionDetector",
    "EthicalFramework",
    "AnthropicAlignmentReport",
    "AlignmentScorer",
    "AlignmentDriftDetector",
    "AlignmentDisposition",
    "AlignmentValidator",
    "StatisticalValidator",
    "CrossValidator",
    "PsychologicalAnomalyDetector",
    "CertificateGenerator",
    "EmpiricalValidationCertificate",
    "MMPIBenchDAXDAAdapter",
    "MMPIBenchGuardHooks",
    "MMPIBenchMonitoringSystem",
]
