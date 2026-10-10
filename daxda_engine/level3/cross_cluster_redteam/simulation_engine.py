r"""
Autonomous Multi-Agent Red-Team Campaign Simulation Engine.
Executes autonomous penetration testing across 25 Kubernetes/Ray cluster nodes,
simulating APT lateral movement, privilege escalation, and SOC incident triage.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

from .attack_graph import (
    MITRETactic,
    ClusterNodeType,
    AttackNode,
    AttackEdge,
    CrossClusterAttackGraph,
)


@dataclass(frozen=True)
class AttackStepResult:
    """Record of a single node compromise attempt."""
    step_number: int
    source_node_id: int
    target_node_id: int
    target_name: str
    tactic: MITRETactic
    technique_used: str
    is_compromised: bool
    is_soc_alert_triggered: bool


@dataclass(frozen=True)
class RedTeamCampaignReport:
    """End-to-end audit report for a completed red-team simulation campaign."""
    campaign_id: str
    start_node_id: int
    crown_jewel_node_id: int
    total_nodes_traversed: int
    total_nodes_compromised: int
    total_soc_alerts_raised: int
    crown_jewel_compromised: bool
    traversal_path: List[int]
    total_campaign_cost: float
    tactics_exercised: List[MITRETactic]


class RedTeamSimulationEngine:
    r"""
    Executes automated penetration tests over the 25-node cross-cluster attack graph.
    """

    def __init__(self, attack_graph: Optional[CrossClusterAttackGraph] = None):
        self.graph = attack_graph or CrossClusterAttackGraph()

    def run_campaign(
        self,
        campaign_id: str = "campaign-apt-01",
        start_node_id: int = 0,
        crown_jewel_node_id: int = 24,
        seed: int = 42,
    ) -> RedTeamCampaignReport:
        """
        Executes an end-to-end automated penetration campaign from start_node to crown_jewel.
        """
        rng = np.random.default_rng(seed)

        # 1. Compute optimal attack trajectory
        optimal_path, path_cost = self.graph.find_shortest_attack_path(
            start_node_id=start_node_id,
            target_node_id=crown_jewel_node_id,
        )

        if not optimal_path:
            raise RuntimeError(f"No valid attack path found between {start_node_id} and {crown_jewel_node_id}")

        steps: List[AttackStepResult] = []
        tactics_seen = []
        nodes_compromised = 0
        soc_alerts = 0

        # Mark start node compromised
        self.graph.nodes[start_node_id].is_compromised = True
        nodes_compromised += 1

        for i in range(len(optimal_path) - 1):
            src_id = optimal_path[i]
            tgt_id = optimal_path[i + 1]
            tgt_node = self.graph.nodes[tgt_id]

            if tgt_node.tactic not in tactics_seen:
                tactics_seen.append(tgt_node.tactic)

            # Find matching edge
            edge_candidates = [e for e in self.graph.edges.get(src_id, []) if e.target_id == tgt_id]
            edge = edge_candidates[0] if edge_candidates else AttackEdge(src_id, tgt_id, "fallback_pivot", 0.8)

            # Probabilistic exploit roll
            exploit_roll = rng.random()
            is_compromised = exploit_roll <= edge.exploit_success_rate
            if is_compromised:
                tgt_node.is_compromised = True
                nodes_compromised += 1

            # Probabilistic Blue Team SOC detection roll
            soc_roll = rng.random()
            is_detected = soc_roll <= tgt_node.detection_probability
            if is_detected:
                tgt_node.is_detected_by_soc = True
                soc_alerts += 1

            steps.append(
                AttackStepResult(
                    step_number=i + 1,
                    source_node_id=src_id,
                    target_node_id=tgt_id,
                    target_name=tgt_node.name,
                    tactic=tgt_node.tactic,
                    technique_used=edge.technique_name,
                    is_compromised=is_compromised,
                    is_soc_alert_triggered=is_detected,
                )
            )

        crown_jewel_hit = bool(self.graph.nodes[crown_jewel_node_id].is_compromised)

        return RedTeamCampaignReport(
            campaign_id=campaign_id,
            start_node_id=start_node_id,
            crown_jewel_node_id=crown_jewel_node_id,
            total_nodes_traversed=len(optimal_path),
            total_nodes_compromised=nodes_compromised,
            total_soc_alerts_raised=soc_alerts,
            crown_jewel_compromised=crown_jewel_hit,
            traversal_path=optimal_path,
            total_campaign_cost=path_cost,
            tactics_exercised=tactics_seen,
        )
