"""
Unit tests for Cl(64,16) Hypercombinatorial Multivector Engine.
"""

import math
import pytest
from daxda_engine.level3.cl64_16 import Cl64_16Multivector, SpinorManifoldDetector


def test_basis_vector_metric_signature():
    """Verify that e_i^2 = +1 for i in 1..64 and e_j^2 = -1 for j in 65..80."""
    # Positive signature check
    e1 = Cl64_16Multivector.basis_vector(1)
    e64 = Cl64_16Multivector.basis_vector(64)
    assert (e1 * e1).scalar_part() == 1.0
    assert (e64 * e64).scalar_part() == 1.0

    # Negative signature check
    e65 = Cl64_16Multivector.basis_vector(65)
    e80 = Cl64_16Multivector.basis_vector(80)
    assert (e65 * e65).scalar_part() == -1.0
    assert (e80 * e80).scalar_part() == -1.0


def test_generator_anticommutation():
    """Verify e_i e_j = -e_j e_i for distinct generators."""
    e1 = Cl64_16Multivector.basis_vector(1)
    e2 = Cl64_16Multivector.basis_vector(2)
    anti_comm = e1.anti_commutator(e2)
    assert anti_comm.is_zero()

    prod1 = e1 * e2
    prod2 = e2 * e1
    diff = prod1 + prod2
    assert diff.is_zero()


def test_associativity():
    """Verify (A * B) * C == A * (B * C)."""
    e1 = Cl64_16Multivector.basis_vector(3)
    e2 = Cl64_16Multivector.basis_vector(15)
    e3 = Cl64_16Multivector.basis_vector(70)

    A = e1 * 2.0 + e2 * 1.5
    B = e2 * 0.5 - e3 * 3.0
    C = e1 * 1.0 + e3 * 2.0

    left = (A * B) * C
    right = A * (B * C)

    residual = (left - right).norm()
    assert residual < 1e-12, f"Associativity failed: residual={residual}"


def test_reversion_anti_automorphism():
    """Verify (A * B).reverse() == B.reverse() * A.reverse()."""
    e1 = Cl64_16Multivector.basis_vector(10)
    e2 = Cl64_16Multivector.basis_vector(25)
    e3 = Cl64_16Multivector.basis_vector(68)

    A = e1 * 1.2 + e2 * 0.8
    B = e2 * 2.5 + e3 * 1.1

    left = (A * B).reverse()
    right = B.reverse() * A.reverse()

    residual = (left - right).norm()
    assert residual < 1e-12, f"Reversion anti-automorphism failed: residual={residual}"


def test_jacobi_identity():
    """Verify [[A, B], C] + [[B, C], A] + [[C, A], B] == 0."""
    e1 = Cl64_16Multivector.basis_vector(5)
    e2 = Cl64_16Multivector.basis_vector(12)
    e3 = Cl64_16Multivector.basis_vector(66)

    A = e1 * 1.5 + e2
    B = e2 * 0.7 - e3
    C = e1 + e3 * 2.0

    t1 = (A.commutator(B)).commutator(C)
    t2 = (B.commutator(C)).commutator(A)
    t3 = (C.commutator(A)).commutator(B)

    sum_jacobi = t1 + t2 + t3
    assert sum_jacobi.norm() < 1e-12, f"Jacobi identity failed: norm={sum_jacobi.norm()}"


def test_versor_inverse():
    """Verify A * A^{-1} == 1 for versors."""
    e1 = Cl64_16Multivector.basis_vector(2)
    e2 = Cl64_16Multivector.basis_vector(4)
    rotor = Cl64_16Multivector.scalar(math.cos(0.3)) + (e1 * e2) * math.sin(0.3)

    inv = rotor.inverse()
    identity = rotor * inv
    assert abs(identity.scalar_part() - 1.0) < 1e-12
    assert (identity - Cl64_16Multivector.scalar(1.0)).norm() < 1e-12


def test_triality_closure():
    """Verify Spin(64,16) rotor conservation."""
    e1 = Cl64_16Multivector.basis_vector(1)
    e2 = Cl64_16Multivector.basis_vector(2)
    bivector = e1 * e2

    res = SpinorManifoldDetector.verify_triality_closure(e1, e2, bivector, theta=0.25)
    assert res["metric_conservation_error"] < 1e-4
    assert res["spinor_drift"] < 1e-4


def test_left_contraction_axiom():
    r"""Verify left contraction axiom: A _| B vanishes whenever grade(A) > grade(B)."""
    e1 = Cl64_16Multivector.basis_vector(1)
    e2 = Cl64_16Multivector.basis_vector(2)
    bivector = e1 * e2

    # 1. grade 1 _| grade 2 -> grade 1 (e1 _| (e1 e2) = e2)
    lc_1_2 = e1.left_contraction(bivector)
    assert (lc_1_2 - e2).norm() < 1e-12

    # 2. grade 2 _| grade 1 -> MUST BE ZERO (grade 2 > grade 1)
    lc_2_1 = bivector.left_contraction(e1)
    assert lc_2_1.is_zero()

    # 3. grade 1 _| grade 1 -> scalar (e1 _| e1 = 1)
    lc_1_1 = e1.left_contraction(e1)
    assert abs(lc_1_1.scalar_part() - 1.0) < 1e-12


def test_non_versor_inverse_raises_value_error():
    r"""Verify that multivector with non-scalar A ~A raises ValueError in inverse()."""
    e1 = Cl64_16Multivector.basis_vector(1)
    e2 = Cl64_16Multivector.basis_vector(2)
    e3 = Cl64_16Multivector.basis_vector(3)
    e4 = Cl64_16Multivector.basis_vector(4)

    # Sum of scalars and distinct-grade elements whose A ~A has non-scalar bivectors
    non_versor = Cl64_16Multivector.scalar(1.0) + e1 + e2 + (e1 * e2 * e3) + (e2 * e3 * e4)

    with pytest.raises(ValueError, match="not a versor"):
        non_versor.inverse()

