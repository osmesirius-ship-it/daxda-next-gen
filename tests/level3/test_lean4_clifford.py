"""
Unit tests for Lean 4 Clifford Formal Theorem Prover Harness.
"""

import pytest
from daxda_engine.level3.lean4_clifford import Lean4ProverAgent, FormalProofReceipt


def test_lean4_theorems_inspection():
    """Verify theorem names are parsed from Lean 4 source."""
    agent = Lean4ProverAgent()
    theorems = agent.inspect_theorems()

    assert len(theorems) >= 4
    assert "reverse_involution" in theorems
    assert "clifford_rev_mul" in theorems
    assert "jacobi_identity" in theorems
    assert "agent_containment_guarantee" in theorems


def test_lean4_theorem_verification():
    """Verify all Lean 4 formal theorems pass type-checking with zero 'sorry' axioms."""
    agent = Lean4ProverAgent()
    receipts = agent.verify_all_theorems()

    for name, receipt in receipts.items():
        assert isinstance(receipt, FormalProofReceipt)
        assert receipt.verified is True, f"Theorem {name} failed formal verification"
        assert len(receipt.proof_kernel_hash) == 64  # Valid SHA-256
        assert receipt.divergence_score == 0.0
