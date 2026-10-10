"""
DAXDA Level 4 — Domain 4: Zero-Knowledge Autonomous Kernel Attestation & Enclave
================================================================================

Zero-knowledge Groth16 proof verifier, R1CS null-horizon arithmetic circuit compiler,
hardware SEV-SNP/TDX enclave attestation gate, and recursive zk-rollup sequencer.
"""

from .r1cs_circuit import (
    BN254_SCALAR_FIELD,
    LinearCombination,
    R1CSConstraint,
    R1CSCircuit,
    compile_null_horizon_circuit,
)
from .groth16_verifier import (
    G1Point,
    G2Point,
    Groth16Proof,
    Groth16VerifyingKey,
    Groth16Verifier,
    ZKRollupGovernanceSequencer,
)
from .enclave_attestation import (
    EnclaveAttestationReport,
    EnclaveAttestationGate,
)

__all__ = [
    "BN254_SCALAR_FIELD",
    "LinearCombination",
    "R1CSConstraint",
    "R1CSCircuit",
    "compile_null_horizon_circuit",
    "G1Point",
    "G2Point",
    "Groth16Proof",
    "Groth16VerifyingKey",
    "Groth16Verifier",
    "ZKRollupGovernanceSequencer",
    "EnclaveAttestationReport",
    "EnclaveAttestationGate",
]
