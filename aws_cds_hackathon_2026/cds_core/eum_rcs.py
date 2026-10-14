"""
AWS Communication Developer Services (CDS) — AWS End User Messaging RCS
=======================================================================
Implements Rich Communication Services (RCS) protocols under AWS EUM.
Supports standalone rich cards, carousel cards, suggested reply chips,
and action chips (dial phone, view map location, open URL).
"""

from __future__ import annotations
import os
import time
import uuid
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

@dataclass
class RCSActionChip:
    chip_type: str  # "SUGGESTED_REPLY", "OPEN_URL", "DIAL_PHONE", "VIEW_LOCATION"
    text: str
    postback_data: str
    target_uri: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class RCSRichCard:
    title: str
    description: str
    media_url: Optional[str] = None
    action_chips: List[RCSActionChip] = field(default_factory=list)

@dataclass
class RCSMessage:
    message_id: str
    destination_phone: str
    agent_id: str
    message_type: str  # "TEXT", "RICH_CARD", "CAROUSEL"
    text_content: Optional[str] = None
    rich_card: Optional[RCSRichCard] = None
    carousel_cards: List[RCSRichCard] = field(default_factory=list)
    suggested_chips: List[RCSActionChip] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    status: str = "DELIVERED"
    direction: str = "OUTBOUND"

class EUMRCSClient:
    """
    AWS End User Messaging RCS Client.
    Delivers next-generation interactive conversational experiences with rich media.
    """
    def __init__(self, rcs_agent_id: str = "daxda-care-rcs-agent", region_name: str = "us-east-1"):
        self.rcs_agent_id = rcs_agent_id
        self.region_name = region_name
        self.history: List[RCSMessage] = []

    def send_rich_card(
        self,
        destination_phone: str,
        title: str,
        description: str,
        media_url: Optional[str] = None,
        chips: Optional[List[RCSActionChip]] = None
    ) -> RCSMessage:
        """
        Sends an interactive RCS Rich Card to a compatible smartphone.
        """
        card = RCSRichCard(
            title=title,
            description=description,
            media_url=media_url,
            action_chips=chips or []
        )
        msg = RCSMessage(
            message_id=f"rcs_{uuid.uuid4().hex[:12]}",
            destination_phone=destination_phone,
            agent_id=self.rcs_agent_id,
            message_type="RICH_CARD",
            rich_card=card,
            suggested_chips=chips or []
        )
        self.history.append(msg)
        return msg

    def send_carousel(
        self,
        destination_phone: str,
        cards: List[RCSRichCard],
        top_level_chips: Optional[List[RCSActionChip]] = None
    ) -> RCSMessage:
        """
        Sends a multi-card interactive carousel for selecting items (e.g. pharmacy locations or time slots).
        """
        msg = RCSMessage(
            message_id=f"rcs_car_{uuid.uuid4().hex[:12]}",
            destination_phone=destination_phone,
            agent_id=self.rcs_agent_id,
            message_type="CAROUSEL",
            carousel_cards=cards,
            suggested_chips=top_level_chips or []
        )
        self.history.append(msg)
        return msg

    def receive_rcs_interaction(
        self,
        source_phone: str,
        user_input_or_postback: str,
        chip_type: str = "SUGGESTED_REPLY"
    ) -> RCSMessage:
        """
        Processes an inbound tap on a suggested action chip or typed message.
        """
        msg = RCSMessage(
            message_id=f"rcs_in_{uuid.uuid4().hex[:12]}",
            destination_phone=self.rcs_agent_id,
            agent_id=source_phone,
            message_type="TEXT",
            text_content=user_input_or_postback,
            direction="INBOUND"
        )
        self.history.append(msg)
        return msg
