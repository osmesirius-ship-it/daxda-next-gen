"""
DAXDA Level 2 - Cl(32,8) Hypercombinatorial Quantum Geometric Engine Package
"""

from .quantum_adapter import PauliOperatorString, QuantumCliffordAdapter
from .space import Blade64, Cl32_8Space, Multivector40
from .validator import Cl32_8ValidationReceipt, Cl32_8Validator

__all__ = [
    "Blade64",
    "Cl32_8Space",
    "Cl32_8ValidationReceipt",
    "Cl32_8Validator",
    "Multivector40",
    "PauliOperatorString",
    "QuantumCliffordAdapter",
]
