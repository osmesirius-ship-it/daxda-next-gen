"""
Unit tests for Fault-Tolerant Quantum Error-Corrected Clifford Gates.
"""

import pytest
from daxda_engine.level3.quantum_error_correction import (
    MagicStateDistillation,
    PauliOperator,
    SteaneCode,
    SurfaceCode,
    SyndromeDecoder,
    TransversalCliffordCompiler,
)


def test_pauli_symplectic_commutation():
    """Verify symplectic inner product correctly evaluates Pauli commutation."""
    X = PauliOperator.from_string("X")
    Z = PauliOperator.from_string("Z")
    Y = PauliOperator.from_string("Y")
    I = PauliOperator.from_string("I")

    assert not X.commutes_with(Z)
    assert not X.commutes_with(Y)
    assert not Y.commutes_with(Z)
    assert X.commutes_with(I)
    assert X.commutes_with(X)


def test_steane_code_stabilizers_abelian():
    """Verify all 6 Steane code stabilizer generators pairwise commute."""
    code = SteaneCode.get_code()
    assert code.verify_abelian() is True
    assert code.verify_logical_commutation() is True


def test_surface_code_abelian():
    """Verify surface code distance 3 stabilizers commute."""
    code = SurfaceCode.get_code(distance=3)
    assert code.verify_abelian() is True


def test_transversal_clifford_compilation():
    """Verify transversal gates compiled on Steane code."""
    code = SteaneCode.get_code()
    h_gate = TransversalCliffordCompiler.apply_transversal_hadamard(code)
    s_gate = TransversalCliffordCompiler.apply_transversal_phase(code)
    cnot_gate = TransversalCliffordCompiler.apply_transversal_cnot(code, code)

    assert h_gate["transversal"] is True
    assert s_gate["transversal"] is True
    assert cnot_gate["transversal"] is True


def test_syndrome_extraction_and_correction():
    """Verify syndrome extraction and error correction on all single-qubit errors in Steane code."""
    code = SteaneCode.get_code()

    # Test single-qubit X error on qubit 2
    err_x2 = PauliOperator.from_string("IIXIIII")
    corr, success = SyndromeDecoder.correct_error(code, err_x2)
    assert success is True
    assert corr.to_string() == "IIXIIII"

    # Test single-qubit Z error on qubit 5
    err_z5 = PauliOperator.from_string("IIIIIZI")
    corr_z, success_z = SyndromeDecoder.correct_error(code, err_z5)
    assert success_z is True
    assert corr_z.to_string() == "IIIIIZI"


def test_magic_state_distillation():
    """Verify 15-to-1 magic state distillation cubic suppression below threshold."""
    res = MagicStateDistillation.distill_magic_state(input_error_rate=0.01)

    assert res["is_subthreshold"] is True
    # 35 * 0.01^3 = 3.5e-5
    assert abs(res["output_error_rate"] - 3.5e-5) < 1e-6
    assert res["suppression_factor"] > 200.0
    assert res["logical_fidelity"] > 0.9999
