"""
DAXDA Cl(16,4) Hypercombinatorial Governance Engine
====================================================

A 16-dimensional hypervolume validation space with 4-dimensional constraint satisfaction
for AGI containment and governance.

Cl(16,4) represents the combinatorial configuration space C(16,4) = 16! / (4! * 12!) = 1820
which provides the mathematical foundation for DAXDA's next-generation validation.
"""

from .combinatorics.cl_space import ClSpace
from .validation.validator import HyperValidator
from .validation.parallel import ParallelValidator
from .validation.adaptive import AdaptiveConstraintManager

__version__ = "1.0.0"
__all__ = ["ClSpace", "HyperValidator", "ParallelValidator", "AdaptiveConstraintManager"]
