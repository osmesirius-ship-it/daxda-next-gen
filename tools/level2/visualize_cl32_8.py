#!/usr/bin/env python3
"""
CLI Tool for Visualizing DAXDA Level 2 Cl(32,8) Hypercombinatorial Spaces.
Renders ASCII basis tables, exports SVG diagrams, or outputs JSON Hamiltonian structures.
"""

import argparse
import json
import math
import os
import sys
from typing import Any, Dict, List

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.level2.cl32_8 import (
    Blade64,
    Cl32_8Space,
    Cl32_8Validator,
    Multivector40,
    QuantumCliffordAdapter,
)


def render_ascii_basis(space: Cl32_8Space, adapter: QuantumCliffordAdapter) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append("DAXDA LEVEL 2: Cl(32,8) HYPERCOMBINATORIAL GEOMETRY & QUANTUM COMPILER")
    lines.append("Total Generators: 40 (32 Space-Like, 8 Time-Like) | Blade Manifold: 2^40")
    lines.append("=" * 80)
    lines.append(f"{'Gen':<6} | {'Type':<12} | {'Signature':<10} | {'64-Bit Bitmask':<18} | {'20-Qubit Pauli String'}")
    lines.append("-" * 80)

    for i in range(40):
        gen_type = "Space-Like" if i < 32 else "Time-Like"
        sig_str = "+1.0 (e^2=+1)" if i < 32 else "-1.0 (e^2=-1)"
        mask_hex = f"0x{(1 << i):010x}"
        pauli = adapter.generator_to_pauli_string(i).operators
        lines.append(f"e_{i+1:<4} | {gen_type:<12} | {sig_str:<10} | {mask_hex:<18} | {pauli}")

    lines.append("=" * 80)
    return "\n".join(lines)


def render_svg_diagram(space: Cl32_8Space) -> str:
    svg_parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 650" width="1000" height="650">',
        '  <rect width="1000" height="650" fill="#05070d"/>',
        '  <text x="50" y="45" font-family="monospace" font-size="20" fill="#06b6d4" font-weight="bold">DAXDA Level 2: Cl(32,8) Geometric Lattice</text>',
        '  <text x="50" y="70" font-family="monospace" font-size="12" fill="#94a3b8">40 Basis Generators • 2^40 ≈ 1,099,511,627,776 Blades • 20 Qubits</text>',
    ]

    # Draw central generator ring
    cx, cy = 500, 350
    radius = 220

    # Draw bivector connecting chords
    for i in range(40):
        a1 = (i / 40.0) * 2.0 * math.pi
        a2 = ((i + 1) / 40.0) * 2.0 * math.pi
        x1 = cx + radius * math.cos(a1)
        y1 = cy + radius * math.sin(a1)
        x2 = cx + radius * math.cos(a2)
        y2 = cy + radius * math.sin(a2)
        svg_parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#0284c7" stroke-width="1.5" opacity="0.4"/>')
        if i % 4 == 0:
            opp_a = ((i + 20) / 40.0) * 2.0 * math.pi
            ox = cx + radius * math.cos(opp_a)
            oy = cy + radius * math.sin(opp_a)
            svg_parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{ox:.1f}" y2="{oy:.1f}" stroke="#8b5cf6" stroke-width="1" stroke-dasharray="3,3" opacity="0.3"/>')

    # Draw generator nodes
    for i in range(40):
        angle = (i / 40.0) * 2.0 * math.pi
        nx = cx + radius * math.cos(angle)
        ny = cy + radius * math.sin(angle)
        is_neg = (i >= 32)
        color = "#ec4899" if is_neg else "#06b6d4"
        r = 6.0 if is_neg else 5.0
        svg_parts.append(f'  <circle cx="{nx:.1f}" cy="{ny:.1f}" r="{r}" fill="{color}" stroke="#ffffff" stroke-width="0.8"/>')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def main():
    parser = argparse.ArgumentParser(description="DAXDA Cl(32,8) Visualizer")
    parser.add_argument("--format", choices=["ascii", "svg", "json", "html"], default="ascii")
    parser.add_argument("--output", type=str, default=None, help="Output destination file")
    args = parser.parse_args()

    space = Cl32_8Space(32, 8)
    adapter = QuantumCliffordAdapter(qubits=20)

    if args.format == "ascii":
        output = render_ascii_basis(space, adapter)
        print(output)
    elif args.format == "svg":
        output = render_svg_diagram(space)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Exported Cl(32,8) SVG diagram to {args.output}")
        else:
            print(output)
    elif args.format == "json":
        data = {
            "space": "Cl(32,8)",
            "dimension": 40,
            "total_blades": 1 << 40,
            "generators": [
                {
                    "index": i,
                    "signature": space._signature[i],
                    "mask_hex": f"0x{(1 << i):x}",
                    "pauli_string": adapter.generator_to_pauli_string(i).operators,
                }
                for i in range(40)
            ],
        }
        output = json.dumps(data, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Exported Cl(32,8) JSON basis to {args.output}")
        else:
            print(output)
    elif args.format == "html":
        visualizer_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../daxda_guard/cl32_8_lattice_visualizer.html")
        )
        print(f"Cl(32,8) 3D WebGL Lattice Visualizer is available at:\nfile://{visualizer_path}")


if __name__ == "__main__":
    main()
