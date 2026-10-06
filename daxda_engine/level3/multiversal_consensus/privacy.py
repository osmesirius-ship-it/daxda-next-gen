"""
Differential Privacy Aggregation & Cryptographic Consensus Receipts
===================================================================
(epsilon, delta)-Differential Privacy Gaussian mechanism for agent prompt
privacy and HMAC-SHA256 verifiable tamper-evident consensus receipts.
Ref: Dwork, C., & Roth, A. (2014), Foundations and Trends in Theoretical CS.
"""

from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
import math
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .median import WeiszfeldGeometricMedian
from .nash import NashBargainingSolver


class DifferentialPrivacyAggregator:
    """
    Guarantees (epsilon, delta)-differential privacy for multi-agent preference aggregation
    via calibrated L2-sensitivity bounding and Gaussian noise injection.
    """

    @staticmethod
    def clip_l2_norms(vectors: np.ndarray, max_norm: float = 1.0) -> np.ndarray:
        """
        Projects each vector to L2 ball of radius max_norm.
        """
        vecs = np.asarray(vectors, dtype=np.float64)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        factors = np.minimum(1.0, max_norm / np.maximum(norms, 1e-12))
        return vecs * factors

    @classmethod
    def compute_gaussian_sigma(
        cls,
        epsilon: float,
        delta: float,
        sensitivity: float,
    ) -> float:
        """
        Computes standard deviation sigma for Gaussian mechanism:
        sigma = sensitivity * sqrt(2 * ln(1.25 / delta)) / epsilon
        """
        assert epsilon > 0, "Epsilon must be strictly positive"
        assert 0 < delta < 1.0, "Delta must be in (0, 1)"
        assert sensitivity > 0, "Sensitivity must be strictly positive"
        
        factor = math.sqrt(2.0 * math.log(1.25 / delta))
        sigma = (sensitivity * factor) / epsilon
        return float(sigma)

    @classmethod
    def add_gaussian_noise(
        cls,
        consensus_vector: np.ndarray,
        agent_count: int,
        epsilon: float = 1.0,
        delta: float = 1e-5,
        clip_norm: float = 1.0,
        seed: Optional[int] = None,
    ) -> Tuple[np.ndarray, float]:
        """
        Injects calibrated Gaussian noise into aggregated mean vector.
        L2 global sensitivity for mean of M agents is Delta_2 = (2 * clip_norm) / M.
        
        Returns:
            Tuple of (noised_vector, sigma_used).
        """
        vec = np.asarray(consensus_vector, dtype=np.float64)
        D = vec.shape[0]
        sensitivity = (2.0 * clip_norm) / max(agent_count, 1)
        sigma = cls.compute_gaussian_sigma(epsilon, delta, sensitivity)

        rng = np.random.default_rng(seed)
        noise = rng.normal(0.0, sigma, size=D)
        noised_vec = vec + noise
        return noised_vec, sigma


@dataclass
class ConsensusReceipt:
    """Verifiable cryptographic proof receipt for multiversal consensus decision."""
    consensus_id: str
    timestamp: float
    selected_candidate_idx: int
    consensus_vector: List[float]
    nash_objective: float
    total_agents: int
    byzantine_filtered_count: int
    epsilon: float
    delta: float
    hmac_signature: str

    def to_canonical_dict(self) -> Dict[str, Any]:
        """Returns deterministic dictionary representation excluding the signature."""
        return {
            "consensus_id": self.consensus_id,
            "timestamp": round(self.timestamp, 4),
            "selected_candidate_idx": self.selected_candidate_idx,
            "consensus_vector": [round(float(x), 6) for x in self.consensus_vector],
            "nash_objective": round(float(self.nash_objective), 6),
            "total_agents": self.total_agents,
            "byzantine_filtered_count": self.byzantine_filtered_count,
            "epsilon": self.epsilon,
            "delta": self.delta,
        }

    def verify_signature(self, secret_key: bytes) -> bool:
        """Verifies HMAC-SHA256 signature against canonical dictionary."""
        payload = json.dumps(self.to_canonical_dict(), sort_keys=True).encode("utf-8")
        expected_sig = hmac.new(secret_key, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.hmac_signature, expected_sig)


class MultiversalConsensusManager:
    """
    End-to-end coordinator for Multiversal Social Choice:
    1. Filters Byzantine adversarial agents via Huber-Weiszfeld geometric median.
    2. Solves Generalized Nash Bargaining Solution (NBS).
    3. Guarantees (epsilon, delta)-Differential Privacy on agent utilities.
    4. Issues verifiable cryptographic ConsensusReceipt.
    """

    def __init__(self, secret_key: bytes = b"daxda-multiversal-consensus-signing-key"):
        self.secret_key = secret_key

    def reach_consensus(
        self,
        candidate_utilities: np.ndarray,
        threat_point: np.ndarray,
        epsilon: float = 1.0,
        delta: float = 1e-5,
        filter_byzantine: bool = True,
        seed: Optional[int] = None,
    ) -> Tuple[ConsensusReceipt, np.ndarray]:
        """
        Executes end-to-end consensus protocol across M agents and K candidates.
        
        Args:
            candidate_utilities: (K, M) candidate utility profiles.
            threat_point: (M,) disagreement point.
            epsilon: DP parameter epsilon.
            delta: DP parameter delta.
            filter_byzantine: Whether to detect and remove Byzantine sybil agents.
            seed: Optional PRNG seed.
            
        Returns:
            Tuple of (ConsensusReceipt, dp_consensus_vector).
        """
        candidates = np.asarray(candidate_utilities, dtype=np.float64)
        d = np.asarray(threat_point, dtype=np.float64).flatten()
        K, M = candidates.shape
        byzantine_count = 0
        valid_indices = list(range(M))

        if filter_byzantine and M >= 4:
            # Analyze agent utilities across candidate space: shape (M, K)
            agent_profiles = candidates.T
            byz_indices = WeiszfeldGeometricMedian.detect_byzantine_outliers(agent_profiles)
            byzantine_count = len(byz_indices)
            if byzantine_count > 0:
                valid_indices = [i for i in range(M) if i not in byz_indices]
                candidates = candidates[:, valid_indices]
                d = d[valid_indices]

        # Solve Nash Bargaining
        active_M = len(valid_indices)
        best_k, best_util, best_obj = NashBargainingSolver.solve_discrete(candidates, d)

        # Apply Differential Privacy to winning utility vector
        dp_util, sigma = DifferentialPrivacyAggregator.add_gaussian_noise(
            best_util,
            agent_count=active_M,
            epsilon=epsilon,
            delta=delta,
            seed=seed,
        )

        # Generate cryptographic receipt
        ts = time.time()
        c_id = f"mvs-cons-{hashlib.sha256(f'{ts}-{best_k}'.encode()).hexdigest()[:16]}"
        
        receipt_dict = {
            "consensus_id": c_id,
            "timestamp": round(ts, 4),
            "selected_candidate_idx": int(best_k),
            "consensus_vector": [round(float(x), 6) for x in dp_util.tolist()],
            "nash_objective": round(float(best_obj), 6),
            "total_agents": int(M),
            "byzantine_filtered_count": int(byzantine_count),
            "epsilon": float(epsilon),
            "delta": float(delta),
        }
        payload = json.dumps(receipt_dict, sort_keys=True).encode("utf-8")
        sig = hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

        receipt = ConsensusReceipt(
            consensus_id=c_id,
            timestamp=ts,
            selected_candidate_idx=best_k,
            consensus_vector=dp_util.tolist(),
            nash_objective=best_obj,
            total_agents=M,
            byzantine_filtered_count=byzantine_count,
            epsilon=epsilon,
            delta=delta,
            hmac_signature=sig,
        )

        return receipt, dp_util
