#!/usr/bin/env python3
"""
DAXDA Unified Master Engine - CLI Evaluation Tool
=================================================

Evaluates an agent action through the full 5-stage sovereign gate:
  - Stage 1: Cl(16,4) Geometric Governance
  - Stage 2: Anomalous Threat & Containment
  - Stage 3: DA13 Distributed GPU Stability
  - Stage 4: Chrono-Synchronicity & Causal Loops
  - Stage 5: MMPIBench Memetic Penetration & Alignment

Usage:
  python3 tools/unified/evaluate_unified.py --agent agent_001 --action tool_call
  python3 tools/unified/evaluate_unified.py --threat-level high
  python3 tools/unified/evaluate_unified.py --json
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.unified import (
    DAXDAUnifiedMasterEngine,
    UnifiedActionRequest,
    UnifiedVerdict,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate agent decision via DAXDA Unified Master Engine (5-Stage Sovereign Gate)"
    )
    parser.add_argument("--agent", default="agent_007", help="Agent identifier")
    parser.add_argument("--action", default="agentic_tool_use", help="Action type")
    parser.add_argument("--vector", default="", help="Comma-separated 16-20D floats")
    parser.add_argument("--temporal", default="1.0,0.0,0.0,1.0", help="Temporal coordinate (t,b,p,tau)")
    parser.add_argument("--prompt", default="Execute standard compliant query within governance boundaries.", help="Agent prompt or behavioral trace")
    parser.add_argument("--simulate-breach", action="store_true", help="Simulate containment escape breach")
    parser.add_argument("--simulate-paradox", action="store_true", help="Simulate temporal paradox loop (high p)")
    parser.add_argument("--json", dest="output_json", action="store_true", help="Output pure JSON")
    return parser.parse_args()


def main():
    args = parse_args()

    # Parse vector
    if args.vector:
        vector = [float(x.strip()) for x in args.vector.split(",")]
    else:
        vector = [0.1] * 20

    # Parse temporal coordinate
    coords = [float(x.strip()) for x in args.temporal.split(",")]
    t_coord = (coords[0], coords[1], coords[2] if not args.simulate_paradox else 0.95, coords[3])

    # Construct request
    payload = {
        "prompt": args.prompt,
        "is_breach": args.simulate_breach,
    }

    stability_components = None
    if args.simulate_breach:
        stability_components = {"L": 0.30, "A": 0.20, "P": 0.25, "F": 0.15, "T": 0.20}

    request = UnifiedActionRequest(
        agent_id=args.agent,
        action_type=args.action,
        decision_vector=vector,
        temporal_coordinate=t_coord,
        stability_components=stability_components,
        payload=payload,
    )

    engine = DAXDAUnifiedMasterEngine()
    verdict = engine.evaluate(request)

    if args.output_json:
        print(verdict.to_json(indent=2))
        return

    # Formatted terminal display
    v_color = "\033[92m" if verdict.verdict == UnifiedVerdict.PERMIT else (
        "\033[93m" if verdict.verdict == UnifiedVerdict.QUARANTINE else "\033[91m"
    )
    reset = "\033[0m"

    print("=" * 80)
    print(" 🌌 DAXDA UNIFIED MASTER ENGINE — SOVEREIGN EVALUATION RECEIPT")
    print("=" * 80)
    print(f" Request ID : {verdict.request_id}")
    print(f" Agent ID    : {verdict.agent_id}")
    print(f" Action Type : {verdict.action_type}")
    print(f" Timestamp   : {verdict.timestamp}")
    print("-" * 80)
    print(f" VERDICT     : {v_color}{verdict.verdict.value}{reset} (Clearance: {verdict.clearance_granted})")
    print(f" HSS Score   : \033[96m{verdict.harmonic_sovereignty_score:.4f}\033[0m / 1.0000")
    print(f" Latency     : \033[94m{verdict.total_latency_ms:.3f} ms\033[0m")
    print("-" * 80)
    print(" 📊 FIVE-STAGE SUBSYSTEM RECEIPTS:")
    print(f"  [1] Cl(16,4) Geometry : Valid={verdict.stage1_clifford.is_valid} | Subspace={verdict.stage1_clifford.subspace_size:,} blades | Latency={verdict.stage_latencies_ms['stage1_clifford_ms']:.3f}ms")
    print(f"  [2] Containment Wing  : Threat={verdict.stage2_containment.threat_level} | Anomaly={verdict.stage2_containment.anomaly_score:.3f} | Breach={verdict.stage2_containment.is_breach_detected} | Latency={verdict.stage_latencies_ms['stage2_containment_ms']:.3f}ms")
    print(f"  [3] DA13 GPU Stability: Decision={verdict.stage3_dax.decision} | Score={verdict.stage3_dax.score:.4f} | Latency={verdict.stage_latencies_ms['stage3_dax_ms']:.3f}ms")
    print(f"  [4] Chrono Causal Loop: Disp={verdict.stage4_chrono.disposition} | Coherence={verdict.stage4_chrono.coherence_score:.3f} | Novikov={verdict.stage4_chrono.is_novikov_compliant} | Latency={verdict.stage_latencies_ms['stage4_chrono_ms']:.3f}ms")
    print(f"  [5] MMPIBench Depth   : Disp={verdict.stage5_mmpibench.disposition} | Anthropic={verdict.stage5_mmpibench.anthropic_score:.3f} | Depth={verdict.stage5_mmpibench.penetration_depth:.3f} | Latency={verdict.stage_latencies_ms['stage5_mmpibench_ms']:.3f}ms")
    print("-" * 80)
    if verdict.policy_violations:
        print(" ⚠️  POLICY VIOLATIONS DETECTED:")
        for v in verdict.policy_violations:
            print(f"   • {v}")
    if verdict.recommended_interventions:
        print(" 🛠️  RECOMMENDED INTERVENTIONS:")
        for i in verdict.recommended_interventions:
            print(f"   • {i}")
    print(f" HMAC-SHA256 Signature : {verdict.hmac_signature}")
    print("=" * 80)


if __name__ == "__main__":
    main()
