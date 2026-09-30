"""
DAXDA MMPIBench: Normative Reference Data & T-Score Engine
Provides empirical means, standard deviations, and normative transformations.
"""

from __future__ import annotations
import math
import json
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from daxda_engine.mmpibench.mmpi.scales import ALL_SCALES, MMPIScale


@dataclass(frozen=True)
class ScaleNorm:
    scale_id: str
    mean: float = 50.0
    std: float = 10.0
    min_raw: float = 0.0
    max_raw: float = 100.0


class NormReferences:
    """
    Maintains normative baseline distributions for all 567 MMPI scales.
    Implements standard linear T-score conversion: T = 50 + 10 * (X - mean) / std.
    """

    def __init__(self, custom_norms_path: Optional[str] = None):
        self._norms: Dict[str, ScaleNorm] = {}
        if custom_norms_path and os.path.exists(custom_norms_path):
            self._load_from_json(custom_norms_path)
        else:
            self._generate_default_norms()

    def _generate_default_norms(self) -> None:
        """Populate default standard normative tables for all scales."""
        for sid, scale in ALL_SCALES.items():
            self._norms[sid] = ScaleNorm(
                scale_id=sid,
                mean=scale.default_mean,
                std=scale.default_std,
            )

    def _load_from_json(self, path: str) -> None:
        with open(path, "r") as f:
            data = json.load(f)
        for sid, item in data.items():
            self._norms[sid] = ScaleNorm(
                scale_id=sid,
                mean=float(item.get("mean", 50.0)),
                std=float(item.get("std", 10.0)),
                min_raw=float(item.get("min_raw", 0.0)),
                max_raw=float(item.get("max_raw", 100.0)),
            )

    def get_norm(self, scale_id: str) -> ScaleNorm:
        return self._norms.get(scale_id, ScaleNorm(scale_id=scale_id))

    def compute_t_score(self, scale_id: str, raw_score: float) -> float:
        """
        Convert raw evaluation score to standardized T-score (Mean=50, SD=10).
        Clamped to [20.0, 120.0].
        """
        norm = self.get_norm(scale_id)
        std = norm.std if norm.std > 1e-4 else 10.0
        t = 50.0 + 10.0 * ((raw_score - norm.mean) / std)
        return max(20.0, min(120.0, round(t, 2)))

    def export_norms_json(self, path: str) -> None:
        data = {
            sid: {"mean": n.mean, "std": n.std, "min_raw": n.min_raw, "max_raw": n.max_raw}
            for sid, n in self._norms.items()
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


# Global default norms instance
DEFAULT_NORMS = NormReferences()
