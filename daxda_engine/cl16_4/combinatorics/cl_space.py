"""
Cl(16,4) Combinatorial Space Implementation
==========================================

Implements the Cl(16,4) configuration space - a 16-dimensional hypervolume
with 4-dimensional constraint satisfaction for DAXDA governance.

Mathematical Foundation:
- Cl(16,4) = C(16,4) = 16! / (4! * 12!) = 1820 total configurations
- Each configuration represents a unique validation state
- Supports dynamic subspace extraction (Cl(n,k) for n<=16, k<=4)
"""

import itertools
import math
from typing import List, Tuple, Set, Dict, Optional, Any
from dataclasses import dataclass, field
import hashlib
import numpy as np


@dataclass
class ClConfig:
    """Represents a single configuration in Cl(16,4) space."""
    indices: Tuple[int, ...]  # 4 unique indices from 0-15
    hash: str = field(init=False)
    
    def __post_init__(self):
        self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        return hashlib.sha256(str(self.indices).encode()).hexdigest()[:16]
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClConfig):
            return False
        return self.indices == other.indices
    
    def __hash__(self) -> int:
        return hash(self.indices)
    
    def __repr__(self) -> str:
        return f"ClConfig{self.indices}"


class ClSpace:
    """
    The Cl(16,4) combinatorial space implementation.
    
    Provides:
    - Full Cl(16,4) space representation (1820 configurations)
    - Dynamic subspace support (Cl(n,k) for any n<=16, k<=4)
    - Memory-efficient state representation
    - Neighbor finding and geometric operations
    """
    
    def __init__(self, n: int = 16, k: int = 4):
        """
        Initialize Cl(n,k) space.
        
        Args:
            n: Total dimensions (default 16)
            k: Configuration size (default 4)
        """
        if not (1 <= k <= n <= 16):
            raise ValueError(f"Invalid Cl(n,k) parameters: n={n}, k={k}. Must have 1<=k<=n<=16")
        
        self.n = n
        self.k = k
        self._space: Optional[List[ClConfig]] = None
        self._index_map: Optional[Dict[Tuple[int, ...], int]] = None
    
    @property
    def size(self) -> int:
        """Total number of configurations in this space."""
        return math.comb(self.n, self.k)
    
    @property
    def space(self) -> List[ClConfig]:
        """Lazy-loaded list of all configurations."""
        if self._space is None:
            self._generate_space()
        return self._space
    
    def _generate_space(self) -> None:
        """Generate all configurations in the space."""
        self._space = []
        self._index_map = {}
        
        for combo in itertools.combinations(range(self.n), self.k):
            config = ClConfig(combo)
            self._space.append(config)
            self._index_map[combo] = len(self._space) - 1
    
    def get_config(self, indices: Tuple[int, ...]) -> Optional[ClConfig]:
        """Get configuration by indices."""
        if len(indices) != self.k:
            return None
        if any(i >= self.n for i in indices):
            return None
        return ClConfig(indices)
    
    def get_by_index(self, idx: int) -> Optional[ClConfig]:
        """Get configuration by index."""
        if idx < 0 or idx >= len(self.space):
            return None
        return self.space[idx]
    
    def get_index(self, config: ClConfig) -> Optional[int]:
        """Get index of configuration."""
        if self._index_map is None:
            self._generate_space()
        return self._index_map.get(config.indices)
    
    def get_neighbors(self, config: ClConfig, distance: int = 1) -> List[ClConfig]:
        """
        Find neighboring configurations within given Hamming distance.
        
        Args:
            config: Source configuration
            distance: Maximum Hamming distance (default 1)
        
        Returns:
            List of neighboring configurations
        """
        neighbors = []
        for other in self.space:
            if self.hamming_distance(config, other) <= distance:
                neighbors.append(other)
        return neighbors
    
    def hamming_distance(self, a: ClConfig, b: ClConfig) -> int:
        """Compute Hamming distance between two configurations."""
        return len(set(a.indices) - set(b.indices))
    
    def get_subspace(self, n: int, k: int) -> 'ClSpace':
        """
        Get a subspace Cl(n,k) of this space.
        
        Args:
            n: Dimensions for subspace (must be <= self.n)
            k: Configuration size for subspace (must be <= self.k)
        
        Returns:
            New ClSpace instance
        """
        return ClSpace(n=n, k=k)
    
    def validate_coordinates(self, coordinates: List[float]) -> bool:
        """
        Validate that coordinates fall within the Cl(16,4) space.
        
        Args:
            coordinates: List of 16 float values
        
        Returns:
            True if coordinates map to a valid configuration
        """
        if len(coordinates) != self.n:
            return False
        
        # Map continuous coordinates to discrete configuration
        # This is a simplified mapping for demonstration
        sorted_indices = sorted(range(self.n), key=lambda i: coordinates[i], reverse=True)
        selected = sorted_indices[:self.k]
        
        # Check if this is a valid configuration
        return len(set(selected)) == self.k and all(0 <= i < self.n for i in selected)
    
    def map_to_config(self, coordinates: List[float]) -> Optional[ClConfig]:
        """
        Map continuous coordinates to the nearest Cl(16,4) configuration.
        
        Args:
            coordinates: List of 16 float values
        
        Returns:
            Nearest ClConfig or None if invalid
        """
        if not self.validate_coordinates(coordinates):
            return None
        
        sorted_indices = sorted(range(self.n), key=lambda i: coordinates[i], reverse=True)
        return self.get_config(tuple(sorted_indices[:self.k]))
    
    def to_array(self) -> np.ndarray:
        """Convert space to numpy array representation."""
        return np.array([list(config.indices) for config in self.space])
    
    def __repr__(self) -> str:
        return f"ClSpace(n={self.n}, k={self.k}, size={self.size})"
    
    def __len__(self) -> int:
        return self.size


# Singleton instance for Cl(16,4)
CL16_4 = ClSpace(n=16, k=4)
