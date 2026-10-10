r"""
Tests for TPU Pod XLA Orchestration Engine.
Verifies 2D toroidal mesh interconnect modeling, automated SPMD sharding,
XLA HLO IR generation, and sub-15ms P99 cluster latency.
"""

import numpy as np
import pytest

from daxda_engine.level3.tpu_xla_orchestrator import (
    TPU2DTorusMesh,
    CollectiveCommunicationResult,
    PartitionSpec,
    ShardGeometry,
    SPMDShardingOrchestrator,
    HLOExecutionProfile,
    XLAHLOCompiler,
)


def test_2d_torus_distance_and_wrap_around():
    r"""Verify shortest path distance on 16x16 2D torus with wrap-around boundaries."""
    mesh = TPU2DTorusMesh(mesh_shape=(16, 16))

    assert mesh.total_chips == 256
    assert mesh.max_torus_diameter() == 16  # 8 + 8

    # Chip (0, 0) and Chip (15, 0) are adjacent across boundary (distance 1)
    chip_0 = 0
    chip_15 = 15
    assert mesh.torus_distance(chip_0, chip_15) == 1

    # Chip (0, 0) and Chip (0, 15) are adjacent across vertical boundary (distance 1)
    chip_vertical = 15 * 16  # (0, 15)
    assert mesh.torus_distance(chip_0, chip_vertical) == 1

    # Opposite corner (8, 8)
    chip_diag = 8 + 8 * 16
    assert mesh.torus_distance(chip_0, chip_diag) == 16


def test_torus_all_reduce_latency_and_bandwidth():
    r"""Verify ring all-reduce on 256 TPU chips meets sub-15ms P99 latency target."""
    mesh = TPU2DTorusMesh(mesh_shape=(16, 16))

    # 16 MB gradient payload
    payload_bytes = 16 * 1024 * 1024
    res: CollectiveCommunicationResult = mesh.simulate_ring_all_reduce(payload_bytes)

    assert res.operation_name == "Ring All-Reduce"
    assert res.meets_15ms_p99_target is True
    assert res.collective_latency_ms < 5.0  # Typically < 1 ms on optical mesh


def test_spmd_partition_spec_and_sharding():
    r"""Verify automated SPMD sharding splits global tensors correctly across 2D mesh."""
    # 4x4 mesh (16 chips) for testing
    orchestrator = SPMDShardingOrchestrator(mesh_shape=(4, 4), axis_names=("data", "model"))

    global_data = np.arange(64 * 32, dtype=np.float32).reshape((64, 32))
    spec = PartitionSpec(dim_partitions=("data", "model"))

    shards = orchestrator.shard_tensor(global_data, spec)
    assert len(shards) == 16

    # Each shard should have shape (64/4, 32/4) = (16, 8)
    for shard in shards:
        assert shard.shape == (16, 8)

    # Reconstruct from shards
    reconstructed = np.zeros_like(global_data)
    for chip_id, shard in enumerate(shards):
        geom = orchestrator.compute_shard_geometry(global_data.shape, spec, chip_id)
        idx = tuple(slice(s[0], s[1]) for s in geom.slice_ranges)
        reconstructed[idx] = shard

    assert np.array_equal(reconstructed, global_data)


def test_xla_hlo_ir_generation_and_profiling():
    r"""Verify XLA HLO textual IR generation and sub-15ms cluster P99 execution profiling."""
    compiler = XLAHLOCompiler(num_chips=256, mesh_shape=(16, 16))

    hlo_text = compiler.generate_hlo_ir(
        module_name="daxda_verify",
        batch_size=4096,
        hidden_dim=2048,
    )

    assert "HloModule daxda_verify" in hlo_text
    assert "all-reduce" in hlo_text
    assert "dot" in hlo_text

    profile: HLOExecutionProfile = compiler.profile_kernel_execution(
        batch_size=4096,
        hidden_dim=2048,
    )

    assert profile.total_gflops > 0.0
    assert profile.computation_time_ms > 0.0
    assert profile.p99_latency_ms < 15.0
    assert profile.meets_15ms_p99_target is True
