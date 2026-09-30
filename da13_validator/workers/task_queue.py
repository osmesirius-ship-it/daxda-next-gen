"""
DA13 Distributed Task Queue with Priority Scheduling
===================================================

Priority-aware queue for distributed validation tasks, supporting
CRITICAL, HIGH, MEDIUM, and LOW priority bands with FIFO ordering per band.
"""

import time
import heapq
import threading
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class PriorityLevel(IntEnum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass(order=True)
class QueuedTask:
    priority: int
    timestamp: float
    task_id: str = field(compare=False)
    payload: Dict[str, Any] = field(compare=False)
    client_id: Optional[str] = field(default=None, compare=False)
    retry_count: int = field(default=0, compare=False)


class DistributedTaskQueue:
    """Thread-safe priority queue for 10,000+ concurrent validation requests."""

    def __init__(self, max_depth: int = 50000):
        self.max_depth = max_depth
        self._heap: List[QueuedTask] = []
        self._lock = threading.Lock()
        self._task_count = 0
        self.total_enqueued = 0
        self.total_dequeued = 0

    def enqueue(
        self,
        payload: Dict[str, Any],
        priority: PriorityLevel = PriorityLevel.MEDIUM,
        task_id: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> str:
        """Enqueues a validation task with a specific priority band."""
        with self._lock:
            if len(self._heap) >= self.max_depth:
                raise OverflowError(f"Task queue depth exceeded capacity ({self.max_depth})")

            self._task_count += 1
            t_id = task_id or f"task-{self._task_count}-{time.time_ns()}"
            task = QueuedTask(
                priority=int(priority),
                timestamp=time.time(),
                task_id=t_id,
                payload=payload,
                client_id=client_id
            )
            heapq.heappush(self._heap, task)
            self.total_enqueued += 1
            return t_id

    def dequeue(self) -> Optional[QueuedTask]:
        """Dequeues the highest priority task (lowest priority integer)."""
        with self._lock:
            if not self._heap:
                return None
            task = heapq.heappop(self._heap)
            self.total_dequeued += 1
            return task

    def dequeue_batch(self, max_batch_size: int = 128) -> List[QueuedTask]:
        """Dequeues a batch of highest-priority tasks for GPU batch processing."""
        with self._lock:
            batch = []
            while self._heap and len(batch) < max_batch_size:
                batch.append(heapq.heappop(self._heap))
            self.total_dequeued += len(batch)
            return batch

    def depth(self) -> int:
        """Returns current pending queue size."""
        with self._lock:
            return len(self._heap)

    def is_empty(self) -> bool:
        """Returns True if the queue has no pending tasks."""
        with self._lock:
            return len(self._heap) == 0

    def clear(self) -> None:
        """Flushes the queue."""
        with self._lock:
            self._heap.clear()
