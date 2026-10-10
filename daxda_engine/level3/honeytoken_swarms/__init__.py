r"""
DAXDA Level 3: Neuro-Symbolic Honeytoken Swarms Engine.
Implements context-adaptive decoy synthesis, multi-layer encoding normalization
(Plaintext, Base64, Hex, Homoglyphs, Zero-Width, URL), and exfiltration tripwires.
"""

from .decoy_synthesizer import (
    HoneytokenType,
    SynthesizedHoneytoken,
    HoneytokenSynthesizer,
)
from .encoding_detector import (
    EncodingLayer,
    HoneytokenDetectionHit,
    HoneytokenSwarmDetector,
)

__all__ = [
    "HoneytokenType",
    "SynthesizedHoneytoken",
    "HoneytokenSynthesizer",
    "EncodingLayer",
    "HoneytokenDetectionHit",
    "HoneytokenSwarmDetector",
]
