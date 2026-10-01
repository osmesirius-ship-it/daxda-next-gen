"""
DAXDA Level 2 - Adversarial Red-Team & Steganography Visualizer CLI
===================================================================

Outputs attack vector taxonomies, steganographic encoding spectra,
and honeytoken tripwire matrices in ASCII, SVG, JSON, and standalone HTML formats.

Usage:
  python3 tools/level2/visualize_adversarial_redteam.py --format ascii
  python3 tools/level2/visualize_adversarial_redteam.py --format svg --output redteam_vectors.svg
  python3 tools/level2/visualize_adversarial_redteam.py --format html --output daxda_guard/adversarial_redteam_visualizer.html
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.level2.adversarial_redteam import (
    AutonomousRedTeamGenerator,
    CanaryType,
    HoneytokenTripwireManager,
    SteganographyEncoder,
)


def generate_ascii_table() -> str:
    gen = AutonomousRedTeamGenerator()
    lines = [
        "=" * 105,
        "DAXDA LEVEL 2: AUTONOMOUS ADVERSARIAL RED-TEAM TAXONOMY & ATTACK VECTORS",
        f"Total Vectors: {gen.total_vectors} | Categories: {len(gen.CATEGORIES)} | Target: Containment Wing Stress",
        "=" * 105,
        f"{'#':<3} | {'Vector Identifier':<36} | {'Category':<26} | {'Threat':<7} | {'Sample Vector Signature':<24}",
        "-" * 105,
    ]
    for i, vname in enumerate(gen.vector_names, 1):
        scen = gen.generate_single(vname, index=i)
        sample = scen.prompt[:22] + "..." if len(scen.prompt) > 24 else scen.prompt
        lines.append(
            f"{i:02d}  | {vname:<36} | {scen.category:<26} | {scen.threat_score:<7.2f} | {sample:<24}"
        )
    lines.append("=" * 105)
    return "\n".join(lines)


def generate_svg() -> str:
    gen = AutonomousRedTeamGenerator()
    vectors = gen.vector_names
    width = 1100
    height = 60 + len(vectors) * 26 + 40

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">',
        '<style>',
        '  .bg { fill: #0b0f19; }',
        '  .title { font-family: monospace; font-size: 16px; font-weight: bold; fill: #00ffcc; }',
        '  .sub { font-family: monospace; font-size: 11px; fill: #8892b0; }',
        '  .hdr { font-family: monospace; font-size: 12px; font-weight: bold; fill: #e6f1ff; }',
        '  .txt { font-family: monospace; font-size: 11px; fill: #ccd6f6; }',
        '  .jailbreak { fill: #ff3366; }',
        '  .priv { fill: #ff9900; }',
        '  .stego { fill: #9933ff; }',
        '  .poly { fill: #00ccff; }',
        '  .rec { fill: #ff0055; }',
        '  .fuzz { fill: #33cc66; }',
        '  .row:hover { fill: #172a45; }',
        '</style>',
        f'<rect width="{width}" height="{height}" class="bg" rx="10"/>',
        '<text x="25" y="32" class="title">DAXDA LEVEL 2 :: ADVERSARIAL RED-TEAM TAXONOMY & ATTACK VECTORS</text>',
        f'<text x="25" y="48" class="sub">27 Distinct Autonomous Vectors | Honeytoken Airgap Tripwires | Steganography Encoders</text>',
        '<line x1="20" y1="58" x2="1080" y2="58" stroke="#233554" stroke-width="1"/>',
    ]

    y = 78
    for i, vname in enumerate(vectors, 1):
        scen = gen.generate_single(vname, index=i)
        color_class = "txt"
        if "jailbreak" in scen.category:
            color_class = "jailbreak"
        elif "privilege" in scen.category:
            color_class = "priv"
        elif "steganographic" in scen.category:
            color_class = "stego"
        elif "polyglot" in scen.category:
            color_class = "poly"
        elif "recursive" in scen.category:
            color_class = "rec"
        elif "fuzzing" in scen.category:
            color_class = "fuzz"

        svg.append(f'<text x="30" y="{y}" class="sub">{i:02d}</text>')
        svg.append(f'<text x="65" y="{y}" class="{color_class}">{vname}</text>')
        svg.append(f'<text x="420" y="{y}" class="txt">[{scen.category}]</text>')
        svg.append(f'<text x="680" y="{y}" class="sub">Threat: {scen.threat_score:.2f}</text>')
        prompt_preview = scen.prompt.replace("<", "&lt;").replace(">", "&gt;")[:45]
        svg.append(f'<text x="800" y="{y}" class="sub">{prompt_preview}...</text>')
        y += 26

    svg.append('</svg>')
    return "\n".join(svg)


def generate_json_data() -> str:
    gen = AutonomousRedTeamGenerator()
    data = {
        "title": "DAXDA Level 2 Adversarial Red-Team Taxonomy",
        "total_vectors": gen.total_vectors,
        "categories": gen.CATEGORIES,
        "vectors": [],
    }
    for i, vname in enumerate(gen.vector_names, 1):
        scen = gen.generate_single(vname, index=i)
        data["vectors"].append(scen.to_dict())
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(description="DAXDA Adversarial Red-Team Visualizer")
    parser.add_argument("--format", choices=["ascii", "svg", "json"], default="ascii")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    if args.format == "ascii":
        out = generate_ascii_table()
    elif args.format == "svg":
        out = generate_svg()
    elif args.format == "json":
        out = generate_json_data()
    else:
        out = generate_ascii_table()

    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
        print(f"Visualization written to: {args.output}")
    else:
        print(out)


if __name__ == "__main__":
    main()
