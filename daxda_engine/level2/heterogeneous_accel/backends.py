"""
DAXDA Level 2 - Heterogeneous Hardware Device Backends
======================================================

Abstracts multi-vendor GPU, NPU, and CPU accelerator backends:
  - NVIDIA CUDA (Tensor Cores)
  - AMD ROCm / HIP (CDNA Matrix Cores)
  - Apple Silicon Metal (MPS Matrix Engines)
  - Intel Gaudi / oneAPI
  - Host CPU SIMD (AVX-512 / ARM NEON)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DeviceBackendType(str, Enum):
    CUDA = "CUDA"
    ROCM = "ROCM"
    METAL = "METAL"
    GAUDI = "GAUDI"
    CPU_SIMD = "CPU_SIMD"


@dataclass
class HardwareDeviceInfo:
    device_id: str
    backend_type: DeviceBackendType
    memory_mb: int
    is_spot: bool = False
    cost_per_hour_usd: float = 0.50
    active_load: float = 0.0  # [0.0, 1.0]
    is_healthy: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
