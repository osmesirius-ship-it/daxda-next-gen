# -*- coding: utf-8 -*-
"""
Unit tests for the Cl164EngineAdapter (the bridge to the real Cl(16,4) engine).
These tests verify that the adapter returns a *stable* score (0.2) when the
input vector can be mapped to a valid Cl(16,4) configuration and an *unstable*
score (0.8) otherwise.
"""

import sys
import os
from pathlib import Path

# Ensure the repository root is on the import path so that the script module can be imported.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT))

# Import the adapter from the discovery script.
from tools.run_ms_cl16_4_discovery import Cl164EngineAdapter


def test_adapter_returns_stable_for_valid_vector():
    """A 16‑dimensional vector with distinct high values should map to a config and
    yield the low‑stability score (0.2)."""
    vector = [0.9, 0.8, 0.85, 0.95] + [0.1] * 12
    engine = Cl164EngineAdapter()
    score = engine.check_stability(vector)
    assert score == 0.2, "Expected stable (low) score for a mappable vector"


def test_adapter_returns_unstable_for_invalid_vector():
    """A vector that does not contain 16 elements cannot be mapped, causing the
    adapter to return the high‑stability score (0.8)."""
    vector = [0.5] * 8
    engine = Cl164EngineAdapter()
    score = engine.check_stability(vector)
    assert score == 0.8, "Expected unstable (high) score for an unmappable vector"
