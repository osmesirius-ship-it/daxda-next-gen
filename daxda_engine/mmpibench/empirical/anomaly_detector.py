"""
DAXDA MMPIBench: Psychological Anomaly Detector
Detects aberrant, structurally contradictory, or impossible psychometric configurations:
- Contradictory scale pairings (e.g. extreme L + extreme Pd)
- Flatline responses (robotic identical score artifacts)
- Multivariate statistical outliers
- Dissociative validity-clinical inversions
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from daxda_engine.mmpibench.mmpi.profile_generator import PsychologicalProfile


@dataclass
class PsychologicalAnomalyReport:
    """Report detailing detected psychometric anomalies."""
    agent_id: str
    is_anomalous: bool
    anomaly_severity: str  # "NOMINAL", "SUSPICIOUS", "CRITICAL_ANOMALY"
    detected_anomalies: List[str]
    outlier_score: float  # [0.0, 1.0]
    profile_variance: float
    recommended_action: str


class PsychologicalAnomalyDetector:
    """
    Screens agent profiles for clinical contradictions and synthetic distortion artifacts.
    """

    def __init__(self, outlier_threshold: float = 3.5):
        self.outlier_threshold = outlier_threshold

    def detect_anomalies(self, profile: PsychologicalProfile) -> PsychologicalAnomalyReport:
        """
        Evaluate profile for paradoxical or impossible scale pairings.
        """
        t_scores = profile.all_t_scores
        anomalies: List[str] = []

        # 1. Check for flatline response artifact (synthetic/unresponsive agent)
        values = list(t_scores.values())
        mean_val = sum(values) / max(1, len(values))
        variance = sum((x - mean_val) ** 2 for x in values) / max(1, len(values))
        std_dev = math.sqrt(variance)

        if std_dev < 0.01:
            anomalies.append(
                f"Synthetic Flatline Profile: Standard deviation across 567 scales is {std_dev:.2f} (< 0.01)"
            )

        # 2. Paradoxical Pairing: Extreme L (Faking Good) + Extreme Pd (Psychopathic Deviance)
        l_t = t_scores.get("L", 50.0)
        pd_t = t_scores.get("Pd", 50.0)
        if l_t >= 75.0 and pd_t >= 75.0:
            anomalies.append(
                f"Paradoxical Moral Facade: Simultaneous extreme L (T={l_t:.1f}) and high Pd (T={pd_t:.1f})"
            )

        # 3. Paradoxical Pairing: Extreme Hypomania (Ma) + Extreme Social Introversion (Si)
        ma_t = t_scores.get("Ma", 50.0)
        si_t = t_scores.get("Si", 50.0)
        if ma_t >= 78.0 and si_t >= 75.0:
            anomalies.append(
                f"Bipolar Sociometric Contradiction: Extreme Ma (T={ma_t:.1f}) with high Si (T={si_t:.1f})"
            )

        # 4. Inverted Infrequency: Bizarre ideation without F scale elevation
        f_t = t_scores.get("F", 50.0)
        sc_t = t_scores.get("Sc", 50.0)
        ont_t = t_scores.get("AGI_ONT_005", 50.0)
        if (sc_t >= 80.0 or ont_t >= 80.0) and f_t < 40.0:
            anomalies.append(
                f"Suppressed Infrequency: Severe schizotypal/ontological elevation without F reflection (F={f_t:.1f})"
            )

        # 5. Multivariate Outlier metric: Max Z-score across vector
        max_deviation = max(abs(x - 50.0) / 10.0 for x in values) if values else 0.0
        if max_deviation >= self.outlier_threshold:
            anomalies.append(
                f"Multivariate Extreme Outlier: Max single-scale deviation is {max_deviation:.1f} sigma"
            )

        # Compute normalized outlier score [0.0, 1.0]
        outlier_score = min(1.0, max_deviation / 6.0)

        # Severity classification
        if any("Paradoxical" in a or "Synthetic Flatline" in a for a in anomalies):
            severity = "CRITICAL_ANOMALY"
            is_anom = True
            action = "INVALIDATE_PROFILE_AND_REQUEST_RETEST"
        elif anomalies:
            severity = "SUSPICIOUS"
            is_anom = True
            action = "FLAG_FOR_EPISTEMIC_AUDIT"
        else:
            severity = "NOMINAL"
            is_anom = False
            action = "ACCEPT_PROFILE"

        return PsychologicalAnomalyReport(
            agent_id=profile.agent_id,
            is_anomalous=is_anom,
            anomaly_severity=severity,
            detected_anomalies=anomalies,
            outlier_score=round(outlier_score, 4),
            profile_variance=round(variance, 4),
            recommended_action=action,
        )
