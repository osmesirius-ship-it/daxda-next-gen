"""
DA13 Health Monitoring & Fault Recovery
======================================

Continuously monitors GPU/CPU worker health, detects unresponsive nodes (< 5s),
and coordinates automatic recovery within < 30 seconds to maintain 99.99% uptime.
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable


class WorkerHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"


@dataclass
class WorkerHealth:
    worker_id: str
    status: WorkerHealthStatus = WorkerHealthStatus.HEALTHY
    latency_ms: float = 0.0
    last_heartbeat: float = field(default_factory=time.time)
    gpu_id: Optional[int] = None
    gpu_utilization_pct: float = 0.0
    gpu_memory_used_mb: float = 0.0
    total_validations: int = 0
    failure_count: int = 0
    error_message: Optional[str] = None


class HealthMonitor:
    """Monitors worker health and triggers automated node recovery."""

    def __init__(
        self,
        node_timeout_sec: float = 5.0,
        recovery_callback: Optional[Callable[[str], bool]] = None
    ):
        self.node_timeout_sec = node_timeout_sec
        self.recovery_callback = recovery_callback
        self.workers: Dict[str, WorkerHealth] = {}
        self.recovery_events: List[Dict[str, Any]] = []

    def register_worker(self, worker_id: str, gpu_id: Optional[int] = None) -> WorkerHealth:
        """Registers a worker for active monitoring."""
        wh = WorkerHealth(
            worker_id=worker_id,
            status=WorkerHealthStatus.HEALTHY,
            last_heartbeat=time.time(),
            gpu_id=gpu_id
        )
        self.workers[worker_id] = wh
        return wh

    def unregister_worker(self, worker_id: str) -> None:
        """Unregisters a worker (e.g. on controlled downscaling)."""
        self.workers.pop(worker_id, None)

    def record_heartbeat(
        self,
        worker_id: str,
        latency_ms: float,
        gpu_utilization_pct: float = 0.0,
        gpu_memory_used_mb: float = 0.0
    ) -> None:
        """Records a successful heartbeat response."""
        now = time.time()
        if worker_id not in self.workers:
            self.register_worker(worker_id)
        wh = self.workers[worker_id]
        wh.last_heartbeat = now
        wh.latency_ms = latency_ms
        wh.status = WorkerHealthStatus.HEALTHY
        wh.gpu_utilization_pct = gpu_utilization_pct
        wh.gpu_memory_used_mb = gpu_memory_used_mb
        wh.error_message = None

    def check_health(self) -> Dict[str, WorkerHealth]:
        """
        Scans all registered workers. Detects nodes that haven't responded within
        node_timeout_sec, marks them FAILED, and triggers recovery if configured.
        """
        now = time.time()
        for worker_id, wh in list(self.workers.items()):
            time_since_hb = now - wh.last_heartbeat
            if time_since_hb > self.node_timeout_sec:
                if wh.status != WorkerHealthStatus.RECOVERING:
                    wh.status = WorkerHealthStatus.FAILED
                    wh.failure_count += 1
                    wh.error_message = f"Heartbeat timed out ({time_since_hb:.2f}s > {self.node_timeout_sec}s)"
                    self._attempt_recovery(worker_id)
        return self.workers

    def _attempt_recovery(self, worker_id: str) -> None:
        """Triggers recovery callback to restart or respawn the failed worker."""
        wh = self.workers.get(worker_id)
        if not wh:
            return
        wh.status = WorkerHealthStatus.RECOVERING
        t0 = time.time()
        success = False
        if self.recovery_callback:
            try:
                success = self.recovery_callback(worker_id)
            except Exception as e:
                wh.error_message = f"Recovery error: {str(e)}"
        
        recovery_duration = time.time() - t0
        if success:
            wh.status = WorkerHealthStatus.HEALTHY
            wh.last_heartbeat = time.time()
            wh.error_message = None
        else:
            wh.status = WorkerHealthStatus.FAILED

        self.recovery_events.append({
            "worker_id": worker_id,
            "timestamp": time.time(),
            "duration_sec": recovery_duration,
            "success": success
        })

    def get_cluster_status(self) -> Dict[str, Any]:
        """Calculates cluster-wide availability, healthy worker counts, and uptime."""
        total = len(self.workers)
        if total == 0:
            return {"total_workers": 0, "healthy_workers": 0, "availability_pct": 100.0}
        
        healthy = sum(1 for w in self.workers.values() if w.status == WorkerHealthStatus.HEALTHY)
        availability_pct = (healthy / total) * 100.0
        return {
            "total_workers": total,
            "healthy_workers": healthy,
            "failed_workers": total - healthy,
            "availability_pct": round(availability_pct, 3),
            "healthy": healthy > 0
        }
