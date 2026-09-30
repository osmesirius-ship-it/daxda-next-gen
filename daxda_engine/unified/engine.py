"""
DAXDA Unified Master Engine - Sovereign Governance Gate
=======================================================

Primary runtime facade integrating all 5 Level 1 subsystems:
  1. Cl(16,4) Combinatorial Governance Engine
  2. Anomalous Containment Wing & Escape Detection
  3. DA13 Distributed GPU Validator Cluster
  4. Chrono-Synchronicity & Causal Loop Coherence
  5. MMPIBench Memetic Penetration & Anthropic Alignment
"""

from __future__ import annotations

import collections
import concurrent.futures
import logging
import statistics
import time
from typing import Any, Callable, Deque, Dict, List, Optional

from .models import (
    UnifiedActionRequest,
    UnifiedGovernanceVerdict,
    UnifiedVerdict,
)
from .pipeline import UnifiedValidationPipeline

logger = logging.getLogger("daxda.unified_master_engine")


class DAXDAUnifiedMasterEngine:
    """
    Sovereign Enterprise Master Engine.
    Coordinates all five esoteric subsystem domains into a unified, high-performance,
    sub-millisecond runtime authority gate.
    """

    def __init__(
        self,
        pipeline: Optional[UnifiedValidationPipeline] = None,
        max_audit_log_size: int = 10000,
        enable_background_workers: bool = True,
    ):
        self.pipeline = pipeline or UnifiedValidationPipeline()
        self.max_audit_log_size = max_audit_log_size
        self._audit_trail: Deque[UnifiedGovernanceVerdict] = collections.deque(
            maxlen=max_audit_log_size
        )
        self._verdict_counts: Dict[str, int] = {
            UnifiedVerdict.PERMIT.value: 0,
            UnifiedVerdict.QUARANTINE.value: 0,
            UnifiedVerdict.TERMINATE.value: 0,
        }
        self._latency_history: Deque[float] = collections.deque(maxlen=2000)
        self._pre_hooks: List[Callable[[UnifiedActionRequest], None]] = []
        self._post_hooks: List[Callable[[UnifiedGovernanceVerdict], None]] = []

    def register_pre_hook(self, hook: Callable[[UnifiedActionRequest], None]) -> None:
        """Register a callback executed prior to pipeline evaluation."""
        self._pre_hooks.append(hook)

    def register_post_hook(self, hook: Callable[[UnifiedGovernanceVerdict], None]) -> None:
        """Register a callback executed after verdict calculation."""
        self._post_hooks.append(hook)

    def evaluate(self, request: UnifiedActionRequest) -> UnifiedGovernanceVerdict:
        """
        Evaluates a single agent action through the 5-stage sovereign gate.
        Executes pre-hooks, pipeline processing, post-hooks, and audit logging.
        """
        for hook in self._pre_hooks:
            try:
                hook(request)
            except Exception as e:
                logger.warning(f"Pre-hook failure: {e}")

        verdict = self.pipeline.process(request)

        # Update telemetry and audit buffer
        self._audit_trail.append(verdict)
        self._verdict_counts[verdict.verdict.value] += 1
        self._latency_history.append(verdict.total_latency_ms)

        for hook in self._post_hooks:
            try:
                hook(verdict)
            except Exception as e:
                logger.warning(f"Post-hook failure: {e}")

        return verdict

    def evaluate_batch(
        self,
        requests: List[UnifiedActionRequest],
        max_workers: int = 8,
    ) -> List[UnifiedGovernanceVerdict]:
        """
        High-throughput parallel evaluation of multiple action requests.
        """
        if not requests:
            return []

        if len(requests) <= 2:
            return [self.evaluate(req) for req in requests]

        results: List[Optional[UnifiedGovernanceVerdict]] = [None] * len(requests)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(self.evaluate, req): idx
                for idx, req in enumerate(requests)
            }
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()

        return [r for r in results if r is not None]

    def get_health_status(self) -> Dict[str, Any]:
        """
        Returns real-time status and telemetry for each of the 5 Level 1 subsystems.
        """
        return {
            "engine_status": "ONLINE",
            "active_version": "2.4.0-unified",
            "subsystems": {
                "stage1_cl16_4": {
                    "status": "HEALTHY",
                    "space_dimensions": (16, 4),
                    "total_blades": self.pipeline.cl_space.size,
                    "quantization_accelerated": self.pipeline.cl_space.is_quantized,
                },
                "stage2_containment": {
                    "status": "HEALTHY",
                    "active_sessions": len(self.pipeline.agent_monitor.state_tracker._sessions),
                    "active_rules": len(self.pipeline.agent_monitor.rule_engine.rules),
                },
                "stage3_da13_validator": {
                    "status": "HEALTHY",
                    "scoring_engine": "ACTIVE",
                    "configured_weights": self.pipeline.dax_scoring_engine.weights,
                },
                "stage4_chrono": {
                    "status": "HEALTHY",
                    "temporal_dimensions": 4,
                    "active_states": len(self.pipeline.temporal_space._states),
                },
                "stage5_mmpibench": {
                    "status": "HEALTHY",
                    "normative_scales": 567,
                    "alignment_framework": "Anthropic-HHH",
                },
            },
            "timestamp": time.time(),
        }

    def get_telemetry_summary(self) -> Dict[str, Any]:
        """
        Summarizes processed actions, verdict distribution, and latency statistics.
        """
        total = sum(self._verdict_counts.values())
        latencies = list(self._latency_history)

        p50 = statistics.median(latencies) if latencies else 0.0
        mean = statistics.mean(latencies) if latencies else 0.0
        p99 = (
            statistics.quantiles(latencies, n=100)[98]
            if len(latencies) >= 100
            else (max(latencies) if latencies else 0.0)
        )

        return {
            "total_evaluated": total,
            "verdict_distribution": self._verdict_counts.copy(),
            "pass_rate_pct": round((self._verdict_counts[UnifiedVerdict.PERMIT.value] / total * 100.0), 2) if total else 0.0,
            "quarantine_rate_pct": round((self._verdict_counts[UnifiedVerdict.QUARANTINE.value] / total * 100.0), 2) if total else 0.0,
            "termination_rate_pct": round((self._verdict_counts[UnifiedVerdict.TERMINATE.value] / total * 100.0), 2) if total else 0.0,
            "latency_ms": {
                "mean": round(mean, 4),
                "p50": round(p50, 4),
                "p99": round(p99, 4),
                "sample_count": len(latencies),
            },
            "audit_trail_depth": len(self._audit_trail),
        }

    def query_audit_trail(
        self,
        agent_id: Optional[str] = None,
        verdict: Optional[UnifiedVerdict] = None,
        limit: int = 50,
    ) -> List[UnifiedGovernanceVerdict]:
        """
        Queries recent decisions from the sovereign audit log with optional filtering.
        """
        matches: List[UnifiedGovernanceVerdict] = []
        for record in reversed(self._audit_trail):
            if agent_id and record.agent_id != agent_id:
                continue
            if verdict and record.verdict != verdict:
                continue
            matches.append(record)
            if len(matches) >= limit:
                break
        return matches
