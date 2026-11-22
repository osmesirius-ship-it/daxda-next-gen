#!/usr/bin/env python3
"""
DAXDA Next-Gen — DePIN Validator Network Cluster Manager
========================================================
Orchestrates a decentralized physical infrastructure network (DePIN) of validator nodes:
  - Validator Staking & Slashing Engine (100% slashing for equivocation/double-signing).
  - P2P Epidemic Gossip Mesh (topology routing, latency, and peer reputation scoring).
  - Cryptographic State Validation Receipts (balanced SHA-256 Merkle trees & signatures).
  - Real-time Byzantine Fault Injection, Slashing Evidence, and State Export.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import random
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from daxda_engine.level3.depin_validator_network.staking_slashing import (
    DePINStakingEngine,
    DePINValidatorNode,
    SlashingEvent,
    SlashingInfraction,
)
from daxda_engine.level3.depin_validator_network.p2p_gossip import (
    GossipMessage,
    P2PGossipNetwork,
)
from daxda_engine.level3.depin_validator_network.receipt_verifier import (
    DePINReceiptVerifier,
    StateValidationReceipt,
)
from daxda_engine.level3.depin_validator_network.compute_broker_bridge import (
    DePINComputeBrokerBridge,
)

OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

logger = logging.getLogger("daxda.depin_cluster")


class DePINClusterManager:
    """
    Decentralized Physical Infrastructure Network (DePIN) Cluster Orchestrator.
    """

    DEFAULT_NODE_REGIONS = [
        "us-east-va", "us-west-or", "eu-central-de", "eu-west-ie",
        "ap-southeast-sg", "ap-northeast-jp", "sa-east-br", "af-south-za"
    ]

    def __init__(
        self,
        node_count: int = 50,
        stake_per_node: float = 10000.0,
        gossip_fanout: int = 4,
        state_export_path: Optional[str] = None,
    ):
        self.node_count = node_count
        self.stake_per_node = stake_per_node
        self.state_export_path = state_export_path or os.path.join(OUTPUTS_DIR, "depin_cluster_state.json")
        self.slashing_log_path = os.path.join(OUTPUTS_DIR, "depin_slashing_history.jsonl")

        self.staking_engine = DePINStakingEngine(min_stake_threshold=1000.0)
        self.gossip_mesh = P2PGossipNetwork(fanout=gossip_fanout)
        self.receipt_verifier = DePINReceiptVerifier()

        self.nodes_metadata: Dict[str, Dict[str, Any]] = {}
        self.current_block_height = 0
        self.total_transactions_verified = 0
        self.total_blocks_sealed = 0
        self.sealed_receipts: List[StateValidationReceipt] = []

        self.compute_broker = DePINComputeBrokerBridge(cluster_manager=self)
        self._boot_cluster()

    def _boot_cluster(self):
        """Initializes validator nodes, stakes tokens, and links P2P gossip mesh."""
        logger.info(f"Bootstrapping DePIN Validator Cluster with {self.node_count} nodes...")
        rng = random.Random(1337)

        for i in range(1, self.node_count + 1):
            region = self.DEFAULT_NODE_REGIONS[(i - 1) % len(self.DEFAULT_NODE_REGIONS)]
            node_id = f"depin-node-{region}-{i:03d}"
            pubkey = hashlib.sha256(f"depin_pubkey_{node_id}_{i}".encode()).hexdigest()

            # Slight stake variation (9,000 to 12,000 DAX)
            stake = round(self.stake_per_node * (0.9 + 0.2 * rng.random()), 2)
            node = self.staking_engine.register_validator(
                validator_id=node_id,
                public_key=pubkey,
                initial_stake=stake
            )

            # Metadata (hardware, geo-region, uptime)
            self.nodes_metadata[node_id] = {
                "validator_id": node_id,
                "region": region,
                "public_key": pubkey,
                "hardware_class": "Enterprise GPU (NVIDIA H100 / RTX 4090)" if i % 3 == 0 else "Consumer Edge (RTX 3090)",
                "uptime_percentage": 99.98,
                "latency_ms": round(rng.uniform(8.5, 34.2), 2),
                "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

            self.gossip_mesh.add_node(node_id)

        # Build resilient peer mesh (k-regular small-world ring + random chords)
        all_node_ids = list(self.nodes_metadata.keys())
        for idx, n_id in enumerate(all_node_ids):
            # Connect to adjacent ring neighbors
            left = all_node_ids[(idx - 1) % len(all_node_ids)]
            right = all_node_ids[(idx + 1) % len(all_node_ids)]
            self.gossip_mesh.connect_peers(n_id, left)
            self.gossip_mesh.connect_peers(n_id, right)

            # Add random cross-region chord
            chord = all_node_ids[(idx + len(all_node_ids) // 2) % len(all_node_ids)]
            if chord != n_id:
                try:
                    self.gossip_mesh.connect_peers(n_id, chord)
                except Exception:
                    pass

        logger.info(f"DePIN Mesh online. Total network stake: {self.get_total_staked_tokens():,.2f} DAX tokens.")
        self.export_state()

    def get_total_staked_tokens(self) -> float:
        """Computes aggregate active stake across non-slashed validators."""
        return sum(v.staked_tokens for v in self.staking_engine.validators.values() if not v.is_slashed)

    def select_proposer(self) -> DePINValidatorNode:
        """Selects validator proposer weighted by active stake and reputation."""
        active_candidates = [
            v for v in self.staking_engine.validators.values()
            if not v.is_jailed and not v.is_slashed and v.staked_tokens > 0
        ]
        if not active_candidates:
            raise RuntimeError("CRITICAL DEPIN ERROR: No active non-jailed validators available.")

        weights = [v.staked_tokens * v.reputation_score for v in active_candidates]
        return random.choices(active_candidates, weights=weights, k=1)[0]

    def execute_validation_round(
        self,
        transaction_batch: Optional[List[str]] = None,
        simulate_byzantine_fault: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes a decentralized validation round:
          1. Selects proposer.
          2. Computes Merkle state root.
          3. Signs StateValidationReceipt.
          4. Propagates block receipt across P2P gossip mesh.
          5. Verifies receipt and enforces slashing on infractions.
        """
        self.current_block_height += 1
        height = self.current_block_height

        # Default synthetic policy transactions if none provided
        if not transaction_batch:
            transaction_batch = [
                f"TX-POLICY-EVAL-{height}-{k:03d}: AGENT-{k} INVARIANT PASS"
                for k in range(1, 101)
            ]

        proposer = self.select_proposer()
        proposer_id = proposer.validator_id

        # Generate canonical post state hash
        state_post_hash = hashlib.sha256(f"DEPIN_STATE_HEIGHT_{height}".encode()).hexdigest()

        # Build Merkle receipt
        receipt = self.receipt_verifier.generate_receipt(
            validator_id=proposer_id,
            block_height=height,
            transactions=transaction_batch,
            state_post_hash=state_post_hash,
            private_signing_key=f"priv_key_{proposer_id}",
        )

        # Record proposal in staking engine
        block_hash = receipt.merkle_root
        slashing_event = self.staking_engine.record_block_proposal(
            validator_id=proposer_id,
            height=height,
            block_hash=block_hash,
        )

        # Byzantine Fault Simulation
        byzantine_slashing_result = None
        if simulate_byzantine_fault == "DOUBLE_SIGNING":
            # Simulate proposer attempting to sign a competing fork block at the same height
            conflicting_hash = hashlib.sha256(f"MALICIOUS_FORK_BLOCK_{height}".encode()).hexdigest()
            byzantine_slashing_result = self.staking_engine.record_block_proposal(
                validator_id=proposer_id,
                height=height,
                block_hash=conflicting_hash,
            )
            self._record_slashing_event(byzantine_slashing_result)
            logger.warning(f"🚨 BYZANTINE DOUBLE-SIGNING DETECTED! Slashed 100% stake of {proposer_id}")

        elif simulate_byzantine_fault == "INVALID_STATE_PROOF":
            # Simulate submitting invalid Merkle root
            byzantine_slashing_result = self.staking_engine.slash_validator(
                validator_id=proposer_id,
                infraction=SlashingInfraction.INVALID_STATE_PROOF,
                evidence_hash="fraud_proof_invalid_merkle_root",
            )
            self._record_slashing_event(byzantine_slashing_result)
            logger.warning(f"🚨 FRAUD PROOF DETECTED! Slashed 20% stake of {proposer_id}")

        # Gossip broadcast across P2P network
        gossip_payload = json.dumps({
            "block_height": height,
            "proposer": proposer_id,
            "merkle_root": receipt.merkle_root,
            "signature": receipt.signature,
        })
        msg, delivered_nodes = self.gossip_mesh.broadcast_message(
            origin_node_id=proposer_id,
            topic="BLOCK_RECEIPT",
            payload=gossip_payload,
        )

        # Peer Verification
        is_verified = self.receipt_verifier.verify_receipt(
            receipt=receipt,
            transactions=transaction_batch,
            private_signing_key=f"priv_key_{proposer_id}",
        )

        self.total_transactions_verified += len(transaction_batch)
        self.total_blocks_sealed += 1
        self.sealed_receipts.append(receipt)

        # Execute monetized compute broker tasks during cycle idle duty-cycle
        if hasattr(self, "compute_broker") and self.compute_broker:
            self.compute_broker.simulate_compute_tick(count=2)

        round_summary = {
            "round_status": "BLOCK_SEALED_VALID",
            "block_height": height,
            "proposer_id": proposer_id,
            "merkle_root": receipt.merkle_root,
            "transaction_count": len(transaction_batch),
            "signature": receipt.signature[:32] + "...",
            "gossip_message_id": msg.message_id[:16] + "...",
            "gossip_delivered_nodes": delivered_nodes,
            "p2p_mesh_coverage_pct": round((delivered_nodes / max(1, len(self.nodes_metadata))) * 100.0, 1),
            "is_cryptographically_verified": is_verified,
            "byzantine_slashing_event": self._format_slashing_event(byzantine_slashing_result),
        }

        self.export_state()
        return round_summary

    def _record_slashing_event(self, ev: Optional[SlashingEvent]):
        """Persists slashing evidence to audit log."""
        if not ev:
            return
        record = {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "validator_id": ev.validator_id,
            "infraction": ev.infraction.value,
            "slashed_tokens": ev.slashed_tokens,
            "remaining_tokens": ev.remaining_tokens,
            "is_jailed": ev.is_jailed,
            "evidence_hash": ev.evidence_hash,
        }
        with open(self.slashing_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def _format_slashing_event(self, ev: Optional[SlashingEvent]) -> Optional[Dict[str, Any]]:
        if not ev:
            return None
        return {
            "validator_id": ev.validator_id,
            "infraction": ev.infraction.value,
            "slashed_tokens": ev.slashed_tokens,
            "remaining_tokens": ev.remaining_tokens,
            "is_jailed": ev.is_jailed,
            "evidence_hash": ev.evidence_hash,
        }

    def get_telemetry(self) -> Dict[str, Any]:
        """Provides real-time telemetry for API endpoints and dashboard UI."""
        total_stake = self.get_total_staked_tokens()
        active_nodes = sum(1 for v in self.staking_engine.validators.values() if not v.is_jailed and not v.is_slashed)
        jailed_nodes = sum(1 for v in self.staking_engine.validators.values() if v.is_jailed)
        slashed_nodes = sum(1 for v in self.staking_engine.validators.values() if v.is_slashed)

        # Node table sample
        nodes_list = []
        for n_id, v in list(self.staking_engine.validators.items())[:20]:
            meta = self.nodes_metadata.get(n_id, {})
            nodes_list.append({
                "validator_id": n_id,
                "region": meta.get("region", "unknown"),
                "hardware": meta.get("hardware_class", "Standard Node"),
                "staked_tokens": v.staked_tokens,
                "reputation_score": v.reputation_score,
                "is_jailed": v.is_jailed,
                "is_slashed": v.is_slashed,
                "latency_ms": meta.get("latency_ms", 15.0),
            })

        return {
            "depin_status": "DEPIN_P2P_MESH_ACTIVE",
            "protocol_version": "DAXDA-DePIN-L3-v1.0",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "current_block_height": self.current_block_height,
            "total_blocks_sealed": self.total_blocks_sealed,
            "total_transactions_verified": self.total_transactions_verified,
            "active_validator_nodes": active_nodes,
            "jailed_validator_nodes": jailed_nodes,
            "slashed_validator_nodes": slashed_nodes,
            "total_network_nodes": len(self.staking_engine.validators),
            "total_network_stake_dax": round(total_stake, 2),
            "slashing_events_count": len(self.staking_engine.slashing_history),
            "average_gossip_fanout": self.gossip_mesh.fanout,
            "max_gossip_ttl_hops": self.gossip_mesh.max_ttl_hops,
            "gossip_network_diameter": max(1, math.ceil(math.log(max(2, len(self.staking_engine.validators)), max(2, self.gossip_mesh.fanout)))),
            "theoretical_capacity_nodes": 100000,
            "latest_merkle_root": self.sealed_receipts[-1].merkle_root if self.sealed_receipts else "NONE",
            "recent_validators": nodes_list,
            "recent_slashing_history": [self._format_slashing_event(e) for e in self.staking_engine.slashing_history[-5:]],
            "compute_broker": self.compute_broker.get_telemetry() if hasattr(self, "compute_broker") and self.compute_broker else {},
        }

    def add_validator_node(
        self,
        node_id: Optional[str] = None,
        region: Optional[str] = None,
        public_key: Optional[str] = None,
        hardware_class: Optional[str] = None,
        initial_stake: Optional[float] = None,
        export: bool = True,
    ) -> Dict[str, Any]:
        """
        Dynamically onboards and stakes a new physical or virtual validator node into the live cluster.
        Wires the node into the P2P gossip mesh with k-regular ring + random chord peering,
        and auto-tunes gossip topology parameters.
        """
        idx = len(self.staking_engine.validators) + 1
        rng = random.Random(int(time.time_ns()) ^ idx)

        region = region or self.DEFAULT_NODE_REGIONS[(idx - 1) % len(self.DEFAULT_NODE_REGIONS)]
        node_id = node_id or f"depin-node-{region}-{idx:04d}"
        public_key = public_key or hashlib.sha256(f"depin_pubkey_{node_id}_{idx}".encode()).hexdigest()
        stake = float(initial_stake) if initial_stake is not None else round(self.stake_per_node * (0.9 + 0.2 * rng.random()), 2)
        hw_class = hardware_class or ("Enterprise GPU (NVIDIA H100 / RTX 4090)" if idx % 3 == 0 else "Consumer Edge (RTX 3090)")

        # Register in staking engine
        node = self.staking_engine.register_validator(
            validator_id=node_id,
            public_key=public_key,
            initial_stake=stake,
        )

        # Record metadata
        meta = {
            "validator_id": node_id,
            "region": region,
            "public_key": public_key,
            "hardware_class": hw_class,
            "uptime_percentage": 99.98,
            "latency_ms": round(rng.uniform(8.5, 34.2), 2),
            "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.nodes_metadata[node_id] = meta

        # Add to gossip mesh
        self.gossip_mesh.add_node(node_id)

        # Wire into peer mesh (connect to existing peers)
        existing_nodes = [nid for nid in self.nodes_metadata.keys() if nid != node_id]
        if existing_nodes:
            self.gossip_mesh.connect_peers(node_id, existing_nodes[-1])
            chord = rng.choice(existing_nodes)
            if chord != existing_nodes[-1]:
                try:
                    self.gossip_mesh.connect_peers(node_id, chord)
                except Exception:
                    pass

        # Auto-tune gossip fanout & TTL
        self.gossip_mesh.auto_tune_parameters()
        self.node_count = len(self.staking_engine.validators)
        if export:
            self.export_state()
        return meta

    def scale_cluster(self, target_node_count: int) -> Dict[str, Any]:
        """
        Scales the active validator cluster to target_node_count.
        """
        current_count = len(self.staking_engine.validators)
        if target_node_count <= current_count:
            return {
                "status": "NOOP",
                "message": f"Cluster already has {current_count} nodes (target was {target_node_count}).",
                "active_nodes": current_count,
                "total_staked_tokens": self.get_total_staked_tokens(),
            }

        added = []
        for _ in range(current_count, target_node_count):
            meta = self.add_validator_node(export=False)
            added.append(meta["validator_id"])

        self.export_state()
        logger.info(f"Scaled DePIN cluster from {current_count} to {target_node_count} nodes.")
        return {
            "status": "SCALED",
            "previous_count": current_count,
            "current_count": len(self.staking_engine.validators),
            "nodes_added_count": len(added),
            "total_staked_tokens": self.get_total_staked_tokens(),
            "average_fanout": self.gossip_mesh.fanout,
            "max_ttl_hops": self.gossip_mesh.max_ttl_hops,
        }

    def export_state(self):
        """Dumps latest cluster state to disk for persistent telemetry."""
        state = self.get_telemetry()
        with open(self.state_export_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)


# Global singleton instance
DEPIN_CLUSTER: Optional[DePINClusterManager] = None


def get_depin_cluster(node_count: Optional[int] = None) -> DePINClusterManager:
    """Returns or boots the global DePIN cluster singleton."""
    global DEPIN_CLUSTER
    if DEPIN_CLUSTER is None:
        count = node_count if node_count is not None else 1000
        DEPIN_CLUSTER = DePINClusterManager(node_count=count)
    elif node_count is not None and node_count > len(DEPIN_CLUSTER.staking_engine.validators):
        DEPIN_CLUSTER.scale_cluster(node_count)
    return DEPIN_CLUSTER
