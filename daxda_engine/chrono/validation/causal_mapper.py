"""
DAXDA Chrono-Synchronicity Mapping: Causal Relationship Mapper
Constructs and maintains causal dependency graphs spanning forward and backward time.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import deque, defaultdict


@dataclass
class CausalEdge:
    source_id: str
    target_id: str
    weight: float = 1.0
    is_retrocausal: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class CausalMapper:
    """
    Maintains a forward and backward causal relationship graph across temporal states.
    Supports topological sorting, causal influence tracing, and high-throughput loop detection.
    """

    def __init__(self, space: TemporalSpace):
        self.space = space
        self._forward_adj: Dict[str, Set[str]] = defaultdict(set)
        self._backward_adj: Dict[str, Set[str]] = defaultdict(set)
        self._edge_weights: Dict[Tuple[str, str], float] = {}

    def add_causal_relation(
        self,
        source_id: str,
        target_id: str,
        coupling_weight: float = 1.0,
        is_retrocausal: bool = False,
        sync_states: bool = False,
    ) -> None:
        """Add a causal relationship edge source -> target."""
        self._forward_adj[source_id].add(target_id)
        self._backward_adj[target_id].add(source_id)
        self._edge_weights[(source_id, target_id)] = coupling_weight

        if sync_states:
            s_state = self.space.get_state(source_id)
            t_state = self.space.get_state(target_id)
            if s_state:
                s_state.successors.add(target_id)
            if t_state:
                t_state.predecessors.add(source_id)
                if is_retrocausal:
                    t_state.retrocausal_influences.add(source_id)

    def add_causal_relations_batch(
        self,
        relations: Iterable[Tuple[str, str, float]]
    ) -> int:
        """High-throughput batch ingestion of causal relationships."""
        count = 0
        f_adj = self._forward_adj
        b_adj = self._backward_adj
        weights = self._edge_weights
        for src, tgt, w in relations:
            f_adj[src].add(tgt)
            b_adj[tgt].add(src)
            weights[(src, tgt)] = w
            count += 1
        return count


    def get_forward_cone(self, state_id: str, max_depth: int = 15) -> Set[str]:
        """Traverse all states downstream in the causal graph from state_id."""
        visited: Set[str] = set()
        queue = deque([(state_id, 0)])

        while queue:
            curr, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for succ in self._forward_adj.get(curr, set()):
                if succ not in visited:
                    visited.add(succ)
                    queue.append((succ, depth + 1))
        return visited

    def get_backward_cone(self, state_id: str, max_depth: int = 15) -> Set[str]:
        """Traverse all states upstream in the causal graph from state_id."""
        visited: Set[str] = set()
        queue = deque([(state_id, 0)])

        while queue:
            curr, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for pred in self._backward_adj.get(curr, set()):
                if pred not in visited:
                    visited.add(pred)
                    queue.append((pred, depth + 1))
        return visited

    def detect_causal_loops(self, max_depth: int = 50) -> List[List[str]]:
        """
        Detect cycles (Closed Timelike Curves) in the causal graph using iterative stack-based DFS.
        Avoids recursion depth limits and scales to deep chronological graphs.
        """
        cycles: List[List[str]] = []
        all_nodes = set(self._forward_adj.keys()).union(self._backward_adj.keys())
        global_visited: Set[str] = set()

        for start_node in all_nodes:
            if start_node in global_visited:
                continue

            # Stack contains: (current_node, iterator_over_neighbors, path_so_far, rec_set)
            stack = [(start_node, iter(self._forward_adj.get(start_node, set())), [start_node], {start_node})]
            global_visited.add(start_node)

            while stack:
                curr, neighbors_iter, path, rec_set = stack[-1]
                if len(path) > max_depth:
                    stack.pop()
                    continue

                try:
                    neighbor = next(neighbors_iter)
                    if neighbor in rec_set:
                        # Cycle found!
                        idx = path.index(neighbor)
                        cycles.append(path[idx:] + [neighbor])
                        if len(cycles) >= 100:
                            return cycles
                    elif neighbor not in global_visited:
                        global_visited.add(neighbor)
                        next_rec_set = set(rec_set)
                        next_rec_set.add(neighbor)
                        stack.append((neighbor, iter(self._forward_adj.get(neighbor, set())), path + [neighbor], next_rec_set))
                except StopIteration:
                    stack.pop()

        return cycles


    def compute_causal_coupling(self, source_id: str, target_id: str) -> float:
        """
        Compute effective causal coupling strength between source and target
        via maximum-strength path traversal.
        """
        if source_id == target_id:
            return 1.0

        # Dijkstra-like search for maximum product path
        strengths: Dict[str, float] = {source_id: 1.0}
        visited: Set[str] = set()
        queue = [( -1.0, source_id )]

        import heapq
        while queue:
            neg_s, curr = heapq.heappop(queue)
            s = -neg_s
            if curr == target_id:
                return s

            if curr in visited:
                continue
            visited.add(curr)

            for succ in self._forward_adj.get(curr, set()):
                w = self._edge_weights.get((curr, succ), 1.0)
                new_s = s * w
                if new_s > strengths.get(succ, 0.0):
                    strengths[succ] = new_s
                    heapq.heappush(queue, (-new_s, succ))

        return strengths.get(target_id, 0.0)

    def topological_sort(self) -> Optional[List[str]]:
        """
        Perform Kahn's topological sort on the causal DAG.
        Returns sorted list of state IDs, or None if cyclic.
        """
        in_degrees: Dict[str, int] = {}
        all_nodes = set(self._forward_adj.keys()).union(self._backward_adj.keys())

        for node in all_nodes:
            in_degrees[node] = len(self._backward_adj.get(node, set()))

        zero_in = deque([n for n, deg in in_degrees.items() if deg == 0])
        sorted_nodes: List[str] = []

        while zero_in:
            u = zero_in.popleft()
            sorted_nodes.append(u)
            for v in self._forward_adj.get(u, set()):
                in_degrees[v] -= 1
                if in_degrees[v] == 0:
                    zero_in.append(v)

        if len(sorted_nodes) == len(all_nodes):
            return sorted_nodes
        return None  # Cycle present

    def clear(self) -> None:
        self._forward_adj.clear()
        self._backward_adj.clear()
        self._edge_weights.clear()
