"""
DAXDA Next-Gen Cartan Triality & Spinor Manifold Obstruction Detector
=====================================================================
Analyzes Lie-Trotter bivector flows, Spin(64,16) spinor transformations,
and topological obstruction invariants in Cl(64,16).
"""

import math
from typing import Dict, List, Tuple
from .multivector import Cl64_16Multivector


class SpinorManifoldDetector:
    """
    Evaluates Spin(64, 16) bivector exponentiation, rotor stability,
    and obstruction invariants over hypermanifolds.
    """

    @staticmethod
    def generate_rotor(bivector: Cl64_16Multivector, theta: float) -> Cl64_16Multivector:
        """
        Computes R = exp(-theta/2 * B) for a unit bivector B where B^2 = -1 or +1.
        Uses Taylor series approximation up to order 8 for arbitrary bivectors.
        """
        half_theta = theta * 0.5
        b_scaled = bivector * (-half_theta)

        # Taylor expansion of exponential: sum_{k=0}^N (b_scaled)^k / k!
        curr = Cl64_16Multivector.scalar(1.0)
        res = Cl64_16Multivector.scalar(1.0)
        fact = 1.0

        for k in range(1, 9):
            fact *= k
            curr = curr * b_scaled
            res = res + (curr * (1.0 / fact))

        return res

    @staticmethod
    def check_spinor_norm_drift(rotor: Cl64_16Multivector) -> float:
        """
        Measures deviation of R ~R from 1 (spinor preservation test).
        Returns |<R ~R>_0 - 1.0|.
        """
        norm_sq = rotor.norm_squared()
        return abs(norm_sq - 1.0)

    @classmethod
    def verify_triality_closure(
        cls,
        v1: Cl64_16Multivector,
        v2: Cl64_16Multivector,
        bivector: Cl64_16Multivector,
        theta: float = 0.1
    ) -> Dict[str, float]:
        """
        Verifies rotor conjugation preservation:
        <R v1 ~R, R v2 ~R> == <v1, v2>.
        """
        rotor = cls.generate_rotor(bivector, theta)
        v1_rot = v1.sandwich(rotor)
        v2_rot = v2.sandwich(rotor)

        inner_orig = (v1 * v2).scalar_part()
        inner_rot = (v1_rot * v2_rot).scalar_part()
        drift = abs(inner_rot - inner_orig)

        return {
            "inner_orig": inner_orig,
            "inner_rot": inner_rot,
            "metric_conservation_error": drift,
            "spinor_drift": cls.check_spinor_norm_drift(rotor),
        }
