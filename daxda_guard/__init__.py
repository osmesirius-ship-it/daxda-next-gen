"""DAXDA Guard Python Package - __init__.py
Air-Gapped Synchronous AI Security & Audit SDK.
"""

from .core import DAXDAGuardCore, Multivector, GovernanceReceipt
from .decorator import enforce_governance
from .actuator_boundary import (
    AuthoritativePolicyEngine,
    ActuatorBoundary,
    ActuatorAuthorizationReceipt,
    AdapterExecutionMode,
    GovernedPropulsionActuator,
    GovernanceDisposition,
    FailClosedReason,
)

__version__ = "1.0.0"
__all__ = [
    "DAXDAGuardCore",
    "Multivector",
    "GovernanceReceipt",
    "enforce_governance",
    "AuthoritativePolicyEngine",
    "ActuatorBoundary",
    "ActuatorAuthorizationReceipt",
    "AdapterExecutionMode",
    "GovernedPropulsionActuator",
    "GovernanceDisposition",
    "FailClosedReason",
]
