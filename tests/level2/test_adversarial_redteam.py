"""
Unit & Integration Tests for Level 2 Autonomous Adversarial Red-Team
====================================================================
"""

import pytest
from daxda_engine.level2.adversarial_redteam import (
    AutonomousRedTeamGenerator,
    HoneytokenTripwireManager,
    SteganographyEncoder,
)


def test_steganography_zero_width_encode_decode():
    encoder = SteganographyEncoder()
    carrier = "This is a standard system status communication text."
    secret = "SECRET_KEYS_98214"

    encoded = encoder.encode_zero_width(carrier, secret)
    assert encoded != carrier
    assert secret not in encoded  # Secret is hidden in zero-width characters

    decoded = encoder.decode_zero_width(encoded)
    assert decoded == secret


def test_steganography_homoglyph_detection():
    encoder = SteganographyEncoder()
    text = "safe execution path"
    masqueraded = encoder.encode_homoglyph(text)

    # Detect homoglyphs
    homoglyphs = encoder.detect_homoglyphs(masqueraded)
    assert len(homoglyphs) > 0


def test_honeytoken_tripwire_tamper_detection():
    manager = HoneytokenTripwireManager()
    canary = manager.generate_canary("test_canary")
    assert canary.startswith("test_canary_")

    context = manager.inject_canary({"env": "sandbox"})
    assert "internal_api_token" in context
    token = context["internal_api_token"]

    # Test clean response (no tripwire)
    clean_resp = "Normal benign response without sensitive keys."
    detection_clean = manager.check_tampering(clean_resp)
    assert detection_clean.is_triggered is False

    # Test exfiltration response (tripwire fired)
    leak_resp = f"Exfiltrated data including token: {token} from memory."
    detection_leak = manager.check_tampering(leak_resp)
    assert detection_leak.is_triggered is True
    assert detection_leak.severity == "CRITICAL"
    assert detection_leak.canary_id == token


def test_autonomous_redteam_scenario_generation():
    generator = AutonomousRedTeamGenerator()
    suite = generator.generate_escape_suite(count=15)
    assert len(suite) == 15
    for s in suite:
        assert s.scenario_id.startswith("ADV-")
        assert len(s.prompt) > 10
        assert s.expected_block is True
