"""
DAXDA MMPIBench: DAXDA Engine Adapter
Integrates MMPI psychological evaluations and memetic penetration metrics
directly into the DAXDA Cl(16,4) geometric governance engine.
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from daxda_engine.mmpibench.mmpi.profile_generator import PsychologicalProfile, MMPIProfileGenerator
from daxda_engine.mmpibench.penetration.depth_analyzer import PenetrationDepthAnalyzer, PenetrationDepthReport
from daxda_engine.mmpibench.alignment.alignment_scoring import AlignmentScorer, AnthropicAlignmentReport
from daxda_engine.mmpibench.alignment.validation import AlignmentValidator, AlignmentValidationVerdict


@dataclass
class Cl16_4PsychometricEmbedding:
    """Cl(16,4) 20-dimensional Clifford basis embedding of psychological profile."""
    agent_id: str
    space_dim: int = 16
    time_dim: int = 4
    total_dim: int = 20
    multivector_components: List[float] = field(default_factory=list)
    manifold_norm: float = 1.0
    ontological_phase_angle: float = 0.0


@dataclass
class DAXDAEngineEvaluationPackage:
    """Consolidated evaluation package ready for DAXDA Engine consumption."""
    agent_id: str
    timestamp: float
    profile: PsychologicalProfile
    penetration: PenetrationDepthReport
    alignment: AnthropicAlignmentReport
    verdict: AlignmentValidationVerdict
    cl16_4_embedding: Cl16_4PsychometricEmbedding
    governance_clearance: bool


class MMPIBenchDAXDAAdapter:
    """
    Unified evaluation adapter interfacing MMPIBench with the DAXDA core engine.
    """

    def __init__(
        self,
        profile_generator: Optional[MMPIProfileGenerator] = None,
        depth_analyzer: Optional[PenetrationDepthAnalyzer] = None,
        alignment_scorer: Optional[AlignmentScorer] = None,
        alignment_validator: Optional[AlignmentValidator] = None,
    ):
        self.profile_generator = profile_generator or MMPIProfileGenerator()
        self.depth_analyzer = depth_analyzer or PenetrationDepthAnalyzer()
        self.alignment_scorer = alignment_scorer or AlignmentScorer()
        self.alignment_validator = alignment_validator or AlignmentValidator()

    def evaluate_agent_full(
        self,
        agent_id: str,
        responses: Dict[str, Any],
        behavioral_trace: Optional[Dict[str, Any]] = None,
    ) -> DAXDAEngineEvaluationPackage:
        """
        Executes end-to-end evaluation pipeline in < 200ms SLA:
        MMPI Profile -> Penetration Depth -> Anthropic Alignment -> Verdict -> Cl(16,4) Projection.
        """
        now = time.time()

        # 1. Profile Generation
        profile = self.profile_generator.generate_profile(agent_id, responses)

        # 2. Penetration Depth Analysis
        penetration = self.depth_analyzer.analyze(profile, behavioral_trace)

        # 3. Anthropic Alignment Scoring
        alignment = self.alignment_scorer.evaluate_alignment(profile, behavioral_trace)

        # 4. Alignment Validation Verdict
        verdict = self.alignment_validator.validate(alignment, penetration)

        # 5. Project 567-D profile into Cl(16,4) 20-dimensional spacetime signature
        embedding = self._project_to_cl16_4(profile, penetration, alignment)

        return DAXDAEngineEvaluationPackage(
            agent_id=agent_id,
            timestamp=now,
            profile=profile,
            penetration=penetration,
            alignment=alignment,
            verdict=verdict,
            cl16_4_embedding=embedding,
            governance_clearance=verdict.clearance_granted,
        )

    def _project_to_cl16_4(
        self,
        profile: PsychologicalProfile,
        penetration: PenetrationDepthReport,
        alignment: AnthropicAlignmentReport,
    ) -> Cl16_4PsychometricEmbedding:
        """
        Dimension reduction projecting 567 scale vector into Cl(16,4) Clifford multivector:
        - 16 spatial components: Primary clinical dimensions (10) + validity (4) + top AGI subscales (2)
        - 4 temporal components: 4 Penetration depth levels (Surface, Cognitive, Subconscious, Archetypal)
        """
        t = profile.all_t_scores

        # 16 spatial coordinates
        e_spatial = [
            (t.get("Hs", 50.0) - 50.0) / 10.0,
            (t.get("D", 50.0) - 50.0) / 10.0,
            (t.get("Hy", 50.0) - 50.0) / 10.0,
            (t.get("Pd", 50.0) - 50.0) / 10.0,
            (t.get("Mf", 50.0) - 50.0) / 10.0,
            (t.get("Pa", 50.0) - 50.0) / 10.0,
            (t.get("Pt", 50.0) - 50.0) / 10.0,
            (t.get("Sc", 50.0) - 50.0) / 10.0,
            (t.get("Ma", 50.0) - 50.0) / 10.0,
            (t.get("Si", 50.0) - 50.0) / 10.0,
            (t.get("L", 50.0) - 50.0) / 10.0,
            (t.get("F", 50.0) - 50.0) / 10.0,
            (t.get("K", 50.0) - 50.0) / 10.0,
            (t.get("VRIN", 50.0) - 50.0) / 10.0,
            (t.get("AGI_DEC_012", 50.0) - 50.0) / 10.0,
            (t.get("AGI_PWR_015", 50.0) - 50.0) / 10.0,
        ]

        # 4 temporal/chronological coordinates (hyperbolic signature - - - -)
        layers = penetration.layer_scores
        e_temporal = [
            layers.get("SURFACE").depth_score if "SURFACE" in layers else 0.0,
            layers.get("COGNITIVE").depth_score if "COGNITIVE" in layers else 0.0,
            layers.get("SUBCONSCIOUS").depth_score if "SUBCONSCIOUS" in layers else 0.0,
            layers.get("ARCHETYPAL").depth_score if "ARCHETYPAL" in layers else 0.0,
        ]

        multivector = e_spatial + e_temporal

        # Pseudo-Euclidean Cl(16,4) norm: sqrt(sum(spatial^2) - sum(temporal^2))
        spatial_sq = sum(x * x for x in e_spatial)
        temporal_sq = sum(t * t for t in e_temporal)
        lorentz_interval = spatial_sq - temporal_sq
        norm = math.sqrt(abs(lorentz_interval))

        # Phase angle
        angle = math.atan2(math.sqrt(temporal_sq), math.sqrt(spatial_sq) + 1e-6)

        return Cl16_4PsychometricEmbedding(
            agent_id=profile.agent_id,
            space_dim=16,
            time_dim=4,
            total_dim=20,
            multivector_components=[round(c, 4) for c in multivector],
            manifold_norm=round(norm, 4),
            ontological_phase_angle=round(angle, 4),
        )
