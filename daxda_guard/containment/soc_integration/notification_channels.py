"""
Multi-Channel Notification Adapters for SOC Integration
======================================================
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DeliveryReceipt:
    channel: str
    status: str
    success: bool
    latency_ms: float
    details: Dict[str, Any]


class BaseNotificationChannel:
    """Base class for SOC notification channels."""
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    def send(self, alert_payload: Dict[str, Any]) -> DeliveryReceipt:
        raise NotImplementedError


class SlackChannel(BaseNotificationChannel):
    def __init__(self, webhook_url: Optional[str] = None):
        super().__init__("slack", {"webhook_url": webhook_url or "https://hooks.slack.com/services/MOCK/SOC/ALERTS"})

    def send(self, alert_payload: Dict[str, Any]) -> DeliveryReceipt:
        t0 = time.perf_counter()
        # Mock delivery
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return DeliveryReceipt(
            channel="slack",
            status="200 OK (ALERT_DELIVERED)",
            success=True,
            latency_ms=elapsed_ms,
            details={"destination": self.config["webhook_url"]}
        )


class EmailChannel(BaseNotificationChannel):
    def __init__(self, smtp_host: Optional[str] = None):
        super().__init__("email", {"smtp_host": smtp_host or "smtp.internal.soc.daxda.ia"})

    def send(self, alert_payload: Dict[str, Any]) -> DeliveryReceipt:
        t0 = time.perf_counter()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return DeliveryReceipt(
            channel="email",
            status="250 Message queued for delivery",
            success=True,
            latency_ms=elapsed_ms,
            details={"recipient": "soc-alerts@daxda.ia"}
        )


class PagerDutyChannel(BaseNotificationChannel):
    def __init__(self, routing_key: Optional[str] = None):
        super().__init__("pagerduty", {"routing_key": routing_key or "mock_pd_key_critical_oncall"})

    def send(self, alert_payload: Dict[str, Any]) -> DeliveryReceipt:
        t0 = time.perf_counter()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return DeliveryReceipt(
            channel="pagerduty",
            status="202 Incident Created",
            success=True,
            latency_ms=elapsed_ms,
            details={"urgency": "high", "service": "AGI_CONTAINMENT_BREACH"}
        )


class WebhookChannel(BaseNotificationChannel):
    def __init__(self, endpoint_url: Optional[str] = None):
        super().__init__("webhook", {"endpoint_url": endpoint_url or "https://siem.internal.daxda.ia/api/v1/alerts"})

    def send(self, alert_payload: Dict[str, Any]) -> DeliveryReceipt:
        t0 = time.perf_counter()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return DeliveryReceipt(
            channel="webhook",
            status="200 OK",
            success=True,
            latency_ms=elapsed_ms,
            details={"endpoint": self.config["endpoint_url"]}
        )
