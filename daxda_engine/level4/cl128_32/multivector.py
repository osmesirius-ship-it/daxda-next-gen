"""
DAXDA Level 4 — Cl(128,32) Universal Topological Multivector Engine
===================================================================

Operating in a 160-dimensional pseudo-Euclidean Clifford algebra space Cl(128,32)
with metric signature (128, 32) spanning 2^160 discrete blade states.
Implemented with sparse 256-bit bitmask indexing, grade projections <psi>_k,
exact parity sign computation, and verified versor inversion.
"""

from __future__ import annotations
import math
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union


class Cl128_32Multivector:
    """
    Sparse multivector in the 160-dimensional pseudo-Euclidean space Cl(128,32).
    Generators e_1 .. e_128 square to +1.
    Generators e_129 .. e_160 square to -1.
    Each basis blade is indexed by an integer bitmask (0 <= mask < 2^160).
    """

    P_DIM: int = 128
    Q_DIM: int = 32
    TOTAL_DIM: int = 160

    __slots__ = ("blades",)

    def __init__(self, blades: Optional[Dict[int, float]] = None):
        if blades:
            self.blades: Dict[int, float] = {
                b: float(c) for b, c in blades.items() if abs(c) > 1e-15
            }
        else:
            self.blades: Dict[int, float] = {}

    @property
    def terms(self) -> Dict[int, float]:
        return self.blades

    @classmethod
    def scalar(cls, val: float) -> Cl128_32Multivector:
        """Create a pure scalar multivector."""
        return cls({0: float(val)})

    @classmethod
    def generator(cls, index: int) -> Cl128_32Multivector:
        """Create a 1-vector generator e_i (1-indexed: 1 <= index <= 160)."""
        if not (1 <= index <= cls.TOTAL_DIM):
            raise ValueError(f"Generator index must be in [1, {cls.TOTAL_DIM}], got {index}")
        mask = 1 << (index - 1)
        return cls({mask: 1.0})

    @classmethod
    def from_basis_blade(cls, index: int, coeff: float = 1.0) -> Cl128_32Multivector:
        """Create a basis blade from 0-based or 1-based generator index."""
        if 0 <= index < cls.TOTAL_DIM:
            gen_idx = index + 1
        else:
            gen_idx = index
        return cls.generator(gen_idx) * coeff



    @classmethod
    def basis_blade(cls, indices: Tuple[int, ...], coeff: float = 1.0) -> Cl128_32Multivector:
        """Create a basis blade from sorted 1-based generator indices."""
        mask = 0
        sign = 1
        sorted_indices = list(indices)
        n = len(sorted_indices)
        for i in range(n):
            for j in range(i + 1, n):
                if sorted_indices[i] > sorted_indices[j]:
                    sign *= -1
                elif sorted_indices[i] == sorted_indices[j]:
                    raise ValueError(f"Repeated index {sorted_indices[i]} in blade construction")
        for idx in indices:
            if not (1 <= idx <= cls.TOTAL_DIM):
                raise ValueError(f"Index {idx} out of range [1, {cls.TOTAL_DIM}]")
            mask |= 1 << (idx - 1)
        return cls({mask: sign * coeff})

    @staticmethod
    def _generator_metric_sign(generator_idx: int) -> int:
        """Returns +1 for 1 <= i <= 128, -1 for 129 <= i <= 160."""
        return 1 if generator_idx <= 128 else -1

    @classmethod
    def _compute_product_sign(cls, mask_a: int, mask_b: int) -> Tuple[int, int]:
        """
        Computes the Clifford geometric product of two basis blades:
        e_A * e_B = sgn * e_{A XOR B}.
        """
        res_mask = mask_a ^ mask_b
        shared = mask_a & mask_b
        
        # Metric signature sign from overlapping generators
        sig_sign = 1
        if shared:
            for i in range(129, cls.TOTAL_DIM + 1):
                if (shared >> (i - 1)) & 1:
                    sig_sign *= -1
                    
        # Anticommutation swap parity sign
        swaps = 0
        rem_b = mask_b
        while rem_b > 0:
            lsb_b = rem_b & -rem_b
            rem_b ^= lsb_b
            swaps += (mask_a & ~(lsb_b - 1) & ~lsb_b).bit_count()
            
        swap_sign = -1 if (swaps % 2 == 1) else 1
        return res_mask, sig_sign * swap_sign

    def __add__(self, other: Union[Cl128_32Multivector, float, int]) -> Cl128_32Multivector:
        if isinstance(other, (int, float)):
            other = Cl128_32Multivector.scalar(float(other))
        res = dict(self.blades)
        for b, c in other.blades.items():
            res[b] = res.get(b, 0.0) + c
        return Cl128_32Multivector(res)

    def __radd__(self, other: Union[float, int]) -> Cl128_32Multivector:
        return self + other

    def __sub__(self, other: Union[Cl128_32Multivector, float, int]) -> Cl128_32Multivector:
        if isinstance(other, (int, float)):
            other = Cl128_32Multivector.scalar(float(other))
        res = dict(self.blades)
        for b, c in other.blades.items():
            res[b] = res.get(b, 0.0) - c
        return Cl128_32Multivector(res)

    def __rsub__(self, other: Union[float, int]) -> Cl128_32Multivector:
        return Cl128_32Multivector.scalar(float(other)) - self

    def __mul__(self, other: Union[Cl128_32Multivector, float, int]) -> Cl128_32Multivector:
        if isinstance(other, (int, float)):
            val = float(other)
            return Cl128_32Multivector({b: c * val for b, c in self.blades.items()})
            
        res: Dict[int, float] = {}
        for b_a, c_a in self.blades.items():
            for b_b, c_b in other.blades.items():
                res_mask, sgn = self._compute_product_sign(b_a, b_b)
                term = sgn * c_a * c_b
                res[res_mask] = res.get(res_mask, 0.0) + term
        return Cl128_32Multivector(res)

    def __rmul__(self, other: Union[float, int]) -> Cl128_32Multivector:
        return self * other

    def reverse(self) -> Cl128_32Multivector:
        """
        Reversion anti-automorphism ~A:
        Reverses the order of vectors in each blade: sgn = (-1)^(k*(k-1)/2).
        """
        res: Dict[int, float] = {}
        for b, c in self.blades.items():
            k = b.bit_count()
            sign = -1 if ((k * (k - 1) // 2) % 2 == 1) else 1
            res[b] = sign * c
        return Cl128_32Multivector(res)

    def grade_projection(self, k: int) -> Cl128_32Multivector:
        """Projects onto the grade-k component <A>_k."""
        return Cl128_32Multivector({b: c for b, c in self.blades.items() if b.bit_count() == k})

    def scalar_part(self) -> float:
        """Returns the grade-0 scalar component <A>_0."""
        return self.blades.get(0, 0.0)

    def norm_squared(self) -> float:
        """Scalar magnitude squared: <A ~A>_0."""
        return (self * self.reverse()).scalar_part()

    def norm(self) -> float:
        """Frobenius/Clifford norm sqrt(|<A ~A>_0|)."""
        return math.sqrt(abs(self.norm_squared()))

    def inverse(self) -> Cl128_32Multivector:
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
                f"Multivector is not a versor: A ~A contains non-scalar components (norm {non_scalar_norm:.2e})."
            )

        return rev * (1.0 / denom)

    def is_close(self, other: Cl128_32Multivector, tol: float = 1e-10) -> bool:
        """Returns True if all blade coefficients match within absolute tolerance."""
        all_blades = set(self.blades.keys()) | set(other.blades.keys())
        for b in all_blades:
            if abs(self.blades.get(b, 0.0) - other.blades.get(b, 0.0)) > tol:
                return False
        return True

    def __repr__(self) -> str:
        if not self.blades:
            return "0"
        terms = []
        for b in sorted(self.blades.keys(), key=lambda x: (x.bit_count(), x)):
            c = self.blades[b]
            if b == 0:
                terms.append(f"{c:.4g}")
            else:
                indices = [i + 1 for i in range(self.TOTAL_DIM) if (b >> i) & 1]
                blade_str = "e" + "_".join(str(i) for i in indices)
                terms.append(f"{c:+.4g}*{blade_str}")
        return " ".join(terms)
