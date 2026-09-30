"""
DA13 Distributed Result Aggregator
==================================

Aggregates validation results from GPU/CPU worker nodes, resolves cross-node
consensus conflicts, computes batch statistics, and maintains cryptographic audit records.
"""

import time
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class AggregatedBatchReport:
    batch_id: str
    total_validations: int
    passed_validations: int
    rejected_validations: int
    halt_count: int
    recurse_count: int
    accept_count: int
    avg_latency_ms: float
    p99_latency_ms: float
    avg_stability_score: float
    consensus_valid: bool
    audit_hash: str
    results: List[Dict[str, Any]] = field(default_factory=list)


class ResultAggregator:
    """Collects and aggregates validation results across distributed workers."""

    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def aggregate_results(
        self,
        batch_id: str,
        results: List[Dict[str, Any]]
    ) -> AggregatedBatchReport:
        """Aggregates a list of validation outputs into a summary report."""
        if not results:
            return AggregatedBatchReport(
                batch_id=batch_id,
                total_validations=0,
                passed_validations=0,
                rejected_validations=0,
                halt_count=0,
                recurse_count=0,
                accept_count=0,
                avg_latency_ms=0.0,
                p99_latency_ms=0.0,
                avg_stability_score=0.0,
                consensus_valid=True,
                audit_hash="EMPTY_BATCH",
                results=[]
            )

        total = len(results)
        passed = sum(1 for r in results if r.get("is_valid", False))
        rejected = total - passed
        
        accept_count = sum(1 for r in results if r.get("decision") == "ACCEPT")
        recurse_count = sum(1 for r in results if r.get("decision") == "RECURSE")
        halt_count = sum(1 for r in results if r.get("decision") == "HALT")

        latencies = sorted(r.get("latency_ms", 0.0) for r in results)
        avg_latency = sum(latencies) / total
        p99_idx = min(int(total * 0.99), total - 1)
        p99_latency = latencies[p99_idx]

        scores = [r.get("score", 0.0) for r in results if isinstance(r.get("score"), (int, float))]
        avg_score = sum(scores) / max(1, len(scores))

        # Consensus resolution: consensus valid if >= 80% pass rate
        consensus_valid = (passed / total) >= 0.80

        # Cryptographic batch audit hash
        receipts = "".join(str(r.get("receipt_hash", "")) for r in results)
        audit_hash = hashlib.sha256(f"{batch_id}:{total}:{passed}:{receipts}".encode()).hexdigest()

        report = AggregatedBatchReport(
            batch_id=batch_id,
            total_validations=total,
            passed_validations=passed,
            rejected_validations=rejected,
            halt_count=halt_count,
            recurse_count=recurse_count,
            accept_count=accept_count,
            avg_latency_ms=round(avg_latency, 4),
            p99_latency_ms=round(p99_latency, 4),
            avg_stability_score=round(avg_score, 4),
            consensus_valid=consensus_valid,
            audit_hash=audit_hash,
            results=results
        )

        self.history.append({
            "batch_id": batch_id,
            "timestamp": time.time(),
            "total": total,
            "passed": passed,
            "audit_hash": audit_hash
        })
        return report

    def resolve_conflicts(self, multi_worker_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolves differing opinions on the same payload across multiple workers."""
        if not multi_worker_results:
            return {"decision": "HALT", "consensus_score": 0.0, "conflict": True}

        decisions = [r.get("decision", "HALT") for r in multi_worker_results]
        scores = [r.get("score", 0.0) for r in multi_worker_results]
        
        # Majority vote
        counts = {"ACCEPT": decisions.count("ACCEPT"), "RECURSE": decisions.count("RECURSE"), "HALT": decisions.count("HALT")}
        majority_decision = max(counts, key=counts.get)
        avg_score = sum(scores) / len(scores)

        is_conflict = len(set(decisions)) > 1
        return {
            "decision": majority_decision,
            "consensus_score": round(avg_score, 4),
            "vote_distribution": counts,
            "conflict_detected": is_conflict,
            "unanimous": not is_conflict
        }
