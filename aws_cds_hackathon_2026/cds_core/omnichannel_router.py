"""
AWS Communication Developer Services (CDS) — Omnichannel Conversational Router
==============================================================================
The core architectural backbone that synchronizes conversational state across
SMS, RCS, WhatsApp, and SES. Ensures that a conversation beginning on SMS
seamlessly transitions to RCS for visual scheduling, hands off to WhatsApp for
AI consultations, and finishes with an SES email confirmation without context loss.
"""

from __future__ import annotations
import time
import uuid
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .eum_sms import EUMSMSClient, SMSMessage
from .eum_rcs import EUMRCSClient, RCSMessage, RCSRichCard, RCSActionChip
from .eum_whatsapp import EUMWhatsAppClient, WhatsAppMessage, WhatsAppButton
from .ses_email import SESEmailClient, SESEmailRecord

@dataclass
class OmnichannelEvent:
    event_id: str
    channel: str  # "SMS", "RCS", "WHATSAPP", "SES"
    direction: str  # "OUTBOUND", "INBOUND"
    sender: str
    recipient: str
    content_summary: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OmnichannelSession:
    session_id: str
    patient_id: str
    patient_name: str
    phone_number: str
    email_address: str
    current_channel: str
    medication_name: str
    dosage: str
    status: str  # "INITIATED", "RCS_CAROUSEL_PRESENTED", "WHATSAPP_ACTIVE", "CONFIRMED_AND_EMAILED"
    scheduled_pickup_window: Optional[str] = None
    pharmacy_selected: Optional[str] = None
    pickup_passcode: Optional[str] = None
    event_stream: List[OmnichannelEvent] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

class OmnichannelCDSRouter:
    """
    Central orchestration engine for AWS CDS omnichannel conversational flows.
    """
    def __init__(self):
        self.sms_client = EUMSMSClient()
        self.rcs_client = EUMRCSClient()
        self.whatsapp_client = EUMWhatsAppClient()
        self.ses_client = SESEmailClient()
        self.sessions: Dict[str, OmnichannelSession] = {}

    def create_session(
        self,
        patient_id: str,
        patient_name: str,
        phone_number: str,
        email_address: str,
        medication_name: str,
        dosage: str
    ) -> OmnichannelSession:
        session_id = f"sess_{uuid.uuid4().hex[:10]}"
        session = OmnichannelSession(
            session_id=session_id,
            patient_id=patient_id,
            patient_name=patient_name,
            phone_number=phone_number,
            email_address=email_address,
            current_channel="SMS",
            medication_name=medication_name,
            dosage=dosage,
            status="INITIATED"
        )
        self.sessions[session_id] = session
        return session

    def trigger_step_1_sms_refill_prompt(self, session_id: str) -> SMSMessage:
        """Step 1: Initiate proactive refill notification via AWS EUM SMS."""
        sess = self.sessions[session_id]
        body = (
            f"Hi {sess.patient_name}, your 30-day refill for {sess.medication_name} ({sess.dosage}) "
            f"is due this Friday. Reply 1 to schedule pickup via RCS, or reply 2 to consult our pharmacist on WhatsApp."
        )
        sms = self.sms_client.send_sms(sess.phone_number, body)
        sess.event_stream.append(OmnichannelEvent(
            event_id=sms.message_id,
            channel="SMS",
            direction="OUTBOUND",
            sender=sms.sender_id,
            recipient=sms.destination_phone,
            content_summary=body
        ))
        sess.updated_at = time.time()
        return sms

    def trigger_step_2_rcs_escalation(self, session_id: str) -> RCSMessage:
        """Step 2: Transition conversation into an interactive RCS Rich Card."""
        sess = self.sessions[session_id]
        sess.current_channel = "RCS"
        sess.status = "RCS_CAROUSEL_PRESENTED"

        chips = [
            RCSActionChip(
                chip_type="SUGGESTED_REPLY",
                text="📍 Pickup Today 5:00 PM (Main St)",
                postback_data="pickup_today_main_st"
            ),
            RCSActionChip(
                chip_type="SUGGESTED_REPLY",
                text="💬 Consult Pharmacist on WhatsApp",
                postback_data="switch_to_whatsapp"
            ),
            RCSActionChip(
                chip_type="DIAL_PHONE",
                text="📞 Call Pharmacy Directly",
                postback_data="call_pharmacy",
                target_uri="tel:+18005550199"
            )
        ]

        rcs_msg = self.rcs_client.send_rich_card(
            destination_phone=sess.phone_number,
            title=f"Refill Authorization: {sess.medication_name}",
            description=f"Dosage: {sess.dosage} • Prescribed by Dr. Nicole S. • Ready for one-tap pickup scheduling.",
            media_url="https://care.daxda.ai/assets/pharmacy_pickup.jpg",
            chips=chips
        )

        sess.event_stream.append(OmnichannelEvent(
            event_id=rcs_msg.message_id,
            channel="RCS",
            direction="OUTBOUND",
            sender=rcs_msg.agent_id,
            recipient=rcs_msg.destination_phone,
            content_summary=f"RCS Rich Card: Refill Authorization for {sess.medication_name}"
        ))
        sess.updated_at = time.time()
        return rcs_msg

    def trigger_step_3_whatsapp_consultation(self, session_id: str, prompt_override: Optional[str] = None) -> WhatsAppMessage:
        """Step 3: Seamlessly pick up conversation on Meta WhatsApp with persistent context."""
        sess = self.sessions[session_id]
        sess.current_channel = "WHATSAPP"
        sess.status = "WHATSAPP_ACTIVE"

        text = prompt_override or (
            f"Hello {sess.patient_name}! 👋 I am your DAXDA Care AI assistant on WhatsApp. "
            f"Picking up from your RCS session: you are refilling *{sess.medication_name} ({sess.dosage})*.\n\n"
            f"Do you have any new symptoms or medications to report, or would you like to confirm pickup at our Main St. location for today at 5:00 PM?"
        )

        buttons = [
            WhatsAppButton(id="confirm_pickup_5pm", title="✅ Confirm 5 PM Pickup"),
            WhatsAppButton(id="ask_side_effects", title="❓ Check Side Effects"),
            WhatsAppButton(id="upload_insurance", title="📸 Upload New Card")
        ]

        wa_msg = self.whatsapp_client.send_interactive_buttons(sess.phone_number, text, buttons)

        sess.event_stream.append(OmnichannelEvent(
            event_id=wa_msg.message_id,
            channel="WHATSAPP",
            direction="OUTBOUND",
            sender=wa_msg.from_number,
            recipient=wa_msg.to_number,
            content_summary=text
        ))
        sess.updated_at = time.time()
        return wa_msg

    def trigger_step_4_ses_email_confirmation(
        self,
        session_id: str,
        pharmacy_location: str = "Walgreens Pharmacy #4192 (120 Main St, Columbus, OH)",
        pickup_window: str = "Today between 5:00 PM – 7:30 PM",
        npi_doctor: str = "NPI-1928472910 (Dr. Nicole S.)"
    ) -> SESEmailRecord:
        """Step 4: Conclude omnichannel flow by issuing cryptographic email receipt via Amazon SES."""
        sess = self.sessions[session_id]
        passcode = f"RX-{uuid.uuid4().hex[:6].upper()}"
        sess.pickup_passcode = passcode
        sess.pharmacy_selected = pharmacy_location
        sess.scheduled_pickup_window = pickup_window
        sess.status = "CONFIRMED_AND_EMAILED"
        sess.current_channel = "SES"

        email_record = self.ses_client.send_clinical_confirmation(
            recipient_email=sess.email_address,
            patient_name=sess.patient_name,
            medication_name=sess.medication_name,
            dosage_schedule=sess.dosage,
            pharmacy_location=pharmacy_location,
            pickup_window=pickup_window,
            pickup_passcode=passcode,
            npi_physician=npi_doctor
        )

        sess.event_stream.append(OmnichannelEvent(
            event_id=email_record.message_id,
            channel="SES",
            direction="OUTBOUND",
            sender=email_record.sender_email,
            recipient=email_record.recipient_email,
            content_summary=f"SES Confirmation sent to {sess.email_address} with passcode {passcode}"
        ))
        sess.updated_at = time.time()
        return email_record

    def get_unified_audit_log(self, session_id: str) -> List[Dict[str, Any]]:
        sess = self.sessions[session_id]
        return [
            {
                "event_id": e.event_id,
                "channel": e.channel,
                "direction": e.direction,
                "summary": e.content_summary,
                "timestamp": e.timestamp
            }
            for e in sess.event_stream
        ]
