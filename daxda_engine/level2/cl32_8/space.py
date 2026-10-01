"""
DAXDA Level 2 - Cl(32,8) Hypercombinatorial Geometry Space
==========================================================

Implements the 40-dimensional Clifford algebra Cl(32,8) with signature (32, 8).
Features:
  - 40 basis vectors (32 positive e_i^2 = +1, 8 negative e_j^2 = -1)
  - 2^40 = 1,099,511,627,776 blade manifold representation via 64-bit integer bitmasks
  - Fast bitwise parity for geometric product sign calculation
  - Sparse multivector algebra (Multivector40) with grade projection, wedge, inner product, and rotor rotation
  - Invariant rotor transformation: psi' = R psi R_rev with R R_rev = 1
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple


@dataclass
class Blade64:
    """Represents a multivector blade using a 64-bit mask for generators e_1..e_40."""
    mask: int          # 64-bit integer where bit k represents generator e_{k+1}
    coefficient: float = 1.0

    @property
    def grade(self) -> int:
        return bin(self.mask).count("1")

    @property
    def generator_indices(self) -> List[int]:
        return [i for i in range(40) if (self.mask >> i) & 1]


class Multivector40:
    """
    Arbitrary multivector in Cl(32,8).
    Stored as a sparse dictionary mapping 64-bit integer blade masks to float coefficients.
    """

    def __init__(self, blades: Optional[Dict[int, float]] = None, space: Optional[Cl32_8Space] = None):
        self.space = space or Cl32_8Space(32, 8)
        self.blades: Dict[int, float] = {}
        if blades:
            for mask, coeff in blades.items():
                if abs(coeff) > 1e-12:
                    self.blades[mask] = coeff

    def set_blade(self, mask: int, coeff: float) -> None:
        if abs(coeff) > 1e-12:
            self.blades[mask] = coeff
        elif mask in self.blades:
            del self.blades[mask]

    def get_blade(self, mask: int) -> float:
        return self.blades.get(mask, 0.0)

    @property
    def grades(self) -> Set[int]:
        return {bin(m).count("1") for m in self.blades.keys()}

    def grade_projection(self, k: int) -> Multivector40:
        """Projects multivector onto Grade-k subspace <ψ>_k."""
        res = Multivector40(space=self.space)
        for mask, coeff in self.blades.items():
            if bin(mask).count("1") == k:
                res.set_blade(mask, coeff)
        return res

    def reverse(self) -> Multivector40:
        """Computes multivector reverse: ~e_{i1...ik} = (-1)^(k(k-1)/2) e_{i1...ik}."""
        res = Multivector40(space=self.space)
        for mask, coeff in self.blades.items():
            k = bin(mask).count("1")
            sign = -1.0 if ((k * (k - 1) // 2) % 2 == 1) else 1.0
            res.set_blade(mask, coeff * sign)
        return res

    def norm_squared(self) -> float:
        """Computes scalar quadratic norm ||ψ||^2 = <ψ ~ψ>_0."""
        rev = self.reverse()
        prod = self.geometric_product(rev)
        return prod.get_blade(0)

    def __add__(self, other: Multivector40) -> Multivector40:
        res = Multivector40(dict(self.blades), space=self.space)
        for m, c in other.blades.items():
            res.set_blade(m, res.get_blade(m) + c)
        return res

    def __sub__(self, other: Multivector40) -> Multivector40:
        res = Multivector40(dict(self.blades), space=self.space)
        for m, c in other.blades.items():
            res.set_blade(m, res.get_blade(m) - c)
        return res

    def scalar_mul(self, scalar: float) -> Multivector40:
        res = Multivector40(space=self.space)
        if abs(scalar) > 1e-12:
            for m, c in self.blades.items():
                res.set_blade(m, c * scalar)
        return res

    def geometric_product(self, other: Multivector40) -> Multivector40:
        """Computes full Clifford geometric product A * B."""
        res = Multivector40(space=self.space)
        space = self.space
        for m_a, c_a in self.blades.items():
            for m_b, c_b in other.blades.items():
                sign = space.compute_geometric_product_sign(m_a, m_b)
                m_res = m_a ^ m_b
                coeff = c_a * c_b * sign
                res.set_blade(m_res, res.get_blade(m_res) + coeff)
        return res

    def wedge_product(self, other: Multivector40) -> Multivector40:
        """Computes outer / wedge product A ^ B."""
        res = Multivector40(space=self.space)
        space = self.space
        for m_a, c_a in self.blades.items():
            g_a = bin(m_a).count("1")
            for m_b, c_b in other.blades.items():
                if (m_a & m_b) == 0:  # No shared generators
                    g_b = bin(m_b).count("1")
                    sign = space.compute_geometric_product_sign(m_a, m_b)
                    m_res = m_a ^ m_b
                    if bin(m_res).count("1") == (g_a + g_b):
                        coeff = c_a * c_b * sign
                        res.set_blade(m_res, res.get_blade(m_res) + coeff)
        return res

    def inner_product(self, other: Multivector40) -> Multivector40:
        """Computes symmetric contraction inner product A . B."""
        prod = self.geometric_product(other)
        # Keep only grade |g_a - g_b| components
        res = Multivector40(space=self.space)
        for m_a, c_a in self.blades.items():
            g_a = bin(m_a).count("1")
            for m_b, c_b in other.blades.items():
                target_grade = abs(g_a - bin(m_b).count("1"))
                sign = self.space.compute_geometric_product_sign(m_a, m_b)
                m_res = m_a ^ m_b
                if bin(m_res).count("1") == target_grade:
                    res.set_blade(m_res, res.get_blade(m_res) + c_a * c_b * sign)
        return res

    def apply_rotor(self, rotor: Multivector40) -> Multivector40:
        """Applies rotor rotation: ψ' = R ψ ~R."""
        rotor_rev = rotor.reverse()
        temp = rotor.geometric_product(self)
        return temp.geometric_product(rotor_rev)


class Cl32_8Space:
    """
    40-dimensional pseudo-Euclidean Clifford algebra space Cl(32,8).
    e_1 .. e_32 : e_i^2 = +1
    e_33 .. e_40: e_j^2 = -1
    """

    def __init__(self, p: int = 32, q: int = 8):
        self.p = p
        self.q = q
        self.total_dim = p + q  # 40
        self.total_blades = 1 << self.total_dim  # 2^40 = 1,099,511,627,776
        # Precompute signature array: first 32 are +1, next 8 are -1
        self._signature = [1.0] * p + [-1.0] * q

    def generator_mask(self, index: int) -> int:
        """Returns 64-bit bitmask for generator e_{index+1} (0-indexed)."""
        assert 0 <= index < self.total_dim, f"Generator index {index} out of range (0..{self.total_dim-1})"
        return 1 << index

    def generator_multivector(self, index: int) -> Multivector40:
        mv = Multivector40(space=self)
        mv.set_blade(self.generator_mask(index), 1.0)
        return mv

    def scalar_multivector(self, value: float) -> Multivector40:
        mv = Multivector40(space=self)
        mv.set_blade(0, value)
        return mv

    def create_rotor(self, plane_idx1: int, plane_idx2: int, theta: float) -> Multivector40:
        """
        Constructs an exact rotor R = cos(theta/2) - B * sin(theta/2)
        in the plane spanned by e_{idx1} and e_{idx2}.
        Satisfies R * ~R = 1.
        """
        assert plane_idx1 != plane_idx2, "Plane indices must be distinct"
        bivector_mask = (1 << plane_idx1) | (1 << plane_idx2)
        # Sign of e1 * e2
        sign = self.compute_geometric_product_sign(1 << plane_idx1, 1 << plane_idx2)

        half_theta = theta / 2.0
        rotor = Multivector40(space=self)
        rotor.set_blade(0, math.cos(half_theta))
        rotor.set_blade(bivector_mask, -math.sin(half_theta) * sign)
        return rotor

    def compute_geometric_product_sign(self, mask_a: int, mask_b: int) -> float:
        """
        Calculates the exact sign of e_A * e_B using bitwise swap parity
        and signature contraction for common generators.
        """
        # 1. Signature contractions for common generators (A & B)
        common = mask_a & mask_b
        sign = 1.0
        if common:
            for i in range(self.total_dim):
                if (common >> i) & 1:
                    sign *= self._signature[i]

        # 2. Count adjacent transpositions required to reorder canonical basis
        swaps = 0
        for i in range(self.total_dim):
            if (mask_a >> i) & 1:
                lower_mask_b = mask_b & ((1 << i) - 1)
                swaps += bin(lower_mask_b).count("1")

        if swaps % 2 == 1:
            sign = -sign
        return sign

    def encode_vector_to_multivector(self, vector: List[float]) -> Multivector40:
        """Encodes a 40-dimensional vector into Grade-1 multivector."""
        mv = Multivector40(space=self)
        for i, val in enumerate(vector[: self.total_dim]):
            if abs(val) > 1e-12:
                mv.set_blade(1 << i, val)
        return mv

    def compute_norm_squared(self, mv_or_blades: Any) -> float:
        """Computes ||ψ||^2 of a multivector."""
        if isinstance(mv_or_blades, Multivector40):
            return mv_or_blades.norm_squared()
        # Fallback for Blade64 list
        norm_sq = 0.0
        for b in mv_or_blades:
            sig = 1.0
            for i in b.generator_indices:
                sig *= self._signature[i]
            norm_sq += sig * (b.coefficient ** 2)
        return norm_sq
