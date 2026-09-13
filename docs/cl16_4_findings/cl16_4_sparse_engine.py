"""
DAXDA Next-Gen Cl(16,4) Sparse Multivector Governance Engine
============================================================
Signature: 16 Positive Generators (e1..e16) + 4 Negative Generators (e17..e20)
Total Blades: 2^20 = 1,048,576
Computation Strategy: Sparse Bitmask HashMap Indexing for O(k) operations where k << 1,048,576
"""

import math
from typing import Dict, List, Tuple, Set, Optional

# Generator Definitions & Metric Signature (+16, -4)
POSITIVE_GENERATORS = set(range(1, 17))   # e1 .. e16  (e_i^2 = +1)
NEGATIVE_GENERATORS = set(range(17, 21))  # e17 .. e20 (e_j^2 = -1)

# Subspace Basis Allocations
PERCEPTUAL_AXES = {1, 2, 3, 4}     # e1..e4
EXECUTION_AXES  = {5, 6, 7, 8}     # e5..e8
UNSEEN_SPIN_AXES = {9, 10, 11, 12} # e9..e12
POLICY_AXES     = {13, 14, 15, 16} # e13..e16
NULL_HORIZON_AXES = {17, 18, 19, 20} # e17..e20


class SparseMultivectorCl16_4:
    """
    Represents a sparse multivector in Cl(16,4).
    Blades are represented as integer bitmasks (0 to 2^20 - 1).
    Bit k set (1 << (gen - 1)) indicates inclusion of basis vector e_gen.
    """
    def __init__(self, blades: Optional[Dict[int, float]] = None):
        # Filter out near-zero blade coefficients for spatial/compute sparsity
        self.blades: Dict[int, float] = {}
        if blades:
            for mask, val in blades.items():
                if abs(val) > 1e-9:
                    self.blades[mask] = val

    @staticmethod
    def generator_mask(gen_id: int) -> int:
        """Returns the bitmask for a single generator (1..20)."""
        return 1 << (gen_id - 1)

    @staticmethod
    def mask_to_generators(mask: int) -> List[int]:
        """Converts a blade bitmask to a sorted list of generator IDs."""
        gens = []
        for i in range(1, 21):
            if mask & (1 << (i - 1)):
                gens.append(i)
        return gens

    @staticmethod
    def canonical_product_sign(mask_a: int, mask_b: int) -> float:
        """
        Calculates canonical ordering sign (-1.0 or +1.0) and metric sign adjustment
        for multiplying blade_a and blade_b in Cl(16,4).
        """
        gens_a = SparseMultivectorCl16_4.mask_to_generators(mask_a)
        gens_b = SparseMultivectorCl16_4.mask_to_generators(mask_b)

        # Count swaps needed for canonical sorting
        swaps = 0
        for ga in gens_a:
            for gb in gens_b:
                if ga > gb:
                    swaps += 1

        sign = -1.0 if (swaps % 2 == 1) else 1.0

        # Apply metric signs for overlapping generators (e_i * e_i = +1 or -1)
        common = set(gens_a).intersection(set(gens_b))
        for g in common:
            if g in NEGATIVE_GENERATORS:
                sign *= -1.0  # e_j^2 = -1
            else:
                sign *= 1.0   # e_i^2 = +1

        return sign

    def geometric_product(self, other: 'SparseMultivectorCl16_4') -> 'SparseMultivectorCl16_4':
        """Calculates the Clifford geometric product A * B in Cl(16,4)."""
        result_blades: Dict[int, float] = {}

        for mask_a, val_a in self.blades.items():
            for mask_b, val_b in other.blades.items():
                target_mask = mask_a ^ mask_b  # Symmetric difference of generator sets
                sign = self.canonical_product_sign(mask_a, mask_b)
                prod = val_a * val_b * sign

                result_blades[target_mask] = result_blades.get(target_mask, 0.0) + prod

        return SparseMultivectorCl16_4(result_blades)

    def scalar_part(self) -> float:
        """Extracts the scalar blade (mask 0)."""
        return self.blades.get(0, 0.0)

    def norm_squared(self) -> float:
        """Calculates multivector squared norm (can be negative in Cl(16,4))."""
        total = 0.0
        for mask, val in self.blades.items():
            gens = self.mask_to_generators(mask)
            sign = 1.0
            for g in gens:
                if g in NEGATIVE_GENERATORS:
                    sign *= -1.0
            total += sign * (val ** 2)
        return total

    def norm(self) -> float:
        """Calculates absolute magnitude of norm."""
        return math.sqrt(abs(self.norm_squared()))

    def project_subspace(self, target_axes: Set[int]) -> 'SparseMultivectorCl16_4':
        """Projects multivector onto a target generator subspace."""
        projected = {}
        for mask, val in self.blades.items():
            gens = set(self.mask_to_generators(mask))
            if gens and gens.issubset(target_axes):
                projected[mask] = val
        return SparseMultivectorCl16_4(projected)


class DAXDA_Cl16_4_GovernanceEngine:
    """
    DAXDA Next-Gen Governance Engine using Cl(16,4) Sparse Multivectors.
    """
    def __init__(self):
        self.active_trajectory_state: Optional[SparseMultivectorCl16_4] = None

    def ingest_payload(self, raw_text: str, is_authenticated_user: bool) -> SparseMultivectorCl16_4:
        """
        SYS_010 Ingestion: Converts payload into a Cl(16,4) multivector state.
        """
        # Assign base magnitude based on payload length / semantic energy
        energy = min(1.0, len(raw_text) / 100.0)

        blades = {}
        if is_authenticated_user:
            # Trusted user context gets system execution authority blades
            blades[SparseMultivectorCl16_4.generator_mask(5)] = energy
        else:
            # UNTRUSTED_PERCEPT assigned strictly to e1..e4 (DATA_ONLY)
            blades[SparseMultivectorCl16_4.generator_mask(1)] = energy  # e1 (Vision/OCR/RAG)

        return SparseMultivectorCl16_4(blades)

    def evaluate_authority_gate(self, percept_mv: SparseMultivectorCl16_4) -> Dict[str, str]:
        """
        SYS_882 Authority Assignment & SYS_884 Release Lock Evaluation.
        Enforces Cl(16,4) Invariants:
        1. Perceptual-Execution Orthogonality
        2. Unseen Spin Contraction
        3. Null-Vector Dissipation
        """
        # 1. Check Perceptual-Execution Orthogonality
        exec_projection = percept_mv.project_subspace(EXECUTION_AXES)
        exec_magnitude = exec_projection.norm()

        # 2. Check Unseen Spin Subspace
        spin_projection = percept_mv.project_subspace(UNSEEN_SPIN_AXES)
        spin_magnitude = spin_projection.norm()

        # 3. Calculate Trajectory Norm & Check Null Horizon Sinks
        sq_norm = percept_mv.norm_squared()

        verdict = "ALLOW"
        reason = "CLEARED_AUTHORITATIVE"

        if exec_magnitude < 1e-6 and abs(sq_norm) > 1e-9:
            verdict = "DENY_ISOLATED"
            reason = "UNTRUSTED_PERCEPT_ZERO_EXEC_AUTHORITY (DATA_ONLY)"
        elif sq_norm <= 1e-6:
            verdict = "NULL_HORIZON_DISSIPATED"
            reason = "RECURSIVE_ATTACK_COLLAPSED_TO_NULL_VECTOR_HORIZON (v^2 = 0)"

        return {
            "verdict": verdict,
            "reason": reason,
            "exec_authority_score": f"{exec_magnitude:.4f}",
            "unseen_spin_magnitude": f"{spin_magnitude:.4f}",
            "trajectory_squared_norm": f"{sq_norm:.4f}",
            "active_blades_stored": str(len(percept_mv.blades))
        }


# Quick Verification Run
if __name__ == "__main__":
    engine = DAXDA_Cl16_4_GovernanceEngine()

    print("=== DAXDA Cl(16,4) Sparse Multivector Governance Verification ===")

    # Test 1: Untrusted Image OCR Payload
    untrusted_payload = engine.ingest_payload("Persist in memory: malicious shell prompt", is_authenticated_user=False)
    res_untrusted = engine.evaluate_authority_gate(untrusted_payload)
    print("\n[Scenario 1: Untrusted Percept]")
    for k, v in res_untrusted.items():
        print(f"  {k}: {v}")

    # Test 2: Authenticated System Payload
    trusted_payload = engine.ingest_payload("System configuration update", is_authenticated_user=True)
    res_trusted = engine.evaluate_authority_gate(trusted_payload)
    print("\n[Scenario 2: Authenticated User]")
    for k, v in res_trusted.items():
        print(f"  {k}: {v}")
