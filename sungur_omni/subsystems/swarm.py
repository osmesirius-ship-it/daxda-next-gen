"""
SUNGUR-OMNI: Cross-Domain Swarm-Sync Protocol Subsystem
=======================================================
Author: arch-yunus | 2026 Sovereign Systems Initiative
Governed by: DAXDA Next-Gen Cl(16,4) Invariants
"""

from typing import Dict, Any, List, Optional
import hashlib
import json
from ..core.types import OperationalDomain, CommChannel, SwarmMessage


class SwarmSyncSubsystem:
    """
    Swarm-Sync: Autonomous Trans-Medium Mesh Communication.
    Routes mission updates, target locks, and tactical telemetry across units
    operating in different physical domains (Sea, Land, Air, Space).
    """

    def __init__(self, unit_id: str = "SUNGUR-OMNI-ALPHA-01"):
        self.unit_id = unit_id
        self.received_messages: List[SwarmMessage] = []
        self.active_links: Dict[str, CommChannel] = {}

    def select_best_channel(self, local_domain: OperationalDomain, peer_domain: OperationalDomain) -> CommChannel:
        """
        Dynamically selects optimal physical communication channel based on mediums.
        """
        if local_domain == OperationalDomain.SEA or peer_domain == OperationalDomain.SEA:
            return CommChannel.BLUE_GREEN_LASER
        elif local_domain == OperationalDomain.SPACE or peer_domain == OperationalDomain.SPACE:
            return CommChannel.SPACE_OPTICAL_LINK
        elif local_domain == OperationalDomain.AIR or peer_domain == OperationalDomain.AIR:
            return CommChannel.MILLIMETRIC_RF
        else:
            return CommChannel.MILLIMETRIC_RF

    def transmit_packet(
        self,
        target_id: str,
        current_domain: OperationalDomain,
        target_domain: OperationalDomain,
        tactical_payload: Dict[str, Any]
    ) -> SwarmMessage:
        """
        Generates and cryptographically signs an outbound swarm packet.
        """
        channel = self.select_best_channel(current_domain, target_domain)
        msg = SwarmMessage(
            sender_id=self.unit_id,
            target_id=target_id,
            channel=channel,
            domain_origin=current_domain,
            payload=tactical_payload
        )
        self.active_links[target_id] = channel
        return msg

    def receive_and_verify(self, message: SwarmMessage) -> Dict[str, Any]:
        """
        Verifies cryptographic integrity and DAXDA provenance seal before ingestion.
        """
        data = f"{message.sender_id}:{message.target_id}:{message.domain_origin}:{json.dumps(message.payload, sort_keys=True)}"
        expected_seal = hashlib.sha256(data.encode()).hexdigest()[:16]

        if message.daxda_seal != expected_seal:
            return {
                "status": "REJECTED_CORRUPT_OR_SPOOFED",
                "verified": False,
                "reason": "DAXDA_PROVENANCE_SEAL_MISMATCH"
            }

        self.received_messages.append(message)
        return {
            "status": "INGESTED_NOMINAL",
            "verified": True,
            "sender": message.sender_id,
            "channel": message.channel.value,
            "domain_origin": message.domain_origin.value,
            "seal": message.daxda_seal
        }
