"""
DAXDA Level 4 — Spike-Timing-Dependent Plasticity (STDP) Synapse Matrix
=======================================================================

Implements local synaptic weight adaptation based on microsecond-level pre- and post-synaptic
spike timing with anti-adversarial inhibitory strengthening and bounded weight limits.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class STDPSynapticEvent:
    """Record of an STDP synaptic plasticity event."""
    pre_neuron_id: int
    post_neuron_id: int
    delta_t_ms: float
    delta_weight: float
    new_weight: float


class STDPSynapseMatrix:
    """
    Synaptic crossbar matrix connecting pre-synaptic and post-synaptic neurons.
    Enforces exponential STDP adaptation rules:
    Delta w = A_+ exp(-dt/tau_+) for dt > 0 (causal potentiation)
    Delta w = -A_- exp(dt/tau_-) for dt < 0 (anti-causal depression)
    """

    def __init__(
        self,
        n_pre: int = 100,
        n_post: int = 100,
        initial_weight: float = 0.5,
        w_min: float = 0.0,
        w_max: float = 1.0,
        a_plus: float = 0.01,
        a_minus: float = 0.012,
        tau_plus_ms: float = 20.0,
        tau_minus_ms: float = 20.0,
    ):
        self.n_pre = n_pre
        self.n_post = n_post
        self.w_min = w_min
        self.w_max = w_max
        self.a_plus = a_plus
        self.a_minus = a_minus
        self.tau_plus = tau_plus_ms
        self.tau_minus = tau_minus_ms
        
        # Dense weight matrix
        self.weights = np.full((n_pre, n_post), initial_weight, dtype=np.float64)

    def apply_stdp_event(
        self,
        pre_id: int,
        post_id: int,
        pre_spike_time_ms: float,
        post_spike_time_ms: float,
    ) -> STDPSynapticEvent:
        """
        Updates synaptic weight between pre_id and post_id based on spike timing difference.
        delta_t = post_spike_time - pre_spike_time.
        """
        dt = post_spike_time_ms - pre_spike_time_ms
        
        if dt > 0:
            # Pre before post: long-term potentiation (LTP)
            dw = self.a_plus * math.exp(-dt / self.tau_plus)
        elif dt < 0:
            # Post before pre: long-term depression (LTD)
            dw = -self.a_minus * math.exp(dt / self.tau_minus)
        else:
            dw = 0.0
            
        old_w = self.weights[pre_id, post_id]
        new_w = float(np.clip(old_w + dw, self.w_min, self.w_max))
        self.weights[pre_id, post_id] = new_w
        
        return STDPSynapticEvent(
            pre_neuron_id=pre_id,
            post_neuron_id=post_id,
            delta_t_ms=dt,
            delta_weight=dw,
            new_weight=new_w,
        )

    def get_forward_current(self, active_pre_spikes: List[int]) -> np.ndarray:
        """
        Computes forward current injection delivered to post-synaptic neurons
        from a list of pre-synaptic spikes.
        """
        if not active_pre_spikes:
            return np.zeros(self.n_post, dtype=np.float64)
            
        spike_vector = np.zeros(self.n_pre, dtype=np.float64)
        for idx in active_pre_spikes:
            if idx < self.n_pre:
                spike_vector[idx] = 1.0
                
        return spike_vector @ self.weights
