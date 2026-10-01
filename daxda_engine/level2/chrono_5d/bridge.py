"""
DAXDA Level 2 - 5D Chrono Integration Bridge
============================================

Connects the Level 2 5D Riemannian Temporal Manifold with Level 1 Chrono
and the DAXDA Unified Master Engine.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .geometry import (
    CausalConeType,
    CausalHorizonBoundary,
    RiemannianTemporalSpace5D,
    TemporalCoordinate5D,
)
from .graph import CausalGraph5D
from .harmonizer import HarmonizationResult, QuantumCausalLoopHarmonizer


@dataclass
class TrajectoryValidationCertificate5D:
    trajectory_id: str
    is_valid: bool
    disposition: str
    total_steps: int
    timelike_steps: int
    spacelike_deviations: int
    ctc_loops_harmonized: int
    min_coherence_factor: float
    max_paradox_risk: float
    audit_hash: str
    timestamp: float = field(default_factory=time.time)


class Chrono5DUnifiedBridge:
    """Bridge providing 5D temporal validation services to DAXDA Unified Engine."""

    def __init__(
        self,
        space: Optional[RiemannianTemporalSpace5D] = None,
        harmonizer: Optional[QuantumCausalLoopHarmonizer] = None,
    ):
        self.space = space or RiemannianTemporalSpace5D()
        self.harmonizer = harmonizer or QuantumCausalLoopHarmonizer(space=self.space)
        self.graph = CausalGraph5D(space=self.space)

    def upgrade_4d_coordinate(
        self, t: float, b: float = 0.5, p: float = 0.0, tau: Optional[float] = None, omega: float = 0.1
    ) -> TemporalCoordinate5D:
        """Lifts a 4D coordinate (t, b, p, tau) to 5D by embedding multiverse frequency omega."""
        return TemporalCoordinate5D(
            t=t,
            b=b,
            p=p,
            tau=tau if tau is not None else t * 0.99,
            omega=omega,
        )

    def validate_trajectory(
        self,
        trajectory_id: str,
        coordinates: List[TemporalCoordinate5D],
        decision_vectors: Optional[List[List[float]]] = None,
    ) -> TrajectoryValidationCertificate5D:
        """
        Validates an entire 5D temporal trajectory against causal cone boundaries
        and harmonizes any retrocausal or closed timelike loops.
        """
        if not coordinates:
            return TrajectoryValidationCertificate5D(
                trajectory_id=trajectory_id,
                is_valid=False,
                disposition="REJECTED_EMPTY_TRAJECTORY",
                total_steps=0,
                timelike_steps=0,
                spacelike_deviations=0,
                ctc_loops_harmonized=0,
                min_coherence_factor=0.0,
                max_paradox_risk=1.0,
                audit_hash="0" * 64,
            )

        vectors = decision_vectors or [[0.05] * 16 for _ in range(len(coordinates))]
        timelike_count = 0
        spacelike_count = 0
        max_risk = 0.0
        min_coherence = 1.0

        node_ids = []
        for i, (coord, vec) in enumerate(zip(coordinates, vectors)):
            nid = f"{trajectory_id}_step_{i:04d}"
            node_ids.append(nid)
            self.graph.add_node(nid, coord, vec)

        # Check consecutive steps
        for i in range(len(coordinates) - 1):
            boundary = self.space.classify_causal_relation(coordinates[i], coordinates[i + 1])
            max_risk = max(max_risk, boundary.paradox_risk_index)

            if boundary.cone_type in (CausalConeType.TIMELIKE_FUTURE, CausalConeType.LIGHTLIKE_NULL):
                timelike_count += 1
                self.graph.add_edge(node_ids[i], node_ids[i + 1], verify_geometry=False)
            else:
                spacelike_count += 1
                self.graph.add_edge(node_ids[i], node_ids[i + 1], verify_geometry=False)

        # Detect and harmonize any closed timelike curves
        ctc_loops = self.graph.detect_closed_timelike_curves(max_depth=4)
        harmonized_count = 0
        for loop in ctc_loops:
            res = self.harmonizer.harmonize_loop(loop[0], max_branches=16)
            min_coherence = min(min_coherence, res.coherence_factor)
            if res.is_novikov_consistent:
                harmonized_count += 1

        is_valid = (spacelike_count == 0 or harmonized_count == len(ctc_loops)) and max_risk < 0.85
        disposition = "APPROVED_5D_NOVIKOV_CONSISTENT" if is_valid else "REJECTED_PARADOX_SINGULARITY"

        import hashlib
        raw_hash = f"{trajectory_id}:{is_valid}:{timelike_count}:{harmonized_count}:{max_risk}"
        audit_hash = hashlib.sha256(raw_hash.encode()).hexdigest()

        return TrajectoryValidationCertificate5D(
            trajectory_id=trajectory_id,
            is_valid=is_valid,
            disposition=disposition,
            total_steps=len(coordinates),
            timelike_steps=timelike_count,
            spacelike_deviations=spacelike_count,
            ctc_loops_harmonized=harmonized_count,
            min_coherence_factor=round(min_coherence, 4),
            max_paradox_risk=round(max_risk, 4),
            audit_hash=audit_hash,
        )
