"""
Unit & Integration Tests: DA13 Workers, Task Queue & Result Aggregator
=====================================================================
"""

import pytest
from da13_validator.workers import (
    DistributedTaskQueue,
    PriorityLevel,
    GPUValidationWorker,
    CPUValidationWorker,
    ResultAggregator
)


class TestDA13Workers:
    """Tests for task queue prioritization, GPU/CPU validation, and result aggregation."""

    def test_priority_task_queue(self):
        queue = DistributedTaskQueue(max_depth=100)
        assert queue.is_empty()

        # Enqueue in reverse priority order
        t_low = queue.enqueue({"msg": "low"}, priority=PriorityLevel.LOW)
        t_med = queue.enqueue({"msg": "medium"}, priority=PriorityLevel.MEDIUM)
        t_crit = queue.enqueue({"msg": "critical"}, priority=PriorityLevel.CRITICAL)
        t_high = queue.enqueue({"msg": "high"}, priority=PriorityLevel.HIGH)

        assert queue.depth() == 4
        assert not queue.is_empty()

        # Dequeue must return CRITICAL first, then HIGH, then MEDIUM, then LOW
        first = queue.dequeue()
        assert first.priority == PriorityLevel.CRITICAL
        assert first.payload["msg"] == "critical"

        second = queue.dequeue()
        assert second.priority == PriorityLevel.HIGH

        third = queue.dequeue()
        assert third.priority == PriorityLevel.MEDIUM

        fourth = queue.dequeue()
        assert fourth.priority == PriorityLevel.LOW

        assert queue.is_empty()

    def test_task_queue_batch_dequeue(self):
        queue = DistributedTaskQueue()
        for i in range(25):
            queue.enqueue({"id": i}, priority=PriorityLevel.MEDIUM)

        batch = queue.dequeue_batch(max_batch_size=10)
        assert len(batch) == 10
        assert queue.depth() == 15

    def test_gpu_worker_validation_and_batch(self):
        worker = GPUValidationWorker(worker_id="gpu-test-0", gpu_id=0)
        assert worker.ping() >= 0.0

        sample_payload = {
            "meta": {"current_iteration": 1, "max_iterations": 5},
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {
                    "L": {"value": 0.90},
                    "A": {"value": 0.85},
                    "P": {"value": 0.80},
                    "F": {"value": 0.85},
                    "T": {"value": 0.95}
                }
            }
        }

        res = worker.validate(sample_payload)
        assert res["worker_id"] == "gpu-test-0"
        assert res["is_valid"] is True
        assert res["decision"] == "ACCEPT"
        assert res["score"] > 0.75
        assert res["latency_ms"] < 1000.0  # sub-second SLA

        # Batch validation
        batch_res = worker.batch_validate([sample_payload] * 10)
        assert len(batch_res) == 10
        assert all(r["is_valid"] for r in batch_res)

    def test_cpu_worker_validation(self):
        cpu_worker = CPUValidationWorker(worker_id="cpu-test-0")
        assert cpu_worker.ping() >= 0.0

        sample_payload = {
            "meta": {"current_iteration": 1, "max_iterations": 5},
            "stability": {
                "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
                "components": {"L": 0.9, "A": 0.8, "P": 0.8, "F": 0.8, "T": 0.8}
            }
        }
        res = cpu_worker.validate(sample_payload)
        assert res["worker_id"] == "cpu-test-0"
        assert res["decision"] == "ACCEPT"

    def test_result_aggregator_and_conflict_resolution(self):
        aggregator = ResultAggregator()

        mock_results = [
            {"worker_id": "w-0", "is_valid": True, "decision": "ACCEPT", "score": 0.85, "latency_ms": 10.0, "receipt_hash": "h1"},
            {"worker_id": "w-1", "is_valid": True, "decision": "ACCEPT", "score": 0.86, "latency_ms": 15.0, "receipt_hash": "h2"},
            {"worker_id": "w-2", "is_valid": False, "decision": "RECURSE", "score": 0.65, "latency_ms": 20.0, "receipt_hash": "h3"},
        ]

        report = aggregator.aggregate_results(batch_id="batch-001", results=mock_results)
        assert report.total_validations == 3
        assert report.passed_validations == 2
        assert report.rejected_validations == 1
        assert report.accept_count == 2
        assert report.recurse_count == 1
        assert report.consensus_valid is False  # 2/3 = 66.7% < 80%

        # Conflict resolution test
        conflict_res = aggregator.resolve_conflicts(mock_results)
        assert conflict_res["decision"] == "ACCEPT"
        assert conflict_res["conflict_detected"] is True
        assert conflict_res["vote_distribution"]["ACCEPT"] == 2
