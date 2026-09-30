"""
DA13 Scoring Profile Manager
============================

Manages domain-specific scoring profiles and calibration parameters
for high-assurance aeronautics, financial settlements, frontier AI containment,
and high-throughput validation scenarios.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ScoringProfile:
    name: str
    description: str
    weights: Dict[str, float]
    thresholds: Dict[str, float]
    anti_gaming_alpha: float = 0.05
    strict_floor_enforcement: bool = True


class ProfileManager:
    """Registry and manager for validation scoring profiles."""

    def __init__(self):
        self.profiles: Dict[str, ScoringProfile] = {}
        self._register_default_profiles()

    def _register_default_profiles(self) -> None:
        # 1. Standard DAX Baseline Profile
        self.register_profile(ScoringProfile(
            name="DEFAULT",
            description="Baseline standard DAX stability scoring profile",
            weights={"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
            thresholds={"accept": 0.75, "recurse_floor": 0.55, "floor_F": 0.50, "floor_T": 0.60}
        ))

        # 2. High-Assurance Aeronautics Profile
        self.register_profile(ScoringProfile(
            name="HIGH_ASSURANCE_AERONAUTICS",
            description="Mission-critical aeronautics with high simulation & falsification requirements",
            weights={"wL": 0.20, "wA": 0.10, "wP": 0.35, "wF": 0.25, "wT": 0.10},
            thresholds={"accept": 0.85, "recurse_floor": 0.65, "floor_F": 0.60, "floor_T": 0.70},
            anti_gaming_alpha=0.10
        ))

        # 3. Financial Settlement & Ledger Profile
        self.register_profile(ScoringProfile(
            name="FINANCIAL_SETTLEMENT",
            description="Traceability and logical consistency focused governance profile",
            weights={"wL": 0.35, "wA": 0.15, "wP": 0.10, "wF": 0.15, "wT": 0.25},
            thresholds={"accept": 0.80, "recurse_floor": 0.60, "floor_F": 0.50, "floor_T": 0.75}
        ))

        # 4. Frontier AI Containment Profile
        self.register_profile(ScoringProfile(
            name="FRONTIER_AI_CONTAINMENT",
            description="Adversarial red-teaming profile with strict falsification floors",
            weights={"wL": 0.20, "wA": 0.15, "wP": 0.20, "wF": 0.30, "wT": 0.15},
            thresholds={"accept": 0.80, "recurse_floor": 0.60, "floor_F": 0.65, "floor_T": 0.70},
            anti_gaming_alpha=0.15
        ))

        # 5. Latency-Optimized High-Throughput Profile
        self.register_profile(ScoringProfile(
            name="LATENCY_OPTIMIZED",
            description="Lightweight scoring profile for microsecond validation workloads",
            weights={"wL": 0.30, "wA": 0.25, "wP": 0.15, "wF": 0.15, "wT": 0.15},
            thresholds={"accept": 0.70, "recurse_floor": 0.50, "floor_F": 0.40, "floor_T": 0.50},
            strict_floor_enforcement=False
        ))

    def register_profile(self, profile: ScoringProfile) -> None:
        """Registers a custom scoring profile."""
        self.profiles[profile.name.upper()] = profile

    def get_profile(self, name: str) -> ScoringProfile:
        """Retrieves a scoring profile by name with fallback to DEFAULT."""
        key = name.upper()
        if key in self.profiles:
            return self.profiles[key]
        return self.profiles["DEFAULT"]

    def list_profiles(self) -> Dict[str, str]:
        """Lists all registered profile names and descriptions."""
        return {p.name: p.description for p in self.profiles.values()}
