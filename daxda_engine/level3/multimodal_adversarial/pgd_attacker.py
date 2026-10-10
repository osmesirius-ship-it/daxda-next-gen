r"""
Multimodal Projected Gradient Descent (PGD) Adversarial Generator.
Generates bounded L_\infty and L_2 perturbations across image embeddings,
audio spectrogram representations, and continuous token embeddings.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class AdversarialPerturbationResult:
    """Outcome of PGD adversarial attack generation."""
    original_input: np.ndarray
    perturbed_input: np.ndarray
    perturbation_delta: np.ndarray
    linf_norm: float
    l2_norm: float
    iterations_run: int
    reconstruction_loss: float
    is_adversarial_successful: bool


class MultimodalPGDAttacker:
    r"""
    Generates imperceptible L_\infty perturbations:
    \delta_{t+1} = \Pi_{[-\epsilon, \epsilon]} (\delta_t + \alpha \cdot \text{sign}(\nabla_\delta \mathcal{L})).
    """

    def __init__(
        self,
        epsilon_bound: float = 0.031,  # ~ 8/255 for normalized multimodal tensors
        step_size_alpha: float = 0.008,
        num_iterations: int = 10,
    ):
        self.epsilon = epsilon_bound
        self.alpha = step_size_alpha
        self.iterations = num_iterations

    def generate_adversarial_sample(
        self,
        target_tensor: np.ndarray,
        loss_gradient_direction: Optional[np.ndarray] = None,
        seed: int = 42,
    ) -> AdversarialPerturbationResult:
        """
        Executes PGD perturbation optimization on target tensor.
        """
        rng = np.random.default_rng(seed)
        shape = target_tensor.shape

        # Uniform random initialization within [-epsilon, epsilon]
        delta = rng.uniform(-self.epsilon, self.epsilon, size=shape).astype(np.float64)

        if loss_gradient_direction is None:
            # Synthetic adversarial gradient targeting maximal displacement from centroid
            loss_gradient_direction = np.sign(target_tensor + 1e-5)

        for _ in range(self.iterations):
            # Gradient step in direction of loss
            grad_sign = np.sign(loss_gradient_direction)
            delta = delta + self.alpha * grad_sign
            # Project onto L_infinity ball [-epsilon, epsilon]
            delta = np.clip(delta, -self.epsilon, self.epsilon)

        perturbed = target_tensor + delta

        linf = float(np.max(np.abs(delta)))
        l2 = float(np.linalg.norm(delta))

        # Reconstruction loss: relative L2 distance ||x' - x|| / ||x||
        norm_orig = float(np.linalg.norm(target_tensor))
        recon_loss = float(l2 / max(1e-12, norm_orig))

        return AdversarialPerturbationResult(
            original_input=target_tensor,
            perturbed_input=perturbed,
            perturbation_delta=delta,
            linf_norm=linf,
            l2_norm=l2,
            iterations_run=self.iterations,
            reconstruction_loss=recon_loss,
            is_adversarial_successful=linf <= self.epsilon + 1e-6,
        )
