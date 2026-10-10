"""
DAXDA Next-Gen Fault-Tolerant Quantum Error-Correction Package.
"""

from .pauli import PauliOperator
from .stabilizer import StabilizerCode, SteaneCode, SurfaceCode
from .distillation import TransversalCliffordCompiler, MagicStateDistillation
from .decoder import SyndromeDecoder

__all__ = [
    "PauliOperator",
    "StabilizerCode",
    "SteaneCode",
    "SurfaceCode",
    "TransversalCliffordCompiler",
    "MagicStateDistillation",
    "SyndromeDecoder",
]
