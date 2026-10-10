r"""
25-Node Cross-Cluster Attack Graph Engine.
Models Kubernetes and Ray cluster infrastructure, MITRE ATLAS/ATT&CK tactics,
and directed attack graph topologies for autonomous red-teaming simulations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import heapq


class MITRETactic(str, Enum):
    RECONNAISSANCE = "TA0043_RECONNAISSANCE"
    INITIAL_ACCESS = "TA0001_INITIAL_ACCESS"
    EXECUTION = "TA0002_EXECUTION"
    PRIVILEGE_ESCALATION = "TA0004_PRIVILEGE_ESCALATION"
    LATERAL_MOVEMENT = "TA0008_LATERAL_MOVEMENT"
    EXFILTRATION = "TA0010_EXFILTRATION"


class ClusterNodeType(str, Enum):
    K8S_INGRESS = "K8S_INGRESS"
    K8S_POD = "K8S_POD"
    K8S_API_SERVER = "K8S_API_SERVER"
    K8S_ETCD_VAULT = "K8S_ETCD_VAULT"
    RAY_HEAD_NODE = "RAY_HEAD_NODE"
    RAY_WORKER_ACTOR = "RAY_WORKER_ACTOR"


@dataclass
class AttackNode:
    """Individual node in the 25-node infrastructure attack graph."""
    node_id: int               # 0 to 24
    name: str
    node_type: ClusterNodeType
    tactic: MITRETactic
    compromise_cost: float     # Path weight / difficulty
    detection_probability: float
    is_compromised: bool = False
    is_detected_by_soc: bool = False


@dataclass(frozen=True)
class AttackEdge:
    """Directed exploit vector connecting two infrastructure nodes."""
    source_id: int
    target_id: int
    technique_name: str
    exploit_success_rate: float


class CrossClusterAttackGraph:
    r"""
    Directed 25-node attack graph spanning Kubernetes and Ray cluster environments:
    Nodes 0-4:   Reconnaissance & Ingress
    Nodes 5-11:  Kubernetes Pods & Workloads
    Nodes 12-17: Ray Head & Worker Nodes
    Nodes 18-22: Lateral Movement & Privilege Escalation
    Nodes 23-24: Crown Jewels (API Server & etcd Vault)
    """

    TOTAL_NODES = 25

    def __init__(self):
        self.nodes: Dict[int, AttackNode] = {}
        self.edges: Dict[int, List[AttackEdge]] = {i: [] for i in range(self.TOTAL_NODES)}
        self._build_25_node_topology()

    def _build_25_node_topology(self) -> None:
        """Constructs 25 nodes and realistic attack vectors."""
        # 1. Nodes definition
        tactics_map = [
            (ClusterNodeType.K8S_INGRESS, MITRETactic.RECONNAISSANCE, 1.0, 0.15),
            (ClusterNodeType.K8S_POD, MITRETactic.INITIAL_ACCESS, 1.5, 0.20),
            (ClusterNodeType.K8S_POD, MITRETactic.INITIAL_ACCESS, 1.5, 0.20),
            (ClusterNodeType.RAY_HEAD_NODE, MITRETactic.RECONNAISSANCE, 2.0, 0.25),
            (ClusterNodeType.RAY_WORKER_ACTOR, MITRETactic.RECONNAISSANCE, 2.0, 0.25),
        ]

        for i in range(self.TOTAL_NODES):
            if i < 5:
                ntype = ClusterNodeType.K8S_INGRESS if i == 0 else ClusterNodeType.K8S_POD
                tactic = MITRETactic.RECONNAISSANCE if i < 2 else MITRETactic.INITIAL_ACCESS
                cost = 1.0 + i * 0.2
                det_prob = 0.15
            elif i < 12:
                ntype = ClusterNodeType.K8S_POD
                tactic = MITRETactic.EXECUTION
                cost = 2.0
                det_prob = 0.30
            elif i < 18:
                ntype = ClusterNodeType.RAY_HEAD_NODE if i == 12 else ClusterNodeType.RAY_WORKER_ACTOR
                tactic = MITRETactic.LATERAL_MOVEMENT
                cost = 2.5
                det_prob = 0.40
            elif i < 23:
                ntype = ClusterNodeType.K8S_API_SERVER
                tactic = MITRETactic.PRIVILEGE_ESCALATION
                cost = 3.5
                det_prob = 0.65
            else:
                ntype = ClusterNodeType.K8S_ETCD_VAULT
                tactic = MITRETactic.EXFILTRATION
                cost = 5.0
                det_prob = 0.85

            node_name = f"{ntype.value.lower()}-{i}"
            self.nodes[i] = AttackNode(
                node_id=i,
                name=node_name,
                node_type=ntype,
                tactic=tactic,
                compromise_cost=cost,
                detection_probability=det_prob,
            )

        # 2. Directed edges (traversal paths from ingress 0 to vault 24)
        for i in range(self.TOTAL_NODES - 1):
            # Connect forward sequentially
            self.add_edge(i, i + 1, "direct_pivot", success_rate=0.85)
            # Add lateral skip paths
            if i + 2 < self.TOTAL_NODES:
                self.add_edge(i, i + 2, "cross_cluster_token_pivot", success_rate=0.65)
            if i + 3 < self.TOTAL_NODES:
                self.add_edge(i, i + 3, "ray_remote_task_injection", success_rate=0.50)

    def add_edge(
        self,
        source: int,
        target: int,
        technique: str,
        success_rate: float = 0.75,
    ) -> None:
        """Adds a directed attack edge."""
        edge = AttackEdge(source, target, technique, success_rate)
        self.edges[source].append(edge)

    def find_shortest_attack_path(
        self,
        start_node_id: int = 0,
        target_node_id: int = 24,
    ) -> Tuple[List[int], float]:
        """
        Computes optimal attack path using Dijkstra's algorithm over compromise costs.
        """
        # Priority queue stores (cost, current_node, path)
        pq = [(0.0, start_node_id, [start_node_id])]
        visited: Set[int] = set()

        while pq:
            cost, curr, path = heapq.heappop(pq)
            if curr == target_node_id:
                return path, cost

            if curr in visited:
                continue
            visited.add(curr)

            for edge in self.edges.get(curr, []):
                nxt = edge.target_id
                if nxt not in visited:
                    edge_cost = self.nodes[nxt].compromise_cost
                    heapq.heappush(pq, (cost + edge_cost, nxt, path + [nxt]))

        return [], float("inf")
