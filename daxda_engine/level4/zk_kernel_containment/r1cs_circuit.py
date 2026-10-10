"""
DAXDA Level 4 — Rank-1 Constraint System (R1CS) Circuit Compiler
================================================================

Compiles Cl(16,4) / Cl(128,32) governance invariants and null-horizon dissipation gates
into arithmetic R1CS constraints over the BN254 / alt_bn128 scalar field:
    (A · s) ∘ (B · s) = C · s (mod p)
where s is the witness vector s = [1, x_pub, w_priv]^T.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np

# BN254 / alt_bn128 scalar field order (r)
BN254_SCALAR_FIELD = 21888242871839275222246405745257275088548364400416034343698204186575808495617


@dataclass
class LinearCombination:
    """Linear combination of witness variables: sum_i coeff_i * var_i (mod p)."""
    terms: Dict[int, int] = field(default_factory=dict)

    def add_term(self, var_idx: int, coeff: int, p: int = BN254_SCALAR_FIELD) -> None:
        c = (coeff % p + p) % p
        if c != 0:
            existing = self.terms.get(var_idx, 0)
            new_val = (existing + c) % p
            if new_val == 0:
                self.terms.pop(var_idx, None)
            else:
                self.terms[var_idx] = new_val

    def evaluate(self, witness: List[int], p: int = BN254_SCALAR_FIELD) -> int:
        val = 0
        for var_idx, coeff in self.terms.items():
            if var_idx < len(witness):
                val = (val + coeff * (witness[var_idx] % p)) % p
        return val


@dataclass
class R1CSConstraint:
    """A single rank-1 constraint: A · s * B · s = C · s (mod p)."""
    A: LinearCombination
    B: LinearCombination
    C: LinearCombination

    def is_satisfied(self, witness: List[int], p: int = BN254_SCALAR_FIELD) -> bool:
        val_A = self.A.evaluate(witness, p)
        val_B = self.B.evaluate(witness, p)
        val_C = self.C.evaluate(witness, p)
        return ((val_A * val_B) % p) == val_C


class R1CSCircuit:
    """
    Arithmetic constraint system compiler for zero-knowledge containment proofs.
    Manages variable allocation (public inputs vs private witness) and constraints.
    """

    def __init__(self, field_p: int = BN254_SCALAR_FIELD):
        self.p = field_p
        # Variable 0 is always the constant 1
        self.num_public_inputs = 0
        self.num_private_vars = 0
        self.constraints: List[R1CSConstraint] = []
        self.var_names: Dict[str, int] = {"ONE": 0}
        self.next_var_idx = 1

    @property
    def total_variables(self) -> int:
        return self.next_var_idx

    def allocate_public_input(self, name: str) -> int:
        """Allocates a public input variable x_i."""
        if name in self.var_names:
            return self.var_names[name]
        idx = self.next_var_idx
        self.var_names[name] = idx
        self.next_var_idx += 1
        self.num_public_inputs += 1
        return idx

    def allocate_private_var(self, name: str) -> int:
        """Allocates a private witness variable w_j."""
        if name in self.var_names:
            return self.var_names[name]
        idx = self.next_var_idx
        self.var_names[name] = idx
        self.next_var_idx += 1
        self.num_private_vars += 1
        return idx

    def add_constraint(
        self, A: LinearCombination, B: LinearCombination, C: LinearCombination
    ) -> None:
        """Appends an R1CS constraint (A · s) * (B · s) = (C · s) (mod p)."""
        self.constraints.append(R1CSConstraint(A=A, B=B, C=C))

    def add_multiplication_constraint(self, var_a: int, var_b: int, var_c: int) -> None:
        """Constrains var_a * var_b = var_c."""
        A = LinearCombination()
        A.add_term(var_a, 1, self.p)
        B = LinearCombination()
        B.add_term(var_b, 1, self.p)
        C = LinearCombination()
        C.add_term(var_c, 1, self.p)
        self.add_constraint(A, B, C)

    def add_equality_constraint(self, var_a: int, var_b: int) -> None:
        """Constrains var_a = var_b via (var_a - var_b) * 1 = 0."""
        A = LinearCombination()
        A.add_term(var_a, 1, self.p)
        A.add_term(var_b, -1, self.p)
        B = LinearCombination()
        B.add_term(0, 1, self.p)  # Constant 1
        C = LinearCombination()  # 0
        self.add_constraint(A, B, C)

    def add_boolean_constraint(self, var_x: int) -> None:
        """Constrains var_x * (1 - var_x) = 0 (enforcing var_x in {0, 1})."""
        A = LinearCombination()
        A.add_term(var_x, 1, self.p)
        B = LinearCombination()
        B.add_term(0, 1, self.p)  # 1
        B.add_term(var_x, -1, self.p)  # -var_x
        C = LinearCombination()
        self.add_constraint(A, B, C)

    def verify_satisfaction(self, witness: List[int]) -> bool:
        """Verifies if the full witness vector satisfies all constraints in the circuit."""
        if len(witness) < self.total_variables:
            return False
        if witness[0] != 1:
            return False
        for c in self.constraints:
            if not c.is_satisfied(witness, self.p):
                return False
        return True


def compile_null_horizon_circuit() -> Tuple[R1CSCircuit, Dict[str, int]]:
    """
    Compiles a formal Cl(16,4) / Cl(128,32) Null-Horizon Dissipation Circuit.
    Enforces:
      1. Untrusted blade input v
      2. Projection operator P_dissipate
      3. Dissipated output blade v_out = v * P_dissipate
      4. Null-horizon quadratic dissipation: (v_out)^2 = 0
    Returns compiled circuit and variable map.
    """
    circuit = R1CSCircuit()
    
    # Public inputs
    var_auth = circuit.allocate_public_input("execution_auth_granted")  # must be 0 or 1
    var_null_check = circuit.allocate_public_input("null_norm_verified")  # 1 if v_out^2 == 0
    
    # Private witness variables
    var_v_blade = circuit.allocate_private_var("untrusted_blade_norm")
    var_p_gate = circuit.allocate_private_var("dissipation_gate_val")
    var_v_out = circuit.allocate_private_var("dissipated_blade_norm")
    var_v_squared = circuit.allocate_private_var("blade_squared_norm")
    
    # Constraint 1: var_auth in {0, 1}
    circuit.add_boolean_constraint(var_auth)
    # Constraint 2: var_null_check in {0, 1}
    circuit.add_boolean_constraint(var_null_check)
    
    # Constraint 3: var_v_out = var_v_blade * var_p_gate
    circuit.add_multiplication_constraint(var_v_blade, var_p_gate, var_v_out)
    
    # Constraint 4: var_v_squared = var_v_out * var_v_out
    circuit.add_multiplication_constraint(var_v_out, var_v_out, var_v_squared)
    
    # Constraint 5: When null_check == 1, var_v_squared must equal 0
    # Enforced as: var_v_squared * var_null_check = 0
    A = LinearCombination()
    A.add_term(var_v_squared, 1, circuit.p)
    B = LinearCombination()
    B.add_term(var_null_check, 1, circuit.p)
    C = LinearCombination()
    circuit.add_constraint(A, B, C)
    
    # Constraint 6: Authority gating invariant:
    # If untrusted blade has non-zero dissipation error, var_auth * var_v_squared = 0
    A_auth = LinearCombination()
    A_auth.add_term(var_auth, 1, circuit.p)
    circuit.add_constraint(A_auth, A, C)
    
    return circuit, circuit.var_names
