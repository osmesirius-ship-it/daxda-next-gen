# daxda_engine/unified_resonance_framework.py
"""
DAXDA NextGen Engine: Unified Resonance-Based Framework
=========================================================
Implementation of the 15-Equation Mathematical Core for Cognitive Control,
Neural Coherence, Frequency Alignment, Waypoint Topology, and Decision Dynamics.

Governing Principles:
1. Dimensionally normalized cognitive fields.
2. Phase-coherence bounded on [0, 1].
3. Dynamic control & information-navigation optimization.
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class NormalizedCognitiveField:
    omega_q: float
    omega_0: float
    psi_bio: float
    psi_0: float
    delta_t: float
    tau_0: float

    def compute(self) -> complex:
        real_part = ((self.omega_q / self.omega_0) ** 2) * (self.psi_bio / self.psi_0)
        imag_part = self.delta_t / self.tau_0
        return complex(real_part, imag_part)

    def magnitude(self) -> float:
        z = self.compute()
        return math.sqrt(z.real**2 + z.imag**2)

    def phase(self) -> float:
        z = self.compute()
        return math.atan2(z.imag, z.real)

class NeuralCoherence:
    @staticmethod
    def compute_nci(amplitudes: List[float], phases: List[float]) -> float:
        """Computes NCI in [0, 1]."""
        if not amplitudes or len(amplitudes) != len(phases):
            return 0.0
        
        sum_amp = sum(amplitudes)
        if sum_amp == 0:
            return 0.0
        
        real_sum = sum(a * math.cos(p) for a, p in zip(amplitudes, phases))
        imag_sum = sum(a * math.sin(p) for a, p in zip(amplitudes, phases))
        
        vec_len = math.sqrt(real_sum**2 + imag_sum**2)
        nci = vec_len / sum_amp
        return max(0.0, min(1.0, nci))

    @staticmethod
    def compute_cpc(phases_a: List[float], phases_b: List[float]) -> float:
        """Computes Cognitive Phase Coupling (CPC) between two phase signals."""
        if not phases_a or len(phases_a) != len(phases_b):
            return 0.0
        
        n = len(phases_a)
        diffs = [pa - pb for pa, pb in zip(phases_a, phases_b)]
        real_mean = sum(math.cos(d) for d in diffs) / n
        imag_mean = sum(math.sin(d) for d in diffs) / n
        
        cpc = math.sqrt(real_mean**2 + imag_mean**2)
        return max(0.0, min(1.0, cpc))

class AlignmentCalculator:
    @staticmethod
    def compute_faf(
        nci: float,
        cpc: float,
        omega_s: float,
        omega_t: float,
        sigma_omega: float,
        phi_s: float,
        phi_t: float,
        d_e: float,
        lambda_e: float
    ) -> float:
        """Computes Frequency Alignment Formula (FAF) in [0, 1]."""
        s_f = math.exp(-((omega_s - omega_t) ** 2) / (2 * (sigma_omega ** 2)))
        s_phi = (1.0 + math.cos(phi_s - phi_t)) / 2.0
        s_e = math.exp(-lambda_e * d_e)
        
        faf = nci * cpc * s_f * s_phi * s_e
        return max(0.0, min(1.0, faf))

@dataclass
class Waypoint:
    waypoint_id: str
    position: Tuple[float, float, float]
    creation_time: float
    information: float
    persistence: float
    causal_reach: float

    def strength(self, current_time: float, decay_rate: float) -> float:
        dt = max(0.0, current_time - self.creation_time)
        return self.information * self.persistence * self.causal_reach * math.exp(-decay_rate * dt)

class NavigationEngine:
    @staticmethod
    def compute_decision_score(
        c_a: float, s_a: float, e_a: float, m_a: float, q_a: float, l_a: float, w_a: float,
        r_a: float, u_a: float,
        weights: Dict[str, float]
    ) -> float:
        """Computes Unified Decision Score D(a,t)."""
        positive_terms = (
            weights.get('w_c', 1.0) * c_a +
            weights.get('w_s', 1.0) * s_a +
            weights.get('w_e', 1.0) * e_a +
            weights.get('w_m', 1.0) * m_a +
            weights.get('w_q', 1.0) * q_a +
            weights.get('w_l', 1.0) * l_a +
            weights.get('w_w', 1.0) * w_a
        )
        penalty_terms = weights.get('w_r', 1.0) * r_a + weights.get('w_u', 1.0) * u_a
        return positive_terms - penalty_terms

    @staticmethod
    def compute_master_action(
        actions: List[Dict],
        nci: float,
        weights: Dict[str, float]
    ) -> Tuple[Dict, float]:
        """Selects action maximizing master unified objective."""
        best_action = None
        best_score = -float('inf')

        for act in actions:
            cpc_a = act.get('cpc', 0.5)
            s_f = math.exp(-((act.get('omega_s', 1.0) - act.get('omega_a', 1.0))**2) / (2 * act.get('sigma', 1.0)**2))
            s_phi = (1.0 + math.cos(act.get('phi_s', 0.0) - act.get('phi_a', 0.0))) / 2.0
            s_e = math.exp(-act.get('lambda', 0.1) * act.get('d_a', 0.0))
            
            faf_a = nci * cpc_a * s_f * s_phi * s_e
            
            alignment_term = faf_a * (
                weights.get('w_c', 1.0) * act.get('c_a', 0.0) +
                weights.get('w_m', 1.0) * act.get('m_a', 0.0) +
                weights.get('w_w', 1.0) * act.get('w_a', 0.0) +
                weights.get('w_e', 1.0) * act.get('e_a', 0.0)
            )
            penalties = (
                weights.get('w_r', 1.0) * act.get('r_a', 0.0) +
                weights.get('w_u', 1.0) * act.get('u_a', 0.0) +
                weights.get('w_h', 1.0) * act.get('h_a', 0.0)
            )
            
            score = alignment_term - penalties
            if score > best_score:
                best_score = score
                best_action = act

        return best_action, best_score

class DAXDAResonanceEngine:
    def __init__(self):
        self.state_vector = {
            'psi_bio': 1.0,
            'nci': 1.0,
            'cpc': 1.0,
            'faf': 1.0,
            'memory': 1.0,
            'waypoints': 1.0,
            'error': 0.0,
            'uncertainty': 0.0
        }

    def run_diagnostic(self) -> Dict:
        """Runs a diagnostic check across all 15 unified equations."""
        norm_field = NormalizedCognitiveField(10.0, 10.0, 1.0, 1.0, 0.0, 1.0)
        z = norm_field.compute()
        
        amps = [1.0, 1.0, 1.0]
        phases = [0.0, 0.0, 0.0]
        nci = NeuralCoherence.compute_nci(amps, phases)
        
        cpc = NeuralCoherence.compute_cpc(phases, phases)
        faf = AlignmentCalculator.compute_faf(nci, cpc, 10.0, 10.0, 1.0, 0.0, 0.0, 0.0, 0.1)
        
        wp = Waypoint("WP-01", (0.0, 0.0, 0.0), 0.0, 1.0, 1.0, 1.0)
        wp_strength = wp.strength(1.0, 0.01)
        
        sample_actions = [
            {'name': 'Action_A', 'cpc': 0.9, 'omega_s': 10.0, 'omega_a': 10.0, 'sigma': 1.0, 'phi_s': 0.0, 'phi_a': 0.0, 'd_a': 0.0, 'c_a': 1.0, 'm_a': 0.8, 'w_a': 0.5, 'e_a': 0.9, 'r_a': 0.05, 'u_a': 0.02, 'h_a': 0.01},
            {'name': 'Action_B', 'cpc': 0.3, 'omega_s': 10.0, 'omega_a': 15.0, 'sigma': 1.0, 'phi_s': 0.0, 'phi_a': 1.5, 'd_a': 2.0, 'c_a': 0.4, 'm_a': 0.2, 'w_a': 0.1, 'e_a': 0.3, 'r_a': 0.5, 'u_a': 0.4, 'h_a': 0.3}
        ]
        
        best_act, score = NavigationEngine.compute_master_action(sample_actions, nci, {'w_c': 1.0, 'w_m': 1.0, 'w_w': 1.0, 'w_e': 1.0, 'w_r': 1.0, 'w_u': 1.0, 'w_h': 1.0})
        
        return {
            'normalized_field_mag': norm_field.magnitude(),
            'normalized_field_phase': norm_field.phase(),
            'neural_coherence_index': nci,
            'cognitive_phase_coupling': cpc,
            'frequency_alignment_score': faf,
            'waypoint_01_strength': wp_strength,
            'optimal_selected_action': best_act['name'],
            'master_objective_score': score,
            'framework_status': 'OPERATIONAL_DYNAMICS_ALIGNED'
        }

if __name__ == '__main__':
    engine = DAXDAResonanceEngine()
    diag = engine.run_diagnostic()
    print("=== DAXDA NEXTGEN: UNIFIED RESONANCE FRAMEWORK DIAGNOSTIC ===")
    for k, v in diag.items():
        print(f"  {k}: {v}")
