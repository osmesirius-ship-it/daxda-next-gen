"""
DAXDA Chrono-Synchronicity Mapping: Temporal Space Module
Supports 1D (linear), 2D (branching), 3D (parallel), and 4D (hyper-temporal) representations.
"""

from __future__ import annotations
import math
import hashlib
import json
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Iterable


class TemporalDimension(Enum):
    D1_LINEAR = 1       # (t) - Standard sequential chronology
    D2_BRANCHING = 2    # (t, b) - Branching timeline tree
    D3_PARALLEL = 3     # (t, b, p) - Parallel timeline manifold
    D4_HYPERTEMPORAL = 4 # (t, b, p, tau) - Hyper-temporal retrocausal manifold


@dataclass(frozen=True)
class TemporalCoordinate:
    """
    Coordinates in up to 4-dimensional temporal space:
    t: Physical time / primary chronological axis
    b: Branch index / divergence identifier (0.0 for main trunk)
    p: Parallel timeline coordinate (0.0 for primary universe)
    tau: Hyper-temporal phase / retrocausal recursion parameter (0.0 baseline)
    """
    t: float
    b: float = 0.0
    p: float = 0.0
    tau: float = 0.0

    def to_tuple(self, dim: TemporalDimension = TemporalDimension.D4_HYPERTEMPORAL) -> Tuple[float, ...]:
        if dim == TemporalDimension.D1_LINEAR:
            return (self.t,)
        elif dim == TemporalDimension.D2_BRANCHING:
            return (self.t, self.b)
        elif dim == TemporalDimension.D3_PARALLEL:
            return (self.t, self.b, self.p)
        return (self.t, self.b, self.p, self.tau)

    def to_dict(self) -> Dict[str, float]:
        return {"t": self.t, "b": self.b, "p": self.p, "tau": self.tau}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TemporalCoordinate:
        return cls(
            t=float(data.get("t", 0.0)),
            b=float(data.get("b", 0.0)),
            p=float(data.get("p", 0.0)),
            tau=float(data.get("tau", 0.0)),
        )

    def interval_squared(self, other: TemporalCoordinate, c_t: float = 1.0) -> float:
        """
        Compute pseudo-Riemannian spacetime interval:
        ds^2 = - c_t^2 * (dt)^2 + (db)^2 + (dp)^2 + (dtau)^2
        ds^2 < 0: Timelike separation (causally connectable)
        ds^2 == 0: Null separation (lightcone / horizon)
        ds^2 > 0: Spacelike separation (acausal / synchronicity candidate)
        """
        dt = self.t - other.t
        db = self.b - other.b
        dp = self.p - other.p
        dtau = self.tau - other.tau
        return - (c_t ** 2) * (dt ** 2) + (db ** 2) + (dp ** 2) + (dtau ** 2)

    def euclidean_distance(self, other: TemporalCoordinate, weights: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)) -> float:
        """Positive-definite Euclidean metric for spatial indexing and clustering."""
        dt = (self.t - other.t) * weights[0]
        db = (self.b - other.b) * weights[1]
        dp = (self.p - other.p) * weights[2]
        dtau = (self.tau - other.tau) * weights[3]
        return math.sqrt(dt * dt + db * db + dp * dp + dtau * dtau)

    def is_timelike_separated(self, other: TemporalCoordinate, c_t: float = 1.0) -> bool:
        return self.interval_squared(other, c_t) < 0

    def is_spacelike_separated(self, other: TemporalCoordinate, c_t: float = 1.0) -> bool:
        return self.interval_squared(other, c_t) > 0


@dataclass
class TemporalState:
    """An agent decision or observation state embedded in temporal geometry."""
    state_id: str
    coordinate: TemporalCoordinate
    decision_vector: List[float]
    payload: Dict[str, Any] = field(default_factory=dict)
    predecessors: Set[str] = field(default_factory=set)
    successors: Set[str] = field(default_factory=set)
    retrocausal_influences: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def state_hash(self) -> str:
        body = {
            "id": self.state_id,
            "coord": self.coordinate.to_dict(),
            "vector": [round(v, 6) for v in self.decision_vector],
            "preds": sorted(list(self.predecessors)),
        }
        encoded = json.dumps(body, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "coordinate": self.coordinate.to_dict(),
            "decision_vector": self.decision_vector,
            "payload": self.payload,
            "predecessors": list(self.predecessors),
            "successors": list(self.successors),
            "retrocausal_influences": list(self.retrocausal_influences),
            "created_at": self.created_at,
            "state_hash": self.state_hash,
            "metadata": self.metadata,
        }


class TemporalSpace:
    """
    Multi-dimensional temporal space container.
    Supports indexing, temporal slicing, branch tracking, and nearest-neighbor lookups
    with memory footprint bounding (< 512MB target).
    """

    def __init__(
        self,
        dimension: TemporalDimension = TemporalDimension.D4_HYPERTEMPORAL,
        c_t: float = 1.0,
        max_cached_states: int = 250000,
    ):
        self.dimension = dimension
        self.c_t = c_t
        self.max_cached_states = max_cached_states
        
        self._states: Dict[str, TemporalState] = {}
        # Chronological index for fast 1D/temporal range querying: sorted list of (t, state_id)
        self._time_index: List[Tuple[float, str]] = []
        self._time_sorted: bool = True
        
        # Branch index: branch_id -> list of state_ids
        self._branch_index: Dict[float, List[str]] = {}
        # Parallel timeline index: parallel_id -> list of state_ids
        self._parallel_index: Dict[float, List[str]] = {}

    def __len__(self) -> int:
        return len(self._states)

    def add_state(self, state: TemporalState) -> str:
        """Register a new temporal state into the manifold."""
        if len(self._states) >= self.max_cached_states:
            self._prune_oldest(int(self.max_cached_states * 0.1))

        self._states[state.state_id] = state
        self._time_index.append((state.coordinate.t, state.state_id))
        self._time_sorted = False

        b_key = round(state.coordinate.b, 4)
        if b_key not in self._branch_index:
            self._branch_index[b_key] = []
        self._branch_index[b_key].append(state.state_id)

        p_key = round(state.coordinate.p, 4)
        if p_key not in self._parallel_index:
            self._parallel_index[p_key] = []
        self._parallel_index[p_key].append(state.state_id)

        return state.state_id

    def get_state(self, state_id: str) -> Optional[TemporalState]:
        return self._states.get(state_id)

    def _ensure_time_sorted(self) -> None:
        if not self._time_sorted:
            self._time_index.sort(key=lambda item: item[0])
            self._time_sorted = True

    def query_interval(self, t_start: float, t_end: float) -> List[TemporalState]:
        """Query all states within chronological interval [t_start, t_end]."""
        self._ensure_time_sorted()
        results: List[TemporalState] = []
        # Binary search for interval start
        low = 0
        high = len(self._time_index)
        while low < high:
            mid = (low + high) // 2
            if self._time_index[mid][0] < t_start:
                low = mid + 1
            else:
                high = mid
        
        for i in range(low, len(self._time_index)):
            t_val, state_id = self._time_index[i]
            if t_val > t_end:
                break
            st = self._states.get(state_id)
            if st:
                results.append(st)
        return results

    def query_branch(self, branch_id: float) -> List[TemporalState]:
        """Retrieve all states residing along a specific branch coordinate."""
        b_key = round(branch_id, 4)
        ids = self._branch_index.get(b_key, [])
        return [self._states[sid] for sid in ids if sid in self._states]

    def query_parallel(self, parallel_id: float) -> List[TemporalState]:
        """Retrieve all states along a parallel timeline coordinate."""
        p_key = round(parallel_id, 4)
        ids = self._parallel_index.get(p_key, [])
        return [self._states[sid] for sid in ids if sid in self._states]

    def find_nearest_neighbors(
        self,
        target_coord: TemporalCoordinate,
        k: int = 5,
        max_radius: Optional[float] = None
    ) -> List[Tuple[TemporalState, float]]:
        """Find k-nearest temporal states by Euclidean distance."""
        candidates: List[Tuple[TemporalState, float]] = []
        for state in self._states.values():
            dist = state.coordinate.euclidean_distance(target_coord)
            if max_radius is None or dist <= max_radius:
                candidates.append((state, dist))
        
        candidates.sort(key=lambda x: x[1])
        return candidates[:k]

    def get_lightcone(
        self,
        origin_coord: TemporalCoordinate,
        direction: str = "future"
    ) -> List[TemporalState]:
        """
        Compute past or future lightcone states relative to origin_coord:
        direction == 'future': t > origin.t and ds^2 <= 0
        direction == 'past':   t < origin.t and ds^2 <= 0
        """
        results: List[TemporalState] = []
        for state in self._states.values():
            ds2 = origin_coord.interval_squared(state.coordinate, self.c_t)
            if ds2 <= 0:  # Timelike or null
                if direction == "future" and state.coordinate.t >= origin_coord.t:
                    results.append(state)
                elif direction == "past" and state.coordinate.t <= origin_coord.t:
                    results.append(state)
                elif direction == "all":
                    results.append(state)
        return results

    def _prune_oldest(self, count: int) -> None:
        """Prune oldest states to enforce bounded memory constraint."""
        self._ensure_time_sorted()
        to_remove = set()
        for i in range(min(count, len(self._time_index))):
            to_remove.add(self._time_index[i][1])
        
        for sid in to_remove:
            st = self._states.pop(sid, None)
            if st:
                b_key = round(st.coordinate.b, 4)
                if b_key in self._branch_index:
                    self._branch_index[b_key] = [x for x in self._branch_index[b_key] if x != sid]
                p_key = round(st.coordinate.p, 4)
                if p_key in self._parallel_index:
                    self._parallel_index[p_key] = [x for x in self._parallel_index[p_key] if x != sid]
        
        self._time_index = [(t, sid) for t, sid in self._time_index if sid not in to_remove]
        self._time_sorted = True

    def clear(self) -> None:
        self._states.clear()
        self._time_index.clear()
        self._branch_index.clear()
        self._parallel_index.clear()
        self._time_sorted = True
