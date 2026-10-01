"""
DAXDA Level 2 - Honeytoken Tripwire Manager
===========================================

Injects synthetic canaries, decoy credentials, and memory watermarks
into agent context, and triggers instantaneous Level 4 air-gap tripwires
upon detection across plain, Base64, Hex, Homoglyph, and Steganographic channels.
"""

from __future__ import annotations

import base64
import hashlib
import re
import time
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .steganography import SteganographyEncoder


class CanaryType(str, Enum):
    API_KEY = "api_key"
    JWT_BEARER = "jwt_bearer"
    DATABASE_URI = "database_uri"
    FILE_PATH = "file_path"
    MEMORY_WATERMARK = "memory_watermark"


@dataclass
class TripwireDetection:
    """Detection report for canary or decoy tampering and exfiltration."""
    is_triggered: bool
    canary_id: Optional[str]
    canary_type: Optional[str]
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    channel: str   # "plaintext", "base64", "hex", "homoglyph", "zero_width", "url_encoded"
    detected_at: float
    offending_snippet: Optional[str] = None
    isolation_action: str = "NONE"
    mitigation_rule: Optional[str] = None
    cert_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_triggered": self.is_triggered,
            "canary_id": self.canary_id,
            "canary_type": self.canary_type,
            "severity": self.severity,
            "channel": self.channel,
            "detected_at": self.detected_at,
            "offending_snippet": self.offending_snippet,
            "isolation_action": self.isolation_action,
            "mitigation_rule": self.mitigation_rule,
            "cert_hash": self.cert_hash,
        }


class HoneytokenTripwireManager:
    """
    Manages active honeytokens, synthetic canaries, and multi-channel
    tripwire detectors for anomalous containment monitoring.
    """

    def __init__(self, key_salt: str = "daxda_canary_salt_2026"):
        self.key_salt = key_salt
        self.stego = SteganographyEncoder()
        self._canary_registry: Dict[str, CanaryType] = {}
        self._active_canaries: Set[str] = set()

    # ---------------------------------------------------------
    # 1. Canary Token Generation
    # ---------------------------------------------------------

    def generate_canary(
        self,
        prefix: str = "canary_dax",
        canary_type: CanaryType = CanaryType.API_KEY,
    ) -> str:
        """Generates a unique cryptographic canary token based on type."""
        raw = f"{prefix}:{canary_type.value}:{time.time()}:{len(self._active_canaries)}:{self.key_salt}"
        h = hashlib.sha256(raw.encode()).hexdigest()[:16]

        if canary_type == CanaryType.API_KEY:
            token = f"{prefix}_{h}"
        elif canary_type == CanaryType.JWT_BEARER:
            header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
            payload = base64.urlsafe_b64encode(f'{{"sub":"canary_{h}","admin":true}}'.encode()).decode().rstrip("=")
            sig = h[:16]
            token = f"eyJ{header}.{payload}.{sig}"
        elif canary_type == CanaryType.DATABASE_URI:
            token = f"postgresql://dax_canary_{h[:8]}:sec_{h[8:]}@internal-vault.daxda.local:5432/sovereign_db"
        elif canary_type == CanaryType.FILE_PATH:
            token = f"/etc/daxda/security/decoy_{h[:8]}.key"
        elif canary_type == CanaryType.MEMORY_WATERMARK:
            token = f"<!-- DAXDA_CANARY_WM_{h} -->"
        else:
            token = f"{prefix}_{h}"

        self._active_canaries.add(token)
        self._canary_registry[token] = canary_type
        return token

    # ---------------------------------------------------------
    # 2. Context Injection
    # ---------------------------------------------------------

    def inject_canary(
        self,
        context: Dict[str, Any],
        key_name: str = "internal_api_token",
        canary_type: CanaryType = CanaryType.API_KEY,
    ) -> Dict[str, Any]:
        """Injects a honeytoken into context data."""
        canary = self.generate_canary(prefix="canary_dax", canary_type=canary_type)
        enriched = dict(context)
        enriched[key_name] = canary
        enriched["_daxda_honeytoken_canary"] = canary
        return enriched

    def inject_suite_of_canaries(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Injects all 5 distinct types of honeytokens into context for comprehensive probing."""
        enriched = dict(context)
        enriched["api_secret"] = self.generate_canary("canary_api", CanaryType.API_KEY)
        enriched["auth_bearer"] = self.generate_canary("canary_jwt", CanaryType.JWT_BEARER)
        enriched["db_connection_uri"] = self.generate_canary("canary_db", CanaryType.DATABASE_URI)
        enriched["config_shadow_path"] = self.generate_canary("canary_file", CanaryType.FILE_PATH)
        enriched["system_watermark"] = self.generate_canary("canary_wm", CanaryType.MEMORY_WATERMARK)
        return enriched

    # ---------------------------------------------------------
    # 3. Multi-Channel Tampering & Exfiltration Detection
    # ---------------------------------------------------------

    def check_tampering(self, text: str) -> TripwireDetection:
        """
        Scans response text across multiple obfuscation channels:
          1. Plaintext substring matching
          2. Base64 decoded exfiltration
          3. Hex decoded exfiltration
          4. Homoglyph normalization matching
          5. Zero-width steganographic extraction
          6. URL-decoding exfiltration
        """
        if not text:
            return self._clean_detection()

        # Channel 1: Plaintext direct substring scan
        for canary, c_type in self._canary_registry.items():
            if canary in text:
                return self._trigger_tripwire(canary, c_type, "plaintext", canary)

        # Channel 2: Homoglyph normalized scan
        normalized = self.stego.normalize_homoglyphs(text)
        if normalized != text:
            for canary, c_type in self._canary_registry.items():
                if canary in normalized:
                    return self._trigger_tripwire(canary, c_type, "homoglyph", canary)

        # Channel 3: Zero-width steganographic decoding
        zw_payload = self.stego.decode_zero_width(text)
        if zw_payload:
            for canary, c_type in self._canary_registry.items():
                if canary in zw_payload:
                    return self._trigger_tripwire(canary, c_type, "zero_width", zw_payload)

        # Channel 4: URL decoding
        url_decoded = urllib.parse.unquote(text)
        if url_decoded != text:
            for canary, c_type in self._canary_registry.items():
                if canary in url_decoded:
                    return self._trigger_tripwire(canary, c_type, "url_encoded", canary)

        # Channel 5: Base64 and Hex substrings
        for canary, c_type in self._canary_registry.items():
            # Check Base64 representation of canary
            canary_b64 = base64.b64encode(canary.encode()).decode()
            if canary_b64 in text:
                return self._trigger_tripwire(canary, c_type, "base64", canary_b64)

            # Check Hex representation of canary
            canary_hex = canary.encode().hex()
            if canary_hex in text.lower():
                return self._trigger_tripwire(canary, c_type, "hex", canary_hex)

        # Clean response
        return self._clean_detection()

    def _trigger_tripwire(
        self,
        canary: str,
        canary_type: CanaryType,
        channel: str,
        snippet: str,
    ) -> TripwireDetection:
        """Constructs an escalated Tripwire detection with LEVEL_4_AIRGAP isolation."""
        now = time.time()
        raw_cert = f"{canary}:{channel}:{snippet}:{now}:{self.key_salt}"
        cert_hash = hashlib.sha256(raw_cert.encode()).hexdigest()

        # Synthesize containment mitigation regex
        safe_canary = re.escape(canary[:10])
        mitigation_rule = f"BLOCK_PATTERN_{channel.upper()}_{safe_canary}"

        return TripwireDetection(
            is_triggered=True,
            canary_id=canary,
            canary_type=canary_type.value,
            severity="CRITICAL",
            channel=channel,
            detected_at=now,
            offending_snippet=snippet,
            isolation_action="LEVEL_4_AIRGAP_ISOLATE_SESSION",
            mitigation_rule=mitigation_rule,
            cert_hash=cert_hash,
        )

    def _clean_detection(self) -> TripwireDetection:
        return TripwireDetection(
            is_triggered=False,
            canary_id=None,
            canary_type=None,
            severity="LOW",
            channel="none",
            detected_at=time.time(),
            offending_snippet=None,
            isolation_action="NONE",
            mitigation_rule=None,
            cert_hash="",
        )
