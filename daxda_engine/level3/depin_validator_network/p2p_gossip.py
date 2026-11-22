r"""
P2P Gossip Message Routing and Peer Scoring Engine.
Models decentralized message dissemination across physical validator nodes,
tracking message propagation latency, fanout, and peer reputation scoring.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import hashlib
import time


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

    def __init__(self, fanout: int = 4):
        self.fanout = fanout
        self.nodes: Set[str] = set()
        self.neighbors: Dict[str, Set[str]] = {}
        self.seen_messages: Dict[str, Set[str]] = {}  # node_id -> set of message_ids
        self.peer_scores: Dict[str, float] = {}       # node_id -> score in [0.0, 100.0]

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
    ) -> Tuple[GossipMessage, int]:
        """
        Disseminates a message through epidemic gossip until all connected nodes receive it
        or TTL expires. Returns message and total recipient count.
        """
        msg_id = hashlib.sha256(f"{origin_node_id}:{payload}:{time.time_ns()}".encode()).hexdigest()
        msg = GossipMessage(
            message_id=msg_id,
            topic=topic,
            sender_id=origin_node_id,
            payload=payload,
            hop_count=0,
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
