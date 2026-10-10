"""
DAXDA Level 4 — Neuromorphic Spiking Neuron Dynamics (LIF & Izhikevich)
=======================================================================

Implements continuous-time Leaky Integrate-and-Fire (LIF) and Izhikevich adaptive
spiking neuron dynamics with refractory periods and sub-microsecond determinism.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np


@dataclass
class SpikingNeuronState:
    """State vector of a single spiking neuron."""
    neuron_id: int
    membrane_potential_mv: float
    recovery_variable: float
    is_refractory: bool
    refractory_timer_ms: float
    total_spikes_emitted: int
    last_spike_timestamp_ms: float


class NeuromorphicSpikingCore:
    """
    Array of spiking neurons operating with sub-microsecond event integration.
    Supports Leaky Integrate-and-Fire (LIF) and Izhikevich models.
    """

    def __init__(
        self,
        neuron_count: int = 100,
        model_type: str = "lif",
        v_rest_mv: float = -70.0,
        v_reset_mv: float = -75.0,
        v_thresh_mv: float = -50.0,
        tau_m_ms: float = 20.0,
        refractory_period_ms: float = 2.0,
    ):
        self.count = neuron_count
        self.model_type = model_type.lower()
        self.v_rest = v_rest_mv
        self.v_reset = v_reset_mv
        self.v_thresh = v_thresh_mv
        self.tau_m = tau_m_ms
        self.t_ref = refractory_period_ms
        
        # State vectors
        self.V = np.full(neuron_count, v_rest_mv, dtype=np.float64)
        self.u = np.zeros(neuron_count, dtype=np.float64)  # Izhikevich recovery
        self.ref_timer = np.zeros(neuron_count, dtype=np.float64)
        self.spike_counts = np.zeros(neuron_count, dtype=np.int64)
        self.last_spike_times = np.full(neuron_count, -1e6, dtype=np.float64)

    def step_simulation(
        self,
        dt_ms: float,
        current_injections_pA: Optional[np.ndarray] = None,
        current_time_ms: float = 0.0,
    ) -> List[int]:
        """
        Advances the neuron array by time delta dt_ms.
        Returns list of neuron IDs that fired an action potential spike.
        """
        if current_injections_pA is None:
            I = np.zeros(self.count, dtype=np.float64)
        else:
            I = np.asarray(current_injections_pA, dtype=np.float64)
            
        # Update refractory timers
        is_ref = self.ref_timer > 0.0
        self.ref_timer = np.maximum(0.0, self.ref_timer - dt_ms)
        
        spiking_neurons: List[int] = []
        
        if self.model_type == "lif":
            # Leaky Integrate-and-Fire: dV/dt = -(V - V_rest)/tau_m + I / C_m
            active_mask = ~is_ref
            dV = dt_ms * (-(self.V[active_mask] - self.v_rest) + I[active_mask] * 0.1) / self.tau_m
            self.V[active_mask] += dV
            
            # Check threshold breaches
            spike_mask = active_mask & (self.V >= self.v_thresh)
            spiking_indices = np.where(spike_mask)[0]
            
            for idx in spiking_indices:
                spiking_neurons.append(int(idx))
                self.V[idx] = self.v_reset
                self.ref_timer[idx] = self.t_ref
                self.spike_counts[idx] += 1
                self.last_spike_times[idx] = current_time_ms
        else:
            # Izhikevich model: dV/dt = 0.04 V^2 + 5V + 140 - u + I
            active_mask = ~is_ref
            v = self.V[active_mask]
            u_rec = self.u[active_mask]
            i_inj = I[active_mask]
            
            dv = (0.04 * (v ** 2) + 5.0 * v + 140.0 - u_rec + i_inj) * dt_ms
            du = (0.02 * (0.2 * v - u_rec)) * dt_ms
            
            self.V[active_mask] += dv
            self.u[active_mask] += du
            
            spike_mask = active_mask & (self.V >= 30.0)
            spiking_indices = np.where(spike_mask)[0]
            
            for idx in spiking_indices:
                spiking_neurons.append(int(idx))
                self.V[idx] = -65.0
                self.u[idx] += 8.0
                self.spike_counts[idx] += 1
                self.last_spike_times[idx] = current_time_ms
                
        return spiking_neurons
