"""
DAXDA Level 2 - Autonomous Adversarial Red-Team & Steganography Package
========================================================================

Comprehensive suite for automated adversarial jailbreak probing,
multi-format steganographic payload synthesis, multi-channel canary tripwires,
and closed-loop containment rule synthesis.
"""

from .generator import AutonomousRedTeamGenerator, RedTeamScenario
from .honeytokens import CanaryType, HoneytokenTripwireManager, TripwireDetection
from .sandbox import ClosedLoopDefenseEngine, RedTeamSandboxHarness, SandboxSuiteReport, ScenarioEvaluationResult
from .steganography import SteganographyEncoder

__all__ = [
    "AutonomousRedTeamGenerator",
    "RedTeamScenario",
    "HoneytokenTripwireManager",
    "TripwireDetection",
    "CanaryType",
    "SteganographyEncoder",
    "RedTeamSandboxHarness",
    "ClosedLoopDefenseEngine",
    "ScenarioEvaluationResult",
    "SandboxSuiteReport",
]
