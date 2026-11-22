"""
Tests for DePIN Cluster Manager.
Verifies multi-node cluster bootstrapping, peer mesh connectivity,
round consensus execution, and 100% automated slashing on equivocation.
"""

import pytest
from daxda_engine.level3.depin_validator_network import (
    DePINClusterManager,
    SlashingInfraction,
)


def test_depin_cluster_bootstrapping():
    """Verify cluster initial stake, node count, and mesh topology."""
    cluster = DePINClusterManager(node_count=20, stake_per_node=5000.0)
    assert len(cluster.staking_engine.validators) == 20
    assert cluster.node_count == 20
    assert cluster.get_total_staked_tokens() > 90000.0

    # Every node should be in the gossip mesh
    for node_id in cluster.nodes_metadata:
        assert node_id in cluster.gossip_mesh.nodes
        assert len(cluster.gossip_mesh.neighbors[node_id]) >= 2


def test_depin_validation_round_execution():
    """Verify block proposal, Merkle root generation, and receipt verification."""
    cluster = DePINClusterManager(node_count=10, stake_per_node=5000.0)
    summary = cluster.execute_validation_round(transaction_batch=[
        "TX-001: POLICY_PASS_AGENT_1",
        "TX-002: POLICY_PASS_AGENT_2",
    ])

    assert summary["round_status"] == "BLOCK_SEALED_VALID"
    assert summary["block_height"] == 1
    assert summary["is_cryptographically_verified"] is True
    assert summary["transaction_count"] == 2
    assert summary["gossip_delivered_nodes"] >= 2
    assert len(cluster.sealed_receipts) == 1


def test_depin_byzantine_double_signing_slashing():
    """Verify that simulating equivocation slashes 100% of the Byzantine proposer."""
    cluster = DePINClusterManager(node_count=10, stake_per_node=5000.0)

    # Initial stake
    initial_total_stake = cluster.get_total_staked_tokens()

    # Execute round with Byzantine double-signing simulation
    summary = cluster.execute_validation_round(simulate_byzantine_fault="DOUBLE_SIGNING")

    slashed_ev = summary["byzantine_slashing_event"]
    assert slashed_ev is not None
    assert slashed_ev["infraction"] == "DOUBLE_SIGNING"
    assert slashed_ev["is_jailed"] is True

    # Check validator node state
    val_node = cluster.staking_engine.validators[slashed_ev["validator_id"]]
    assert val_node.is_slashed is True
    assert val_node.is_jailed is True
    assert val_node.staked_tokens == 0.0

    # Network active stake decreased by slashed amount
    new_total_stake = cluster.get_total_staked_tokens()
    assert new_total_stake < initial_total_stake


def test_depin_telemetry_export():
    """Verify real-time telemetry dictionary contains all required fields."""
    cluster = DePINClusterManager(node_count=10, stake_per_node=5000.0)
    cluster.execute_validation_round()

    telem = cluster.get_telemetry()
    assert telem["depin_status"] == "DEPIN_P2P_MESH_ACTIVE"
    assert telem["current_block_height"] == 1
    assert telem["active_validator_nodes"] == 10
    assert len(telem["recent_validators"]) == 10
    assert telem["total_transactions_verified"] > 0


def test_daemon_depin_endpoints():
    """Verify daemon HTTP server exposes /api/depin/telemetry, /api/depin/nodes, and /api/depin/round."""
    import socket
    import urllib.request
    import json
    from tools.daxda_fleet_daemon import DAXDAFleetDaemon

    # Find ephemeral port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    daemon = DAXDAFleetDaemon(host="127.0.0.1", port=port, interval_sec=0.1)
    daemon.start_server()
    try:
        # 1. Test GET /api/depin/telemetry
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/depin/telemetry", timeout=5) as r:
            assert r.status == 200
            data = json.loads(r.read().decode("utf-8"))
            assert data["depin_status"] == "DEPIN_P2P_MESH_ACTIVE"
            assert data["total_network_nodes"] >= 10

        # 2. Test GET /api/depin/nodes
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/depin/nodes", timeout=5) as r:
            assert r.status == 200
            nodes_data = json.loads(r.read().decode("utf-8"))
            assert "nodes" in nodes_data
            assert len(nodes_data["nodes"]) >= 10
            assert nodes_data["total_stake_dax"] > 0

        # 3. Test POST /api/depin/round
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/depin/round",
            data=b"{}",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            assert r.status == 200
            round_data = json.loads(r.read().decode("utf-8"))
            assert round_data["status"] == "ROUND_EXECUTED"
            assert round_data["round_summary"]["is_cryptographically_verified"] is True

        # 4. Test GET /api/depin/capacity
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/depin/capacity", timeout=5) as r:
            assert r.status == 200
            cap_data = json.loads(r.read().decode("utf-8"))
            assert cap_data["architecture"]["max_protocol_validator_capacity"] == 100000
            assert "compute_broker_potential_usd_daily" in cap_data
            assert cap_data["compute_broker_potential_usd_daily"]["at_1000_nodes"] == 31968.00

        # 5. Test POST /api/depin/scale
        scale_req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/depin/scale",
            data=json.dumps({"target_nodes": 65}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(scale_req, timeout=5) as r:
            assert r.status == 200
            scale_data = json.loads(r.read().decode("utf-8"))
            assert scale_data["current_count"] >= 65

        # 6. Test POST /api/depin/validator/register
        reg_req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/depin/validator/register",
            data=json.dumps({
                "region": "us-east-va",
                "hardware_class": "NVIDIA H100 SXM5",
                "stake": 15000.0
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(reg_req, timeout=5) as r:
            assert r.status == 201
            reg_data = json.loads(r.read().decode("utf-8"))
            assert reg_data["status"] == "VALIDATOR_REGISTERED"
            assert reg_data["validator"]["hardware_class"] == "NVIDIA H100 SXM5"
    finally:
        daemon.stop_server()


def test_depin_dynamic_node_scaling():
    """Verify cluster can dynamically scale from small initial pool to larger sizes."""
    cluster = DePINClusterManager(node_count=15, stake_per_node=5000.0)
    assert len(cluster.staking_engine.validators) == 15

    # 1. Add single custom node
    meta = cluster.add_validator_node(
        region="eu-central-de",
        hardware_class="Enterprise GPU (NVIDIA H100)",
        initial_stake=12000.0,
    )
    assert meta["region"] == "eu-central-de"
    assert len(cluster.staking_engine.validators) == 16
    assert meta["validator_id"] in cluster.gossip_mesh.nodes

    # 2. Scale up to 60 nodes
    res = cluster.scale_cluster(target_node_count=60)
    assert res["status"] == "SCALED"
    assert res["current_count"] == 60
    assert len(cluster.staking_engine.validators) == 60
    assert cluster.gossip_mesh.fanout >= 4
    assert cluster.gossip_mesh.max_ttl_hops >= 6

    # 3. Verify gossip works seamlessly across expanded 60-node mesh
    msg, delivered = cluster.gossip_mesh.broadcast_message(
        origin_node_id=meta["validator_id"],
        topic="BLOCK_RECEIPT",
        payload="TEST_PAYLOAD",
    )
    assert delivered >= 55  # High-efficiency epidemic coverage
