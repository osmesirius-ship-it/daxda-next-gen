"""
Unit Tests for DAXDA V13 Challenge 8: Gravitational Cognitive Interfacing in Cl(7,0)
Author: Nicole Bess (DAXDA Technologies / DAXDA AI, LLC)
"""

import unittest
import numpy as np
import math

from daxda_engine.cl70_gravitational_cognitive_interfacing import (
    build_cl70_generators,
    Clifford70PhaseSpace,
    build_g2_forms,
    verify_hyperbolic_operator,
    compute_dispersion,
    evaluate_shannon_capacity,
    evaluate_orch_or_7d
)


class TestCl70GravitationalCognitiveInterfacing(unittest.TestCase):

    def setUp(self):
        self.space = Clifford70PhaseSpace()

    def test_generator_anticommutation(self):
        """Verify {e_i, e_j} = 2 * delta_ij * I_8 for all 7 generators."""
        gens = self.space.generators
        self.assertEqual(len(gens), 7)
        for i in range(7):
            for j in range(7):
                anticomm = gens[i] @ gens[j] + gens[j] @ gens[i]
                expected = 2.0 * np.eye(8, dtype=complex) if i == j else np.zeros((8, 8), dtype=complex)
                np.testing.assert_allclose(anticomm, expected, atol=1e-12)

    def test_pseudoscalar_square(self):
        """Verify I_7^2 = -I_8 in Cl(7,0)."""
        I7 = self.space.pseudoscalar_matrix
        I7_sq = I7 @ I7
        np.testing.assert_allclose(I7_sq, -np.eye(8, dtype=complex), atol=1e-12)

    def test_phase_space_grading(self):
        """Verify 128 dimensions across all 8 grades."""
        expected_counts = {
            0: 1,   # Scalar
            1: 7,   # Vectors
            2: 21,  # Bivectors
            3: 35,  # Trivectors
            4: 35,  # Quadvectors
            5: 21,  # 5-vectors
            6: 7,   # 6-vectors
            7: 1    # Pseudoscalar
        }
        for grade, count in expected_counts.items():
            self.assertEqual(len(self.space.grades[grade]), count, f"Grade {grade} count mismatch")
        self.assertEqual(self.space.total_dimensions(), 128)

    def test_hyperbolic_operator_identity(self):
        """Verify e156 * I7 = -e2347, (e156 * I7)^2 = +I_8, and exact analytical inverse."""
        checks = verify_hyperbolic_operator(self.space, lambda_bci=0.35)
        self.assertAlmostEqual(checks["duality_residual"], 0.0, places=10)
        self.assertAlmostEqual(checks["hyperbolic_square_residual"], 0.0, places=10)
        self.assertAlmostEqual(checks["analytical_inverse_residual"], 0.0, places=10)

    def test_dispersion_tachyonic_superluminal(self):
        """Verify superluminal group velocity near resonance."""
        disp = compute_dispersion(k1=1.0, k7=1.0001, mu_eff=1.414)
        self.assertTrue(disp.is_superluminal)
        self.assertGreater(disp.v_group_c, 1.0)

    def test_multivector_channel_capacity(self):
        """Verify Shannon-Hartley capacity matches derivation: ~718 Tbps raw, ~91.9 Pbps G2."""
        report = evaluate_shannon_capacity(b_eff=1e11, p_total=10.0, noise_variance=1e-18)
        self.assertAlmostEqual(report.snr_db, 168.93, places=1)
        self.assertAlmostEqual(report.total_raw_capacity_tbps, 718.29, places=0)
        self.assertAlmostEqual(report.g2_multiplexed_capacity_pbps, 91.94, places=0)

    def test_orch_or_7d_collapse_time(self):
        """Verify 7D volume factor scales collapse time to picosecond regime."""
        orch = evaluate_orch_or_7d(tau_4d_ms=25.0, v3_extra_amplification=2.5e10)
        self.assertAlmostEqual(orch["tau_7d_picoseconds"], 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
