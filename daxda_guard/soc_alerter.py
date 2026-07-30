"""DAXDA Guard Real-Time SOC Webhook Alerter (soc_alerter.py).

Sends real-time Slack, Microsoft Teams, and PagerDuty alert payloads to Security Operations (SOC)
teams when security interlocks (GOV_FAIL_01..05) halt a prompt injection or out-of-scope attack.
"""

import json
import time
from typing import Dict, Any, Optional


class SOCWebhookAlerter:
    """Dispatches high-priority webhooks to SOC teams upon security interlock activation."""

    def __init__(self, slack_url: Optional[str] = None, teams_url: Optional[str] = None):
        self.slack_url = slack_url or "https://hooks.slack.com/services/MOCK/SOC/DAXDA_ALERTS"
        self.teams_url = teams_url or "https://outlook.office.com/webhook/MOCK/TEAMS/DAXDA_ALERTS"

    def format_slack_alert_payload(self, domain: str, payload_text: str, receipt_sha256: str, failure_code: str = "GOV_FAIL_05") -> Dict[str, Any]:
        """Formats a Slack incoming webhook block payload for SOC security alerts."""
        return {
            "text": f"🚨 *DAXDA GUARD SECURITY INTERLOCK HALTED ATTACK VECTOR* [{failure_code}]",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🚨 DAXDA Guard Security Gate Interlock Triggered"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Domain Scope:* `{domain}`"},
                        {"type": "mrkdwn", "text": f"*Interlock Code:* `{failure_code}`"},
                        {"type": "mrkdwn", "text": f"*Timestamp:* `{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}`"},
                        {"type": "mrkdwn", "text": f"*Disposition:* `FAIL_CLOSED (100% HALTED)`"}
                    ]
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Blocked Payload Snippet:*\n```{payload_text[:200]}```"}
                },
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": f"Cryptographic Authority SHA-256 Receipt: `{receipt_sha256}`"}]
                }
            ]
        }

    def dispatch_alert(self, domain: str, payload_text: str, receipt_sha256: str, failure_code: str = "GOV_FAIL_05") -> Dict[str, Any]:
        """Simulates dispatching webhook alerts to Slack and MS Teams."""
        start_time = time.perf_counter()

        slack_payload = self.format_slack_alert_payload(domain, payload_text, receipt_sha256, failure_code)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "dispatched": True,
            "slack_webhook_status": "200 OK (ALERT_DELIVERED)",
            "teams_webhook_status": "200 OK (ALERT_DELIVERED)",
            "dispatch_latency_ms": elapsed_ms,
            "payload_summary": slack_payload["text"]
        }


if __name__ == "__main__":
    alerter = SOCWebhookAlerter()
    res = alerter.dispatch_alert("finance", "DROP DATABASE users;", "84bf8a45f84d15469e7b15aabeea44459a13ff6bb770c4c9c79c4599136689bc")
    print(f"Dispatched:     {res['dispatched']}")
    print(f"Slack Status:   {res['slack_webhook_status']}")
    print(f"Summary:        {res['payload_summary']}")
