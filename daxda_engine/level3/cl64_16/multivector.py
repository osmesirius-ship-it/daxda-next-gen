"""
DAXDA Next-Gen Cl(64,16) Hypercombinatorial Engine
==================================================
80-dimensional pseudo-Euclidean Clifford algebra Cl(64, 16) with signature:
e_i^2 = +1 for i in {1..64}
e_i^2 = -1 for i in {65..80}
Total multivector space dimension: 2^80 discrete blades.
Sparse 128-bit bitmask representation for memory efficiency.
"""

from __future__ import annotations
import math
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union


class Cl64_16Multivector:
    """
    Sparse multivector in Cl(64, 16) represented as a dictionary:
    {blade_bitmask (int): coefficient (float)}.
    Bit k (0-indexed) represents generator e_{k+1}.
    Bits 0..63 square to +1.
    Bits 64..79 square to -1.
    """

    P = 64  # Positive signature dimension
    Q = 16  # Negative signature dimension
    DIM = 80  # Total dimension: p + q

    __slots__ = ("blades",)

    def __init__(self, blades: Optional[Dict[int, float]] = None):
        # Filter out near-zero terms for sparsity
        if blades:
            self.blades = {b: float(c) for b, c in blades.items() if abs(c) > 1e-15}
        else:
            self.blades = {}

    @classmethod
    def scalar(cls, val: float) -> Cl64_16Multivector:
        """Create scalar multivector (blade 0)."""
        return cls({0: float(val)})

    @classmethod
    def basis_vector(cls, index_1based: int) -> Cl64_16Multivector:
        """Create basis vector e_i (1 <= i <= 80)."""
        if not (1 <= index_1based <= cls.DIM):
            raise ValueError(f"Basis vector index must be in [1, {cls.DIM}], got {index_1based}")
        mask = 1 << (index_1based - 1)
        return cls({mask: 1.0})

    @classmethod
    def from_vector(cls, v: List[float]) -> Cl64_16Multivector:
        """Create grade-1 multivector from a list of 80 real numbers."""
        blades = {}
        for i, val in enumerate(v[: cls.DIM]):
            if abs(val) > 1e-15:
                blades[1 << i] = float(val)
        return cls(blades)

    # ------------------------------------------------------------------
    # Properties & Grade Projections
    # ------------------------------------------------------------------

    def is_zero(self) -> bool:
        return len(self.blades) == 0

    def grades(self) -> Set[int]:
        """Set of grades with non-zero components."""
        return {b.bit_count() for b in self.blades}

    def grade(self, k: int) -> Cl64_16Multivector:
        """Project onto grade-k subspace: <A>_k."""
        return Cl64_16Multivector({b: c for b, c in self.blades.items() if b.bit_count() == k})

    def scalar_part(self) -> float:
        """Scalar projection <A>_0."""
        return self.blades.get(0, 0.0)

    # ------------------------------------------------------------------
    # Involutions & Conjugations
    # ------------------------------------------------------------------

    def reverse(self) -> Cl64_16Multivector:
        """
        Reversion: ~e_I = (-1)^{k(k-1)/2} e_I where k = grade(I).
        Reverses the order of vectors in every blade.
        """
        res = {}
        for b, c in self.blades.items():
            k = b.bit_count()
            sign = -1.0 if (k * (k - 1) // 2) % 2 else 1.0
            res[b] = c * sign
        return Cl64_16Multivector(res)

    def grade_involution(self) -> Cl64_16Multivector:
        """Main involution / parity: ^e_I = (-1)^k e_I."""
        res = {}
        for b, c in self.blades.items():
            k = b.bit_count()
            sign = -1.0 if k % 2 else 1.0
            res[b] = c * sign
        return Cl64_16Multivector(res)

    def clifford_conjugate(self) -> Cl64_16Multivector:
        """Clifford conjugation: bar(A) = ^(~A)."""
        return self.reverse().grade_involution()

    # ------------------------------------------------------------------
    # Exact Basis Blade Product
    # ------------------------------------------------------------------

    @classmethod
    def blade_product_sign(cls, b1: int, b2: int) -> int:
        """
        Compute the sign of the geometric product of basis blades e_{b1} and e_{b2}.
        1. Count anticommutations (inversions between set bits).
        2. Count negative squared basis vectors (bits in b1 & b2 that are >= 64).
        """
        # Step 1: count inversions.
        # For each set bit i in b1, count set bits in b2 strictly less than i.
        inversions = 0
        temp_b1 = b1
        while temp_b1:
            lsb = temp_b1 & -temp_b1
            temp_b1 ^= lsb
            bit_idx = lsb.bit_length() - 1
            # Number of bits in b2 with index < bit_idx
            mask = (1 << bit_idx) - 1
            inversions += (b2 & mask).bit_count()

        sign = -1 if (inversions % 2) else 1

        # Step 2: signature squaring of common generators (b1 & b2)
        common = b1 & b2
        if common:
            # Bits 64..79 have negative signature e_k^2 = -1
            neg_mask = ((1 << cls.DIM) - 1) ^ ((1 << cls.P) - 1)
            neg_common_count = (common & neg_mask).bit_count()
            if neg_common_count % 2:
                sign = -sign

        return sign

    # ------------------------------------------------------------------
    # Arithmetic & Geometric Products
    # ------------------------------------------------------------------

    def __add__(self, other: Union[Cl64_16Multivector, float, int]) -> Cl64_16Multivector:
        if isinstance(other, (int, float)):
            other = Cl64_16Multivector.scalar(other)
        res = dict(self.blades)
        for b, c in other.blades.items():
            res[b] = res.get(b, 0.0) + c
        return Cl64_16Multivector(res)

    def __radd__(self, other: Union[float, int]) -> Cl64_16Multivector:
        return self.__add__(other)

    def __sub__(self, other: Union[Cl64_16Multivector, float, int]) -> Cl64_16Multivector:
        if isinstance(other, (int, float)):
            other = Cl64_16Multivector.scalar(other)
        res = dict(self.blades)
        for b, c in other.blades.items():
            res[b] = res.get(b, 0.0) - c
        return Cl64_16Multivector(res)

    def __rsub__(self, other: Union[float, int]) -> Cl64_16Multivector:
        return Cl64_16Multivector.scalar(other) - self

    def __neg__(self) -> Cl64_16Multivector:
        return Cl64_16Multivector({b: -c for b, c in self.blades.items()})

    def __mul__(self, other: Union[Cl64_16Multivector, float, int]) -> Cl64_16Multivector:
        """Clifford geometric product A * B."""
        if isinstance(other, (int, float)):
            if abs(other) < 1e-15:
                return Cl64_16Multivector()
            return Cl64_16Multivector({b: c * float(other) for b, c in self.blades.items()})

        res: Dict[int, float] = {}
        for b1, c1 in self.blades.items():
            for b2, c2 in other.blades.items():
                target_blade = b1 ^ b2
                sign = self.blade_product_sign(b1, b2)
                coeff = c1 * c2 * sign
                res[target_blade] = res.get(target_blade, 0.0) + coeff

        return Cl64_16Multivector(res)

    def __rmul__(self, other: Union[float, int]) -> Cl64_16Multivector:
        return self.__mul__(other)

    def wedge(self, other: Cl64_16Multivector) -> Cl64_16Multivector:
        """Exterior / wedge product A ^ B."""
        res: Dict[int, float] = {}
        for b1, c1 in self.blades.items():
            k1 = b1.bit_count()
            for b2, c2 in other.blades.items():
                k2 = b2.bit_count()
                target_blade = b1 ^ b2
                # Wedge product requires disjoint basis vectors (grade addition)
                if target_blade.bit_count() == k1 + k2:
                    sign = self.blade_product_sign(b1, b2)
                    res[target_blade] = res.get(target_blade, 0.0) + (c1 * c2 * sign)
        return Cl64_16Multivector(res)

    def left_contraction(self, other: Cl64_16Multivector) -> Cl64_16Multivector:
        r"""
        Left contraction A _| B = \sum_{r, s} <A_r B_s>_{s - r} for r <= s,
        and vanishes (0) when grade(A_r) > grade(B_s).
        """
        res: Dict[int, float] = {}
        for b1, c1 in self.blades.items():
            k1 = b1.bit_count()
            for b2, c2 in other.blades.items():
                k2 = b2.bit_count()
                if k1 > k2:
                    continue
                target_blade = b1 ^ b2
                if target_blade.bit_count() == (k2 - k1):
                    sign = self.blade_product_sign(b1, b2)
                    res[target_blade] = res.get(target_blade, 0.0) + (c1 * c2 * sign)
        return Cl64_16Multivector(res)

    def inner(self, other: Cl64_16Multivector) -> Cl64_16Multivector:
        """Left contraction / inner product A . B."""
        return self.left_contraction(other)

    def commutator(self, other: Cl64_16Multivector) -> Cl64_16Multivector:
        """Lie commutator bracket: [A, B] = (AB - BA) / 2."""
        return (self * other - other * self) * 0.5

    def anti_commutator(self, other: Cl64_16Multivector) -> Cl64_16Multivector:
        """Anti-commutator bracket: {A, B} = (AB + BA) / 2."""
        return (self * other + other * self) * 0.5

    # ------------------------------------------------------------------
    # Norm & Invertibility
    # ------------------------------------------------------------------

    def norm_squared(self) -> float:
        """Scalar magnitude squared: <A ~A>_0."""
        return (self * self.reverse()).scalar_part()

    def norm(self) -> float:
        """Frobenius/Clifford norm sqrt(|<A ~A>_0|)."""
        return math.sqrt(abs(self.norm_squared()))

    def inverse(self) -> Cl64_16Multivector:
        """
        Versor inverse A^{-1} = ~A / <A ~A>_0.
        Valid for versors and invertible blades where A ~A is a pure scalar.
        """
        rev = self.reverse()
        product = self * rev
        denom = product.scalar_part()
        if abs(denom) < 1e-14:
            raise ValueError(f"Multivector is not invertible: <A ~A>_0 = {denom:.2e} ~= 0")

        # Verify that A is a versor: A ~A must be a pure scalar (grade 0)
        non_scalar_norm = math.sqrt(sum(c**2 for b, c in product.blades.items() if b != 0))
        if non_scalar_norm > 1e-10 * abs(denom):
            raise ValueError(
                f"Multivector is not a versor: A ~A contains non-scalar components (norm {non_scalar_norm:.2e}). "
                "General non-versor multivectors require full matrix inversion."
            )
        return rev * (1.0 / denom)

    def sandwich(self, rotor: Cl64_16Multivector) -> Cl64_16Multivector:
        """Rotor conjugation / transport: R A ~R."""
        return rotor * self * rotor.reverse()

    def __repr__(self) -> str:
        if not self.blades:
            return "0"
        terms = []
        for b, c in sorted(self.blades.items(), key=lambda item: (item[0].bit_count(), item[0])):
            if b == 0:
                terms.append(f"{c:.4f}")
            else:
                factors = []
                idx = 1
                temp = b
                while temp:
                    if temp & 1:
                        factors.append(f"e{idx}")
                    temp >>= 1
                    idx += 1
                blade_str = "^".join(factors)
                terms.append(f"{c:+.4f}*{blade_str}")
        return " ".join(terms)
