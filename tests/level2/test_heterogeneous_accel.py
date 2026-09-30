"""
Unit & Integration Tests for Level 2 Heterogeneous Hardware Acceleration
========================================================================
"""

import pytest
from daxda_engine.level2.heterogeneous_accel import (
    DeviceBackendType,
    HeterogeneousClusterScheduler,
    WorkerArbitrageManager,
)


def test_heterogeneous_device_registration_and_dispatch():
    scheduler = HeterogeneousClusterScheduler()
    scheduler.register_device(DeviceBackendType.CUDA, "h100_01", memory_mb=80000)
    scheduler.register_device(DeviceBackendType.ROCM, "mi300x_01", memory_mb=192000)
    scheduler.register_device(DeviceBackendType.METAL, "m4_max_01", memory_mb=36000)

    assert scheduler.active_backend_count == 3

    payload = {
        "stability": {
            "components": {"L": 0.95, "A": 0.92, "P": 0.90, "F": 0.88, "T": 0.95}
        }
    }

    res = scheduler.dispatch_validation(payload)
    assert res["decision"] == "ACCEPT"
    assert res["backend"] in [DeviceBackendType.CUDA.value, DeviceBackendType.ROCM.value, DeviceBackendType.METAL.value]
    assert res["latency_ms"] >= 0.0


def test_heterogeneous_parallel_dispatch():
    scheduler = HeterogeneousClusterScheduler()
    scheduler.register_device(DeviceBackendType.CPU_SIMD, "avx512_cpu_0", memory_mb=32768)

    batches = [
        {"stability": {"components": {"L": 0.9, "A": 0.9, "P": 0.9, "F": 0.9, "T": 0.9}}}
        for _ in range(10)
    ]
    results = scheduler.dispatch_parallel_validation(batches)
    assert len(results) == 10
    for r in results:
        assert r["decision"] == "ACCEPT"


def test_worker_arbitrage_preemption_handling():
    manager = WorkerArbitrageManager()
    optimal = manager.get_optimal_spot_provider()
    assert optimal in ["aws", "gcp", "azure"]

    event = manager.handle_preemption_warning(
        provider="aws",
        instance_id="i-0abcd1234ef",
        active_tasks=[{"task_id": "t1"}, {"task_id": "t2"}],
    )
    assert event.event_id.startswith("PREEMPT-AWS")
    assert event.tasks_migrated_count == 2
    assert event.migration_completed_at is not None
