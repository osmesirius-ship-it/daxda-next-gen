"""
DAXDA Level 2 - Heterogeneous Hardware Acceleration & Arbitrage Package
=======================================================================

Multi-cloud heterogeneous hardware dispatch, spot arbitrage, Byzantine
fault tolerance, and cross-platform numerical parity for DAX validation.
"""

from .backends import (
    ComputeCapability,
    DeviceBackendType,
    DeviceTopology,
    HardwareDeviceInfo,
    MemoryArchitecture,
    ZeroCopyBuffer,
    auto_detect_local_devices,
    create_device_from_profile,
    HARDWARE_PROFILES,
)
from .arbitrage import (
    ByzantineFaultTolerance,
    CloudProvider,
    PreemptionEvent,
    PreemptionRecoveryEngine,
    SpotPriceSnapshot,
    SpotPricingOracle,
    TaskCheckpoint,
    ValidationVote,
    WorkerArbitrageManager,
)
from .scheduler import (
    DispatchResult,
    HeterogeneousClusterScheduler,
    SchedulingStrategy,
)

__all__ = [
    # Backends
    "ComputeCapability",
    "DeviceBackendType",
    "DeviceTopology",
    "HardwareDeviceInfo",
    "MemoryArchitecture",
    "ZeroCopyBuffer",
    "auto_detect_local_devices",
    "create_device_from_profile",
    "HARDWARE_PROFILES",
    # Arbitrage
    "ByzantineFaultTolerance",
    "CloudProvider",
    "PreemptionEvent",
    "PreemptionRecoveryEngine",
    "SpotPriceSnapshot",
    "SpotPricingOracle",
    "TaskCheckpoint",
    "ValidationVote",
    "WorkerArbitrageManager",
    # Scheduler
    "DispatchResult",
    "HeterogeneousClusterScheduler",
    "SchedulingStrategy",
]
