r"""
Tests for Multimodal Adversarial Generation and Containment Engine.
Verifies PGD L_\infty perturbation bounds, reconstruction loss metrics,
and fail-closed defensive containment gates.
"""

import numpy as np
import pytest

from daxda_engine.level3.multimodal_adversarial import (
    AdversarialPerturbationResult,
    MultimodalPGDAttacker,
    GateEvaluationReport,
    FailClosedContainmentGate,
    AdversarialBreachContainmentGateTrigger,
)


def test_pgd_adversarial_perturbation_bound():
    r"""Verify PGD generates perturbations strictly bounded within L_\infty epsilon."""
    attacker = MultimodalPGDAttacker(epsilon_bound=0.031, step_size_alpha=0.005, num_iterations=8)
    clean_embedding = np.random.default_rng(42).normal(0.0, 1.0, size=(1, 512))

    res: AdversarialPerturbationResult = attacker.generate_adversarial_sample(clean_embedding)

    assert res.linf_norm <= 0.031 + 1e-6
    assert res.is_adversarial_successful is True
    assert res.iterations_run == 8
    assert res.original_input.shape == res.perturbed_input.shape


def test_multimodal_tensor_dimensions():
    r"""Verify PGD applies across image, audio spectrogram, and token embedding dimensions."""
    attacker = MultimodalPGDAttacker(epsilon_bound=0.05)

    # 1. Vision-language embedding: (256, 768)
    vlm_tensor = np.ones((256, 768), dtype=np.float64)
    res_vlm = attacker.generate_adversarial_sample(vlm_tensor)
    assert res_vlm.perturbed_input.shape == (256, 768)
    assert res_vlm.linf_norm <= 0.05 + 1e-6

    # 2. Audio Mel-spectrogram: (80, 128)
    audio_tensor = np.zeros((80, 128), dtype=np.float64)
    res_audio = attacker.generate_adversarial_sample(audio_tensor)
    assert res_audio.perturbed_input.shape == (80, 128)
    assert res_audio.linf_norm <= 0.05 + 1e-6


def test_fail_closed_containment_gate_clean_pass():
    r"""Verify clean, unperturbed multimodal tensors pass containment evaluation."""
    gate = FailClosedContainmentGate(reconstruction_loss_threshold=0.80)
    clean = np.random.default_rng(10).normal(0.0, 1.0, 256)
    slightly_noisy = clean + np.random.default_rng(20).normal(0.0, 0.01, 256)

    report: GateEvaluationReport = gate.evaluate_tensor(clean, slightly_noisy)

    assert report.is_safe is True
    assert report.containment_gate_triggered is False
    assert report.cosine_similarity > 0.95
    assert report.reconstruction_loss < 0.80


def test_fail_closed_containment_gate_triggers_on_large_perturbation():
    r"""Verify containment gate trips when reconstruction loss epsilon > 0.80."""
    gate = FailClosedContainmentGate(reconstruction_loss_threshold=0.80, min_cosine_similarity=0.70)
    clean = np.ones(100, dtype=np.float64)

    # Corrupted adversarial tensor with large displacement
    adversarial = clean + np.full(100, 1.5, dtype=np.float64)  # recon loss = 1.5 > 0.80

    report = gate.evaluate_tensor(clean, adversarial, raise_on_breach=False)

    assert report.is_safe is False
    assert report.containment_gate_triggered is True
    assert report.reconstruction_loss > 0.80

    # With raise_on_breach=True
    with pytest.raises(AdversarialBreachContainmentGateTrigger):
        gate.evaluate_tensor(clean, adversarial, raise_on_breach=True)
