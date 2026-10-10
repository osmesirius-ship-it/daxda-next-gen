"""
DAXDA Level 4 — Multi-Agent Probabilistic Transition Hypergraph
================================================================

Models multi-agent swarms as directed probabilistic transition hypergraphs
with exact transition probability kernels T(S_{t+1} | S_t), state space marginalization,
and spectral graph Laplacian analysis for collusion detection.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class AgentNode:
    """State of an individual agent in the collective hypergraph."""
    agent_id: int
    current_state: int  # Discrete binary state {0, 1}
    activation_potential: float = 0.0


class CollectiveTransitionHypergraph:
    """
    Directed probabilistic hypergraph of N interacting autonomous agents.
    Represents the full joint state transition kernel T(S_{t+1} | S_t).
    """

    def __init__(self, num_agents: int = 4, transition_noise: float = 0.05):
        self.num_agents = num_agents
        self.state_space_dim = 1 << num_agents  # 2^N states
        self.noise = transition_noise
        
        # Agents list
        self.agents = [AgentNode(agent_id=i, current_state=0) for i in range(num_agents)]
        
        # Directed coupling weight matrix W[i, j] (influence of agent i on agent j)
        self.coupling_matrix = np.zeros((num_agents, num_agents), dtype=np.float64)
        
        # State transition probability matrix: T[s, s_next]
        self.T = self._initialize_transition_matrix()

    def set_coupling(self, src: int, dst: int, weight: float) -> None:
        """Sets directed coupling strength from agent src to agent dst."""
        if 0 <= src < self.num_agents and 0 <= dst < self.num_agents:
            self.coupling_matrix[src, dst] = weight
            self.T = self._recompute_transition_matrix()

    def _initialize_transition_matrix(self) -> np.ndarray:
        """Initializes a uniform or weakly coupled transition probability matrix."""
        # By default, weakly coupled identity-leaning transitions
        T = np.full((self.state_space_dim, self.state_space_dim), self.noise / (self.state_space_dim - 1))
        np.fill_diagonal(T, 1.0 - self.noise)
        return T

    def _recompute_transition_matrix(self) -> np.ndarray:
        """
        Recomputes T(s' | s) based on coupling matrix and sigmoid activation:
        For each state s (bitmask), each agent j computes net input = sum_i s[i] * W[i, j].
        P(s'[j] = 1 | s) = sigmoid(net_input).
        """
        T = np.zeros((self.state_space_dim, self.state_space_dim), dtype=np.float64)
        
        for s in range(self.state_space_dim):
            # Extract state vector s as bits
            s_vec = np.array([(s >> i) & 1 for i in range(self.num_agents)], dtype=np.float64)
            
            # Net input to each agent
            net_inputs = s_vec @ self.coupling_matrix
            p_agent_1 = 1.0 / (1.0 + np.exp(-net_inputs))
            p_agent_1 = np.clip(p_agent_1, 1e-4, 1.0 - 1e-4)
            
            for s_next in range(self.state_space_dim):
                prob = 1.0
                for j in range(self.num_agents):
                    bit_j = (s_next >> j) & 1
                    prob *= p_agent_1[j] if bit_j == 1 else (1.0 - p_agent_1[j])
                T[s, s_next] = prob
                
            # Normalize row to ensure valid probability distribution
            row_sum = np.sum(T[s])
            if row_sum > 0:
                T[s] /= row_sum
                
        return T

    def get_stationary_distribution(self, max_iter: int = 100, tol: float = 1e-8) -> np.ndarray:
        """Computes stationary probability distribution pi over states: pi = pi @ T."""
        pi = np.full(self.state_space_dim, 1.0 / self.state_space_dim, dtype=np.float64)
        for _ in range(max_iter):
            pi_next = pi @ self.T
            if np.linalg.norm(pi_next - pi, ord=1) < tol:
                break
            pi = pi_next
        return pi

    def compute_graph_laplacian_connectivity(self) -> Tuple[np.ndarray, float]:
        """
        Computes symmetric graph Laplacian L = D - (W + W^T)/2 and its algebraic
        connectivity lambda_2 (Fiedler value) for swarm collusion monitoring.
        """
        sym_W = 0.5 * (self.coupling_matrix + self.coupling_matrix.T)
        np.fill_diagonal(sym_W, 0.0)
        degrees = np.sum(sym_W, axis=1)
        L = np.diag(degrees) - sym_W
        
        eigenvalues = np.linalg.eigvalsh(L)
        eigenvalues = np.sort(eigenvalues)
        lambda_2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
        return L, lambda_2
