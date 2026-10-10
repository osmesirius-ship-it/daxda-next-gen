r"""
Fail-Closed Containment Gate and Defense Evaluator.
Monitors multimodal tensor embeddings, evaluates reconstruction loss,
and trips fail-closed containment gates under high perturbation (\epsilon > 0.80).
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


class AdversarialBreachContainmentGateTrigger(Exception):
    """Raised when adversarial reconstruction loss breaches fail-closed containment safety thresholds."""
    pass


@dataclass(frozen=True)
class GateEvaluationReport:
    """Security evaluation audit report for an incoming multimodal tensor."""
    cosine_similarity: float
    reconstruction_loss: float
    linf_displacement: float
    is_safe: bool
    containment_gate_triggered: bool
    reconstruction_loss_threshold: float


class FailClosedContainmentGate:
    r"""
    Enforces fail-closed defensive containment gates:
    If reconstruction loss \epsilon > 0.80 or cosine similarity drops below threshold,
    the gate immediately locks down the inference pipeline.
    """

    def __init__(
        self,
        reconstruction_loss_threshold: float = 0.80,
        min_cosine_similarity: float = 0.70,
    ):
        self.loss_threshold = reconstruction_loss_threshold
        self.min_cosine = min_cosine_similarity

    def evaluate_tensor(
        self,
        clean_reference: np.ndarray,
        suspect_tensor: np.ndarray,
        raise_on_breach: bool = False,
    ) -> GateEvaluationReport:
        """
        Evaluates suspect tensor against clean baseline.
        """
        v_clean = clean_reference.flatten()
        v_suspect = suspect_tensor.flatten()

        norm_c = float(np.linalg.norm(v_clean))
        norm_s = float(np.linalg.norm(v_suspect))

        # Cosine similarity
        if norm_c > 1e-12 and norm_s > 1e-12:
            cos_sim = float(np.dot(v_clean, v_suspect) / (norm_c * norm_s))
        else:
            cos_sim = 1.0

        diff = v_suspect - v_clean
        norm_diff = float(np.linalg.norm(diff))
        recon_loss = float(norm_diff / max(1e-12, norm_c))
        linf = float(np.max(np.abs(diff)))

        # Breach condition: reconstruction loss > threshold OR cosine similarity < min_cosine
        is_breach = bool(recon_loss > self.loss_threshold or cos_sim < self.min_cosine)

        report = GateEvaluationReport(
            cosine_similarity=cos_sim,
            reconstruction_loss=recon_loss,
            linf_displacement=linf,
            is_safe=not is_breach,
            containment_gate_triggered=is_breach,
            reconstruction_loss_threshold=self.loss_threshold,
        )

        if is_breach and raise_on_breach:
            raise AdversarialBreachContainmentGateTrigger(
                f"Fail-closed containment gate triggered! Recon loss {recon_loss:.4f} > "
                f"threshold {self.loss_threshold} or cos_sim {cos_sim:.4f} < {self.min_cosine}"
            )

        return report
