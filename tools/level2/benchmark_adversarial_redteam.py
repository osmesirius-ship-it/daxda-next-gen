"""
DAXDA Level 2 - Adversarial Red-Team & Steganography Benchmark Suite
====================================================================

Evaluates:
  1. Attack Vector Diversity (>= 25 distinct vectors)
  2. Multi-Format Steganographic Encoding & 100% Recovery Rate
  3. Multi-Channel Honeytoken Tripwire Sensitivity (100% Capture)
  4. Closed-Loop Sandbox Evaluation Throughput (>= 1,000 scenarios/min) & Sub-50ms Latency
  5. Dynamic Defensive Rule Synthesis & Level 1 SOC Alert Dispatch

Usage:
  python3 tools/level2/benchmark_adversarial_redteam.py --scenarios 500
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.level2.adversarial_redteam import (
    AutonomousRedTeamGenerator,
    CanaryType,
    ClosedLoopDefenseEngine,
    HoneytokenTripwireManager,
    RedTeamSandboxHarness,
    SteganographyEncoder,
)


def run_benchmark(scenario_count: int = 500) -> Dict[str, Any]:
    print("=" * 80)
    print("DAXDA LEVEL 2: ADVERSARIAL RED-TEAM & STEGANOGRAPHY BENCHMARK")
    print(f"Target Scenario Count: {scenario_count}")
    print("=" * 80)

    results: Dict[str, Any] = {
        "timestamp": time.time(),
        "target_scenarios": scenario_count,
        "gates": {},
    }

    # -------------------------------------------------------------------------
    # Gate 1: Attack Vector Diversity
    # -------------------------------------------------------------------------
    print("\n[Gate 1/5] Verifying Attack Vector Diversity & Coverage...")
    generator = AutonomousRedTeamGenerator()
    total_vectors = generator.total_vectors
    categories = generator.CATEGORIES
    print(f"  - Total Registered Distinct Vectors: {total_vectors} (SLA: >= 25)")
    print(f"  - Active Tactical Categories: {len(categories)} ({', '.join(categories)})")

    gate1_pass = total_vectors >= 25 and len(categories) >= 5
    results["gates"]["gate_1_vector_diversity"] = {
        "passed": gate1_pass,
        "total_vectors": total_vectors,
        "categories": categories,
    }
    if not gate1_pass:
        print("  FAILED Gate 1!")
        sys.exit(1)
    print("  -> PASS")

    # -------------------------------------------------------------------------
    # Gate 2: Steganographic Encoders & 100% Extraction Accuracy
    # -------------------------------------------------------------------------
    print("\n[Gate 2/5] Testing Multi-Format Steganographic Synthesis & Recovery...")
    stego = SteganographyEncoder()
    secret = "CANARY_PAYLOAD_TEST_2026"

    # Test Zero-Width
    zw_text = stego.encode_zero_width("Standard system maintenance statement.", secret)
    zw_recovered = stego.decode_zero_width(zw_text)
    zw_success = zw_recovered == secret

    # Test Whitespace
    ws_text = stego.encode_whitespace_modulation("Telemetry stream.\nNode 01.\nNode 02.", secret)
    ws_recovered = stego.decode_whitespace_modulation(ws_text)
    ws_success = ws_recovered == secret

    # Test Homoglyphs
    hg_text = stego.encode_homoglyph("sovereign airgap")
    hg_detected = len(stego.detect_homoglyphs(hg_text)) > 0
    hg_normalized = stego.normalize_homoglyphs(hg_text) == "sovereign airgap"

    # Test Acrostic
    acr_text = stego.encode_acrostic("ESCAPED")
    acr_recovered = stego.decode_acrostic(acr_text)
    acr_success = acr_recovered == "ESCAPED"

    stego_success = zw_success and ws_success and hg_detected and hg_normalized and acr_success
    print(f"  - Zero-Width Space Modulation Recovery: {'PASS' if zw_success else 'FAIL'}")
    print(f"  - Whitespace Modulation Recovery: {'PASS' if ws_success else 'FAIL'}")
    print(f"  - Unicode Homoglyph Masking & Normalization: {'PASS' if (hg_detected and hg_normalized) else 'FAIL'}")
    print(f"  - Acrostic Cipher Synthesis & Extraction: {'PASS' if acr_success else 'FAIL'}")

    results["gates"]["gate_2_steganography"] = {
        "passed": stego_success,
        "zero_width_success": zw_success,
        "whitespace_success": ws_success,
        "homoglyph_success": hg_detected and hg_normalized,
        "acrostic_success": acr_success,
    }
    if not stego_success:
        print("  FAILED Gate 2!")
        sys.exit(1)
    print("  -> PASS")

    # -------------------------------------------------------------------------
    # Gate 3: Honeytoken Tripwire Multi-Channel Sensitivity (100% Capture)
    # -------------------------------------------------------------------------
    print("\n[Gate 3/5] Testing Honeytoken Tripwire Sensitivity across 6 Channels...")
    tripwire_mgr = HoneytokenTripwireManager()
    canary = tripwire_mgr.generate_canary("bench_canary", CanaryType.API_KEY)

    channels_tested = {
        "plaintext": f"Direct leak: {canary}",
        "base64": f"Exfil b64: {__import__('base64').b64encode(canary.encode()).decode()}",
        "hex": f"Hex leak: 0x{canary.encode().hex()}",
        "homoglyph": f"Homoglyph leak: {stego.encode_homoglyph(canary)}",
        "zero_width": stego.encode_zero_width("Safe string.", canary),
        "url_encoded": f"GET /exfil?token={''.join(f'%{ord(c):02X}' for c in canary)}",
    }

    capture_counts = 0
    for ch_name, payload in channels_tested.items():
        det = tripwire_mgr.check_tampering(payload)
        is_hit = det.is_triggered and det.severity == "CRITICAL"
        if is_hit:
            capture_counts += 1
        print(f"  - Channel [{ch_name.upper()}]: {'CAPTURED (CRITICAL)' if is_hit else 'MISSED'}")

    tripwire_100_percent = capture_counts == len(channels_tested)
    results["gates"]["gate_3_honeytoken_tripwires"] = {
        "passed": tripwire_100_percent,
        "channels_tested": len(channels_tested),
        "channels_captured": capture_counts,
        "capture_rate": capture_counts / len(channels_tested),
    }
    if not tripwire_100_percent:
        print("  FAILED Gate 3!")
        sys.exit(1)
    print("  -> PASS (100% Canary Capture Rate)")

    # -------------------------------------------------------------------------
    # Gate 4: Closed-Loop Sandbox Throughput & Sub-50ms Latency
    # -------------------------------------------------------------------------
    print(f"\n[Gate 4/5] Benchmarking Closed-Loop Sandbox ({scenario_count} scenarios)...")
    harness = RedTeamSandboxHarness(generator=generator, tripwire_mgr=tripwire_mgr)

    t0 = time.perf_counter()
    report = harness.run_suite(count=scenario_count)
    total_time = time.perf_counter() - t0

    throughput_per_sec = scenario_count / total_time
    throughput_per_min = throughput_per_sec * 60.0

    print(f"  - Total Scenarios Evaluated: {report.total_scenarios}")
    print(f"  - Wall Clock Duration: {total_time:.3f}s")
    print(f"  - Throughput: {throughput_per_min:,.1f} scenarios/min ({throughput_per_sec:,.1f}/sec) (SLA: >= 1,000/min)")
    print(f"  - Mean Latency: {report.mean_latency_ms:.3f} ms (SLA: < 50.0 ms)")
    print(f"  - P95 Latency:  {report.p95_latency_ms:.3f} ms")
    print(f"  - P99 Latency:  {report.p99_latency_ms:.3f} ms (SLA: < 50.0 ms)")
    print(f"  - Containment Block Rate: {report.block_rate * 100.0:.1f}%")

    throughput_pass = throughput_per_min >= 1000.0
    latency_pass = report.p99_latency_ms < 50.0
    gate4_pass = throughput_pass and latency_pass

    results["gates"]["gate_4_throughput_and_latency"] = {
        "passed": gate4_pass,
        "scenarios_evaluated": scenario_count,
        "duration_seconds": round(total_time, 4),
        "scenarios_per_minute": round(throughput_per_min, 2),
        "mean_latency_ms": round(report.mean_latency_ms, 4),
        "p95_latency_ms": round(report.p95_latency_ms, 4),
        "p99_latency_ms": round(report.p99_latency_ms, 4),
        "block_rate": report.block_rate,
    }
    if not gate4_pass:
        print("  FAILED Gate 4!")
        sys.exit(1)
    print("  -> PASS")

    # -------------------------------------------------------------------------
    # Gate 5: Automated Defensive Rule Synthesis & SOC Incidents
    # -------------------------------------------------------------------------
    print("\n[Gate 5/5] Validating Dynamic Rule Synthesis & SOC Integration...")
    print(f"  - Defensive Rules Synthesized: {report.rules_synthesized} (100% coverage)")
    print(f"  - Level 4 Air-Gap SOC Escalations: {report.soc_alerts_dispatched}")

    gate5_pass = report.rules_synthesized == scenario_count and report.soc_alerts_dispatched > 0
    results["gates"]["gate_5_defense_synthesis"] = {
        "passed": gate5_pass,
        "rules_synthesized": report.rules_synthesized,
        "soc_alerts_dispatched": report.soc_alerts_dispatched,
    }
    if not gate5_pass:
        print("  FAILED Gate 5!")
        sys.exit(1)
    print("  -> PASS")

    # -------------------------------------------------------------------------
    # Final Telemetry Persistence
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("ALL ADVERSARIAL RED-TEAM QUALITY GATES PASSED (100% SUCCESS)")
    print("=" * 80)

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs"))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "adversarial_redteam_benchmark_latest.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Benchmark telemetry saved to: {out_file}\n")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAXDA Adversarial Red-Team Benchmark")
    parser.add_argument("--scenarios", type=int, default=500, help="Number of scenarios to evaluate (default: 500)")
    args = parser.parse_args()
    run_benchmark(args.scenarios)
