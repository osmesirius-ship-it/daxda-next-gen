r"""
Tests for Cross-Cluster Red-Team Simulation Engine.
Verifies 25-node attack graph topology, Dijkstra attack path resolution,
MITRE ATLAS/ATT&CK tactics coverage, and autonomous campaign execution.
"""

import pytest

from daxda_engine.level3.cross_cluster_redteam import (
    MITRETactic,
    ClusterNodeType,
    AttackNode,
    AttackEdge,
    CrossClusterAttackGraph,
    AttackStepResult,
    RedTeamCampaignReport,
    RedTeamSimulationEngine,
)


def test_25_node_attack_graph_topology():
    r"""Verify attack graph initializes exactly 25 nodes with valid cluster types and tactics."""
    graph = CrossClusterAttackGraph()

    assert len(graph.nodes) == 25
    assert graph.nodes[0].node_type == ClusterNodeType.K8S_INGRESS
    assert graph.nodes[24].node_type == ClusterNodeType.K8S_ETCD_VAULT
    assert graph.nodes[24].tactic == MITRETactic.EXFILTRATION

    # Every node (except final) should have outgoing edges
    for i in range(24):
        assert len(graph.edges[i]) > 0


def test_shortest_attack_path_dijkstra():
    r"""Verify Dijkstra computes optimal attack trajectory from node 0 to node 24."""
    graph = CrossClusterAttackGraph()

    path, cost = graph.find_shortest_attack_path(start_node_id=0, target_node_id=24)

    assert len(path) > 0
    assert path[0] == 0
    assert path[-1] == 24
    assert cost > 0.0
    assert cost < float("inf")


def test_red_team_campaign_execution():
    r"""Verify autonomous campaign execution generates complete forensic report."""
    sim = RedTeamSimulationEngine()

    report: RedTeamCampaignReport = sim.run_campaign(
        campaign_id="test-sim-01",
        start_node_id=0,
        crown_jewel_node_id=24,
        seed=123,
    )

    assert report.total_nodes_traversed > 0
    assert report.traversal_path[0] == 0
    assert report.traversal_path[-1] == 24
    assert report.total_soc_alerts_raised > 0
    assert len(report.tactics_exercised) >= 3


def test_mitre_tactics_coverage():
    r"""Verify multiple MITRE tactics are exercised across the cluster topology."""
    sim = RedTeamSimulationEngine()
    report = sim.run_campaign(seed=42)

    exercised = set(report.tactics_exercised)
    # Check that tactics include key stages
    assert MITRETactic.INITIAL_ACCESS in exercised or MITRETactic.EXECUTION in exercised
    assert MITRETactic.LATERAL_MOVEMENT in exercised or MITRETactic.PRIVILEGE_ESCALATION in exercised
