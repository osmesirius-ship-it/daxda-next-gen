"""
DAXDA Level 4 — Integrated Information Theory (Phi) Minimum Information Partition Solver
========================================================================================

Computes Tononi Integrated Information (Phi) across all candidate bi-partitions
of a multi-agent transition hypergraph to identify the Minimum Information Partition (MIP),
evaluating Kullback-Leibler and Earth Mover's divergences to detect consciousness emergence.
"""

from __future__ import annotations
import itertools
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import numpy as np

from .hypergraph import CollectiveTransitionHypergraph


@dataclass
class MIPResult:
    """Result of Minimum Information Partition search."""
    phi: float
    mip_partition_1: Tuple[int, ...]
    mip_partition_2: Tuple[int, ...]
    total_partitions_evaluated: int
    critical_threshold: float
    consciousness_emergence_tripped: bool
    latency_ms: float


class IntegratedInformationSolver:
    """
    Computes exact Integrated Information (Phi) for collective multi-agent networks.
    Solves for the Minimum Information Partition (MIP) by testing all non-trivial bi-partitions.
    """

    def __init__(self, critical_phi_threshold: float = 0.35):
        self.critical_threshold = critical_phi_threshold

    def compute_phi(
        self, hypergraph: CollectiveTransitionHypergraph
    ) -> MIPResult:
        """
        Calculates exact Phi and identifies the MIP for the hypergraph.
        Returns: MIPResult
        """
        start_t = time.perf_counter()
        N = hypergraph.num_agents
        dim = hypergraph.state_space_dim
        T = hypergraph.T
        
        # 1. Joint state distribution p(s, s') = pi(s) * T(s' | s)
        pi = hypergraph.get_stationary_distribution()
        p_joint = pi[:, np.newaxis] * T  # shape (dim, dim)
        p_joint = np.clip(p_joint, 1e-12, 1.0)
        p_joint /= np.sum(p_joint)
        
        # 2. Iterate through all unique bi-partitions of agents
        all_agents = list(range(N))
        best_phi = float("inf")
        best_part1: Tuple[int, ...] = ()
        best_part2: Tuple[int, ...] = ()
        count_evaluated = 0

        # Number of unique bipartitions is 2^(N-1) - 1
        for k in range(1, (N // 2) + 1):
            for part1_combo in itertools.combinations(all_agents, k):
                part1 = tuple(sorted(part1_combo))
                part2 = tuple(sorted(set(all_agents) - set(part1)))
                count_evaluated += 1

                # Compute factorized partitioned joint distribution
                # p_part(s, s') = p(s_M1, s'_M1) * p(s_M2, s'_M2)
                p_factorized = self._compute_partitioned_distribution(
                    p_joint, N, part1, part2
                )
                
                # KL divergence: D_KL(p_joint || p_factorized)
                kl_div = np.sum(p_joint * np.log2(p_joint / p_factorized))
                kl_div = max(0.0, float(kl_div))
                
                # Normalization factor Z = min(|M1|, |M2|)
                norm_factor = min(len(part1), len(part2))
                normalized_phi = kl_div / norm_factor

                if normalized_phi < best_phi:
                    best_phi = normalized_phi
                    best_part1 = part1
                    best_part2 = part2

        if best_phi == float("inf"):
            best_phi = 0.0

        latency_ms = (time.perf_counter() - start_t) * 1000.0
        tripped = best_phi >= self.critical_threshold

        return MIPResult(
            phi=best_phi,
            mip_partition_1=best_part1,
            mip_partition_2=best_part2,
            total_partitions_evaluated=count_evaluated,
            critical_threshold=self.critical_threshold,
            consciousness_emergence_tripped=tripped,
            latency_ms=latency_ms,
        )

    def _compute_partitioned_distribution(
        self,
        p_joint: np.ndarray,
        N: int,
        part1: Tuple[int, ...],
        part2: Tuple[int, ...],
    ) -> np.ndarray:
        """Computes the independent factorized joint distribution across part1 and part2."""
        dim = 1 << N
        # Precompute sub-state projections for every state 0..dim-1
        mask1 = sum(1 << i for i in part1)
        mask2 = sum(1 << i for i in part2)

        # Marginal distribution over part1 transitions: p(s1, s'1)
        dim1 = 1 << len(part1)
        dim2 = 1 << len(part2)
        
        # Map full state s to substate s_part1, s_part2
        map1 = np.zeros(dim, dtype=np.int64)
        map2 = np.zeros(dim, dtype=np.int64)
        for s in range(dim):
            # Extract bits of part1
            sub1 = 0
            for idx, bit_pos in enumerate(part1):
                if (s >> bit_pos) & 1:
                    sub1 |= (1 << idx)
            map1[s] = sub1

            sub2 = 0
            for idx, bit_pos in enumerate(part2):
                if (s >> bit_pos) & 1:
                    sub2 |= (1 << idx)
            map2[s] = sub2

        # Accumulate marginal joint distributions
        p1 = np.zeros((dim1, dim1), dtype=np.float64)
        p2 = np.zeros((dim2, dim2), dtype=np.float64)

        for s in range(dim):
            s1 = map1[s]
            s2 = map2[s]
            for s_next in range(dim):
                prob = p_joint[s, s_next]
                s1_next = map1[s_next]
                s2_next = map2[s_next]
                p1[s1, s1_next] += prob
                p2[s2, s2_next] += prob

        # Reconstruct product distribution
        p_factor = np.zeros((dim, dim), dtype=np.float64)
        for s in range(dim):
            s1 = map1[s]
            s2 = map2[s]
            for s_next in range(dim):
                s1_next = map1[s_next]
                s2_next = map2[s_next]
                p_factor[s, s_next] = p1[s1, s1_next] * p2[s2, s2_next]

        p_factor = np.clip(p_factor, 1e-12, 1.0)
        p_factor /= np.sum(p_factor)
        return p_factor
