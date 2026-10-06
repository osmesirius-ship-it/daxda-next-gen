"""
Generalized Nash Bargaining & Pareto Frontier Solver
====================================================
Solves the axiomatic Nash Bargaining Solution (NBS) with disagreement
threat points d in R^M and bargaining weights alpha in Delta^M.
Ref: Nash, J. (1950), Econometrica; Kalai & Smorodinsky (1975).
"""

from typing import List, Optional, Tuple
import numpy as np


class NashBargainingSolver:
    """
    Solves the multi-agent Generalized Nash Bargaining Problem:
    x* = argmax_{x in X, u_i(x) > d_i} sum_{i=1}^M alpha_i * ln(u_i(x) - d_i)
    """

    @staticmethod
    def compute_nash_objective(
        utilities: np.ndarray,
        threat_point: np.ndarray,
        weights: np.ndarray,
    ) -> float:
        """
        Computes logarithmic Nash objective sum_i alpha_i * ln(max(u_i - d_i, eps)).
        Returns -inf if any utility strictly violates the threat point u_i <= d_i.
        """
        diff = utilities - threat_point
        if np.any(diff <= 1e-12):
            return -float("inf")
        return float(np.sum(weights * np.log(diff)))

    @classmethod
    def solve_discrete(
        cls,
        candidate_utilities: np.ndarray,
        threat_point: np.ndarray,
        weights: Optional[np.ndarray] = None,
    ) -> Tuple[int, np.ndarray, float]:
        """
        Finds optimal candidate policy from a discrete candidate matrix (K candidates x M agents).
        
        Args:
            candidate_utilities: (K, M) array of agent utilities for each candidate.
            threat_point: (M,) disagreement utility threat point d.
            weights: (M,) simplex weights alpha > 0, sum(alpha) = 1. Defaults to uniform 1/M.
            
        Returns:
            Tuple of (best_candidate_idx, best_utility_vector, max_nash_objective).
            If no candidate strictly dominates threat point, returns fallback best-effort.
        """
        candidates = np.asarray(candidate_utilities, dtype=np.float64)
        K, M = candidates.shape
        d = np.asarray(threat_point, dtype=np.float64).flatten()
        assert len(d) == M, f"Threat point dimension {len(d)} must match agent count {M}"

        if weights is None:
            w = np.ones(M, dtype=np.float64) / float(M)
        else:
            w = np.asarray(weights, dtype=np.float64).flatten()
            assert len(w) == M, f"Weights dimension {len(w)} must match agent count {M}"
            assert np.all(w >= 0), "Weights must be non-negative"
            assert np.sum(w) > 0, "Weights sum must be positive"
            w = w / np.sum(w)

        best_idx = -1
        best_obj = -float("inf")

        for k in range(K):
            obj = cls.compute_nash_objective(candidates[k], d, w)
            if obj > best_obj:
                best_obj = obj
                best_idx = k

        # Fallback if no candidate strictly dominates threat point
        if best_idx == -1:
            # Fallback to candidate that minimizes maximum regret / shortfall below threat point
            shortfalls = np.maximum(0.0, d - candidates)
            max_shortfalls = np.max(shortfalls, axis=1)
            best_idx = int(np.argmin(max_shortfalls))
            best_obj = -1e9

        return best_idx, candidates[best_idx], best_obj

    @staticmethod
    def is_pareto_efficient(candidates: np.ndarray, selected_idx: int) -> bool:
        """
        Checks whether the selected candidate is Pareto-efficient within the candidate set.
        A candidate x is Pareto-dominated if there exists y such that
        u_i(y) >= u_i(x) for all i, and u_j(y) > u_j(x) for at least one j.
        """
        selected = candidates[selected_idx]
        K = candidates.shape[0]

        for k in range(K):
            if k == selected_idx:
                continue
            other = candidates[k]
            # Does other weakly dominate selected in all dimensions?
            if np.all(other >= selected - 1e-12):
                # Does other strictly dominate in at least one dimension?
                if np.any(other > selected + 1e-8):
                    return False
        return True

    @staticmethod
    def extract_pareto_frontier(candidates: np.ndarray) -> List[int]:
        """
        Returns list of indices belonging to the non-dominated Pareto frontier.
        """
        K = candidates.shape[0]
        pareto_indices: List[int] = []

        for i in range(K):
            is_dominated = False
            for j in range(K):
                if i == j:
                    continue
                if np.all(candidates[j] >= candidates[i] - 1e-12) and np.any(candidates[j] > candidates[i] + 1e-8):
                    is_dominated = True
                    break
            if not is_dominated:
                pareto_indices.append(i)

        return pareto_indices
