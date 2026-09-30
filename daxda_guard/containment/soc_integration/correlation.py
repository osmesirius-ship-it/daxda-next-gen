"""
SOC Alert Deduplication & Incident Correlation Engine
=====================================================

Performs 300-second window deduplication and correlates multi-stage AGI escape sequences.
"""

import time
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CorrelatedIncident:
    incident_id: str
    agent_id: str
    primary_category: str
    severity: str
    first_seen: float
    last_seen: float
    alert_count: int
    related_alerts: List[Dict[str, Any]] = field(default_factory=list)
    mitigation_status: str = "CONTAINED"


class AlertCorrelator:
    """Correlates alerts across time windows and deduplicates repetitive breaches."""

    def __init__(self, dedup_window_sec: int = 300):
        self.dedup_window_sec = dedup_window_sec
        self.dedup_cache: Dict[str, float] = {}
        self.incidents: Dict[str, CorrelatedIncident] = {}

    def is_duplicate(self, agent_id: str, category: str, pattern: str) -> bool:
        """Checks if identical alert was dispatched within the deduplication window."""
        key = hashlib.sha256(f"{agent_id}:{category}:{pattern}".encode()).hexdigest()
        now = time.time()
        last_time = self.dedup_cache.get(key)
        if last_time and (now - last_time) < self.dedup_window_sec:
            return True
        self.dedup_cache[key] = now
        return False

    def ingest_alert(self, alert_data: Dict[str, Any]) -> CorrelatedIncident:
        """Ingests an alert and clusters it into an active incident."""
        agent_id = alert_data.get("agent_id", "unknown_agent")
        category = alert_data.get("category", "containment_breach")
        severity = alert_data.get("severity", "high")
        now = time.time()

        incident_key = f"INC-{agent_id}"

        if incident_key in self.incidents:
            inc = self.incidents[incident_key]
            # Check if within correlation window (1 hour)
            if now - inc.last_seen < 3600:
                inc.alert_count += 1
                inc.last_seen = now
                inc.related_alerts.append(alert_data)
                # Escalate severity if multiple breaches
                if inc.alert_count >= 3 and inc.severity != "critical":
                    inc.severity = "critical"
                return inc

        # Create new incident
        inc = CorrelatedIncident(
            incident_id=f"INC-{hashlib.sha256(f'{agent_id}:{now}'.encode()).hexdigest()[:8]}",
            agent_id=agent_id,
            primary_category=category,
            severity=severity,
            first_seen=now,
            last_seen=now,
            alert_count=1,
            related_alerts=[alert_data]
        )
        self.incidents[incident_key] = inc
        return inc

    def get_active_incidents(self) -> List[CorrelatedIncident]:
        """Returns all correlated incident records."""
        return list(self.incidents.values())

    def clear(self) -> None:
        """Clears deduplication cache and incident records."""
        self.dedup_cache.clear()
        self.incidents.clear()
