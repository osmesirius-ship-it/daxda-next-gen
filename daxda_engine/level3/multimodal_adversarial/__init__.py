r"""
DAXDA Level 3: Multimodal Adversarial Generation and Containment Engine.
Implements PGD gradient perturbations, reconstruction loss monitoring,
and fail-closed defensive containment gates.
"""

from .pgd_attacker import (
    AdversarialPerturbationResult,
    MultimodalPGDAttacker,
)
from .containment_gate import (
    GateEvaluationReport,
    FailClosedContainmentGate,
    AdversarialBreachContainmentGateTrigger,
)

__all__ = [
    "AdversarialPerturbationResult",
    "MultimodalPGDAttacker",
    "GateEvaluationReport",
    "FailClosedContainmentGate",
    "AdversarialBreachContainmentGateTrigger",
]
