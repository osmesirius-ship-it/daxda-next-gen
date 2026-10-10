"""
Tests for DAXDA Level 4 — Domain 1: Cl(128,32) Multivector Algebra & Anyonic Braid Compiler
"""

import numpy as np
import pytest

from daxda_engine.level4.cl128_32 import (
    Cl128_32Multivector,
    AnyonicBraidCompiler,
)


def test_cl128_32_multivector_basis_blades():
    # Construct basis blades e_1 (positive), e_129 (negative)
    e1 = Cl128_32Multivector.generator(1)
    e129 = Cl128_32Multivector.generator(129)
    
    assert len(e1.terms) == 1
    assert len(e129.terms) == 1
    assert e1.norm() == pytest.approx(1.0)
    assert e129.norm() == pytest.approx(1.0)


def test_cl128_32_geometric_product_signature():
    # Positive generator squares to +1
    e1 = Cl128_32Multivector.generator(1)
    e1_sq = e1 * e1
    assert 0 in e1_sq.terms
    assert pytest.approx(e1_sq.scalar_part()) == 1.0

    # Negative generator squares to -1
    e129 = Cl128_32Multivector.generator(129)
    e129_sq = e129 * e129
    assert 0 in e129_sq.terms
    assert pytest.approx(e129_sq.scalar_part()) == -1.0


def test_cl128_32_anticommutation():
    e1 = Cl128_32Multivector.generator(1)
    e2 = Cl128_32Multivector.generator(2)
    
    prod1 = e1 * e2
    prod2 = e2 * e1
    
    # Orthogonal basis blades anticommute: e1 * e2 = - e2 * e1
    sum_prod = prod1 + prod2
    assert len(sum_prod.terms) == 0 or sum_prod.norm() < 1e-12


def test_cl128_32_grade_projection_and_reversion():
    e1 = Cl128_32Multivector.generator(1) * 2.0
    e2 = Cl128_32Multivector.generator(2) * 3.0
    bivector = e1 * e2  # grade 2
    
    scalar_part = bivector.grade_projection(0)
    assert len(scalar_part.terms) == 0
    
    grade2_part = bivector.grade_projection(2)
    assert len(grade2_part.terms) == 1
    
    # Reversion of grade 2 negates it: (e1 * e2)~ = e2 * e1 = - e1 * e2
    rev = bivector.reverse()
    diff = rev + bivector
    assert diff.norm() < 1e-12


def test_anyonic_braid_compiler_fibonacci():
    compiler = AnyonicBraidCompiler(braid_type="fibonacci")
    U = compiler.compile_braid_sequence([1, 2, 1])
    
    # Check unitarity: U @ U^dagger = I
    dim = U.shape[0]
    identity = np.eye(dim, dtype=np.complex128)
    product = U @ U.conj().T
    assert np.allclose(product, identity, atol=1e-6)
    
    # Attestation
    attestation = compiler.generate_topological_attestation([1, 2, 1])
    assert attestation["topologically_protected"] is True
    assert attestation["unitary_error"] < 1e-6
    assert len(attestation["braid_digest"]) == 64


def test_anyonic_braid_compiler_ising():
    compiler = AnyonicBraidCompiler(braid_type="ising")
    U = compiler.compile_braid_sequence([1, 2])
    
    dim = U.shape[0]
    identity = np.eye(dim, dtype=np.complex128)
    assert np.allclose(U @ U.conj().T, identity, atol=1e-6)
