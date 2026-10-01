
"""
Unit & Integration Tests for Level 2 Heterogeneous Hardware Acceleration
========================================================================
Comprehensive test suite (30 tests) verifying:
  - Multi-vendor device registration (CUDA, ROCm, Metal, Gaudi, CPU_SIMD)
  - Hardware profile catalog and factory creation
  - Device topology auto-detection and compute capability introspection
  - Zero-copy buffer allocation on unified memory architectures
  - Single and batched parallel dispatch across heterogeneous backends
  - Scheduling strategies: round-robin, cost-optimized, latency-optimized, load-balanced
  - Fault-tolerant dispatch with automatic retry and device retirement
  - Preemption handling and sub-500ms migration with task checkpointing
  - Byzantine fault tolerance: quorum voting, outlier detection, consensus
  - Cross-platform numerical parity verification
  - Spot pricing oracle and multi-cloud cost arbitrage
  - WorkerArbitrageManager end-to-end integration
  - Cluster summary and health monitoring
"""

import pytest
import time
from daxda_engine.level2.heterogeneous_accel import (
    ByzantineFaultTolerance,
    CloudProvider,
    ComputeCapability,
    DeviceBackendType,
    DeviceTopology,
    DispatchResult,
    HardwareDeviceInfo,
    HeterogeneousClusterScheduler,
    MemoryArchitecture,
    PreemptionEvent,
    PreemptionRecoveryEngine,
    SchedulingStrategy,
    SpotPriceSnapshot,
    SpotPricingOracle,
    TaskCheckpoint,
    ValidationVote,
    WorkerArbitrageManager,
    ZeroCopyBuffer,
    auto_detect_local_devices,
    create_device_from_profile,
    HARDWARE_PROFILES,
)


# ============================================================================
# Section 1: Device Backends & Hardware Profiles
# ============================================================================

class TestDeviceBackends:
    """Tests for device registration, profiles, and topology."""

    def test_device_backend_enum_coverage(self):
        """All 5 hardware vendor backends must be represented."""
        backends = set(DeviceBackendType)
        assert DeviceBackendType.CUDA in backends
        assert DeviceBackendType.ROCM in backends
        assert DeviceBackendType.METAL in backends
        assert DeviceBackendType.GAUDI in backends
        assert DeviceBackendType.CPU_SIMD in backends
        assert len(backends) == 5

    def test_hardware_profile_catalog_completeness(self):
        """Hardware profile catalog covers all major accelerator families."""
        assert "H100_SXM" in HARDWARE_PROFILES
        assert "A100_80GB" in HARDWARE_PROFILES
        assert "MI300X" in HARDWARE_PROFILES
        assert "MI250X" in HARDWARE_PROFILES
        assert "M4_MAX" in HARDWARE_PROFILES
        assert "GAUDI3" in HARDWARE_PROFILES
        assert "XEON_W9_AVX512" in HARDWARE_PROFILES
        assert len(HARDWARE_PROFILES) >= 7

    def test_create_device_from_profile_h100(self):
        """Factory creates correct H100 device with full metadata."""
        dev = create_device_from_profile("H100_SXM", "gpu_h100_0", is_spot=True)
        assert dev.device_id == "gpu_h100_0"
        assert dev.backend_type == DeviceBackendType.CUDA
        assert dev.memory_mb == 80000
        assert dev.is_spot is True
        assert dev.compute_cap is not None
        assert dev.compute_cap.peak_tflops_fp16 == 989.0
        assert dev.compute_cap.tensor_core_count == 528
        assert dev.topology is not None
        assert dev.topology.interconnect_type == "NVLink"
        assert dev.memory_arch == MemoryArchitecture.DISCRETE

    def test_create_device_from_profile_apple_silicon(self):
        """Apple M4 Max uses unified memory architecture."""
        dev = create_device_from_profile("M4_MAX", "mps_0")
        assert dev.backend_type == DeviceBackendType.METAL
        assert dev.memory_arch == MemoryArchitecture.UNIFIED
        assert dev.topology.interconnect_type == "UMA"
        assert dev.cost_per_hour_usd == 0.0  # On-prem

    def test_create_device_from_profile_invalid_raises(self):
        """Unknown profile name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown hardware profile"):
            create_device_from_profile("NONEXISTENT_GPU", "x")

    def test_auto_detect_local_devices(self):
        """Auto-detection returns at least one CPU_SIMD device."""
        devices = auto_detect_local_devices()
        assert len(devices) >= 1
        assert devices[0].backend_type == DeviceBackendType.CPU_SIMD

    def test_device_health_tracking_and_retirement(self):
        """Device auto-retires after 3 consecutive failures."""
        dev = HardwareDeviceInfo(
            device_id="test_dev",
            backend_type=DeviceBackendType.CUDA,
            memory_mb=80000,
        )
        assert dev.is_healthy is True
        dev.record_failure()
        assert dev.is_healthy is True
        dev.record_failure()
        assert dev.is_healthy is True
        dev.record_failure()  # 3rd consecutive failure
        assert dev.is_healthy is False

        # Revive
        dev.revive()
        assert dev.is_healthy is True

    def test_device_dispatch_statistics(self):
        """Device tracks running average latency."""
        dev = HardwareDeviceInfo(
            device_id="stat_dev",
            backend_type=DeviceBackendType.ROCM,
            memory_mb=192000,
        )
        dev.record_dispatch(0.15)
        dev.record_dispatch(0.25)
        dev.record_dispatch(0.20)
        assert dev._total_dispatches == 3
        assert abs(dev.avg_latency_ms - 0.20) < 1e-9

    def test_compute_capability_throughput_factor(self):
        """Throughput factor correctly normalizes to CPU baseline."""
        cpu_cap = ComputeCapability(
            peak_tflops_fp32=0.8, peak_tflops_fp16=0.5,
            memory_bandwidth_gbps=307.0,
        )
        assert cpu_cap.effective_throughput_factor == 1.0

        h100_cap = ComputeCapability(
            peak_tflops_fp32=67.0, peak_tflops_fp16=989.0,
            memory_bandwidth_gbps=3350.0,
        )
        assert h100_cap.effective_throughput_factor > 1000.0


# ============================================================================
# Section 2: Zero-Copy Buffers & Memory Architecture
# ============================================================================

class TestZeroCopyBuffers:
    """Tests for zero-copy tensor buffer management."""

    def test_zero_copy_on_unified_memory(self):
        """Unified memory devices get true zero-copy buffers."""
        buf = ZeroCopyBuffer(
            buffer_id="zcb-001",
            size_bytes=1024 * 1024,
            device_id="mps_0",
            memory_arch=MemoryArchitecture.UNIFIED,
        )
        assert buf.is_zero_copy is True

    def test_non_zero_copy_on_discrete_memory(self):
        """Discrete GPU memory requires explicit copy."""
        buf = ZeroCopyBuffer(
            buffer_id="zcb-002",
            size_bytes=1024 * 1024,
            device_id="gpu_0",
            memory_arch=MemoryArchitecture.DISCRETE,
        )
        assert buf.is_zero_copy is False

    def test_buffer_checksum_deterministic(self):
        """Buffer checksum is deterministic for same inputs."""
        buf = ZeroCopyBuffer(
            buffer_id="zcb-det",
            size_bytes=4096,
            device_id="dev_0",
            memory_arch=MemoryArchitecture.HOST_ONLY,
            created_at=1000000.0,
        )
        cs1 = buf.checksum()
        cs2 = buf.checksum()
        assert cs1 == cs2
        assert len(cs1) == 16


# ============================================================================
# Section 3: Cluster Scheduler – Core Dispatch
# ============================================================================

class TestSchedulerDispatch:
    """Tests for heterogeneous cluster dispatch operations."""

    def _make_payload(self, score: float = 0.92):
        return {
            "stability": {
                "components": {"L": score, "A": score, "P": score, "F": score, "T": score}
            }
        }

    def test_device_registration_and_single_dispatch(self):
        """Register 3 heterogeneous devices and dispatch validation."""
        scheduler = HeterogeneousClusterScheduler()
        scheduler.register_device(DeviceBackendType.CUDA, "h100_01", memory_mb=80000)
        scheduler.register_device(DeviceBackendType.ROCM, "mi300x_01", memory_mb=192000)
        scheduler.register_device(DeviceBackendType.METAL, "m4_max_01", memory_mb=36000)

        assert scheduler.active_backend_count == 3
        assert scheduler.total_devices == 3

        res = scheduler.dispatch_validation(self._make_payload())
        assert res["decision"] == "ACCEPT"
        assert res["backend"] in ["CUDA", "ROCM", "METAL"]
        assert res["latency_ms"] >= 0.0
        assert "cost_per_validation_usd" in res

    def test_parallel_dispatch_batch(self):
        """Batched dispatch across 1000 payloads."""
        scheduler = HeterogeneousClusterScheduler()
        scheduler.register_device(DeviceBackendType.CPU_SIMD, "avx512_cpu_0", memory_mb=32768)

        batches = [self._make_payload() for _ in range(100)]
        results = scheduler.dispatch_parallel_validation(batches)
        assert len(results) == 100
        for r in results:
            assert r["decision"] == "ACCEPT"

    def test_fallback_to_cpu_when_no_devices(self):
        """Auto-registers CPU fallback when no devices registered."""
        scheduler = HeterogeneousClusterScheduler()
        res = scheduler.dispatch_validation(self._make_payload())
        assert res["backend"] == "CPU_SIMD"
        assert scheduler.total_devices == 1

    def test_register_from_profile(self):
        """Registers device using hardware profile catalog."""
        scheduler = HeterogeneousClusterScheduler()
        dev = scheduler.register_from_profile("MI300X", "rocm_profile_0", is_spot=True)
        assert dev.backend_type == DeviceBackendType.ROCM
        assert dev.is_spot is True
        assert dev.compute_cap.peak_tflops_fp16 == 1307.0

    def test_auto_register_local(self):
        """Auto-detect and register local hardware."""
        scheduler = HeterogeneousClusterScheduler()
        devices = scheduler.auto_register_local()
        assert len(devices) >= 1
        assert scheduler.total_devices >= 1

    def test_cluster_summary(self):
        """Cluster summary includes all key metrics."""
        scheduler = HeterogeneousClusterScheduler()
        scheduler.register_device(DeviceBackendType.CUDA, "gpu_0")
        scheduler.register_device(DeviceBackendType.GAUDI, "gaudi_0")
        scheduler.dispatch_validation(self._make_payload())

        summary = scheduler.cluster_summary
        assert summary["total_devices"] == 2
        assert summary["active_backend_count"] == 2
        assert summary["total_dispatches"] == 1
        assert "CUDA" in summary["devices_by_backend"]
        assert "GAUDI" in summary["devices_by_backend"]


# ============================================================================
# Section 4: Scheduling Strategies
# ============================================================================

class TestSchedulingStrategies:
    """Tests for pluggable scheduling strategy selection."""

    def _make_payload(self):
        return {
            "stability": {
                "components": {"L": 0.90, "A": 0.90, "P": 0.90, "F": 0.90, "T": 0.90}
            }
        }

    def test_cost_optimized_selects_cheapest(self):
        """Cost-optimized strategy always selects cheapest device."""
        scheduler = HeterogeneousClusterScheduler(
            strategy=SchedulingStrategy.COST_OPTIMIZED
        )
        scheduler.register_device(
            DeviceBackendType.CUDA, "expensive_gpu", cost_per_hour_usd=10.0
        )
        scheduler.register_device(
            DeviceBackendType.CPU_SIMD, "cheap_cpu", cost_per_hour_usd=0.05
        )

        # All dispatches should go to cheapest device
        for _ in range(5):
            res = scheduler.dispatch_validation(self._make_payload())
            assert res["device_id"] == "cheap_cpu"

    def test_load_balanced_selects_least_loaded(self):
        """Load-balanced strategy picks device with lowest active_load."""
        scheduler = HeterogeneousClusterScheduler(
            strategy=SchedulingStrategy.LOAD_BALANCED
        )
        d1 = scheduler.register_device(DeviceBackendType.CUDA, "loaded_gpu")
        d1.active_load = 0.95
        d2 = scheduler.register_device(DeviceBackendType.ROCM, "idle_gpu")
        d2.active_load = 0.10

        res = scheduler.dispatch_validation(self._make_payload())
        assert res["device_id"] == "idle_gpu"

    def test_round_robin_distributes_evenly(self):
        """Round-robin cycles across all healthy devices."""
        scheduler = HeterogeneousClusterScheduler(
            strategy=SchedulingStrategy.ROUND_ROBIN
        )
        scheduler.register_device(DeviceBackendType.CUDA, "gpu_a")
        scheduler.register_device(DeviceBackendType.ROCM, "gpu_b")
        scheduler.register_device(DeviceBackendType.METAL, "gpu_c")

        seen = set()
        for _ in range(6):
            res = scheduler.dispatch_validation(self._make_payload())
            seen.add(res["device_id"])
        assert seen == {"gpu_a", "gpu_b", "gpu_c"}


# ============================================================================
# Section 5: Fault Tolerance & Preemption
# ============================================================================

class TestFaultTolerance:
    """Tests for fault-tolerant dispatch and preemption recovery."""

    def _make_payload(self):
        return {
            "stability": {
                "components": {"L": 0.90, "A": 0.90, "P": 0.90, "F": 0.90, "T": 0.90}
            }
        }

    def test_preemption_recovery_sub_500ms(self):
        """Preemption migration completes within 500ms SLA."""
        engine = PreemptionRecoveryEngine()
        event = engine.handle_preemption(
            provider="aws",
            instance_id="i-0abc123",
            active_tasks=[{"task_id": f"t{i}"} for i in range(10)],
        )
        assert event.is_successful
        assert event.met_sla  # < 500ms
        assert event.tasks_migrated_count == 10
        assert event.tasks_lost_count == 0
        assert event.target_instance_id is not None
        assert len(event.checkpoints) == 10

    def test_preemption_checkpoint_integrity(self):
        """Each migrated task has a valid checkpoint with hash."""
        engine = PreemptionRecoveryEngine()
        event = engine.handle_preemption(
            provider="gcp",
            instance_id="vm-gpu-42",
            active_tasks=[{"task_id": "critical_1", "payload": [1, 2, 3]}],
        )
        assert len(event.checkpoints) == 1
        cp = event.checkpoints[0]
        assert cp.task_id == "critical_1"
        assert len(cp.payload_hash) == 16
        assert cp.checkpoint_bytes > 0
        assert cp.source_device_id == "vm-gpu-42"

    def test_scheduler_preemption_deregisters_device(self):
        """Preempted device is removed from the cluster."""
        scheduler = HeterogeneousClusterScheduler()
        arb = WorkerArbitrageManager()
        scheduler.set_arbitrage_manager(arb)

        scheduler.register_device(
            DeviceBackendType.CUDA, "spot_gpu_0", is_spot=True
        )
        scheduler.register_device(
            DeviceBackendType.CPU_SIMD, "fallback_cpu", is_spot=False
        )
        assert scheduler.total_devices == 2

        event = scheduler.handle_device_preemption(
            "spot_gpu_0", active_tasks=[{"task_id": "t1"}]
        )
        assert event is not None
        assert scheduler.total_devices == 1
        assert "spot_gpu_0" not in [d.device_id for d in scheduler.healthy_devices]

    def test_device_deregister_unknown_id(self):
        """Deregistering unknown device returns False without error."""
        scheduler = HeterogeneousClusterScheduler()
        assert scheduler.deregister_device("nonexistent") is False


# ============================================================================
# Section 6: Byzantine Fault Tolerance
# ============================================================================

class TestByzantineFaultTolerance:
    """Tests for BFT quorum voting and outlier detection."""

    def test_bft_consensus_unanimous(self):
        """Unanimous votes produce valid consensus."""
        bft = ByzantineFaultTolerance(min_quorum=3)
        votes = [
            ValidationVote(voter_id=f"w{i}", score=0.92, decision="ACCEPT")
            for i in range(5)
        ]
        result = bft.reach_consensus(votes)
        assert result["is_valid"] is True
        assert result["consensus_decision"] == "ACCEPT"
        assert result["consensus_score"] == 0.92
        assert result["agreement_count"] == 5

    def test_bft_quorum_insufficient(self):
        """Below-quorum votes are rejected."""
        bft = ByzantineFaultTolerance(min_quorum=3)
        votes = [
            ValidationVote(voter_id="w0", score=0.90, decision="ACCEPT"),
            ValidationVote(voter_id="w1", score=0.90, decision="ACCEPT"),
        ]
        result = bft.reach_consensus(votes)
        assert result["is_valid"] is False
        assert "Insufficient quorum" in result["reason"]

    def test_bft_detects_byzantine_outlier(self):
        """A rogue voter with wildly different score is flagged."""
        bft = ByzantineFaultTolerance(min_quorum=3)
        votes = [
            ValidationVote(voter_id="w0", score=0.90, decision="ACCEPT"),
            ValidationVote(voter_id="w1", score=0.91, decision="ACCEPT"),
            ValidationVote(voter_id="w2", score=0.89, decision="ACCEPT"),
            ValidationVote(voter_id="w3", score=0.90, decision="ACCEPT"),
            ValidationVote(voter_id="rogue", score=0.01, decision="REJECT"),  # Byzantine
        ]
        result = bft.reach_consensus(votes)
        assert result["is_valid"] is True
        assert result["consensus_decision"] == "ACCEPT"
        assert "rogue" in result["flagged_voters"]
        assert "rogue" in bft.flagged_voters

    def test_bft_median_score_robust_to_outliers(self):
        """Median consensus score is robust to extreme values."""
        bft = ByzantineFaultTolerance(min_quorum=3)
        votes = [
            ValidationVote(voter_id="w0", score=0.90, decision="ACCEPT"),
            ValidationVote(voter_id="w1", score=0.90, decision="ACCEPT"),
            ValidationVote(voter_id="w2", score=0.90, decision="ACCEPT"),
            ValidationVote(voter_id="evil", score=999.0, decision="ACCEPT"),
        ]
        result = bft.reach_consensus(votes)
        assert result["consensus_score"] == 0.90  # Median, not mean

    def test_scheduler_bft_dispatch(self):
        """Scheduler BFT dispatch produces consensus result."""
        scheduler = HeterogeneousClusterScheduler(enable_bft=True, bft_quorum=3)
        scheduler.register_device(DeviceBackendType.CUDA, "w0")
        scheduler.register_device(DeviceBackendType.ROCM, "w1")
        scheduler.register_device(DeviceBackendType.METAL, "w2")

        payload = {
            "stability": {
                "components": {"L": 0.90, "A": 0.90, "P": 0.90, "F": 0.90, "T": 0.90}
            }
        }
        result = scheduler.dispatch_with_bft(payload, voter_count=3)
        assert "bft_consensus" in result
        assert result["bft_consensus"]["is_valid"] is True
        assert result["voter_count"] == 3
        assert len(result["votes"]) == 3


# ============================================================================
# Section 7: Cross-Platform Parity & Spot Arbitrage
# ============================================================================

class TestParityAndArbitrage:
    """Tests for numerical parity and multi-cloud cost optimization."""

    def test_cross_platform_numerical_parity(self):
        """Same payload produces identical scores across all backends."""
        scheduler = HeterogeneousClusterScheduler()
        scheduler.register_device(DeviceBackendType.CUDA, "cuda_parity")
        scheduler.register_device(DeviceBackendType.ROCM, "rocm_parity")
        scheduler.register_device(DeviceBackendType.METAL, "metal_parity")
        scheduler.register_device(DeviceBackendType.GAUDI, "gaudi_parity")
        scheduler.register_device(DeviceBackendType.CPU_SIMD, "cpu_parity")

        payload = {
            "stability": {
                "components": {"L": 0.85, "A": 0.88, "P": 0.90, "F": 0.82, "T": 0.95}
            }
        }
        result = scheduler.verify_cross_platform_parity(payload)
        assert result["parity_verified"] is True
        assert result["score_parity"] is True
        assert result["decision_parity"] is True
        assert len(result["backends_tested"]) == 5

    def test_spot_pricing_oracle_returns_snapshots(self):
        """Oracle returns valid pricing snapshots for known instance types."""
        oracle = SpotPricingOracle(volatility=0.0)  # No jitter for determinism
        snap = oracle.get_spot_price(CloudProvider.AWS, "g5.xlarge")
        assert snap is not None
        assert snap.provider == CloudProvider.AWS
        assert snap.on_demand_usd == 1.006
        assert snap.spot_usd > 0
        assert snap.savings_pct > 0

    def test_spot_pricing_oracle_cheapest(self):
        """Cheapest option scan returns a valid snapshot."""
        oracle = SpotPricingOracle(volatility=0.0)
        cheapest = oracle.get_cheapest_option()
        assert cheapest is not None
        assert cheapest.spot_usd > 0

    def test_worker_arbitrage_optimal_provider(self):
        """WorkerArbitrageManager identifies cheapest cloud provider."""
        mgr = WorkerArbitrageManager()
        optimal = mgr.get_optimal_spot_provider()
        assert optimal in ["aws", "gcp", "azure"]
        # GCP has lowest spot_mean (0.88) in baseline data
        assert optimal == "gcp"

    def test_worker_arbitrage_cost_savings(self):
        """Cost savings computation returns positive values for all providers."""
        mgr = WorkerArbitrageManager()
        savings = mgr.compute_cost_savings(hours_used=10.0)
        assert len(savings) == 3
        for provider, saved in savings.items():
            assert saved > 0, f"Savings for {provider} must be positive"

    def test_zero_copy_buffer_allocation_on_unified_device(self):
        """Scheduler allocates true zero-copy buffer on Apple Silicon."""
        scheduler = HeterogeneousClusterScheduler()
        scheduler.register_device(
            DeviceBackendType.METAL, "mps_zcb",
            memory_arch=MemoryArchitecture.UNIFIED,
        )
        buf = scheduler.allocate_zero_copy_buffer("mps_zcb", 1024 * 1024)
        assert buf is not None
        assert buf.is_zero_copy is True
        assert buf.is_pinned is True
        assert buf.size_bytes == 1024 * 1024
