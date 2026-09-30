"""
DA13 WebSocket Streaming Server
===============================

WebSocket server for streaming real-time validation results,
queue depth transitions, and worker telemetry to operator dashboards.
"""

import time
import json
from typing import Dict, Any, List, Set, Optional


class WebSocketServer:
    """Manages real-time WebSocket client connections and telemetry broadcasting."""

    def __init__(self):
        self.active_connections: Set[str] = set()
        self.channel_subscriptions: Dict[str, Set[str]] = {
            "validation_events": set(),
            "cluster_health": set(),
            "telemetry": set()
        }
        self.event_history: List[Dict[str, Any]] = []

    def connect_client(self, client_id: str) -> None:
        """Registers a new WebSocket client connection."""
        self.active_connections.add(client_id)
        # Default subscribe to all channels
        for ch in self.channel_subscriptions:
            self.channel_subscriptions[ch].add(client_id)

    def disconnect_client(self, client_id: str) -> None:
        """Removes a disconnected client."""
        self.active_connections.discard(client_id)
        for ch in self.channel_subscriptions.values():
            ch.discard(client_id)

    def subscribe(self, client_id: str, channel: str) -> bool:
        """Subscribes a client to a specific event channel."""
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].add(client_id)
            return True
        return False

    def broadcast_event(self, channel: str, data: Dict[str, Any]) -> int:
        """
        Broadcasts an event message to all subscribed clients.
        Returns the count of clients notified.
        """
        message = {
            "channel": channel,
            "timestamp": time.time(),
            "data": data
        }
        self.event_history.append(message)
        subscribers = self.channel_subscriptions.get(channel, set())
        return len(subscribers)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "active_clients": len(self.active_connections),
            "channels": {k: len(v) for k, v in self.channel_subscriptions.items()},
            "total_broadcasts": len(self.event_history)
        }
