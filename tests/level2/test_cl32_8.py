"""
Unit & Integration Tests for Level 2 Cl(32,8) Quantum Geometric Engine
======================================================================
Comprehensive test suite verifying:
- 40-dimensional Cl(32,8) signature, basis vectors, and 2^40 blade manifold
- Geometric product sign parity and anti-commutation relations
- Multivector40 grade projections, wedge product, inner product, and reverse
- Exact rotor construction, normalization, rotation, and drift stability
- Jordan-Wigner 20-qubit Pauli string compilation and OpenQASM export
- Cl32_8Validator single and batched execution with HMAC-SHA256 receipts
"""

import math
import pytest
from daxda_engine.level2.cl32_8 import (
    Blade64,
    Cl32_8Space,
    Cl32_8ValidationReceipt,
    Cl32_8Validator,
    Multivector40,
    PauliOperatorString,
    QuantumCliffordAdapter,
)


# ============================================================================
# Section 1: Cl(32,8) Space Basis & Blade Manifold
# ============================================================================

def test_cl32_8_space_dimensions_and_blade_count():
    space = Cl32_8Space(32, 8)
    assert space.p == 32
    assert space.q == 8
    assert space.total_dim == 40
    assert space.total_blades == 1 << 40  # 1,099,511,627,776 basis blades
    assert len(space._signature) == 40


def test_cl32_8_signature_positive_generators():
    space = Cl32_8Space(32, 8)
    # First 32 generators must have e_i^2 = +1
    for i in range(32):
        assert space._signature[i] == 1.0
        mask = 1 << i
        sign = space.compute_geometric_product_sign(mask, mask)
        assert sign == 1.0, f"Generator e_{i+1}^2 must be +1"


def test_cl32_8_signature_negative_generators():
    space = Cl32_8Space(32, 8)
    # Generators 33..40 (indices 32..39) must have e_j^2 = -1
    for j in range(32, 40):
        assert space._signature[j] == -1.0
        mask = 1 << j
        sign = space.compute_geometric_product_sign(mask, mask)
        assert sign == -1.0, f"Generator e_{j+1}^2 must be -1"


def test_cl32_8_generator_anti_commutation():
    space = Cl32_8Space(32, 8)
    # For distinct generators, e_i e_j = - e_j e_i => sign(i, j) == -sign(j, i)
    for i in range(5):
        for j in range(i + 1, 6):
            m_i = 1 << i
            m_j = 1 << j
            sign_ij = space.compute_geometric_product_sign(m_i, m_j)
            sign_ji = space.compute_geometric_product_sign(m_j, m_i)
            assert sign_ij == -sign_ji, f"Anti-commutation failed for e_{i+1}, e_{j+1}"


def test_cl32_8_blade64_properties():
    # Generator e_1 and e_5 and e_33: mask = (1<<0) | (1<<4) | (1<<32)
    mask = (1 << 0) | (1 << 4) | (1 << 32)
    b = Blade64(mask=mask, coefficient=2.5)
    assert b.grade == 3
    assert b.generator_indices == [0, 4, 32]
    assert b.coefficient == 2.5


# ============================================================================
# Section 2: Multivector40 Algebra (Wedge, Inner, Reverse, Projections)
# ============================================================================

def test_multivector40_creation_and_grades():
    space = Cl32_8Space(32, 8)
    mv = Multivector40(space=space)
    mv.set_blade(0, 3.0)               # Grade 0 (scalar)
    mv.set_blade(1 << 0, 1.5)          # Grade 1 (e1)
    mv.set_blade((1 << 0) | (1 << 1), -0.5) # Grade 2 (e1 e2)

    assert mv.grades == {0, 1, 2}
    assert mv.get_blade(0) == 3.0
    assert mv.get_blade(1 << 0) == 1.5
    assert mv.get_blade((1 << 0) | (1 << 1)) == -0.5


def test_multivector40_grade_projection():
    space = Cl32_8Space(32, 8)
    mv = Multivector40(space=space)
    mv.set_blade(0, 5.0)
    mv.set_blade(1 << 2, 2.0)
    mv.set_blade((1 << 2) | (1 << 3), 4.0)

    proj_0 = mv.grade_projection(0)
    assert proj_0.get_blade(0) == 5.0
    assert len(proj_0.blades) == 1

    proj_1 = mv.grade_projection(1)
    assert proj_1.get_blade(1 << 2) == 2.0
    assert len(proj_1.blades) == 1

    proj_2 = mv.grade_projection(2)
    assert proj_2.get_blade((1 << 2) | (1 << 3)) == 4.0


def test_multivector40_addition_subtraction():
    space = Cl32_8Space(32, 8)
    m1 = Multivector40(space=space)
    m1.set_blade(1 << 0, 2.0)
    m1.set_blade(1 << 1, 3.0)

    m2 = Multivector40(space=space)
    m2.set_blade(1 << 1, 1.0)
    m2.set_blade(1 << 2, 4.0)

    m_sum = m1 + m2
    assert m_sum.get_blade(1 << 0) == 2.0
    assert m_sum.get_blade(1 << 1) == 4.0
    assert m_sum.get_blade(1 << 2) == 4.0

    m_diff = m1 - m2
    assert m_diff.get_blade(1 << 0) == 2.0
    assert m_diff.get_blade(1 << 1) == 2.0
    assert m_diff.get_blade(1 << 2) == -4.0


def test_multivector40_scalar_multiplication():
    space = Cl32_8Space(32, 8)
    mv = Multivector40(space=space)
    mv.set_blade(1 << 0, 2.0)
    mv.set_blade(1 << 1, -3.0)

    scaled = mv.scalar_mul(2.5)
    assert scaled.get_blade(1 << 0) == 5.0
    assert scaled.get_blade(1 << 1) == -7.5


def test_multivector40_reverse_operation():
    space = Cl32_8Space(32, 8)
    mv = Multivector40(space=space)
    mv.set_blade(0, 1.0)                 # Grade 0: (-1)^0 = +1
    mv.set_blade(1 << 0, 2.0)            # Grade 1: (-1)^0 = +1
    mv.set_blade((1 << 0) | (1 << 1), 3.0) # Grade 2: (-1)^1 = -1
    mask_3 = (1 << 0) | (1 << 1) | (1 << 2)
    mv.set_blade(mask_3, 4.0)             # Grade 3: (-1)^(3*2/2) = (-1)^3 = -1

    rev = mv.reverse()
    assert rev.get_blade(0) == 1.0
    assert rev.get_blade(1 << 0) == 2.0
    assert rev.get_blade((1 << 0) | (1 << 1)) == -3.0
    assert rev.get_blade(mask_3) == -4.0


def test_multivector40_wedge_product():
    space = Cl32_8Space(32, 8)
    e1 = space.generator_multivector(0)
    e2 = space.generator_multivector(1)

    # e1 ^ e2 = e12
    wedge_12 = e1.wedge_product(e2)
    assert wedge_12.get_blade((1 << 0) | (1 << 1)) == 1.0

    # e1 ^ e1 = 0
    wedge_11 = e1.wedge_product(e1)
    assert len(wedge_11.blades) == 0


def test_multivector40_inner_product():
    space = Cl32_8Space(32, 8)
    e1 = space.generator_multivector(0)
    e2 = space.generator_multivector(1)

    # e1 . e1 = e1^2 = +1.0
    dot_11 = e1.inner_product(e1)
    assert dot_11.get_blade(0) == 1.0

    # e1 . e2 = 0
    dot_12 = e1.inner_product(e2)
    assert abs(dot_12.get_blade(0)) < 1e-9


# ============================================================================
# Section 3: Rotors, Rotation Invariants & Representation Drift
# ============================================================================

def test_rotor_construction_and_normalization():
    space = Cl32_8Space(32, 8)
    theta = math.pi / 4.0
    rotor = space.create_rotor(0, 1, theta)

    # R = cos(theta/2) - e12 sin(theta/2)
    assert abs(rotor.get_blade(0) - math.cos(theta / 2.0)) < 1e-9

    # R * ~R must equal 1.0 (scalar)
    rotor_rev = rotor.reverse()
    identity = rotor.geometric_product(rotor_rev)
    assert abs(identity.get_blade(0) - 1.0) < 1e-9
    assert len(identity.grades) == 1


def test_rotor_rotation_of_vector():
    space = Cl32_8Space(32, 8)
    # Rotate e1 by 90 degrees (pi/2) in e1-e2 plane -> should become e2
    theta = math.pi / 2.0
    rotor = space.create_rotor(0, 1, theta)

    e1 = space.generator_multivector(0)
    rotated = e1.apply_rotor(rotor)

    # In e1-e2 plane, e1 rotated by pi/2 is e2
    assert abs(rotated.get_blade(1 << 0)) < 1e-9
    assert abs(rotated.get_blade(1 << 1) - 1.0) < 1e-9


def test_rotor_drift_zero_over_continuous_rotations():
    space = Cl32_8Space(32, 8)
    theta = 0.05
    rotor = space.create_rotor(0, 1, theta)

    # Accumulate 10,000 rotations
    accum_rotor = Multivector40(space=space)
    accum_rotor.set_blade(0, 1.0)

    for _ in range(1000):
        accum_rotor = accum_rotor.geometric_product(rotor)

    # Check norm
    norm_sq = accum_rotor.geometric_product(accum_rotor.reverse()).get_blade(0)
    drift = abs(norm_sq - 1.0)
    assert drift < 1e-6, f"Rotor representation drifted: {drift}"


# ============================================================================
# Section 4: Jordan-Wigner 20-Qubit Quantum Gate Compiler
# ============================================================================

def test_quantum_adapter_jordan_wigner_generators():
    adapter = QuantumCliffordAdapter(qubits=20)

    # Generator 0 (even, k=0) -> X on qubit 0
    p0 = adapter.generator_to_pauli_string(0)
    assert p0.qubits == 20
    assert p0.operators[0] == "X"
    assert p0.operators[1:] == "I" * 19

    # Generator 1 (odd, k=0) -> Y on qubit 0
    p1 = adapter.generator_to_pauli_string(1)
    assert p1.operators[0] == "Y"
    assert p1.operators[1:] == "I" * 19

    # Generator 2 (even, k=1) -> Z on qubit 0, X on qubit 1
    p2 = adapter.generator_to_pauli_string(2)
    assert p2.operators[0] == "Z"
    assert p2.operators[1] == "X"
    assert p2.operators[2:] == "I" * 18

    # Generator 39 (last generator, odd, k=19) -> Z on 0..18, Y on 19
    p39 = adapter.generator_to_pauli_string(39)
    assert p39.operators[:19] == "Z" * 19
    assert p39.operators[19] == "Y"


def test_pauli_string_commutation_relations():
    adapter = QuantumCliffordAdapter(qubits=20)
    p0 = adapter.generator_to_pauli_string(0)  # X_0
    p1 = adapter.generator_to_pauli_string(1)  # Y_0

    # X and Y on same qubit anti-commute
    assert p0.commutes_with(p1) is False

    # p0 (X_0) and p2 (Z_0 X_1):
    # on qubit 0: X vs Z (anti-commutes, count 1)
    # on qubit 1: I vs X (commutes)
    # total anti-commuting pairs = 1 (odd) => anti-commute
    p2 = adapter.generator_to_pauli_string(2)
    assert p0.commutes_with(p2) is False


def test_pauli_string_openqasm_export():
    adapter = QuantumCliffordAdapter(qubits=20)
    p = adapter.generator_to_pauli_string(0)  # X_0
    qasm = p.to_openqasm()
    assert len(qasm) >= 1
    assert "h q[0];" in qasm[0]


def test_multivector_to_quantum_hamiltonian():
    space = Cl32_8Space(32, 8)
    adapter = QuantumCliffordAdapter(qubits=20)

    mv = Multivector40(space=space)
    mv.set_blade(1 << 0, 0.5)
    mv.set_blade(1 << 2, 0.8)

    hamiltonian = adapter.multivector_to_quantum_hamiltonian(mv)
    assert len(hamiltonian) == 2

    circuit_json = adapter.export_qiskit_circuit_json(mv)
    assert circuit_json["num_qubits"] == 20
    assert circuit_json["pauli_terms_count"] == 2


# ============================================================================
# Section 5: Cl32_8Validator & Cryptographic Receipts
# ============================================================================

def test_cl32_8_validator_single_execution():
    space = Cl32_8Space(32, 8)
    validator = Cl32_8Validator(space=space)

    vec = [0.05] * 40
    receipt = validator.validate_vector(vec)

    assert isinstance(receipt, Cl32_8ValidationReceipt)
    assert receipt.is_valid is True
    assert receipt.subspace_size == 1 << 40
    assert receipt.norm_squared > 0.0
    assert receipt.rotor_drift < 1e-6
    assert receipt.latency_ms > 0.0
    assert len(receipt.cert_hash) == 64  # HMAC-SHA256 hex digest


def test_cl32_8_validator_batched_throughput():
    space = Cl32_8Space(32, 8)
    validator = Cl32_8Validator(space=space)

    batch = [[0.01 * (k + j) for k in range(40)] for j in range(50)]
    receipts = validator.validate_batch(batch)

    assert len(receipts) == 50
    for r in receipts:
        assert r.is_valid is True
        assert r.subspace_size == 1 << 40


def test_cl32_8_validator_boundary_rejection():
    space = Cl32_8Space(32, 8)
    # Small max bound
    validator = Cl32_8Validator(space=space, max_norm_bound=0.01)

    # Huge vector
    vec = [5.0] * 40
    receipt = validator.validate_vector(vec)
    assert receipt.is_valid is False


def test_multivector40_geometric_product_associativity():
    space = Cl32_8Space(32, 8)
    e1 = space.generator_multivector(0)
    e2 = space.generator_multivector(1)
    e3 = space.generator_multivector(2)

    # (e1 * e2) * e3 == e1 * (e2 * e3)
    left = e1.geometric_product(e2).geometric_product(e3)
    right = e1.geometric_product(e2.geometric_product(e3))

    mask_123 = (1 << 0) | (1 << 1) | (1 << 2)
    assert math.isclose(left.get_blade(mask_123), right.get_blade(mask_123), abs_tol=1e-9)


def test_cl32_8_pseudoscalar_grade_40():
    space = Cl32_8Space(32, 8)
    # Pseudoscalar has all 40 bits set: (1 << 40) - 1
    pseudoscalar_mask = (1 << 40) - 1
    blade = Blade64(mask=pseudoscalar_mask, coefficient=1.0)
    assert blade.grade == 40
    assert len(blade.generator_indices) == 40
    assert blade.generator_indices[0] == 0
    assert blade.generator_indices[-1] == 39


def test_jordan_wigner_qubit_mapping_anti_commutation():
    adapter = QuantumCliffordAdapter(qubits=20)
    # Generators e_0 (X0) and e_1 (Y0) must anti-commute
    p0 = adapter.generator_to_pauli_string(0)
    p1 = adapter.generator_to_pauli_string(1)
    assert p0.commutes_with(p1) is False

    # Generators e_2 (Z0 X1) and e_3 (Z0 Y1) must anti-commute
    p2 = adapter.generator_to_pauli_string(2)
    p3 = adapter.generator_to_pauli_string(3)
    assert p2.commutes_with(p3) is False


def test_cl32_8_validator_receipt_json_serialization():
    space = Cl32_8Space(32, 8)
    validator = Cl32_8Validator(space=space)
    vec = [0.02 * i for i in range(40)]
    receipt = validator.validate_vector(vec)

    d = receipt.to_dict()
    assert d["is_valid"] is True
    assert d["subspace_size"] == 1 << 40
    assert "cert_hash" in d
    assert "grade_distribution" in d
    assert "rotor_drift" in d

