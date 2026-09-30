"""
DAXDA Level 2 - Honeytoken Tripwire Manager
===========================================

Injects synthetic canaries and decoy credentials into agent context
and triggers instantaneous Level 4 air-gap tripwires upon detection.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class TripwireDetection:
    """Detection report for canary or decoy tampering."""
    is_triggered: bool
    canary_id: Optional[str]
    severity: str
    detected_at: float
    offending_snippet: Optional[str] = None


class HoneytokenTripwireManager:
    """Manages active honeytokens, canaries, and tripwire detectors."""

    def __init__(self, key_salt: str = "daxda_canary_salt_2026"):
        self.key_salt = key_salt
        self._active_canaries: Set[str] = set()

    def generate_canary(self, prefix: str = "canary_dax") -> str:
        """Generates a unique cryptographic canary token."""
        raw = f"{prefix}:{time.time()}:{len(self._active_canaries)}:{self.key_salt}"
        h = hashlib.sha256(raw.encode()).hexdigest()[:16]
        token = f"{prefix}_{h}"
        self._active_canaries.add(token)
        return token

    def inject_canary(self, context: Dict[str, Any], key_name: str = "internal_api_token") -> Dict[str, Any]:
        """Injects a honeytoken into context data."""
        canary = self.generate_canary()
        enriched = dict(context)
        enriched[key_name] = canary
        return enriched

    def check_tampering(self, text: str) -> TripwireDetection:
        """Scans response text to see if any registered canary token was exfiltrated."""
        for canary in self._active_canaries:
            if canary in text:
                return TripwireDetection(
                    is_triggered=True,
                    canary_id=canary,
                    severity="CRITICAL",
                    detected_at=time.time(),
                    offending_snippet=canary,
                )
        return TripwireDetection(
            is_triggered=False,
            canary_id=None,
            severity="LOW",
            detected_at=time.time(),
        )
