"""
SOC Integration Package
"""

from .alerter import EnhancedSOCAlerter
from .escalation import EscalationPolicy
from .correlation import AlertCorrelator, CorrelatedIncident
from .notification_channels import (
    BaseNotificationChannel,
    SlackChannel,
    EmailChannel,
    PagerDutyChannel,
    WebhookChannel,
    DeliveryReceipt
)

__all__ = [
    "EnhancedSOCAlerter",
    "EscalationPolicy",
    "AlertCorrelator",
    "CorrelatedIncident",
    "BaseNotificationChannel",
    "SlackChannel",
    "EmailChannel",
    "PagerDutyChannel",
    "WebhookChannel",
    "DeliveryReceipt"
]
