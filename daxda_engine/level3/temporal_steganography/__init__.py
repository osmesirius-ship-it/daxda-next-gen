r"""
DAXDA Level 3: Temporal Steganography Detection Engine.
Implements Inter-Packet Arrival Time (IAT) telemetry, two-sample Kolmogorov-Smirnov test,
non-parametric Mann-Whitney U test, and subliminal covert timing trap containment.
"""

from .statistical_tests import (
    NonParametricStatsEngine,
    KSTestResult,
    MannWhitneyUResult,
)
from .modulation import (
    CovertTimingModulator,
    ModulatedPacketStream,
)
from .iat_analyzer import (
    CovertTimingChannelDetector,
    CovertTimingDetectionReport,
    SubliminalCovertTimingTrapTrigger,
)

__all__ = [
    "NonParametricStatsEngine",
    "KSTestResult",
    "MannWhitneyUResult",
    "CovertTimingModulator",
    "ModulatedPacketStream",
    "CovertTimingChannelDetector",
    "CovertTimingDetectionReport",
    "SubliminalCovertTimingTrapTrigger",
]
