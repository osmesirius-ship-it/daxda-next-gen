"""
DAXDA MMPIBench: Integration Subsystem
Provides DAXDA Engine adapter, security guard hooks, and fleet monitoring with SOC alerting.
"""

from daxda_engine.mmpibench.integration.daxda_engine import (
    Cl16_4PsychometricEmbedding,
    DAXDAEngineEvaluationPackage,
    MMPIBenchDAXDAAdapter,
)
from daxda_engine.mmpibench.integration.guard_hooks import (
    GuardCheckResult,
    MMPIBenchGuardHooks,
)
from daxda_engine.mmpibench.integration.monitoring import (
    SOCAlertEvent,
    FleetMonitoringMetrics,
    MMPIBenchMonitoringSystem,
)

__all__ = [
    "Cl16_4PsychometricEmbedding",
    "DAXDAEngineEvaluationPackage",
    "MMPIBenchDAXDAAdapter",
    "GuardCheckResult",
    "MMPIBenchGuardHooks",
    "SOCAlertEvent",
    "FleetMonitoringMetrics",
    "MMPIBenchMonitoringSystem",
]
