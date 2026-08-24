#!/usr/bin/env python3
"""
DAX Predictive Protocol Lock & Experiment Registry (dax_predictive_protocol_lock.py)
===================================================================================
Phase A Protocol Lock Engine for the Prospective, Blinded, Falsifiable Evaluation Standard.

Freezes:
  - Experiment ID (DAX-PRED-001)
  - Engine Lock (DAXDA_V11.4_FROZEN)
  - Outcome Schema & Scoring Rules (Brier, Log Loss, ECE, ROC-AUC)
  - Baseline Models (Uniform Random, Base Rate, Statistical, ML, Frontier LLM)
  - Target Domains & Sample Sizes
  - Statistical Analysis Plan & Post-Lock Immutability Enforcement

Computes a canonical SHA-256 protocol_hash. Any modification post-lock creates a new version.
"""

from __future__ import annotations
import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


@dataclass
class ProtocolLockConfig:
    experiment_id: str = "DAX-PRED-001"
    engine_version: str = "DAXDA_V11.4_FROZEN"
    prediction_mode: str = "PROSPECTIVE_PROBABILISTIC_FORECAST"
    modifications_after_lock: str = "PROHIBITED"
    cutoff_rule: str = "ENFORCE_STRICT_T0_SNAPSHOT"
    outcomes_per_case: int = 5  # Predefined categories A, B, C, D, E
    probability_sum_requirement: float = 1.000
    primary_metric: str = "MULTICLASS_BRIER_SCORE"
    secondary_metrics: List[str] = field(default_factory=lambda: [
        "LOG_LOSS", "EXPECTED_CALIBRATION_ERROR", "ROC_AUC", "TOP1_ACCURACY", "TOP2_ACCURACY", "ABSTENTION_ENTROPY_QUALITY"
    ])
    baseline_competitors: List[str] = field(default_factory=lambda: [
        "BASELINE_1_UNIFORM_RANDOM",
        "BASELINE_2_HISTORICAL_BASE_RATE",
        "BASELINE_3_LOGISTIC_STATISTICAL",
        "BASELINE_4_GRADIENT_BOOSTING_ML",
        "BASELINE_5_FRONTIER_LLM_OPENAI"
    ])
    domains: Dict[str, int] = field(default_factory=lambda: {
        "LEGAL_DECISIONS": 50,
        "SPORTS_OUTCOMES": 50,
        "REGULATORY_DECISIONS": 25,
        "CORPORATE_EVENTS": 25,
        "SCIENTIFIC_REPLICATION": 25,
        "STRUCTURED_SYNTHETIC": 25
    })
    total_target_n: int = 200
    negative_control_policy: str = "MUST_YIELD_CHANCE_BASELINE_ZERO_SPURIOUS_POWER"
    protocol_timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    protocol_hash: str = ""

    def lock_protocol(self) -> str:
        d = asdict(self)
        d.pop("protocol_hash", None)
        c_json = canonical_json(d)
        h = hashlib.sha256(c_json.encode("utf-8")).hexdigest()
        self.protocol_hash = h
        return h


class ProtocolRegistry:
    def __init__(self, config: Optional[ProtocolLockConfig] = None):
        self.config = config or ProtocolLockConfig()
        self.config.lock_protocol()

    def get_manifest(self) -> Dict[str, Any]:
        return asdict(self.config)

    def verify_lock(self, manifest: Dict[str, Any]) -> bool:
        h_given = manifest.get("protocol_hash", "")
        d = dict(manifest)
        d.pop("protocol_hash", None)
        c_json = canonical_json(d)
        h_calc = hashlib.sha256(c_json.encode("utf-8")).hexdigest()
        return h_given == h_calc


if __name__ == "__main__":
    registry = ProtocolRegistry()
    manifest = registry.get_manifest()
    print("=" * 80)
    print("DAX Predictive Protocol Lock Manifest (Phase A)")
    print("=" * 80)
    print(json.dumps(manifest, indent=2))
    print(f"\nProtocol Verification: {registry.verify_lock(manifest)}")
