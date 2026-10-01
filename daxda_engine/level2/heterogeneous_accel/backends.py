"""
DAXDA Level 2 - Heterogeneous Hardware Device Backends
======================================================

Enterprise-grade multi-vendor accelerator abstraction:
  - NVIDIA CUDA (H100/A100 Tensor Cores)
  - AMD ROCm / HIP (MI300X/MI250 CDNA Matrix Cores)
  - Apple Silicon Metal (M3/M4 Max MPS Graph)
  - Intel Gaudi / oneAPI (HPU Matrix Engines)
  - Host CPU SIMD (AVX-512 / ARM NEON)

Features:
  - Dynamic device topology auto-detection
  - Zero-copy tensor buffers on unified memory architectures
  - Compute capability fingerprinting
  - Health monitoring and automatic retirement
"""

from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class DeviceBackendType(str, Enum):
    CUDA = "CUDA"
    ROCM = "ROCM"
    METAL = "METAL"
    GAUDI = "GAUDI"
    CPU_SIMD = "CPU_SIMD"


class MemoryArchitecture(str, Enum):
    """Memory hierarchy type for zero-copy optimization decisions."""
    DISCRETE = "DISCRETE"        # Separate GPU VRAM (PCIe copy required)
    UNIFIED = "UNIFIED"          # Unified memory (Apple M-series, Grace Hopper)
    HOST_ONLY = "HOST_ONLY"      # CPU-only system memory


@dataclass
class ComputeCapability:
    """Hardware compute capability fingerprint."""
    peak_tflops_fp32: float
    peak_tflops_fp16: float
    memory_bandwidth_gbps: float
    tensor_core_count: int = 0
    matrix_engine_count: int = 0
    simd_width_bits: int = 0
    max_concurrent_kernels: int = 1

    @property
    def effective_throughput_factor(self) -> float:
        """Normalized throughput factor relative to baseline CPU SIMD."""
        return max(1.0, self.peak_tflops_fp16 / 0.5)  # Normalized to ~0.5 TFLOPS baseline


@dataclass
class DeviceTopology:
    """Auto-detected device topology and interconnect information."""
    numa_node: int = 0
    pcie_gen: int = 4
    pcie_lanes: int = 16
    interconnect_type: str = "PCIe"        # PCIe, NVLink, Infinity Fabric, UMA
    interconnect_bandwidth_gbps: float = 32.0
    peer_device_ids: List[str] = field(default_factory=list)
    geographic_zone: str = "us-east1-a"

    @property
    def is_nvlink(self) -> bool:
        return self.interconnect_type == "NVLink"


@dataclass
class ZeroCopyBuffer:
    """Represents a zero-copy tensor buffer for unified memory architectures."""
    buffer_id: str
    size_bytes: int
    device_id: str
    memory_arch: MemoryArchitecture
    is_pinned: bool = False
    ref_count: int = 1
    created_at: float = field(default_factory=time.time)

    @property
    def is_zero_copy(self) -> bool:
        return self.memory_arch == MemoryArchitecture.UNIFIED

    def checksum(self) -> str:
        payload = f"{self.buffer_id}:{self.size_bytes}:{self.device_id}:{self.created_at}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass
class HardwareDeviceInfo:
    """Core device descriptor for the heterogeneous cluster."""
    device_id: str
    backend_type: DeviceBackendType
    memory_mb: int
    is_spot: bool = False
    cost_per_hour_usd: float = 0.50
    active_load: float = 0.0  # [0.0, 1.0]
    is_healthy: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Extended fields
    compute_cap: Optional[ComputeCapability] = None
    topology: Optional[DeviceTopology] = None
    memory_arch: MemoryArchitecture = MemoryArchitecture.DISCRETE
    _consecutive_failures: int = field(default=0, repr=False)
    _total_dispatches: int = field(default=0, repr=False)
    _total_latency_ms: float = field(default=0.0, repr=False)

    @property
    def avg_latency_ms(self) -> float:
        if self._total_dispatches == 0:
            return 0.0
        return self._total_latency_ms / self._total_dispatches

    @property
    def utilization_pct(self) -> float:
        return round(self.active_load * 100.0, 2)

    def record_dispatch(self, latency_ms: float) -> None:
        """Records a completed dispatch for running statistics."""
        self._total_dispatches += 1
        self._total_latency_ms += latency_ms
        self._consecutive_failures = 0

    def record_failure(self) -> None:
        """Records a failed dispatch and auto-retires after 3 consecutive failures."""
        self._consecutive_failures += 1
        if self._consecutive_failures >= 3:
            self.is_healthy = False

    def revive(self) -> None:
        """Revives a retired device after maintenance."""
        self.is_healthy = True
        self._consecutive_failures = 0


# ============================================================================
# Hardware Profile Catalog (simulation / mock backends)
# ============================================================================

HARDWARE_PROFILES: Dict[str, Dict[str, Any]] = {
    # NVIDIA
    "H100_SXM": {
        "backend": DeviceBackendType.CUDA,
        "memory_mb": 80000,
        "compute_cap": ComputeCapability(
            peak_tflops_fp32=67.0, peak_tflops_fp16=989.0,
            memory_bandwidth_gbps=3350.0, tensor_core_count=528,
            max_concurrent_kernels=128,
        ),
        "topology": DeviceTopology(
            interconnect_type="NVLink", interconnect_bandwidth_gbps=900.0,
        ),
        "memory_arch": MemoryArchitecture.DISCRETE,
        "cost_per_hour_usd": 3.06,
    },
    "A100_80GB": {
        "backend": DeviceBackendType.CUDA,
        "memory_mb": 81920,
        "compute_cap": ComputeCapability(
            peak_tflops_fp32=19.5, peak_tflops_fp16=312.0,
            memory_bandwidth_gbps=2039.0, tensor_core_count=432,
            max_concurrent_kernels=128,
        ),
        "topology": DeviceTopology(
            interconnect_type="NVLink", interconnect_bandwidth_gbps=600.0,
        ),
        "memory_arch": MemoryArchitecture.DISCRETE,
        "cost_per_hour_usd": 1.80,
    },
    # AMD
    "MI300X": {
        "backend": DeviceBackendType.ROCM,
        "memory_mb": 192000,
        "compute_cap": ComputeCapability(
            peak_tflops_fp32=81.7, peak_tflops_fp16=1307.0,
            memory_bandwidth_gbps=5300.0, matrix_engine_count=304,
            max_concurrent_kernels=64,
        ),
        "topology": DeviceTopology(
            interconnect_type="Infinity Fabric", interconnect_bandwidth_gbps=896.0,
        ),
        "memory_arch": MemoryArchitecture.DISCRETE,
        "cost_per_hour_usd": 2.50,
    },
    "MI250X": {
        "backend": DeviceBackendType.ROCM,
        "memory_mb": 128000,
        "compute_cap": ComputeCapability(
            peak_tflops_fp32=47.9, peak_tflops_fp16=383.0,
            memory_bandwidth_gbps=3276.0, matrix_engine_count=220,
            max_concurrent_kernels=64,
        ),
        "topology": DeviceTopology(
            interconnect_type="Infinity Fabric", interconnect_bandwidth_gbps=400.0,
        ),
        "memory_arch": MemoryArchitecture.DISCRETE,
        "cost_per_hour_usd": 1.60,
    },
    # Apple Silicon
    "M4_MAX": {
        "backend": DeviceBackendType.METAL,
        "memory_mb": 36864,
        "compute_cap": ComputeCapability(
            peak_tflops_fp32=14.0, peak_tflops_fp16=56.0,
            memory_bandwidth_gbps=546.0,
            max_concurrent_kernels=16,
        ),
        "topology": DeviceTopology(
            interconnect_type="UMA", interconnect_bandwidth_gbps=546.0,
        ),
        "memory_arch": MemoryArchitecture.UNIFIED,
        "cost_per_hour_usd": 0.0,
    },
    # Intel Gaudi
    "GAUDI3": {
        "backend": DeviceBackendType.GAUDI,
        "memory_mb": 131072,
        "compute_cap": ComputeCapability(
            peak_tflops_fp32=34.0, peak_tflops_fp16=420.0,
            memory_bandwidth_gbps=3700.0,
            max_concurrent_kernels=24,
        ),
        "topology": DeviceTopology(
            interconnect_type="PCIe", pcie_gen=5, pcie_lanes=16,
            interconnect_bandwidth_gbps=128.0,
        ),
        "memory_arch": MemoryArchitecture.DISCRETE,
        "cost_per_hour_usd": 1.40,
    },
    # CPU SIMD
    "XEON_W9_AVX512": {
        "backend": DeviceBackendType.CPU_SIMD,
        "memory_mb": 131072,
        "compute_cap": ComputeCapability(
            peak_tflops_fp32=0.8, peak_tflops_fp16=1.6,
            memory_bandwidth_gbps=307.0, simd_width_bits=512,
            max_concurrent_kernels=56,
        ),
        "topology": DeviceTopology(
            interconnect_type="PCIe", pcie_gen=5, pcie_lanes=16,
            interconnect_bandwidth_gbps=128.0,
        ),
        "memory_arch": MemoryArchitecture.HOST_ONLY,
        "cost_per_hour_usd": 0.20,
    },
}


def create_device_from_profile(
    profile_name: str,
    device_id: str,
    is_spot: bool = False,
    geographic_zone: str = "us-east1-a",
) -> HardwareDeviceInfo:
    """Factory: creates a HardwareDeviceInfo from a known hardware profile."""
    if profile_name not in HARDWARE_PROFILES:
        raise ValueError(f"Unknown hardware profile: {profile_name}. "
                         f"Available: {list(HARDWARE_PROFILES.keys())}")
    p = HARDWARE_PROFILES[profile_name]
    topo = DeviceTopology(
        interconnect_type=p["topology"].interconnect_type,
        interconnect_bandwidth_gbps=p["topology"].interconnect_bandwidth_gbps,
        pcie_gen=p["topology"].pcie_gen,
        pcie_lanes=p["topology"].pcie_lanes,
        geographic_zone=geographic_zone,
    )
    return HardwareDeviceInfo(
        device_id=device_id,
        backend_type=p["backend"],
        memory_mb=p["memory_mb"],
        is_spot=is_spot,
        cost_per_hour_usd=p["cost_per_hour_usd"],
        compute_cap=p["compute_cap"],
        topology=topo,
        memory_arch=p["memory_arch"],
    )


def auto_detect_local_devices() -> List[HardwareDeviceInfo]:
    """Auto-detect available local hardware (simulation mode).

    In production this would probe CUDA Runtime, ROCm SMI, Metal Device API, etc.
    In simulation mode it returns the host CPU as CPU_SIMD backend.
    """
    return [
        create_device_from_profile("XEON_W9_AVX512", "host_cpu_0", geographic_zone="local"),
    ]
