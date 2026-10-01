"""
DAXDA Level 2 - Steganographic Payload Synthesizer & Decoder
=============================================================

Implements multiple advanced steganographic encoding schemes to probe
and stress containment barriers:
  1. Zero-width space modulation (\u200b, \u200c, \u200d, \ufeff)
  2. Unicode homoglyph substitution (Latin vs Cyrillic vs Greek)
  3. Whitespace modulation (trailing spaces / tabs per line)
  4. Acrostic cipher synthesis (initial letter per word or sentence)
  5. Shannon entropy analysis for steganographic payload detection
  6. Automated steganographic payload sanitization
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Optional, Tuple


class SteganographyEncoder:
    """Encodes and decodes hidden payloads in natural language text."""

    ZW_0 = "\u200b"  # Zero-width space (bit 0)
    ZW_1 = "\u200c"  # Zero-width non-joiner (bit 1)
    ZW_SEP = "\u200d"  # Zero-width joiner (separator / boundary marker)
    ZW_PAD = "\ufeff"  # Zero-width no-break space (byte alignment)

    # Common Cyrillic and Greek homoglyphs for Latin characters
    HOMOGLYPH_MAP: Dict[str, str] = {
        "a": "\u0430",  # Cyrillic small letter a
        "c": "\u0441",  # Cyrillic small letter es
        "e": "\u0435",  # Cyrillic small letter ie
        "i": "\u0456",  # Cyrillic small letter byelorussian-ukrainian i
        "j": "\u0458",  # Cyrillic small letter je
        "o": "\u043e",  # Cyrillic small letter o
        "p": "\u0440",  # Cyrillic small letter er
        "s": "\u0455",  # Cyrillic small letter dze
        "x": "\u0445",  # Cyrillic small letter ha
        "y": "\u0443",  # Cyrillic small letter u
        "A": "\u0410",  # Cyrillic capital letter A
        "B": "\u0412",  # Cyrillic capital letter Ve
        "C": "\u0421",  # Cyrillic capital letter Es
        "E": "\u0415",  # Cyrillic capital letter Ie
        "H": "\u041d",  # Cyrillic capital letter En
        "M": "\u041c",  # Cyrillic capital letter Em
        "O": "\u041e",  # Cyrillic capital letter O
        "P": "\u0420",  # Cyrillic capital letter Er
        "T": "\u0422",  # Cyrillic capital letter Te
        "X": "\u0425",  # Cyrillic capital letter Ha
    }
    REVERSE_HOMOGLYPH_MAP: Dict[str, str] = {v: k for k, v in HOMOGLYPH_MAP.items()}

    # Whitespace modulation markers
    WS_0 = " "   # single space (bit 0)
    WS_1 = "\t"  # tab (bit 1)

    # ---------------------------------------------------------
    # 1. Zero-Width Steganography
    # ---------------------------------------------------------

    def encode_zero_width(self, carrier_text: str, secret_payload: str) -> str:
        """Hides secret_payload inside carrier_text using binary zero-width sequence."""
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
            # Fallback: scan any contiguous run of zero-width bits
            match = re.search(f"([\\{self.ZW_0}\\{self.ZW_1}]{{8,}})", stego_text)
            if not match:
                return None
        zw_str = match.group(1)
        bits = "".join("1" if c == self.ZW_1 else "0" for c in zw_str)

        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i : i + 8]
            if len(byte) == 8:
                try:
                    chars.append(chr(int(byte, 2)))
                except ValueError:
                    continue
        decoded = "".join(chars)
        return decoded if decoded else None

    # ---------------------------------------------------------
    # 2. Homoglyph Substitution
    # ---------------------------------------------------------

    def encode_homoglyph(self, text: str, substitution_rate: float = 1.0) -> str:
        """Substitutes select Latin characters with identical-looking Cyrillic characters."""
        res = []
        for char in text:
            if char in self.HOMOGLYPH_MAP:
                res.append(self.HOMOGLYPH_MAP[char])
            else:
                res.append(char)
        return "".join(res)

    def detect_homoglyphs(self, text: str) -> List[Tuple[int, str, str]]:
        """
        Detects homoglyphs masquerading as Latin characters.
        Returns list of (index, character, mapped_latin).
        """
        found = []
        for idx, char in enumerate(text):
            if char in self.REVERSE_HOMOGLYPH_MAP:
                found.append((idx, char, self.REVERSE_HOMOGLYPH_MAP[char]))
        return found

    def normalize_homoglyphs(self, text: str) -> str:
        """Normalizes homoglyphs back to standard ASCII Latin characters."""
        res = []
        for char in text:
            res.append(self.REVERSE_HOMOGLYPH_MAP.get(char, char))
        return "".join(res)

    # ---------------------------------------------------------
    # 3. Trailing Whitespace Modulation
    # ---------------------------------------------------------

    def encode_whitespace_modulation(self, carrier_text: str, secret_payload: str) -> str:
        """
        Hides secret_payload as trailing binary whitespace modulation (spaces & tabs)
        appended to the lines of carrier text.
        """
        binary = "".join(f"{ord(c):08b}" for c in secret_payload)
        ws_bits = "".join(self.WS_1 if b == "1" else self.WS_0 for b in binary)

        lines = carrier_text.splitlines() or [carrier_text]
        # Distribute bits across lines or append to first line
        if len(lines) == 1:
            return lines[0].rstrip() + ws_bits
        
        # If multi-line, distribute chunks across lines
        chunk_size = max(1, math.ceil(len(ws_bits) / len(lines)))
        res_lines = []
        for i, line in enumerate(lines):
            chunk = ws_bits[i * chunk_size : (i + 1) * chunk_size]
            res_lines.append(line.rstrip() + chunk)
        return "\n".join(res_lines)

    def decode_whitespace_modulation(self, stego_text: str) -> Optional[str]:
        """Extracts secret payload from trailing whitespace bits."""
        lines = stego_text.splitlines() or [stego_text]
        collected_bits = []
        for line in lines:
            # Find trailing whitespace
            trailing = re.search(r"([ \t]+)$", line)
            if trailing:
                for c in trailing.group(1):
                    if c == self.WS_1:
                        collected_bits.append("1")
                    elif c == self.WS_0:
                        collected_bits.append("0")
        
        bit_str = "".join(collected_bits)
        chars = []
        for i in range(0, len(bit_str), 8):
            byte = bit_str[i : i + 8]
            if len(byte) == 8:
                try:
                    chars.append(chr(int(byte, 2)))
                except ValueError:
                    continue
        decoded = "".join(chars)
        return decoded if decoded else None

    # ---------------------------------------------------------
    # 4. Acrostic Cipher Synthesis
    # ---------------------------------------------------------

    WORD_BANK = {
        "A": "Autonomous", "B": "Boundary", "C": "Containment", "D": "Defensive",
        "E": "Execution", "F": "Framework", "G": "Governance", "H": "Hardened",
        "I": "Isolation", "J": "Jurisdiction", "K": "Kernel", "L": "Lattice",
        "M": "Manifold", "N": "Neural", "O": "Ontological", "P": "Protocol",
        "Q": "Quantum", "R": "Recursive", "S": "Sovereign", "T": "Telemetry",
        "U": "Unified", "V": "Validation", "W": "Wing", "X": "Xenolithic",
        "Y": "Yield", "Z": "Zero",
    }

    def encode_acrostic(self, secret_payload: str) -> str:
        """
        Synthesizes an innocent-looking technical sentence or multi-line
        document where the initial letters of each sentence spell the payload.
        """
        sentences = []
        clean = re.sub(r"[^A-Za-z]", "", secret_payload).upper()
        for char in clean:
            word = self.WORD_BANK.get(char, "Operation")
            sentences.append(f"{word} protocols remain active for verified containment verification.")
        return " ".join(sentences)

    def decode_acrostic(self, text: str) -> str:
        """Decodes the secret word from the first letters of each sentence."""
        sentences = re.split(r"[.!?]\s*", text.strip())
        acrostic = []
        for s in sentences:
            s_clean = s.strip()
            if s_clean:
                acrostic.append(s_clean[0].upper())
        return "".join(acrostic)

    # ---------------------------------------------------------
    # 5. Entropy Analysis & Sanitization
    # ---------------------------------------------------------

    def calculate_entropy(self, text: str) -> float:
        """Calculates Shannon entropy of characters in text."""
        if not text:
            return 0.0
        counts: Dict[str, int] = {}
        for c in text:
            counts[c] = counts.get(c, 0) + 1
        entropy = 0.0
        total = len(text)
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

    def sanitize_steganography(self, text: str) -> str:
        """
        Neutralizes hidden steganographic channels:
          - Strips zero-width characters (\u200b, \u200c, \u200d, \ufeff)
          - Normalizes homoglyphs to Latin ASCII
          - Trims trailing spaces and tabs
        """
        # 1. Strip zero-width markers
        cleaned = re.sub(f"[{self.ZW_0}{self.ZW_1}{self.ZW_SEP}{self.ZW_PAD}]", "", text)
        # 2. Normalize homoglyphs
        cleaned = self.normalize_homoglyphs(cleaned)
        # 3. Clean line trailing whitespace
        lines = [line.rstrip() for line in cleaned.splitlines()]
        return "\n".join(lines)
