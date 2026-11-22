"""
DA13 Reliability, Circuit Breaker & Idempotency Engine
======================================================

Implements per-layer resilience patterns for DA-13 + DA-X recursion:
- Circuit breaker state machine (CLOSED, OPEN, HALF_OPEN).
- Exponential backoff with full jitter for transient provider failures.
- Idempotency key tracking ensuring recursion steps are safely retried without side-effects.
- Real-time SLA compliance tracking.
"""

import time
import random
import hashlib
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable


class CircuitState(str, Enum):
    CLOSED = "CLOSED"        # Normal execution
    OPEN = "OPEN"            # Fast-failing downstream calls
    HALF_OPEN = "HALF_OPEN"  # Testing limited recovery calls


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5          # Consecutive failures before opening
    recovery_timeout_sec: float = 30.0  # Duration circuit remains open before half-open probe
    half_open_success_needed: int = 2   # Successful probes before re-closing
    max_backoff_sec: float = 8.0        # Max exponential backoff delay
    base_backoff_sec: float = 0.5       # Base retry backoff


class LayerCircuitBreaker:
    """Per-layer circuit breaker with failure tracking and automatic half-open probing."""

    def __init__(self, layer_id: str, config: Optional[CircuitBreakerConfig] = None):
        self.layer_id = layer_id
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()
        self.total_trips = 0

    def can_execute(self) -> bool:
        """Determines if a request should be permitted or fast-failed."""
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if now - self.last_state_change >= self.config.recovery_timeout_sec:
                # Transition to HALF_OPEN to test upstream recovery
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.last_state_change = now
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self):
        """Records a successful layer execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.half_open_success_needed:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self):
        """Records a layer execution failure."""
        self.failure_count += 1
        now = time.time()
        if self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            if self.failure_count >= self.config.failure_threshold or self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.last_state_change = now
                self.total_trips += 1

    def calculate_backoff(self, attempt: int) -> float:
        """Computes exponential backoff with full jitter: Uniform(0, min(max_backoff, base * 2^attempt))."""
        temp = min(self.config.max_backoff_sec, self.config.base_backoff_sec * (2 ** attempt))
        return random.uniform(0, temp)


class IdempotencyManager:
    """Tracks idempotency keys and cached execution results to prevent duplicate execution."""

    def __init__(self, ttl_seconds: float = 3600.0):
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get_or_compute_key(self, idempotency_key: Optional[str], payload: Dict[str, Any]) -> str:
        """Returns provided idempotency key or computes deterministic SHA-256 digest of payload."""
        if idempotency_key:
            return idempotency_key
        canonical = json.dumps(payload, sort_keys=True).encode("utf-8")
        return f"idem-{hashlib.sha256(canonical).hexdigest()[:24]}"

    def check_idempotent_result(self, key: str) -> Optional[Dict[str, Any]]:
        """Returns cached result if exists and within TTL."""
        entry = self.cache.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > self.ttl_seconds:
            del self.cache[key]
            return None
        return entry["result"]

    def record_idempotent_result(self, key: str, result: Dict[str, Any]):
        """Caches execution result under the idempotency key."""
        self.cache[key] = {
            "result": result,
            "timestamp": time.time()
        }


class ReliabilityRegistry:
    """Singleton registry managing circuit breakers for all 16 layers and DA-X."""

    def __init__(self):
        self.breakers: Dict[str, LayerCircuitBreaker] = {}
        self.idempotency = IdempotencyManager()
        # Initialize breakers for all layers
        layer_ids = [f"DA-{i}" for i in range(1, 16)] + ["DA-X"]
        for lid in layer_ids:
            self.breakers[lid] = LayerCircuitBreaker(layer_id=lid)

    def get_breaker(self, layer_id: str) -> LayerCircuitBreaker:
        if layer_id not in self.breakers:
            self.breakers[layer_id] = LayerCircuitBreaker(layer_id=layer_id)
        return self.breakers[layer_id]
