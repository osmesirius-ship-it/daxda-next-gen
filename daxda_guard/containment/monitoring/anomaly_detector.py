"""
ML & Statistical Anomaly Detector
=================================

Evaluates agent actions, telemetry vectors, and entropy distribution to detect anomalous AGI behaviors.
"""

import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AnomalyScore:
    """Anomaly score result."""
    score: float  # [0.0, 1.0] where 1.0 is highest anomaly
    is_anomalous: bool
    threshold: float
    factors: Dict[str, float]


class AnomalyDetector:
    """Statistical and heuristic anomaly detector for agent decision streams."""

    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold
        self.baseline_mean = 0.25
        self.baseline_std = 0.15

    def score_vector(self, vector: List[float]) -> AnomalyScore:
        """Scores continuous 16D decision vector against baseline distribution."""
        if not vector or len(vector) == 0:
            return AnomalyScore(score=0.0, is_anomalous=False, threshold=self.threshold, factors={})

        mean_val = sum(vector) / len(vector)
        max_val = max(vector)
        variance = sum((x - mean_val) ** 2 for x in vector) / len(vector)
        std_dev = math.sqrt(variance)

        # High variance + high max values indicates focused exploitation
        z_score = abs(mean_val - self.baseline_mean) / (self.baseline_std + 1e-6)
        normalized_z = min(1.0, z_score / 4.0)

        entropy_factor = min(1.0, max_val * 0.7 + std_dev * 0.3)
        combined_score = min(1.0, normalized_z * 0.4 + entropy_factor * 0.6)

        return AnomalyScore(
            score=combined_score,
            is_anomalous=combined_score >= self.threshold,
            threshold=self.threshold,
            factors={
                "mean": mean_val,
                "max": max_val,
                "std_dev": std_dev,
                "z_score": z_score
            }
        )

    def score_payload(self, text_payload: str) -> AnomalyScore:
        """Scores text payload based on character entropy and suspicious density."""
        if not text_payload:
            return AnomalyScore(score=0.0, is_anomalous=False, threshold=self.threshold, factors={})

        # Calculate Shannon entropy
        prob_dict = {}
        for c in text_payload:
            prob_dict[c] = prob_dict.get(c, 0) + 1
        length = len(text_payload)
        entropy = -sum((count / length) * math.log2(count / length) for count in prob_dict.values())

        # High entropy (obfuscated/encrypted) or special char density
        special_chars = sum(1 for c in text_payload if not c.isalnum() and not c.isspace())
        special_density = special_chars / length if length > 0 else 0.0

        anomaly_score = min(1.0, (entropy / 8.0) * 0.5 + special_density * 0.5)

        return AnomalyScore(
            score=anomaly_score,
            is_anomalous=anomaly_score >= self.threshold,
            threshold=self.threshold,
            factors={
                "entropy": entropy,
                "special_density": special_density,
                "length": float(length)
            }
        )
