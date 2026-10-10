"""
DAXDA Level 4 — Cl(128,32) Universal Topological Multivector Package
"""

from .multivector import Cl128_32Multivector
from .anyonic_braiding import (
    AnyonicBraidingEngine,
    TopologicalBraidReceipt,
)

# Alias for compatibility
AnyonicBraidCompiler = AnyonicBraidingEngine

__all__ = [
    "Cl128_32Multivector",
    "AnyonicBraidingEngine",
    "AnyonicBraidCompiler",
    "TopologicalBraidReceipt",
]
