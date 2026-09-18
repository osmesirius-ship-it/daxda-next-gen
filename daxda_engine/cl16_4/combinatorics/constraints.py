"""
Constraint System for Cl(16,4) Validation
======================================

Implements 4-dimensional constraint satisfaction for the Cl(16,4) space.
"""

from typing import List, Dict, Set, Tuple, Callable, Optional
from dataclasses import dataclass, field
from .cl_space import ClConfig, ClSpace
import numpy as np


@dataclass
class Constraint:
    """A single constraint in the Cl(16,4) space."""
    name: str
    description: str
    check_func: Callable[[ClConfig], bool]
    severity: str = "hard"  # "hard" or "soft"
    metadata: Dict = field(default_factory=dict)


@dataclass
class ConstraintResult:
    """Result of checking a configuration against constraints."""
    config: ClConfig
    passed: List[str]  # Names of passed constraints
    failed: List[str]  # Names of failed constraints
    soft_failed: List[str]  # Names of soft constraints that failed
    score: float  # Overall score (0-1)


class ConstraintSystem:
    """
    Manages constraints for Cl(16,4) validation.
    
    Provides:
    - Constraint registration and management
    - Configuration validation against constraints
    - Scoring and ranking of configurations
    - Dynamic constraint adjustment
    """
    
    def __init__(self, space: Optional[ClSpace] = None):
        self.space = space or ClSpace(n=16, k=4)
        self.constraints: Dict[str, Constraint] = {}
        self._initialize_default_constraints()
    
    def _initialize_default_constraints(self) -> None:
        """Initialize with default Cl(16,4) constraints."""
        
        # Dimension bounds constraints (hard)
        for i in range(4):
            self.register_constraint(
                name=f"dim_{i}_bounds",
                description=f"Dimension {i} must be in range [0, 15]",
                check_func=lambda c, idx=i: 0 <= c.indices[idx] < 16,
                severity="hard"
            )
        
        # Uniqueness constraint (hard)
        self.register_constraint(
            name="unique_dimensions",
            description="All 4 dimensions must be unique",
            check_func=lambda c: len(set(c.indices)) == 4,
            severity="hard"
        )
        
        # Sorted constraint (soft - for canonical form)
        self.register_constraint(
            name="sorted_order",
            description="Dimensions should be in sorted order",
            check_func=lambda c: list(c.indices) == sorted(c.indices),
            severity="soft"
        )
        
        # Minimum spread constraint (soft)
        self.register_constraint(
            name="min_spread",
            description="Minimum spread between dimensions",
            check_func=lambda c: max(c.indices) - min(c.indices) >= 3,
            severity="soft"
        )
    
    def register_constraint(self, name: str, description: str, 
                          check_func: Callable[[ClConfig], bool],
                          severity: str = "hard", metadata: Dict = None) -> None:
        """Register a new constraint."""
        self.constraints[name] = Constraint(
            name=name,
            description=description,
            check_func=check_func,
            severity=severity,
            metadata=metadata or {}
        )
    
    def check_config(self, config: ClConfig) -> ConstraintResult:
        """Check a configuration against all constraints."""
        passed = []
        failed = []
        soft_failed = []
        
        for name, constraint in self.constraints.items():
            try:
                if constraint.check_func(config):
                    passed.append(name)
                else:
                    if constraint.severity == "hard":
                        failed.append(name)
                    else:
                        soft_failed.append(name)
            except Exception as e:
                failed.append(f"{name}_error")
        
        # Calculate score
        total = len(self.constraints)
        hard_count = sum(1 for c in self.constraints.values() if c.severity == "hard")
        passed_count = len(passed)
        
        score = passed_count / total if total > 0 else 1.0
        
        return ConstraintResult(
            config=config,
            passed=passed,
            failed=failed,
            soft_failed=soft_failed,
            score=score
        )
    
    def validate_all(self) -> Dict[ClConfig, ConstraintResult]:
        """Validate all configurations in the space."""
        results = {}
        for config in self.space.space:
            results[config] = self.check_config(config)
        return results
    
    def get_valid_configs(self) -> List[ClConfig]:
        """Get all configurations that pass all hard constraints."""
        valid = []
        for config in self.space.space:
            result = self.check_config(config)
            if not result.failed:
                valid.append(config)
        return valid
    
    def get_top_configs(self, n: int = 10) -> List[Tuple[ClConfig, float]]:
        """Get top N configurations by score."""
        scored = []
        for config in self.space.space:
            result = self.check_config(config)
            scored.append((config, result.score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:n]
    
    def add_dynamic_constraint(self, name: str, condition: Dict) -> None:
        """
        Add a dynamic constraint based on conditions.
        
        Args:
            name: Constraint name
            condition: Dictionary of conditions
        """
        def check_func(config: ClConfig) -> bool:
            for key, value in condition.items():
                if key == "min_sum":
                    if sum(config.indices) < value:
                        return False
                elif key == "max_sum":
                    if sum(config.indices) > value:
                        return False
                elif key == "contains":
                    if not any(i in config.indices for i in value):
                        return False
                elif key == "excludes":
                    if any(i in config.indices for i in value):
                        return False
            return True
        
        self.register_constraint(
            name=name,
            description=f"Dynamic constraint: {condition}",
            check_func=check_func,
            severity="hard"
        )
    
    def remove_constraint(self, name: str) -> bool:
        """Remove a constraint by name."""
        if name in self.constraints:
            del self.constraints[name]
            return True
        return False
    
    def clear_constraints(self) -> None:
        """Remove all constraints."""
        self.constraints.clear()
    
    def __len__(self) -> int:
        return len(self.constraints)
    
    def __repr__(self) -> str:
        return f"ConstraintSystem({len(self.constraints)} constraints)"


# Default constraint system for Cl(16,4)
DEFAULT_CONSTRAINTS = ConstraintSystem()
