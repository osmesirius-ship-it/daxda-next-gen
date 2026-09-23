"""
Memory-Efficient State Representation for Cl(16,4)
=================================================

Provides compact binary and integer representations of Cl(16,4) configurations
to minimize memory footprint while maintaining fast lookup.
"""

from typing import Tuple, List, Optional
import struct


class ClState:
    """
    Memory-efficient representation of Cl(16,4) state.
    
    Uses bit-packing to represent configurations in minimal space:
    - 16 bits can represent any dimension index (0-15)
    - 4 indices * 16 bits = 64 bits = 8 bytes per configuration
    - Full Cl(16,4) space (1820 configs) = 1820 * 8 = 14,560 bytes (~14KB)
    """
    
    def __init__(self, indices: Tuple[int, ...]):
        """
        Initialize with configuration indices.
        
        Args:
            indices: Tuple of k indices (must be sorted and unique)
        """
        self.indices = tuple(sorted(indices))
        self._validate()
    
    def _validate(self) -> None:
        """Validate that indices are valid."""
        if len(self.indices) != 4:
            raise ValueError(f"Cl(16,4) requires exactly 4 indices, got {len(self.indices)}")
        if len(set(self.indices)) != 4:
            raise ValueError("Indices must be unique")
        if any(i < 0 or i >= 16 for i in self.indices):
            raise ValueError("Indices must be in range [0, 15]")
    
    @classmethod
    def from_int(cls, packed: int) -> 'ClState':
        """
        Create ClState from packed 64-bit integer.
        
        Format: 4 x 16-bit integers packed into 64 bits
        """
        # Extract 4 x 16-bit values
        mask = 0xFFFF
        indices = [
            (packed >> 48) & mask,
            (packed >> 32) & mask,
            (packed >> 16) & mask,
            packed & mask
        ]
        return cls(tuple(indices))
    
    def to_int(self) -> int:
        """Convert to packed 64-bit integer."""
        return (self.indices[0] << 48) | (self.indices[1] << 32) | \
               (self.indices[2] << 16) | self.indices[3]
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'ClState':
        """Create ClState from 8 bytes."""
        if len(data) != 8:
            raise ValueError(f"Expected 8 bytes, got {len(data)}")
        packed = int.from_bytes(data, byteorder='big')
        return cls.from_int(packed)
    
    def to_bytes(self) -> bytes:
        """Convert to 8 bytes."""
        return self.to_int().to_bytes(8, byteorder='big')
    
    # Note: bitstring methods removed to avoid dependency
    # Can be added back if bitstring is installed
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClState):
            return False
        return self.indices == other.indices
    
    def __hash__(self) -> int:
        return hash(self.indices)
    
    def __repr__(self) -> str:
        return f"ClState{self.indices}"
    
    def __lt__(self, other: 'ClState') -> bool:
        return self.indices < other.indices


class StateLookupTable:
    """
    Pre-computed lookup table for all Cl(16,4) states.
    
    Provides O(1) access to any configuration by index.
    """
    
    def __init__(self):
        self._table: List[ClState] = []
        self._reverse: dict = {}
        self._build_table()
    
    def _build_table(self) -> None:
        """Build the full lookup table."""
        import itertools
        
        for combo in itertools.combinations(range(16), 4):
            state = ClState(combo)
            idx = len(self._table)
            self._table.append(state)
            self._reverse[state.indices] = idx
    
    def __getitem__(self, idx: int) -> ClState:
        return self._table[idx]
    
    def __len__(self) -> int:
        return len(self._table)
    
    def get_index(self, state: ClState) -> Optional[int]:
        return self._reverse.get(state.indices)
    
    def get_by_indices(self, indices: Tuple[int, ...]) -> Optional[ClState]:
        idx = self._reverse.get(indices)
        return self._table[idx] if idx is not None else None


# Pre-built lookup table
STATE_TABLE = StateLookupTable()
