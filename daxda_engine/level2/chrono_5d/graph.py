"""
DAXDA Level 2 - 5D Temporal Causal Graph Engine
================================================

High-throughput, large-scale causal graph supporting 10,000+ nodes,
fast batch causal cone evaluation (>50,000 checks/sec), and automated
closed timelike curve (CTC) cycle detection and harmonization.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

from .geometry import (
    CausalConeType,
    CausalHorizonBoundary,
    RiemannianTemporalSpace5D,
    TemporalCoordinate5D,
)
from .harmonizer import HarmonizationResult, QuantumCausalLoopHarmonizer


@dataclass
class CausalNode5D:
    node_id: str
    coordinate: TemporalCoordinate5D
    decision_vector: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalEdge5D:
    source_id: str
    target_id: str
    cone_type: CausalConeType
    ds_squared: float
    is_retrocausal: bool = False
    weight: float = 1.0


class CausalGraph5D:
    """
    High-performance 5D Causal Graph engine.
    Designed for scale (10,000+ nodes) and sub-millisecond graph queries.
    """

    def __init__(self, space: Optional[RiemannianTemporalSpace5D] = None):
        self.space = space or RiemannianTemporalSpace5D()
        self.nodes: Dict[str, CausalNode5D] = {}
        self.edges: Dict[str, List[CausalEdge5D]] = {}
        self.reverse_edges: Dict[str, List[CausalEdge5D]] = {}

    def add_node(
        self,
        node_id: str,
        coordinate: TemporalCoordinate5D,
        decision_vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CausalNode5D:
        """Adds a 5D temporal node to the graph."""
        vec = decision_vector or [0.05] * 16
        node = CausalNode5D(
            node_id=node_id,
            coordinate=coordinate,
            decision_vector=vec,
            metadata=metadata or {},
        )
        self.nodes[node_id] = node
        if node_id not in self.edges:
            self.edges[node_id] = []
        if node_id not in self.reverse_edges:
            self.reverse_edges[node_id] = []
        # Register in underlying space
        self.space.create_state(coordinate=coordinate, decision_vector=vec, state_id=node_id)
        return node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        weight: float = 1.0,
        verify_geometry: bool = True,
    ) -> Optional[CausalEdge5D]:
        """Adds a directed causal edge between two 5D nodes."""
        src = self.nodes.get(source_id)
        tgt = self.nodes.get(target_id)
        if not src or not tgt:
            return None

        if verify_geometry:
            boundary = self.space.classify_causal_relation(src.coordinate, tgt.coordinate)
            cone_type = boundary.cone_type
            ds_sq = boundary.proper_interval_squared
            is_retro = boundary.dt < 0.0
        else:
            cone_type = CausalConeType.TIMELIKE_FUTURE
            ds_sq = 1.0
            is_retro = False

        edge = CausalEdge5D(
            source_id=source_id,
            target_id=target_id,
            cone_type=cone_type,
            ds_squared=ds_sq,
            is_retrocausal=is_retro,
            weight=weight,
        )
        self.edges[source_id].append(edge)
        self.reverse_edges[target_id].append(edge)
        return edge

    def batch_check_causal_relations(
        self, node_pairs: List[Tuple[str, str]]
    ) -> List[CausalHorizonBoundary]:
        """
        High-throughput batch evaluation of 5D causal relations.
        Optimized for >50,000 checks per second.
        """
        results: List[CausalHorizonBoundary] = []
        classify = self.space.classify_causal_relation

        for src_id, tgt_id in node_pairs:
            src = self.nodes.get(src_id)
            tgt = self.nodes.get(tgt_id)
            if src and tgt:
                results.append(classify(src.coordinate, tgt.coordinate))

        return results

    def detect_closed_timelike_curves(self, max_depth: int = 5) -> List[List[str]]:
        """
        Finds directed closed causal loops (Closed Timelike Curves) up to max_depth.
        Uses depth-limited cycle search.
        """
        ctc_loops: List[List[str]] = []
        visited_in_path: Set[str] = set()

        def dfs(current: str, start: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            for edge in self.edges.get(current, []):
                nxt = edge.target_id
                if nxt == start and len(path) > 1:
                    ctc_loops.append(list(path + [nxt]))
                elif nxt not in visited_in_path and depth < max_depth:
                    visited_in_path.add(nxt)
                    path.append(nxt)
                    dfs(nxt, start, path, depth + 1)
                    path.pop()
                    visited_in_path.remove(nxt)

        for node_id in list(self.nodes.keys()):
            visited_in_path.add(node_id)
            dfs(node_id, node_id, [node_id], 1)
            visited_in_path.remove(node_id)

        # Remove duplicate loop cycles (cyclic permutations)
        unique_loops = []
        seen_sets = set()
        for loop in ctc_loops:
            loop_nodes = tuple(sorted(set(loop)))
            if loop_nodes not in seen_sets:
                seen_sets.add(loop_nodes)
                unique_loops.append(loop)

        return unique_loops

    def harmonize_causal_graph(
        self,
        harmonizer: Optional[QuantumCausalLoopHarmonizer] = None,
        max_branches: int = 16,
    ) -> Dict[str, Any]:
        """
        Detects all CTC loops in the graph and harmonizes them using multi-branch Novikov solver.
        Returns detailed telemetry report.
        """
        harm = harmonizer or QuantumCausalLoopHarmonizer(space=self.space)
        start_time = time.perf_counter()

        ctc_loops = self.detect_closed_timelike_curves(max_depth=4)
        harmonized_count = 0
        loop_results: List[HarmonizationResult] = []

        for loop in ctc_loops:
            # Harmonize target node in the cycle
            target_node = loop[0]
            res = harm.harmonize_loop(target_node, max_branches=max_branches)
            loop_results.append(res)
            if res.is_novikov_consistent:
                harmonized_count += 1

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "total_nodes": len(self.nodes),
            "ctc_loops_detected": len(ctc_loops),
            "harmonized_loops": harmonized_count,
            "all_novikov_consistent": harmonized_count == len(ctc_loops),
            "execution_time_ms": round(elapsed_ms, 3),
            "loop_summaries": [
                {
                    "loop": loop,
                    "consistent": res.is_novikov_consistent,
                    "branches": res.converged_branches_count,
                    "geodesic": res.geodesic_distance,
                }
                for loop, res in zip(ctc_loops, loop_results)
            ],
        }

    @classmethod
    def generate_synthetic_graph(
        cls,
        node_count: int = 10000,
        edge_probability: float = 0.001,
        ctc_probability: float = 0.0005,
        seed: int = 42,
    ) -> CausalGraph5D:
        """
        Synthesizes a 5D temporal causal graph for benchmarking and validation.
        Injects controlled closed timelike curves (CTCs) and branching trajectories.
        """
        random.seed(seed)
        graph = cls()

        # Step 1: Generate 5D temporal nodes
        node_ids = []
        for i in range(node_count):
            node_id = f"node_{i:06d}"
            node_ids.append(node_id)
            coord = TemporalCoordinate5D(
                t=float(i) * 0.05 + random.uniform(-0.02, 0.02),
                b=random.uniform(0.1, 0.9),
                p=random.uniform(0.0, 0.3),  # baseline low paradox phase
                tau=float(i) * 0.048,
                omega=random.uniform(0.05, 0.5),
            )
            vec = [random.uniform(-0.1, 0.1) for _ in range(16)]
            graph.add_node(node_id=node_id, coordinate=coord, decision_vector=vec)

        # Step 2: Generate forward causal edges in local temporal windows
        window_size = 15
        for i in range(node_count):
            src_id = node_ids[i]
            max_j = min(node_count, i + window_size)
            for j in range(i + 1, max_j):
                if random.random() < 0.25:
                    tgt_id = node_ids[j]
                    graph.add_edge(src_id, tgt_id, verify_geometry=False)

        # Step 3: Inject controlled closed timelike curves (CTCs)
        ctc_targets = int(node_count * ctc_probability)
        for _ in range(ctc_targets):
            idx = random.randint(5, node_count - 10)
            # Create a backwards cycle: idx -> idx+1 -> idx+2 -> idx
            n0 = node_ids[idx]
            n1 = node_ids[idx + 1]
            n2 = node_ids[idx + 2]
            graph.add_edge(n0, n1, verify_geometry=False)
            graph.add_edge(n1, n2, verify_geometry=False)
            graph.add_edge(n2, n0, verify_geometry=False)  # Backwards closed loop

        return graph
