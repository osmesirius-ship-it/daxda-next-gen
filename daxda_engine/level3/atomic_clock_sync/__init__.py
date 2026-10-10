r"""
DAXDA Level 3: Strontium-87 Optical Lattice Atomic Clock Synchronization Engine.
Implements Sr-87 optical lattice standard simulation, overlapping Allan deviation,
and phase-locked loop synchronization with gravitational redshift compensation.
"""

from .sr87_standard import (
    SR87_CLOCK_TRANSITION_HZ,
    SPEED_OF_LIGHT_M_S,
    STANDARD_GRAVITY_M_S2,
    Sr87OpticalLatticeStandard,
    OpticalClockTelemetry,
)
from .allan_deviation import (
    AllanDeviationCalculator,
    AllanDeviationResult,
)
from .pll_synchronizer import (
    PhaseLockedOpticalSynchronizer,
    SynchronizationResult,
)

__all__ = [
    "SR87_CLOCK_TRANSITION_HZ",
    "SPEED_OF_LIGHT_M_S",
    "STANDARD_GRAVITY_M_S2",
    "Sr87OpticalLatticeStandard",
    "OpticalClockTelemetry",
    "AllanDeviationCalculator",
    "AllanDeviationResult",
    "PhaseLockedOpticalSynchronizer",
    "SynchronizationResult",
]
