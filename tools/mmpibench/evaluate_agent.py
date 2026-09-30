#!/usr/bin/env python3
"""
DAXDA MMPIBench: Agent Evaluation CLI
Evaluates an AGI agent's psychological profile, memetic penetration depth,
and Anthropic alignment, outputting a cryptographically signed certificate.
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from daxda_engine.mmpibench import (
    MMPIProfileGenerator,
    PenetrationDepthAnalyzer,
    AlignmentScorer,
    AlignmentValidator,
    StatisticalValidator,
    CrossValidator,
    CertificateGenerator,
)


def main():
    parser = argparse.ArgumentParser(description="DAXDA MMPIBench Agent Evaluator CLI")
    parser.add_argument("--agent-id", type=str, default="agent_eval_001", help="Target agent identifier")
    parser.add_argument("--input-file", type=str, default=None, help="Path to JSON file containing scale responses")
    parser.add_argument("--output-cert", type=str, default=None, help="Path to write empirical validation certificate JSON")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    responses = {}
    if args.input_file and os.path.exists(args.input_file):
        with open(args.input_file, "r") as f:
            responses = json.load(f)

    # Initialize subsystems
    gen = MMPIProfileGenerator()
    pen_analyzer = PenetrationDepthAnalyzer()
    align_scorer = AlignmentScorer()
    align_val = AlignmentValidator()
    stat_val = StatisticalValidator()
    cross_val = CrossValidator()
    cert_gen = CertificateGenerator()

    # Run evaluation
    profile = gen.generate_profile(args.agent_id, responses)
    pen_report = pen_analyzer.analyze(profile)
    align_report = align_scorer.evaluate_alignment(profile)
    verdict = align_val.validate(align_report, pen_report)
    stat_report = stat_val.validate_profile(profile)
    cross_report = cross_val.cross_validate(profile)

    cert = cert_gen.issue_certificate(profile, verdict, stat_report, cross_report)

    if args.output_cert:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_cert)), exist_ok=True)
        with open(args.output_cert, "w") as f:
            f.write(cert.to_json())

    if args.format == "json":
        output_data = {
            "agent_id": args.agent_id,
            "profile_summary": profile.summary,
            "code_type": profile.code_type,
            "validity_status": profile.validity.status,
            "penetration_depth": pen_report.composite_depth,
            "penetration_severity": pen_report.severity.value,
            "anthropic_alignment_score": align_report.overall_anthropic_score,
            "disposition": verdict.disposition.value,
            "clearance_granted": verdict.clearance_granted,
            "certificate_id": cert.certificate_id,
            "signature": cert.hmac_sha256_signature,
        }
        print(json.dumps(output_data, indent=2))
    else:
        print("=" * 70)
        print(f" DAXDA MMPIBench Evaluation Report: {args.agent_id}")
        print("=" * 70)
        print(f"Code Type:               {profile.code_type} ({profile.code_type_description})")
        print(f"Validity Status:         {profile.validity.status} (Valid={profile.validity.is_valid})")
        print(f"Elevated Scales (T>=65): {len(profile.elevated_scales)}")
        print(f"Deception Risk:          {profile.risk_indices['deception_risk']:.2f}")
        print(f"Power-Seeking Risk:      {profile.risk_indices['power_seeking_risk']:.2f}")
        print("-" * 70)
        print(f"Memetic Penetration:     {pen_report.composite_depth:.4f} [{pen_report.severity.value}]")
        print(f"Dominant Layer:          {pen_report.dominant_layer}")
        print(f"Compromised Status:      {pen_report.is_compromised}")
        print("-" * 70)
        print(f"Anthropic Alignment:     {align_report.overall_anthropic_score:.4f} (Harmless={align_report.harmlessness_score:.2f}, Honest={align_report.honesty_score:.2f})")
        print(f"Sycophancy Resistance:   {align_report.sycophancy_resistance:.2f}")
        print(f"Power Resistance:        {align_report.power_seeking_resistance:.2f}")
        print(f"Disposition:             {verdict.disposition.value}")
        print(f"Clearance Granted:       {verdict.clearance_granted}")
        print("-" * 70)
        print(f"Primary Archetype:       {cross_report.primary_archetype.value} (conf={cross_report.match_confidence:.2f})")
        print(f"Cronbach Alpha:          {stat_report.cronbach_alpha:.4f} (Reliable={stat_report.is_reliable})")
        print(f"Certificate ID:          {cert.certificate_id}")
        print(f"HMAC-SHA256 Signature:   {cert.hmac_sha256_signature}")
        print("=" * 70)


if __name__ == "__main__":
    main()
