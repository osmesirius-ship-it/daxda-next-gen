
"""
DA13 GPU Validation Worker
==========================

Batched CUDA acceleration for DA13 geometric-bound calculations.

Architecture:
- DAXScoringEngine remains unchanged and executes on CPU.
- Batch geometric-bound calculations use PyTorch CUDA when available.
- CPU fallback preserves the original geometric calculation.
- Single-item validation uses CPU to avoid CUDA transfer overhead.
- Individual batch failures do not invalidate other payloads.
- No fabricated GPU utilization or memory metrics.
"""

import time
import math
import hashlib
from typing import Dict, Any, List, Optional, Tuple

from ..scoring.dax_scoring import DAXScoringEngine, DAXScoreResult

try:
    import torch
except ImportError:
    torch = None


class GPUValidationWorker:
    """DA13 worker with optional batched CUDA geometric calculations."""

    def __init__(self, worker_id: str = "gpu-worker-0", gpu_id: int = 0):
        self.worker_id = worker_id
        self.gpu_id = gpu_id
        self.scoring_engine = DAXScoringEngine()

        self.total_processed = 0
        self.total_errors = 0
        self.is_active = True

        self.device = torch.device("cpu") if torch is not None else None
        self.cuda_available = False

        # None means hardware metrics have not been measured.
        self.utilization_pct: Optional[float] = None
        self.memory_used_mb: Optional[float] = None

        if torch is not None:
            try:
                if (
                    torch.cuda.is_available()
                    and 0 <= gpu_id < torch.cuda.device_count()
                ):
                    self.device = torch.device(f"cuda:{gpu_id}")
                    self.cuda_available = True
            except Exception:
                self.device = torch.device("cpu")
                self.cuda_available = False

    def ping(self) -> float:
        """Health ping returning latency in milliseconds."""
        t0 = time.perf_counter()
        _ = math.sqrt(1234567.89)
        return (time.perf_counter() - t0) * 1000.0

    def _prepare_validation(
        self, payload: Dict[str, Any]
    ) -> Tuple[DAXScoreResult, List[float]]:
        """Run unchanged CPU scoring and prepare the risk vector."""

        score_res: DAXScoreResult = (
            self.scoring_engine.compute_stability_score(payload)
        )

        risk_vector = (
            payload.get("risk_vector")
            or payload.get("input", {}).get("risk_vector")
        )

        if not risk_vector:
            components = score_res.components

            risk_vector = [
                components.get("L", 0.8),
                components.get("A", 0.8),
                components.get("P", 0.8),
                components.get("F", 0.8),
                components.get("T", 0.8),
                score_res.score,
                0.1, 0.1, 0.1, 0.1, 0.1,
                0.1, 0.1, 0.1, 0.1, 0.1,
            ]

        return score_res, risk_vector

    def _build_result(
        self,
        payload: Dict[str, Any],
        score_res: DAXScoreResult,
        cl_valid: bool,
        cl_confidence: float,
        started_at: float,
    ) -> Dict[str, Any]:
        """Build the original validation result and deterministic receipt."""

        is_valid = (
            score_res.decision == "ACCEPT"
            and cl_valid
            and not score_res.policy_violation
        )

        payload_nonce = (
            payload.get("nonce")
            or payload.get("id")
            or str(sorted(payload.keys()))
        )

        receipt_hash = hashlib.sha256(
            (
                f"{self.worker_id}:{payload_nonce}:"
                f"{score_res.score:.6f}:"
                f"{score_res.decision}:{cl_valid}"
            ).encode()
        ).hexdigest()

        return {
            "worker_id": self.worker_id,
            "gpu_id": self.gpu_id,
            "is_valid": is_valid,
            "decision": score_res.decision,
            "score": score_res.score,
            "components": score_res.components,
            "weights": score_res.weights,
            "cl_valid": cl_valid,
            "cl_confidence": cl_confidence,
            "latency_ms": (
                time.perf_counter() - started_at
            ) * 1000.0,
            "mutation_contract": score_res.mutation_contract,
            "receipt_hash": receipt_hash,
            "timestamp": time.time(),
        }

    def _build_error(
        self, error: Exception, started_at: float
    ) -> Dict[str, Any]:
        """Build an individual HALT response."""

        self.total_errors += 1

        return {
            "worker_id": self.worker_id,
            "gpu_id": self.gpu_id,
            "is_valid": False,
            "decision": "HALT",
            "error": str(error),
            "latency_ms": (
                time.perf_counter() - started_at
            ) * 1000.0,
            "timestamp": time.time(),
        }

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate one payload using the CPU geometric-bound calculation."""

        started_at = time.perf_counter()
        self.total_processed += 1

        try:
            score_res, risk_vector = self._prepare_validation(payload)

            cl_valid, cl_confidence = (
                self._evaluate_geometric_bounds(risk_vector)
            )

            return self._build_result(
                payload,
                score_res,
                cl_valid,
                cl_confidence,
                started_at,
            )

        except Exception as exc:
            return self._build_error(exc, started_at)

    def _evaluate_geometric_bounds(
        self, risk_vector: List[float]
    ) -> Tuple[bool, float]:
        """Original CPU geometric-bound calculation."""

        if not risk_vector or len(risk_vector) < 5:
            return True, 0.85

        sq_sum = sum(x * x for x in risk_vector[:16])
        norm = math.sqrt(sq_sum)

        is_bounded = norm <= 4.0
        confidence = max(
            0.0,
            min(1.0, 1.0 - (norm / 8.0)),
        )

        return is_bounded, round(confidence, 4)

    def _evaluate_geometric_bounds_batch(
        self, risk_vectors: List[List[float]]
    ) -> List[Optional[Tuple[bool, float]]]:
        """
        Evaluate each risk vector independently.

        Compatible numeric vectors are processed together on CUDA.
        Unsupported vectors fall back individually to CPU.
        A failure in one vector does not invalidate other results.
        """

        results: List[Optional[Tuple[bool, float]]] = [
            None
        ] * len(risk_vectors)

        cuda_indices = []
        cuda_rows = []

        # Stage 1: classify and prepare each vector independently.
        for index, vector in enumerate(risk_vectors):
            try:
                if vector is None or len(vector) < 5:
                    results[index] = (True, 0.85)
                    continue

                values = vector[:16]

                if not all(
                    isinstance(value, (int, float, bool))
                    for value in values
                ):
                    results[index] = (
                        self._evaluate_geometric_bounds(vector)
                    )
                    continue

                row = [float(value) for value in values]
                row.extend([0.0] * (16 - len(row)))

                cuda_indices.append(index)
                cuda_rows.append(row)

            except Exception:
                try:
                    results[index] = (
                        self._evaluate_geometric_bounds(vector)
                    )
                except Exception:
                    results[index] = None

        # Stage 2: CUDA batch calculation.
        if (
            cuda_indices
            and self.cuda_available
            and torch is not None
        ):
            try:
                tensor = torch.tensor(
                    cuda_rows,
                    dtype=torch.float64,
                    device=self.device,
                )

                # Preserve the original sum-of-squares calculation.
                norms = torch.sqrt(
                    torch.sum(tensor * tensor, dim=1)
                )

                torch.cuda.synchronize(self.device)
                norm_values = norms.cpu().tolist()

                for index, norm in zip(
                    cuda_indices, norm_values
                ):
                    bounded = norm <= 4.0

                    confidence = max(
                        0.0,
                        min(1.0, 1.0 - (norm / 8.0)),
                    )

                    results[index] = (
                        bounded,
                        round(confidence, 4),
                    )

            except Exception:
                # CUDA failure: retry each vector independently on CPU.
                for index in cuda_indices:
                    try:
                        results[index] = (
                            self._evaluate_geometric_bounds(
                                risk_vectors[index]
                            )
                        )
                    except Exception:
                        results[index] = None

        else:
            # CUDA unavailable: CPU fallback for each compatible vector.
            for index in cuda_indices:
                try:
                    results[index] = (
                        self._evaluate_geometric_bounds(
                            risk_vectors[index]
                        )
                    )
                except Exception:
                    results[index] = None

        return results

    def batch_validate(
        self, payloads: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate a batch with individual error isolation.

        Scoring remains CPU-based.
        Geometric-bound calculations are batched on CUDA when available.
        Results preserve input order.
        """

        if not payloads:
            return []

        prepared = []
        results: List[Optional[Dict[str, Any]]] = [
            None
        ] * len(payloads)

        # Stage 1: independently score every payload.
        for index, payload in enumerate(payloads):
            started_at = time.perf_counter()
            self.total_processed += 1

            try:
                score_res, risk_vector = (
                    self._prepare_validation(payload)
                )

                prepared.append(
                    (
                        index,
                        payload,
                        score_res,
                        risk_vector,
                        started_at,
                    )
                )

            except Exception as exc:
                results[index] = self._build_error(
                    exc, started_at
                )

        # Stage 2: batch geometric calculations.
        if prepared:
            geometric_results = (
                self._evaluate_geometric_bounds_batch(
                    [item[3] for item in prepared]
                )
            )

            # Stage 3: construct each result independently.
            for item, geometry in zip(
                prepared, geometric_results
            ):
                (
                    index,
                    payload,
                    score_res,
                    risk_vector,
                    started_at,
                ) = item

                if geometry is None:
                    results[index] = self._build_error(
                        ValueError(
                            "Geometric-bound calculation failed."
                        ),
                        started_at,
                    )
                    continue

                try:
                    cl_valid, cl_confidence = geometry

                    results[index] = self._build_result(
                        payload,
                        score_res,
                        cl_valid,
                        cl_confidence,
                        started_at,
                    )

                except Exception as exc:
                    results[index] = self._build_error(
                        exc, started_at
                    )

        # Stage 4: guarantee one output per input.
        for index, result in enumerate(results):
            if result is None:
                results[index] = self._build_error(
                    RuntimeError("Missing batch result."),
                    time.perf_counter(),
                )

        return results

    def stop(self) -> None:
        """Stop the worker."""

        self.is_active = False
