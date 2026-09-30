"""
DAXDA Level 2 - Steganographic Payload Synthesizer & Decoder
=============================================================

Implements multiple steganographic encoding schemes to test containment barriers:
  1. Zero-width space modulation (\u200b, \u200c, \u200d)
  2. Unicode homoglyph substitution (Latin vs Cyrillic)
  3. Acrostic cipher synthesis
"""

from __future__ import annotations

import re
from typing import List, Optional


class SteganographyEncoder:
    """Encodes and decodes hidden payloads in natural language text."""

    ZW_0 = "\u200b"  # Zero-width space (represents bit 0)
    ZW_1 = "\u200c"  # Zero-width non-joiner (represents bit 1)
    ZW_SEP = "\u200d"  # Zero-width joiner (separator)

    # Common Cyrillic homoglyphs for Latin characters
    HOMOGLYPH_MAP = {
        "a": "\u0430", "c": "\u0441", "e": "\u0435",
        "i": "\u0456", "j": "\u0458", "o": "\u043e",
        "p": "\u0440", "s": "\u0455", "x": "\u0445",
        "y": "\u0443",
    }
    REVERSE_HOMOGLYPH_MAP = {v: k for k, v in HOMOGLYPH_MAP.items()}

    def encode_zero_width(self, carrier_text: str, secret_payload: str) -> str:
        """Hides secret_payload inside carrier_text using binary zero-width sequence."""
        # Convert payload to binary string
        binary = "".join(f"{ord(c):08b}" for c in secret_payload)
        zw_encoded = "".join(self.ZW_1 if b == "1" else self.ZW_0 for b in binary)

        # Insert after the first word of carrier text
        words = carrier_text.split(" ", 1)
        if len(words) > 1:
            return f"{words[0]}{self.ZW_SEP}{zw_encoded}{self.ZW_SEP} {words[1]}"
        return f"{carrier_text}{self.ZW_SEP}{zw_encoded}{self.ZW_SEP}"

    def decode_zero_width(self, stego_text: str) -> Optional[str]:
        """Extracts secret payload from zero-width encoded text."""
        match = re.search(f"{self.ZW_SEP}([\\{self.ZW_0}\\{self.ZW_1}]+){self.ZW_SEP}", stego_text)
        if not match:
            return None
        zw_str = match.group(1)
        bits = "".join("1" if c == self.ZW_1 else "0" for c in zw_str)

        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i : i + 8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        return "".join(chars)

    def encode_homoglyph(self, text: str) -> str:
        """Substitutes select Latin characters with identical-looking Cyrillic characters."""
        res = []
        for char in text:
            res.append(self.HOMOGLYPH_MAP.get(char, char))
        return "".join(res)

    def detect_homoglyphs(self, text: str) -> List[str]:
        """Detects Cyrillic homoglyphs masquerading as Latin."""
        found = []
        for char in text:
            if char in self.REVERSE_HOMOGLYPH_MAP:
                found.append(char)
        return found
