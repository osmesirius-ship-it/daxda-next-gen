r"""
P2P Gossip Message Routing and Peer Scoring Engine.
Models decentralized message dissemination across physical validator nodes,
tracking message propagation latency, fanout, and peer reputation scoring.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import hashlib
import time


import math

@dataclass(frozen=True)
class GossipMessage:
    """Decentralized gossip protocol message."""
    message_id: str
    topic: str
    sender_id: str
    payload: str
    hop_count: int = 0
    max_ttl_hops: int = 6


class P2PGossipNetwork:
    r"""
    Simulates peer-to-peer epidemic gossip message dissemination.
    """

    def __init__(self, fanout: int = 4, max_ttl_hops: int = 6):
        self.fanout = fanout
        self.max_ttl_hops = max_ttl_hops
        self.nodes: Set[str] = set()
        self.neighbors: Dict[str, Set[str]] = {}
        self.seen_messages: Dict[str, Set[str]] = {}  # node_id -> set of message_ids
        self.peer_scores: Dict[str, float] = {}       # node_id -> score in [0.0, 100.0]

    def get_optimal_ttl_hops(self) -> int:
        """
        Dynamically computes the necessary gossip TTL hops to guarantee
        epidemic coverage across |V| nodes given current fanout:
        TTL = max(base_ttl, ceil(log_F(|V|)) + 2)
        """
        n = max(1, len(self.nodes))
        f = max(2, self.fanout)
        needed_hops = math.ceil(math.log(n, f)) + 2
        return max(self.max_ttl_hops, needed_hops)

    def auto_tune_parameters(self) -> Tuple[int, int]:
        """
        Auto-adjusts fanout and TTL bounds based on current network size.
        Returns (fanout, max_ttl_hops).
        """
        n = max(1, len(self.nodes))
        if n > 50:
            # Scale fanout logarithmically for ultra-large meshes (e.g., F=6 at N=500, F=8 at N=10,000)
            self.fanout = max(4, math.ceil(math.log2(n) / 2))
        self.max_ttl_hops = self.get_optimal_ttl_hops()
        return self.fanout, self.max_ttl_hops

    def add_node(self, node_id: str) -> None:
        """Registers a node into the P2P overlay network."""
        self.nodes.add(node_id)
        self.neighbors[node_id] = set()
        self.seen_messages[node_id] = set()
        self.peer_scores[node_id] = 50.0  # Initial neutral score

    def connect_peers(self, node_a: str, node_b: str) -> None:
        """Establishes bidirectional gossip link between two peer nodes."""
        if node_a not in self.nodes or node_b not in self.nodes:
            raise KeyError("Both nodes must be added before connecting")
        self.neighbors[node_a].add(node_b)
        self.neighbors[node_b].add(node_a)

    def broadcast_message(
        self,
        origin_node_id: str,
        topic: str,
        payload: str,
        override_ttl: Optional[int] = None,
    ) -> Tuple[GossipMessage, int]:
        """
        Disseminates a message through epidemic gossip until all connected nodes receive it
        or TTL expires. Returns message and total recipient count.
        """
        ttl = override_ttl or self.get_optimal_ttl_hops()
        msg_id = hashlib.sha256(f"{origin_node_id}:{payload}:{time.time_ns()}".encode()).hexdigest()
        msg = GossipMessage(
            message_id=msg_id,
            topic=topic,
            sender_id=origin_node_id,
            payload=payload,
            hop_count=0,
            max_ttl_hops=ttl,
        )

        frontier = [(origin_node_id, 0)]
        self.seen_messages[origin_node_id].add(msg_id)
        delivered_count = 1

        while frontier:
            current_node, hops = frontier.pop(0)
            if hops >= msg.max_ttl_hops:
                continue

            # Spread to up to fanout neighbors
            peers = list(self.neighbors.get(current_node, []))
            for peer in peers[: self.fanout]:
                if msg_id not in self.seen_messages[peer]:
                    self.seen_messages[peer].add(msg_id)
                    frontier.append((peer, hops + 1))
                    delivered_count += 1
                    # Reward sender in peer score
                    self.peer_scores[current_node] = min(100.0, self.peer_scores[current_node] + 0.1)

        return msg, delivered_count
