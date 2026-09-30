"""
Enhanced SOC Alerter with Multi-Channel Escalation
=================================================

Integrates with daxda_guard.soc_alerter and dispatches multi-channel alerts
across Slack, Microsoft Teams, Email, PagerDuty, and SIEM Webhooks.
"""

import time
from typing import Dict, Any, Optional, List
from daxda_guard.soc_alerter import SOCWebhookAlerter
from .notification_channels import SlackChannel, EmailChannel, PagerDutyChannel, WebhookChannel, DeliveryReceipt
from .escalation import EscalationPolicy
from .correlation import AlertCorrelator, CorrelatedIncident


class EnhancedSOCAlerter(SOCWebhookAlerter):
    """
    Enterprise-grade SOC Alerter with multi-channel dispatch,
    deduplication, correlation, and tier-based escalation.
    """

    def __init__(
        self,
        slack_url: Optional[str] = None,
        teams_url: Optional[str] = None,
        escalation_policy: Optional[EscalationPolicy] = None,
        correlator: Optional[AlertCorrelator] = None
    ):
        super().__init__(slack_url=slack_url, teams_url=teams_url)
        self.escalation = escalation_policy or EscalationPolicy()
        self.correlator = correlator or AlertCorrelator()

        # Initialize delivery channels
        self.channels = {
            "slack": SlackChannel(webhook_url=self.slack_url),
            "email": EmailChannel(),
            "pagerduty": PagerDutyChannel(),
            "webhook": WebhookChannel()
        }

    def dispatch_containment_alert(
        self,
        agent_id: str,
        category: str,
        pattern: str,
        severity: str = "high",
        receipt_sha256: str = "GENESIS_RECEIPT",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dispatches multi-channel containment alert with deduplication and correlation.
        """
        t0 = time.perf_counter()

        # Step 1: Check deduplication (300s window)
        if self.correlator.is_duplicate(agent_id, category, pattern):
            return {
                "dispatched": False,
                "deduplicated": True,
                "reason": "Duplicate alert suppressed within 300s deduplication window",
                "dispatch_latency_ms": (time.perf_counter() - t0) * 1000.0
            }

        # Step 2: Correlate into incident
        alert_payload = {
            "agent_id": agent_id,
            "category": category,
            "pattern": pattern,
            "severity": severity,
            "receipt_sha256": receipt_sha256,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        incident = self.correlator.ingest_alert(alert_payload)

        # Step 3: Determine target channels from escalation policy
        target_channels = self.escalation.get_channels_for_severity(incident.severity)

        # Step 4: Dispatch to target channels
        channel_receipts: Dict[str, Any] = {}
        for ch_name in target_channels:
            if ch_name in self.channels:
                receipt = self.channels[ch_name].send(alert_payload)
                channel_receipts[ch_name] = {
                    "status": receipt.status,
                    "success": receipt.success,
                    "latency_ms": receipt.latency_ms
                }

        # Step 5: Format parent webhook alert (for backward compatibility)
        base_dispatch = self.dispatch_alert(
            domain=category,
            payload_text=pattern,
            receipt_sha256=receipt_sha256,
            failure_code="GOV_FAIL_05_CONTAINMENT_BREACH"
        )

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "dispatched": True,
            "deduplicated": False,
            "incident_id": incident.incident_id,
            "severity": incident.severity,
            "target_channels": target_channels,
            "channel_receipts": channel_receipts,
            "dispatch_latency_ms": elapsed_ms,
            "base_webhook_status": base_dispatch["slack_webhook_status"]
        }
