"""
DA13 Validator Cluster Configuration Management
===============================================

Defines configuration parameters for the distributed GPU validator cluster,
worker nodes, Ray runtime environments, autoscaling parameters, and fault detection.
"""

import os
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional


@dataclass
class ClusterConfig:
    """Cluster topology and runtime configuration for DA13."""
    cluster_id: str = "da13-gpu-validator-cluster"
    ray_address: str = "auto"
    min_workers: int = 1
    max_workers: int = 1024
    initial_workers: int = 4
    gpu_per_worker: int = 1
    cpu_per_worker: int = 4
    memory_per_worker_gb: float = 16.0
    
    # Scaling thresholds
    autoscale_interval_sec: float = 5.0
    scale_up_p99_threshold_ms: float = 800.0
    scale_down_p99_threshold_ms: float = 200.0
    scale_up_queue_threshold: int = 100
    per_gpu_qps_capacity: float = 100.0
    
    # Fault tolerance & health
    health_check_interval_sec: float = 2.0
    node_timeout_sec: float = 5.0
    fault_recovery_timeout_sec: float = 30.0
    max_worker_retries: int = 3
    
    # Priority queue & batching
    max_batch_size: int = 128
    batch_timeout_ms: float = 10.0
    max_queue_depth: int = 50000
    
    # Ports & Networking
    api_port: int = 8000
    metrics_port: int = 9090
    websocket_port: int = 8765
    
    extra_env: Dict[str, str] = field(default_factory=lambda: {
        "DAXDA_CL_SPACE": "16,4",
        "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
        "PYTHONUNBUFFERED": "1"
    })

    @classmethod
    def from_env(cls) -> "ClusterConfig":
        """Instantiates ClusterConfig from environment variables."""
        return cls(
            cluster_id=os.getenv("DA13_CLUSTER_ID", "da13-gpu-validator-cluster"),
            ray_address=os.getenv("DA13_RAY_ADDRESS", "auto"),
            min_workers=int(os.getenv("DA13_MIN_WORKERS", "1")),
            max_workers=int(os.getenv("DA13_MAX_WORKERS", "1024")),
            initial_workers=int(os.getenv("DA13_INITIAL_WORKERS", "4")),
            gpu_per_worker=int(os.getenv("DA13_GPU_PER_WORKER", "1")),
            cpu_per_worker=int(os.getenv("DA13_CPU_PER_WORKER", "4")),
            memory_per_worker_gb=float(os.getenv("DA13_MEMORY_PER_WORKER_GB", "16.0")),
            api_port=int(os.getenv("DA13_API_PORT", "8000")),
            metrics_port=int(os.getenv("DA13_METRICS_PORT", "9090")),
            websocket_port=int(os.getenv("DA13_WEBSOCKET_PORT", "8765")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
