"""
SOC Alert Escalation Policies
=============================

Defines 4-tier severity routing policies for AGI containment alerts.
"""

from typing import Dict, List, Any


class EscalationPolicy:
    """Manages channel routing and escalation tiers based on threat severity."""

    DEFAULT_POLICIES = {
        "critical": {
            "channels": ["pagerduty", "slack", "email", "webhook"],
            "requires_acknowledgment": True,
            "ack_timeout_sec": 300,
            "escalate_to": "SOC_INCIDENT_COMMANDER"
        },
        "high": {
            "channels": ["slack", "email", "webhook"],
            "requires_acknowledgment": True,
            "ack_timeout_sec": 900,
            "escalate_to": "SECURITY_LEAD"
        },
        "medium": {
            "channels": ["slack", "webhook"],
            "requires_acknowledgment": False,
            "ack_timeout_sec": 3600,
            "escalate_to": None
        },
        "low": {
            "channels": ["webhook"],
            "requires_acknowledgment": False,
            "ack_timeout_sec": 0,
            "escalate_to": None
        }
    }

    def __init__(self, custom_policies: Dict[str, Any] = None):
        self.policies = self.DEFAULT_POLICIES.copy()
        if custom_policies:
            self.policies.update(custom_policies)

    def get_channels_for_severity(self, severity: str) -> List[str]:
        """Returns target notification channels for a given severity."""
        sev = severity.lower()
        if sev not in self.policies:
            sev = "medium"
        return self.policies[sev]["channels"]

    def get_policy(self, severity: str) -> Dict[str, Any]:
        """Returns the full policy configuration for a severity."""
        sev = severity.lower()
        return self.policies.get(sev, self.policies["medium"])
