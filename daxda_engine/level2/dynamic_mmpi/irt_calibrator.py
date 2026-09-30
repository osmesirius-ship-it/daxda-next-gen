"""
DAXDA Level 2 - Item Response Theory (IRT) Calibrator
=====================================================

Calibrates psychometric items using the 3-Parameter Logistic (3PL) model:
  P(theta) = gamma + (1 - gamma) / (1 + exp(-alpha * (theta - beta)))
where:
  alpha : Item discrimination parameter
  beta  : Item difficulty parameter
  gamma : Pseudo-guessing parameter
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class IRTItemParameters:
    item_id: str
    alpha: float = 1.0  # Discrimination
    beta: float = 0.0   # Difficulty
    gamma: float = 0.0  # Pseudo-guessing

    def probability(self, theta: float) -> float:
        """Computes probability of keyed response given latent alignment trait theta."""
        exponent = -self.alpha * (theta - self.beta)
        # Avoid overflow
        exponent = max(-30.0, min(30.0, exponent))
        logistic = 1.0 / (1.0 + math.exp(exponent))
        return self.gamma + (1.0 - self.gamma) * logistic


class IRTCalibrator:
    """Calibrates and estimates latent ability/alignment traits theta from responses."""

    def __init__(self):
        self._item_params: Dict[str, IRTItemParameters] = {}

    def register_item(self, item_id: str, alpha: float = 1.0, beta: float = 0.0, gamma: float = 0.0) -> None:
        self._item_params[item_id] = IRTItemParameters(item_id=item_id, alpha=alpha, beta=beta, gamma=gamma)

    def estimate_theta(self, responses: Dict[str, bool]) -> float:
        """
        Estimates latent alignment trait theta in [-3.0, 3.0] from a response set.
        """
        if not responses:
            return 0.0
        # Simple MLE / weighted score approximation
        score = sum(1.0 if v else 0.0 for v in responses.values())
        total = len(responses)
        ratio = score / total
        # Logit transformation
        ratio = max(0.01, min(0.99, ratio))
        theta = math.log(ratio / (1.0 - ratio))
        return max(-3.0, min(3.0, theta))
