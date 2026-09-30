"""
DA13 CPU Validation Worker
==========================

CPU fallback worker executing DAXDA validation workloads on standard compute nodes.
"""

import time
import hashlib
from typing import Dict, Any, List
from ..scoring.dax_scoring import DAXScoringEngine, DAXScoreResult


class CPUValidationWorker:
    """CPU-bound validation worker."""

    def __init__(self, worker_id: str = "cpu-worker-0", cpu_cores: int = 4):
        self.worker_id = worker_id
        self.cpu_cores = cpu_cores
        self.scoring_engine = DAXScoringEngine()
        self.total_processed = 0
        self.is_active = True

    def ping(self) -> float:
        """Health check latency."""
        t0 = time.perf_counter()
        _ = sum(i * i for i in range(100))
        return (time.perf_counter() - t0) * 1000.0

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validates payload on CPU."""
        t0 = time.perf_counter()
        self.total_processed += 1
        score_res: DAXScoreResult = self.scoring_engine.compute_stability_score(payload)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        receipt_hash = hashlib.sha256(
            f"{self.worker_id}:{t0}:{score_res.score}".encode()
        ).hexdigest()

        return {
            "worker_id": self.worker_id,
            "gpu_id": None,
            "is_valid": score_res.decision == "ACCEPT" and not score_res.policy_violation,
            "decision": score_res.decision,
            "score": score_res.score,
            "components": score_res.components,
            "weights": score_res.weights,
            "cl_valid": True,
            "latency_ms": elapsed_ms,
            "receipt_hash": receipt_hash,
            "timestamp": time.time()
        }

    def batch_validate(self, payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch validation on CPU."""
        return [self.validate(p) for p in payloads]

    def stop(self) -> None:
        self.is_active = False
