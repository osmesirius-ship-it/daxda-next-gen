#!/usr/bin/env python3
"""
AWS Communication Developer Services (CDS) — Unified Omnichannel Simulator Server
==================================================================================
Runs an interactive developer dashboard simulating all 4 AWS CDS communication channels:
- AWS EUM SMS (2-way text)
- AWS EUM RCS (Rich Cards & Action Chips)
- AWS EUM Social WhatsApp (Interactive buttons & consultation)
- Amazon SES (HTML email confirmation)
"""

from __future__ import annotations
import os
import sys
import json
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure root paths in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = CURRENT_DIR.parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from cds_core.omnichannel_router import OmnichannelCDSRouter
from bedrock_agent.agent_core import BedrockAgentCore
from governance.hipaa_sentinel import DAXDAHIPAASentinel

# Global singletons
router = OmnichannelCDSRouter()
agent_core = BedrockAgentCore()
sentinel = DAXDAHIPAASentinel()

# Seed default demonstration session
demo_session = router.create_session(
    patient_id="patient_8841",
    patient_name="Alex Morgan",
    phone_number="+16145550144",
    email_address="alex.morgan@example.com",
    medication_name="Metformin HCL",
    dosage="500mg Oral Tablet (Twice daily with meals)"
)

class CDSSimulatorHandler(SimpleHTTPRequestHandler):
    """
    HTTP handler serving REST API endpoints and static simulator UI.
    """
    def __init__(self, *args, **kwargs):
        static_dir = os.path.join(CURRENT_DIR, "static")
        super().__init__(*args, directory=static_dir, **kwargs)

    def _set_json_headers(self, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_json_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self._set_json_headers(200)
            payload = {
                "session": {
                    "session_id": demo_session.session_id,
                    "patient_name": demo_session.patient_name,
                    "phone": demo_session.phone_number,
                    "email": demo_session.email_address,
                    "medication": demo_session.medication_name,
                    "dosage": demo_session.dosage,
                    "current_channel": demo_session.current_channel,
                    "status": demo_session.status,
                    "pickup_passcode": demo_session.pickup_passcode,
                    "scheduled_pickup_window": demo_session.scheduled_pickup_window
                },
                "sms_messages": [
                    {
                        "id": m.message_id,
                        "direction": m.direction,
                        "body": m.message_body,
                        "timestamp": m.timestamp
                    }
                    for m in router.sms_client.sent_messages
                ],
                "rcs_messages": [
                    {
                        "id": m.message_id,
                        "type": m.message_type,
                        "title": m.rich_card.title if m.rich_card else "",
                        "description": m.rich_card.description if m.rich_card else "",
                        "chips": [{"text": c.text, "postback": c.postback_data} for c in m.suggested_chips]
                    }
                    for m in router.rcs_client.history
                ],
                "whatsapp_messages": [
                    {
                        "id": m.message_id,
                        "direction": m.direction,
                        "text": m.text_body,
                        "buttons": [{"id": b.id, "title": b.title} for b in m.buttons]
                    }
                    for m in router.whatsapp_client.get_thread_history(demo_session.phone_number)
                ],
                "ses_emails": [
                    {
                        "id": e.message_id,
                        "subject": e.subject,
                        "recipient": e.recipient_email,
                        "passcode": e.metadata.get("pickup_passcode"),
                        "audit_sha256": e.sha256_audit_receipt,
                        "html_preview": e.html_body
                    }
                    for e in router.ses_client.sent_emails
                ]
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        # Serve static simulator UI
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        body = json.loads(post_data.decode("utf-8")) if post_data else {}

        if parsed.path == "/api/flow/step1_sms":
            sms = router.trigger_step_1_sms_refill_prompt(demo_session.session_id)
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "SUCCESS", "message": sms.message_body}).encode("utf-8"))

        elif parsed.path == "/api/flow/step2_rcs":
            rcs = router.trigger_step_2_rcs_escalation(demo_session.session_id)
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "SUCCESS", "title": rcs.rich_card.title}).encode("utf-8"))

        elif parsed.path == "/api/flow/step3_whatsapp":
            wa = router.trigger_step_3_whatsapp_consultation(demo_session.session_id)
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "SUCCESS", "message": wa.text_body}).encode("utf-8"))

        elif parsed.path == "/api/flow/step4_ses":
            ses = router.trigger_step_4_ses_email_confirmation(demo_session.session_id)
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "SUCCESS", "passcode": ses.metadata.get("pickup_passcode")}).encode("utf-8"))

        elif parsed.path == "/api/agent/interact":
            user_msg = body.get("message", "")
            channel = body.get("channel", "WHATSAPP")

            # 1. Run through DAXDA Sentinel PEP for HIPAA/PII Compliance
            verdict = sentinel.audit_outbound_message(channel, user_msg, {"medication_name": demo_session.medication_name})

            if verdict.disposition == "DENY":
                self._set_json_headers(200)
                self.wfile.write(json.dumps({
                    "reply": "Request blocked by safety policy: adversarial pattern detected.",
                    "governance": verdict.__dict__
                }).encode("utf-8"))
                return

            # 2. Invoke Bedrock AgentCore
            context = {
                "patient_id": demo_session.patient_id,
                "patient_name": demo_session.patient_name,
                "medication_name": demo_session.medication_name,
                "dosage": demo_session.dosage,
                "zip_code": "43215"
            }
            agent_resp = agent_core.process_patient_turn(
                patient_message=verdict.sanitized_text,
                patient_context=context,
                conversation_history=[],
                current_channel=channel
            )

            # Record turn on WhatsApp client
            router.whatsapp_client.receive_inbound_message(demo_session.phone_number, text_body=user_msg)
            router.whatsapp_client.send_text_message(demo_session.phone_number, agent_resp.reply_text)

            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "reply": agent_resp.reply_text,
                "action_taken": agent_resp.action_taken,
                "action_result": agent_resp.action_result,
                "governance": {
                    "disposition": verdict.disposition,
                    "violations": verdict.violations,
                    "audit_receipt": verdict.audit_receipt_sha256
                },
                "latency_ms": agent_resp.latency_ms
            }).encode("utf-8"))

        else:
            self._set_json_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

def run_server(port: int = 8085):
    server = HTTPServer(("0.0.0.0", port), CDSSimulatorHandler)
    print("=" * 70)
    print("🚀 DAXDA AmbientCDS — AWS Communication Developer Services Simulator")
    print(f"📡 Dashboard running at: http://localhost:{port}")
    print(f"📦 Channels Simulated: SMS, RCS, WhatsApp (Meta Cloud API), Amazon SES")
    print("=" * 70)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
    run_server(p)
