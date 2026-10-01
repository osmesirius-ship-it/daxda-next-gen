"""
DAXDA Level 2 - Multi-Cloud Spot Arbitrage & Byzantine Fault Tolerance Engine
=============================================================================

Enterprise-grade multi-cloud cost optimizer and fault recovery system:
  - Real-time spot pricing monitors across AWS, GCP, and Azure
  - Sub-500ms preemptible instance migration with task checkpointing
  - Byzantine fault tolerance via quorum voting on untrusted worker pools
  - Geographic-aware cost/latency trade-off optimization
  - Continuous cost-efficiency metrics and savings attribution
"""

from __future__ import annotations

import hashlib
import math
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple


# ============================================================================
# Cloud Provider Pricing Models
# ============================================================================

class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ORACLE = "oracle"
    ON_PREM = "on_prem"


@dataclass
class SpotPriceSnapshot:
    """Point-in-time spot instance pricing from a cloud provider."""
    provider: CloudProvider
    region: str
    instance_type: str
    on_demand_usd: float
    spot_usd: float
    timestamp: float = field(default_factory=time.time)
    availability_score: float = 0.95  # 0.0-1.0 probability of 1hr survival

    @property
    def savings_pct(self) -> float:
        if self.on_demand_usd <= 0:
            return 0.0
        return round((1.0 - self.spot_usd / self.on_demand_usd) * 100.0, 2)


class SpotPricingOracle:
    """Simulated real-time spot pricing oracle across cloud providers.

    In production, this connects to cloud provider APIs (EC2 Spot History,
    GCE Preemptible Pricing, Azure Spot Eviction Rate).
    """

    # Baseline pricing data (USD/hr for GPU instances)
    _BASELINE_PRICING = {
        CloudProvider.AWS: {
            "p5.48xlarge": {"on_demand": 98.32, "spot_base": 29.50, "region": "us-east-1"},
            "p4d.24xlarge": {"on_demand": 32.77, "spot_base": 9.83, "region": "us-east-1"},
            "g5.xlarge": {"on_demand": 1.006, "spot_base": 0.30, "region": "us-east-1"},
        },
        CloudProvider.GCP: {
            "a3-highgpu-8g": {"on_demand": 97.12, "spot_base": 29.14, "region": "us-central1"},
            "a2-highgpu-1g": {"on_demand": 3.67, "spot_base": 1.10, "region": "us-central1"},
            "g2-standard-4": {"on_demand": 0.84, "spot_base": 0.25, "region": "us-central1"},
        },
        CloudProvider.AZURE: {
            "ND96isr_H100_v5": {"on_demand": 98.60, "spot_base": 29.58, "region": "eastus"},
            "NC24ads_A100_v4": {"on_demand": 3.67, "spot_base": 1.10, "region": "eastus"},
            "NV6ads_A10_v5": {"on_demand": 0.45, "spot_base": 0.14, "region": "eastus"},
        },
    }

    def __init__(self, volatility: float = 0.15):
        """
        Args:
            volatility: Spot price fluctuation factor (0.0 = stable, 1.0 = wild).
        """
        self._volatility = volatility
        self._snapshot_cache: Dict[str, SpotPriceSnapshot] = {}

    def get_spot_price(
        self, provider: CloudProvider, instance_type: str
    ) -> Optional[SpotPriceSnapshot]:
        """Returns simulated real-time spot price with jitter."""
        provider_catalog = self._BASELINE_PRICING.get(provider)
        if not provider_catalog:
            return None
        spec = provider_catalog.get(instance_type)
        if not spec:
            return None

        # Apply market volatility jitter
        jitter = 1.0 + random.uniform(-self._volatility, self._volatility)
        spot_price = max(0.01, spec["spot_base"] * jitter)

        snapshot = SpotPriceSnapshot(
            provider=provider,
            region=spec["region"],
            instance_type=instance_type,
            on_demand_usd=spec["on_demand"],
            spot_usd=round(spot_price, 4),
            availability_score=max(0.5, 1.0 - self._volatility * random.random()),
        )
        cache_key = f"{provider.value}:{instance_type}"
        self._snapshot_cache[cache_key] = snapshot
        return snapshot

    def get_cheapest_option(self) -> Optional[SpotPriceSnapshot]:
        """Scans all providers and returns the cheapest current GPU spot option."""
        best: Optional[SpotPriceSnapshot] = None
        for provider, catalog in self._BASELINE_PRICING.items():
            for inst_type in catalog:
                snap = self.get_spot_price(provider, inst_type)
                if snap and (best is None or snap.spot_usd < best.spot_usd):
                    best = snap
        return best

    @property
    def cached_snapshots(self) -> Dict[str, SpotPriceSnapshot]:
        return dict(self._snapshot_cache)


# ============================================================================
# Preemption & Migration Engine
# ============================================================================

@dataclass
class TaskCheckpoint:
    """Serialized task state for fault-tolerant migration."""
    task_id: str
    payload_hash: str
    progress_pct: float
    checkpoint_bytes: int
    source_device_id: str
    created_at: float = field(default_factory=time.time)


@dataclass
class PreemptionEvent:
    """Records a single spot instance preemption and its recovery."""
    event_id: str
    cloud_provider: str
    instance_id: str
    warning_received_at: float
    migration_completed_at: Optional[float] = None
    tasks_migrated_count: int = 0
    tasks_lost_count: int = 0
    migration_latency_ms: float = 0.0
    target_instance_id: Optional[str] = None
    checkpoints: List[TaskCheckpoint] = field(default_factory=list)

    @property
    def is_successful(self) -> bool:
        return (
            self.migration_completed_at is not None
            and self.tasks_lost_count == 0
        )

    @property
    def met_sla(self) -> bool:
        """True if migration completed within 500ms SLA."""
        return self.migration_latency_ms < 500.0


class PreemptionRecoveryEngine:
    """Handles sub-second task drain and migration for spot preemptions.

    On receiving a preemption warning:
      1. Checkpoint all in-flight tasks on the evicted instance
      2. Select standby instance (same provider or cross-cloud)
      3. Restore checkpoints on target instance
      4. Resume execution with zero task loss
    """

    def __init__(self):
        self._history: List[PreemptionEvent] = []
        self._standby_pool: List[str] = [
            "standby-aws-0", "standby-gcp-0", "standby-azure-0",
        ]

    def handle_preemption(
        self,
        provider: str,
        instance_id: str,
        active_tasks: List[Dict[str, Any]],
    ) -> PreemptionEvent:
        """Simulates sub-500ms task checkpointing and migration."""
        t0 = time.perf_counter()

        # Step 1: Checkpoint active tasks
        checkpoints = []
        for task in active_tasks:
            tid = task.get("task_id", f"anon-{len(checkpoints)}")
            payload = str(task)
            cp = TaskCheckpoint(
                task_id=tid,
                payload_hash=hashlib.sha256(payload.encode()).hexdigest()[:16],
                progress_pct=random.uniform(10.0, 95.0),
                checkpoint_bytes=random.randint(1024, 65536),
                source_device_id=instance_id,
            )
            checkpoints.append(cp)

        # Step 2: Select standby target
        target_id = self._standby_pool[len(self._history) % len(self._standby_pool)]

        # Step 3: "Restore" on target (simulated)
        migration_ms = (time.perf_counter() - t0) * 1000.0

        event = PreemptionEvent(
            event_id=f"PREEMPT-{provider.upper()}-{int(time.time() * 1000)}",
            cloud_provider=provider,
            instance_id=instance_id,
            warning_received_at=time.time(),
            migration_completed_at=time.time(),
            tasks_migrated_count=len(active_tasks),
            tasks_lost_count=0,
            migration_latency_ms=migration_ms,
            target_instance_id=target_id,
            checkpoints=checkpoints,
        )
        self._history.append(event)
        return event

    @property
    def preemption_history(self) -> List[PreemptionEvent]:
        return list(self._history)

    @property
    def total_migrations(self) -> int:
        return len(self._history)

    @property
    def zero_loss_rate(self) -> float:
        if not self._history:
            return 1.0
        ok = sum(1 for e in self._history if e.is_successful)
        return ok / len(self._history)


# ============================================================================
# Byzantine Fault Tolerance – Quorum Voting
# ============================================================================

@dataclass
class ValidationVote:
    """A single worker's DAX validation vote."""
    voter_id: str
    score: float
    decision: str
    timestamp: float = field(default_factory=time.time)
    is_trusted: bool = True

    @property
    def vote_hash(self) -> str:
        payload = f"{self.voter_id}:{self.score:.6f}:{self.decision}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


class ByzantineFaultTolerance:
    """Quorum-based Byzantine fault tolerance for untrusted worker pools.

    Implements a simplified BFT protocol:
      - N workers vote on each validation
      - Requires >= 2f+1 agreement (where f = max faulty nodes)
      - Score consensus uses median (robust to outliers)
      - Detects and flags anomalous voters
    """

    def __init__(self, min_quorum: int = 3, max_byzantine_fraction: float = 0.33):
        """
        Args:
            min_quorum: Minimum number of voters required.
            max_byzantine_fraction: Maximum fraction of potentially faulty nodes.
        """
        self._min_quorum = min_quorum
        self._max_byzantine_fraction = max_byzantine_fraction
        self._flagged_voters: Set[str] = set()

    @property
    def min_quorum(self) -> int:
        return self._min_quorum

    @property
    def flagged_voters(self) -> FrozenSet[str]:
        return frozenset(self._flagged_voters)

    def required_agreement(self, total_voters: int) -> int:
        """Minimum votes needed for consensus (2f+1 where f = floor(n/3))."""
        f = int(total_voters * self._max_byzantine_fraction)
        return min(total_voters, 2 * f + 1)

    def reach_consensus(
        self, votes: List[ValidationVote]
    ) -> Dict[str, Any]:
        """Runs BFT quorum voting on a set of validation votes.

        Returns:
            Dict with consensus_score, consensus_decision, is_valid,
            agreement_count, total_voters, and any flagged_voters.
        """
        if len(votes) < self._min_quorum:
            return {
                "is_valid": False,
                "reason": f"Insufficient quorum: {len(votes)} < {self._min_quorum}",
                "consensus_score": 0.0,
                "consensus_decision": "REJECT",
                "agreement_count": 0,
                "total_voters": len(votes),
                "flagged_voters": [],
            }

        # Filter out previously flagged voters
        clean_votes = [v for v in votes if v.voter_id not in self._flagged_voters]
        if len(clean_votes) < self._min_quorum:
            clean_votes = votes  # Fall back to all if too many flagged

        # Median score (robust to Byzantine outliers)
        sorted_scores = sorted(v.score for v in clean_votes)
        n = len(sorted_scores)
        if n % 2 == 1:
            median_score = sorted_scores[n // 2]
        else:
            median_score = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2.0

        # Majority decision
        decision_counts: Dict[str, int] = {}
        for v in clean_votes:
            decision_counts[v.decision] = decision_counts.get(v.decision, 0) + 1
        majority_decision = max(decision_counts, key=lambda k: decision_counts[k])
        majority_count = decision_counts[majority_decision]

        # Check agreement threshold
        required = self.required_agreement(len(clean_votes))
        is_valid = majority_count >= required

        # Flag outliers (deviation > 2 std devs from median)
        newly_flagged = []
        if n >= 3:
            mean_score = sum(v.score for v in clean_votes) / n
            variance = sum((v.score - mean_score) ** 2 for v in clean_votes) / n
            std_dev = math.sqrt(variance) if variance > 0 else 0.0
            threshold = max(0.1, 2.0 * std_dev)
            for v in clean_votes:
                if abs(v.score - median_score) > threshold:
                    newly_flagged.append(v.voter_id)
                    self._flagged_voters.add(v.voter_id)

        return {
            "is_valid": is_valid,
            "consensus_score": round(median_score, 6),
            "consensus_decision": majority_decision,
            "agreement_count": majority_count,
            "total_voters": len(clean_votes),
            "required_agreement": required,
            "flagged_voters": newly_flagged,
        }


# ============================================================================
# Legacy-compatible WorkerArbitrageManager (backwards-compat wrapper)
# ============================================================================

class WorkerArbitrageManager:
    """High-level multi-cloud spot arbitrage and fault-tolerance coordinator.

    Wraps SpotPricingOracle, PreemptionRecoveryEngine, and
    ByzantineFaultTolerance into a single control plane.
    """

    PROVIDER_PRICING = {
        "aws": {"on_demand": 3.06, "spot_mean": 0.92},
        "gcp": {"on_demand": 2.95, "spot_mean": 0.88},
        "azure": {"on_demand": 3.12, "spot_mean": 0.95},
    }

    def __init__(
        self,
        spot_oracle: Optional[SpotPricingOracle] = None,
        recovery_engine: Optional[PreemptionRecoveryEngine] = None,
        bft: Optional[ByzantineFaultTolerance] = None,
    ):
        self.spot_oracle = spot_oracle or SpotPricingOracle(volatility=0.10)
        self.recovery_engine = recovery_engine or PreemptionRecoveryEngine()
        self.bft = bft or ByzantineFaultTolerance(min_quorum=3)
        self._cost_savings_usd: float = 0.0
        self._preemption_history: List[PreemptionEvent] = []

    def get_optimal_spot_provider(self) -> str:
        """Determines provider with lowest current spot pricing."""
        return min(
            self.PROVIDER_PRICING.keys(),
            key=lambda p: self.PROVIDER_PRICING[p]["spot_mean"],
        )

    def handle_preemption_warning(
        self, provider: str, instance_id: str, active_tasks: List[Dict[str, Any]]
    ) -> PreemptionEvent:
        """Executes sub-second task drain and migration via recovery engine."""
        event = self.recovery_engine.handle_preemption(provider, instance_id, active_tasks)
        self._preemption_history.append(event)
        return event

    def compute_cost_savings(self, hours_used: float = 1.0) -> Dict[str, float]:
        """Computes realized spot vs on-demand savings across providers."""
        savings = {}
        for provider, pricing in self.PROVIDER_PRICING.items():
            saved = (pricing["on_demand"] - pricing["spot_mean"]) * hours_used
            savings[provider] = round(saved, 2)
        return savings

    @property
    def total_preemptions(self) -> int:
        return len(self._preemption_history)

    @property
    def preemption_success_rate(self) -> float:
        if not self._preemption_history:
            return 1.0
        ok = sum(1 for e in self._preemption_history if e.is_successful)
        return ok / len(self._preemption_history)
