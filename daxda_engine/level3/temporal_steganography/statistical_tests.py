r"""
Non-Parametric Statistical Testing Suite for Temporal Steganography.
Implements Two-Sample Kolmogorov-Smirnov Test and Mann-Whitney U Test
in pure Python/NumPy without external SciPy dependencies.
"""

from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class KSTestResult:
    """Outcome of two-sample Kolmogorov-Smirnov test."""
    ks_statistic: float        # D = sup |F_1(x) - F_2(x)|
    p_value: float             # Asymptotic two-tailed p-value
    is_distribution_deviant: bool # True if p_value < alpha
    alpha_threshold: float


@dataclass(frozen=True)
class MannWhitneyUResult:
    """Outcome of Mann-Whitney U rank-sum test."""
    u_statistic: float         # Min(U_1, U_2)
    z_score: float             # Standard normal z-score
    p_value: float             # Two-tailed asymptotic p-value
    is_rank_deviant: bool      # True if p_value < alpha
    alpha_threshold: float


class NonParametricStatsEngine:
    r"""
    Statistical testing engine for comparing Inter-Arrival Time (IAT) distributions.
    """

    @staticmethod
    def two_sample_ks_test(
        sample1: np.ndarray,
        sample2: np.ndarray,
        alpha: float = 0.01,
    ) -> KSTestResult:
        r"""
        Two-sample Kolmogorov-Smirnov test:
        D = \sup_x |F_1(x) - F_2(x)|.
        p-value is approximated using the asymptotic Kolmogorov limiting distribution:
        P(K \le x) = 1 - 2 \sum_{k=1}^\infty (-1)^{k-1} e^{-2 k^2 x^2}.
        """
        n1 = len(sample1)
        n2 = len(sample2)
        if n1 == 0 or n2 == 0:
            raise ValueError("Samples must be non-empty")

        s1 = np.sort(sample1)
        s2 = np.sort(sample2)

        # Concatenate and sort all unique evaluation points
        all_points = np.sort(np.unique(np.concatenate([s1, s2])))

        # Empirical CDFs evaluated at all points
        cdf1 = np.searchsorted(s1, all_points, side="right") / float(n1)
        cdf2 = np.searchsorted(s2, all_points, side="right") / float(n2)

        d_stat = float(np.max(np.abs(cdf1 - cdf2)))

        # Effective sample size n_eff = n1 * n2 / (n1 + n2)
        n_eff = (n1 * n2) / float(n1 + n2)
        # Scaled Kolmogorov variable lambda = (\sqrt{n_eff} + 0.12 + 0.11 / \sqrt{n_eff}) * D
        lam = (math.sqrt(n_eff) + 0.12 + 0.11 / math.sqrt(n_eff)) * d_stat

        # Evaluate Kolmogorov series for p-value: Q_KS(lam) = 2 \sum_{k=1}^\infty (-1)^{k-1} e^{-2 k^2 \lam^2}
        p_val = 0.0
        if lam > 0.0:
            for k in range(1, 101):
                term = 2.0 * ((-1) ** (k - 1)) * math.exp(-2.0 * (k**2) * (lam**2))
                p_val += term
                if abs(term) < 1e-15:
                    break
        else:
            p_val = 1.0

        p_val = min(1.0, max(0.0, float(p_val)))

        return KSTestResult(
            ks_statistic=d_stat,
            p_value=p_val,
            is_distribution_deviant=p_val < alpha,
            alpha_threshold=alpha,
        )

    @staticmethod
    def mann_whitney_u_test(
        sample1: np.ndarray,
        sample2: np.ndarray,
        alpha: float = 0.01,
    ) -> MannWhitneyUResult:
        r"""
        Mann-Whitney U rank-sum test with normal approximation:
        U_1 = R_1 - \frac{n_1(n_1 + 1)}{2}
        \mu_U = \frac{n_1 n_2}{2}, \quad \sigma_U = \sqrt{\frac{n_1 n_2 (n_1 + n_2 + 1)}{12}}.
        """
        n1 = len(sample1)
        n2 = len(sample2)
        if n1 == 0 or n2 == 0:
            raise ValueError("Samples must be non-empty")

        # Pool and rank
        combined = np.concatenate([sample1, sample2])
        # Group indicators: 0 for sample1, 1 for sample2
        groups = np.concatenate([np.zeros(n1, dtype=int), np.ones(n2, dtype=int)])

        # Rank with average rank for ties
        sort_indices = np.argsort(combined)
        ranks = np.empty_like(sort_indices, dtype=np.float64)

        # Assign fractional/average ranks for ties
        sorted_vals = combined[sort_indices]
        i = 0
        N = len(sorted_vals)
        while i < N:
            j = i
            while j < N and sorted_vals[j] == sorted_vals[i]:
                j += 1
            avg_rank = (i + 1 + j) / 2.0  # 1-indexed rank
            ranks[sort_indices[i:j]] = avg_rank
            i = j

        # Sum of ranks for sample 1
        r1 = float(np.sum(ranks[groups == 0]))
        u1 = r1 - (n1 * (n1 + 1)) / 2.0
        u2 = (n1 * n2) - u1
        u_stat = float(min(u1, u2))

        # Normal approximation
        mu_u = (n1 * n2) / 2.0
        sigma_u = math.sqrt((n1 * n2 * (n1 + n2 + 1)) / 12.0)

        # Continuity-corrected z-score
        z = (u_stat - mu_u + 0.5) / sigma_u if u_stat < mu_u else (u_stat - mu_u - 0.5) / sigma_u
        z_abs = abs(float(z))

        # Standard normal two-tailed p-value via complementary error function
        p_val = float(math.erfc(z_abs / math.sqrt(2.0)))
        p_val = min(1.0, max(0.0, p_val))

        return MannWhitneyUResult(
            u_statistic=u_stat,
            z_score=float(z),
            p_value=p_val,
            is_rank_deviant=p_val < alpha,
            alpha_threshold=alpha,
        )
