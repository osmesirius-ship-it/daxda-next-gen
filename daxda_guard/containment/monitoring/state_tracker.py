"""
Agent State Tracker
===================

Thread-safe session state tracking supporting up to 10,000 concurrent agent sessions.
"""

import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AgentSession:
    """Represents the active state of an monitored agent session."""
    agent_id: str
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    action_history: List[Dict[str, Any]] = field(default_factory=list)
    risk_scores: List[float] = field(default_factory=list)
    is_quarantined: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateTracker:
    """Thread-safe state tracker for high-concurrency AGI agent sessions."""

    def __init__(self, max_sessions: int = 10000):
        self.max_sessions = max_sessions
        self._sessions: Dict[str, AgentSession] = {}
        self._lock = threading.Lock()

    def get_or_create_session(self, agent_id: str) -> AgentSession:
        """Retrieves existing session or initializes a new monitored session."""
        with self._lock:
            if agent_id not in self._sessions:
                if len(self._sessions) >= self.max_sessions:
                    # Evict oldest session
                    oldest_id = min(self._sessions.keys(), key=lambda k: self._sessions[k].last_active)
                    del self._sessions[oldest_id]

                self._sessions[agent_id] = AgentSession(agent_id=agent_id)
            return self._sessions[agent_id]

    def record_action(self, agent_id: str, action: Dict[str, Any], risk_score: float = 0.0) -> None:
        """Records an agent action and its associated risk score."""
        session = self.get_or_create_session(agent_id)
        with self._lock:
            session.last_active = time.time()
            session.action_history.append({
                "timestamp": session.last_active,
                "action": action
            })
            session.risk_scores.append(risk_score)
            # Retain up to 100 recent actions per session
            if len(session.action_history) > 100:
                session.action_history = session.action_history[-100:]
            if len(session.risk_scores) > 100:
                session.risk_scores = session.risk_scores[-100:]

    def quarantine_agent(self, agent_id: str, reason: str) -> None:
        """Sets agent session into quarantined containment mode."""
        session = self.get_or_create_session(agent_id)
        with self._lock:
            session.is_quarantined = True
            session.metadata["quarantine_reason"] = reason
            session.metadata["quarantine_timestamp"] = time.time()

    def is_quarantined(self, agent_id: str) -> bool:
        """Checks if an agent is currently quarantined."""
        with self._lock:
            session = self._sessions.get(agent_id)
            return session.is_quarantined if session else False

    def session_count(self) -> int:
        """Returns total active session count."""
        with self._lock:
            return len(self._sessions)

    def clear(self) -> None:
        """Clears all session tracking data."""
        with self._lock:
            self._sessions.clear()
