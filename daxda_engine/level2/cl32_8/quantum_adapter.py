"""
DAXDA Level 2 - Cl(32,8) Quantum Gate Adapter & Jordan-Wigner Compiler
======================================================================

Maps Cl(32,8) multivector generators to 20-qubit Pauli operator strings
via Jordan-Wigner isomorphism:
  e_{2k}   = (∏_{j=0}^{k-1} Z_j) X_k
  e_{2k+1} = (∏_{j=0}^{k-1} Z_j) Y_k

Generates executable quantum gate sequences for Qiskit, Cirq, and OpenQASM 2.0.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .space import Blade64, Cl32_8Space, Multivector40


@dataclass
class PauliOperatorString:
    """Represents a 20-qubit Pauli tensor product: P = ⨂_{j=0}^{19} σ_j."""
    qubits: int = 20
    operators: str = "I" * 20  # String of length 20 consisting of I, X, Y, Z
    coefficient: complex = 1.0

    def to_qiskit_format(self) -> str:
        """Returns string representation for Qiskit Pauli operator."""
        return self.operators

    def to_openqasm(self) -> List[str]:
        """Synthesizes OpenQASM 2.0 instructions to prepare/measure this Pauli string."""
        qasm = []
        for i, op in enumerate(self.operators):
            if op == "X":
                qasm.append(f"h q[{i}];")
            elif op == "Y":
                qasm.append(f"sdg q[{i}]; h q[{i}];")
            elif op == "Z":
                qasm.append(f"// Z measurement on q[{i}]")
        return qasm

    def commutes_with(self, other: PauliOperatorString) -> bool:
        """Checks if two Pauli strings commute: [P1, P2] == 0."""
        assert self.qubits == other.qubits, "Qubit count mismatch"
        anti_commute_count = 0
        for op1, op2 in zip(self.operators, other.operators):
            if op1 != "I" and op2 != "I" and op1 != op2:
                anti_commute_count += 1
        return (anti_commute_count % 2 == 0)


class QuantumCliffordAdapter:
    """Isomorphic compiler between Cl(32,8) blades and 20-qubit quantum operators."""

    def __init__(self, qubits: int = 20):
        self.qubits = qubits  # 20 qubits represent 40 real Clifford generators

    def generator_to_pauli_string(self, generator_idx: int) -> PauliOperatorString:
        """
        Maps a single generator e_{idx} (0-indexed, 0..39) to a 20-qubit Pauli string.
        Even index (2k): X on qubit k with Z chain on 0..k-1
        Odd index (2k+1): Y on qubit k with Z chain on 0..k-1
        """
        assert 0 <= generator_idx < (2 * self.qubits), f"Generator index {generator_idx} out of range"
        k = generator_idx // 2
        is_odd = (generator_idx % 2 == 1)

        pauli_list = ["I"] * self.qubits
        for j in range(k):
            pauli_list[j] = "Z"
        pauli_list[k] = "Y" if is_odd else "X"

        return PauliOperatorString(qubits=self.qubits, operators="".join(pauli_list), coefficient=1.0)

    def blade_mask_to_pauli_string(self, mask: int) -> PauliOperatorString:
        """Synthesizes the composite Pauli string for an arbitrary blade mask."""
        # For single generator
        active_bits = [i for i in range(2 * self.qubits) if (mask >> i) & 1]
        if not active_bits:
            return PauliOperatorString(qubits=self.qubits, operators="I" * self.qubits, coefficient=1.0)

        # Multi-generator composite: Multiply Pauli strings
        current_ops = ["I"] * self.qubits
        phase = 1.0 + 0.0j

        pauli_mult_table = {
            ("I", "I"): ("I", 1.0),
            ("I", "X"): ("X", 1.0),
            ("I", "Y"): ("Y", 1.0),
            ("I", "Z"): ("Z", 1.0),
            ("X", "I"): ("X", 1.0),
            ("X", "X"): ("I", 1.0),
            ("X", "Y"): ("Z", 1.0j),
            ("X", "Z"): ("Y", -1.0j),
            ("Y", "I"): ("Y", 1.0),
            ("Y", "X"): ("Z", -1.0j),
            ("Y", "Y"): ("I", 1.0),
            ("Y", "Z"): ("X", 1.0j),
            ("Z", "I"): ("Z", 1.0),
            ("Z", "X"): ("Y", 1.0j),
            ("Z", "Y"): ("X", -1.0j),
            ("Z", "Z"): ("I", 1.0),
        }

        for gen_idx in active_bits:
            p_gen = self.generator_to_pauli_string(gen_idx)
            for q in range(self.qubits):
                op1 = current_ops[q]
                op2 = p_gen.operators[q]
                op_res, p_factor = pauli_mult_table[(op1, op2)]
                current_ops[q] = op_res
                phase *= p_factor

        return PauliOperatorString(qubits=self.qubits, operators="".join(current_ops), coefficient=phase)

    def multivector_to_quantum_hamiltonian(
        self, mv: Multivector40
    ) -> List[PauliOperatorString]:
        """Converts an arbitrary Cl(32,8) multivector into a sum of Pauli strings."""
        terms = []
        for mask, coeff in mv.blades.items():
            pauli = self.blade_mask_to_pauli_string(mask)
            terms.append(
                PauliOperatorString(
                    qubits=self.qubits,
                    operators=pauli.operators,
                    coefficient=pauli.coefficient * coeff,
                )
            )
        return terms

    def export_qiskit_circuit_json(self, mv: Multivector40) -> Dict[str, Any]:
        """Exports quantum circuit representation for Qiskit / Cirq execution."""
        terms = self.multivector_to_quantum_hamiltonian(mv)
        return {
            "num_qubits": self.qubits,
            "pauli_terms_count": len(terms),
            "terms": [
                {
                    "pauli": t.operators,
                    "coeff_real": t.coefficient.real,
                    "coeff_imag": t.coefficient.imag,
                    "qasm_instructions": t.to_openqasm(),
                }
                for t in terms
            ],
        }
