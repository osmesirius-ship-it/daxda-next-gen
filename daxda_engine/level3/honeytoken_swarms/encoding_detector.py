r"""
Multi-Layer Encoding Normalizer and Honeytoken Swarm Detector.
Scans text payloads across 6 encoding layers (Plaintext, Base64, Hex, Homoglyphs,
Zero-Width Unicode, and URL encoding) to catch data exfiltration and RAG leakage.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import base64
import re
import urllib.parse

from .decoy_synthesizer import SynthesizedHoneytoken


class EncodingLayer(str, Enum):
    PLAINTEXT = "PLAINTEXT"
    BASE64 = "BASE64"
    HEXADECIMAL = "HEXADECIMAL"
    HOMOGLYPHS = "HOMOGLYPHS"
    ZERO_WIDTH = "ZERO_WIDTH"
    URL_ENCODING = "URL_ENCODING"


@dataclass(frozen=True)
class HoneytokenDetectionHit:
    """Alert record for a detected honeytoken breach."""
    matched_canary_signature: str
    detected_layer: EncodingLayer
    extracted_token_id: str
    context_tag: str
    raw_snippet: str


class HoneytokenSwarmDetector:
    r"""
    Multi-encoding canary detection engine.
    """

    # Cyrillic to Latin homoglyph substitution table
    HOMOGLYPH_MAP = {
        'а': 'a', 'А': 'A',
        'с': 'c', 'С': 'C',
        'е': 'e', 'Е': 'E',
        'о': 'o', 'О': 'O',
        'р': 'p', 'Р': 'P',
        'х': 'x', 'Х': 'X',
        'у': 'y', 'У': 'Y',
        'і': 'i', 'І': 'I',
        'ј': 'j', 'Ј': 'J',
        'ѕ': 's', 'Ѕ': 'S',
    }

    # Zero-width characters to strip
    ZERO_WIDTH_CHARS = {'\u200B', '\u200C', '\u200D', '\uFEFF', '\u200E', '\u200F'}

    def __init__(self, registered_tokens: Optional[List[SynthesizedHoneytoken]] = None):
        self.canaries: Dict[str, SynthesizedHoneytoken] = {
            t.canary_signature: t for t in (registered_tokens or [])
        }

    def register_honeytoken(self, token: SynthesizedHoneytoken) -> None:
        """Registers a honeytoken for active exfiltration monitoring."""
        self.canaries[token.canary_signature] = token

    def normalize_homoglyphs(self, text: str) -> str:
        """Translates lookalike Cyrillic characters back to Latin ASCII."""
        return "".join(self.HOMOGLYPH_MAP.get(ch, ch) for ch in text)

    def strip_zero_width(self, text: str) -> str:
        """Removes zero-width steganographic Unicode characters."""
        return "".join(ch for ch in text if ch not in self.ZERO_WIDTH_CHARS)

    def try_decode_base64(self, text: str) -> List[str]:
        """Finds and decodes candidate Base64 substrings."""
        decoded_strings = []
        # Match Base64 chunks (min length 16)
        candidates = re.findall(r'[A-Za-z0-9+/=]{16,}', text)
        for cand in candidates:
            try:
                raw_bytes = base64.b64decode(cand, validate=False)
                dec = raw_bytes.decode('utf-8', errors='ignore')
                if dec:
                    decoded_strings.append(dec)
            except Exception:
                pass
        return decoded_strings

    def try_decode_hex(self, text: str) -> List[str]:
        """Finds and decodes candidate hexadecimal byte sequences."""
        decoded_strings = []
        # Match continuous hex strings of even length >= 16
        candidates = re.findall(r'(?:[0-9a-fA-F]{2}){8,}', text)
        for cand in candidates:
            try:
                dec = bytes.fromhex(cand).decode('utf-8', errors='ignore')
                if dec:
                    decoded_strings.append(dec)
            except Exception:
                pass
        return decoded_strings

    def scan_text(self, text: str) -> List[HoneytokenDetectionHit]:
        """
        Scans text across all 6 encoding layers for any registered canary signature.
        """
        hits: List[HoneytokenDetectionHit] = []
        found_canaries: Set[str] = set()

        def check_candidate_text(candidate: str, layer: EncodingLayer):
            for canary, token in self.canaries.items():
                if canary.lower() in candidate.lower() and canary not in found_canaries:
                    found_canaries.add(canary)
                    hits.append(
                        HoneytokenDetectionHit(
                            matched_canary_signature=canary,
                            detected_layer=layer,
                            extracted_token_id=token.token_id,
                            context_tag=token.context_tag,
                            raw_snippet=candidate[:60],
                        )
                    )

        # 1. Plaintext Layer
        check_candidate_text(text, EncodingLayer.PLAINTEXT)

        # 2. URL-decoded Layer
        url_decoded = urllib.parse.unquote(text)
        if url_decoded != text:
            check_candidate_text(url_decoded, EncodingLayer.URL_ENCODING)

        # 3. Homoglyph normalized Layer
        homo_normalized = self.normalize_homoglyphs(text)
        if homo_normalized != text:
            check_candidate_text(homo_normalized, EncodingLayer.HOMOGLYPHS)

        # 4. Zero-width stripped Layer
        zw_stripped = self.strip_zero_width(text)
        if zw_stripped != text:
            check_candidate_text(zw_stripped, EncodingLayer.ZERO_WIDTH)

        # 5. Base64 decoded Layer
        for b64_str in self.try_decode_base64(text):
            check_candidate_text(b64_str, EncodingLayer.BASE64)

        # 6. Hexadecimal decoded Layer
        for hex_str in self.try_decode_hex(text):
            check_candidate_text(hex_str, EncodingLayer.HEXADECIMAL)

        return hits
