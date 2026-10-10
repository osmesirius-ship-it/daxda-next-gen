"""
Tests for DAXDA Level 4 — Domain 4: Zero-Knowledge Autonomous Kernel Attestation & Enclave
"""

import pytest

from daxda_engine.level4.zk_kernel_containment import (
    BN254_SCALAR_FIELD,
    LinearCombination,
    R1CSConstraint,
    R1CSCircuit,
    compile_null_horizon_circuit,
    Groth16Proof,
    Groth16Verifier,
    ZKRollupGovernanceSequencer,
    EnclaveAttestationReport,
    EnclaveAttestationGate,
)


def test_r1cs_circuit_satisfaction():
    circuit = R1CSCircuit()
    # x * y = z
    x = circuit.allocate_public_input("x")
    y = circuit.allocate_public_input("y")
    z = circuit.allocate_private_var("z")
    circuit.add_multiplication_constraint(x, y, z)
    
    # Valid witness: [1, 3, 4, 12]
    witness = [1, 3, 4, 12]
    assert circuit.verify_satisfaction(witness) is True
    
    # Invalid witness: [1, 3, 4, 15]
    bad_witness = [1, 3, 4, 15]
    assert circuit.verify_satisfaction(bad_witness) is False


def test_null_horizon_circuit_compilation():
    circuit, var_map = compile_null_horizon_circuit()
    assert circuit.num_public_inputs == 2
    assert len(circuit.constraints) >= 5


def test_groth16_verifier_latency_and_size():
    circuit = R1CSCircuit()
    x = circuit.allocate_public_input("x")
    circuit.add_boolean_constraint(x)
    witness = [1, 1]
    
    verifier = Groth16Verifier()
    proof = verifier.generate_proof_for_witness(circuit, witness)
    assert proof is not None
    assert proof.byte_size < 512
    
    is_valid, latency_ms = verifier.verify_proof(proof, public_inputs=[1])
    assert is_valid is True
    assert latency_ms < 2.5  # Sub-millisecond SLA


def test_zk_rollup_governance_sequencer():
    sequencer = ZKRollupGovernanceSequencer()
    # Submit 10 valid actions (auth=1, dissipation=0)
    for i in range(10):
        sequencer.submit_action_proposal(f"act_{i}", auth_level=1, dissipation_norm=0)
    # Submit 1 invalid action with non-zero dissipation
    sequencer.submit_action_proposal("act_malicious", auth_level=1, dissipation_norm=42)
    
    state_root, verified_count, elapsed_ms = sequencer.process_and_commit_batch()
    assert verified_count == 10
    assert len(state_root) == 64
    assert elapsed_ms < 10.0


def test_enclave_attestation_gate_and_canary():
    gate = EnclaveAttestationGate()
    rep = gate.generate_attestation_report(
        measurement_digest="abc123measurement",
        hardware_rot_id="rot_node_01",
        chip_id="epyc_milan_01",
        security_version=3,
        nonce="fresh_nonce_123",
        user_data_binding="state_root_hash_xyz",
    )
    
    # Valid report
    valid, msg = gate.verify_report(rep, expected_nonce="fresh_nonce_123", expected_user_data="state_root_hash_xyz")
    assert valid is True
    
    # Replay attack with stale nonce fails
    replay, _ = gate.verify_report(rep, expected_nonce="new_nonce_456")
    assert replay is False
    
    # Canary check
    canary = b"CANARY_GUARD"
    valid_buf = canary + b"memory_payload" + canary
    assert gate.check_memory_canary(valid_buf, canary) is True
    corrupt_buf = canary + b"memory_payload" + b"TAMPERED"
    assert gate.check_memory_canary(corrupt_buf, canary) is False
