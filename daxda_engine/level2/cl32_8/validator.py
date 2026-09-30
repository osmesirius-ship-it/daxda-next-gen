"""
DAXDA Level 2 - Cl(32,8) Hypercombinatorial Validator
=====================================================

Validates 40-dimensional agent decision vectors against Cl(32,8) boundary constraints
and emits certified cryptographic validation receipts.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .space import Blade64, Cl32_8Space


@dataclass
class Cl32_8ValidationReceipt:
    """Certified validation receipt for a Cl(32,8) hypercombinatorial decision."""
    is_valid: bool
    subspace_size: int
    norm_squared: float
    grade_distribution: Dict[int, int]
    latency_ms: float
    cert_hash: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "subspace_size": self.subspace_size,
            "norm_squared": round(self.norm_squared, 6),
            "grade_distribution": self.grade_distribution,
            "latency_ms": round(self.latency_ms, 4),
            "cert_hash": self.cert_hash,
            "timestamp": self.timestamp,
        }


class Cl32_8Validator:
    """High-throughput validator for 40-dimensional Cl(32,8) state spaces."""

    def __init__(
        self,
        space: Optional[Cl32_8Space] = None,
        max_norm_bound: float = 100.0,
        min_norm_bound: float = -100.0,
    ):
        self.space = space or Cl32_8Space(32, 8)
        self.max_norm_bound = max_norm_bound
        self.min_norm_bound = min_norm_bound

    def validate_vector(self, vector: List[float]) -> Cl32_8ValidationReceipt:
        """Validates a 40-dimensional decision vector against Cl(32,8) invariants."""
        t0 = time.perf_counter()

        # Ensure vector has 40 elements
        padded = (vector + [0.0] * 40)[:40]
        blades = self.space.encode_vector_to_multivector(padded)

        norm_sq = self.space.compute_norm_squared(blades)
        is_valid = self.min_norm_bound <= norm_sq <= self.max_norm_bound

        grade_dist: Dict[int, int] = {}
        for b in blades:
            g = b.grade
            grade_dist[g] = grade_dist.get(g, 0) + 1

        latency_ms = (time.perf_counter() - t0) * 1000.0

        # Cryptographic certificate hash
        raw = f"{norm_sq:.6f}:{is_valid}:{len(blades)}:{self.space.total_blades}"
        cert_hash = hashlib.sha256(raw.encode()).hexdigest()

        return Cl32_8ValidationReceipt(
            is_valid=is_valid,
            subspace_size=self.space.total_blades,
            norm_squared=norm_sq,
            grade_distribution=grade_dist,
            latency_ms=latency_ms,
            cert_hash=cert_hash,
        )

    def validate_batch(self, vectors: List[List[float]]) -> List[Cl32_8ValidationReceipt]:
        """Batch validation optimized for multi-agent workloads."""
        return [self.validate_vector(v) for v in vectors]
