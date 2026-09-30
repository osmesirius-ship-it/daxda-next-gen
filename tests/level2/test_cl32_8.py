"""
Unit & Integration Tests for Level 2 Cl(32,8) Quantum Geometric Engine
======================================================================
"""

import pytest
from daxda_engine.level2.cl32_8 import (
    Blade64,
    Cl32_8Space,
    Cl32_8Validator,
    QuantumCliffordAdapter,
)


def test_cl32_8_space_dimensions_and_blade_count():
    space = Cl32_8Space(32, 8)
    assert space.total_dim == 40
    assert space.total_blades == 1 << 40  # 1,099,511,627,776
    assert len(space._signature) == 40
    assert space._signature[0] == 1.0
    assert space._signature[31] == 1.0
    assert space._signature[32] == -1.0
    assert space._signature[39] == -1.0


def test_cl32_8_geometric_product_sign_parity():
    space = Cl32_8Space(32, 8)
    # e_1 * e_2 = - (e_2 * e_1)
    sign_12 = space.compute_geometric_product_sign(1 << 0, 1 << 1)
    sign_21 = space.compute_geometric_product_sign(1 << 1, 1 << 0)
    assert sign_12 == -sign_21

    # e_1^2 = +1
    sign_11 = space.compute_geometric_product_sign(1 << 0, 1 << 0)
    assert sign_11 == 1.0

    # e_33^2 = -1 (first negative generator)
    sign_33_33 = space.compute_geometric_product_sign(1 << 32, 1 << 32)
    assert sign_33_33 == -1.0


def test_cl32_8_validator_execution():
    space = Cl32_8Space(32, 8)
    validator = Cl32_8Validator(space=space)

    vec = [0.05] * 40
    receipt = validator.validate_vector(vec)

    assert receipt.is_valid is True
    assert receipt.subspace_size == 1 << 40
    assert receipt.latency_ms > 0.0
    assert len(receipt.cert_hash) == 64

    # Batch validation
    batch = [[0.02 * j for _ in range(40)] for j in range(5)]
    receipts = validator.validate_batch(batch)
    assert len(receipts) == 5
    for r in receipts:
        assert r.is_valid is True


def test_quantum_adapter_jordan_wigner_mapping():
    adapter = QuantumCliffordAdapter(qubits=20)
    p0 = adapter.generator_to_pauli_string(0)
    assert p0.qubits == 20
    assert p0.operators[0] == "X"

    p1 = adapter.generator_to_pauli_string(1)
    assert p1.operators[0] == "Y"

    # Generator 2 (qubit 1 even) -> Z on qubit 0, X on qubit 1
    p2 = adapter.generator_to_pauli_string(2)
    assert p2.operators[0] == "Z"
    assert p2.operators[1] == "X"
