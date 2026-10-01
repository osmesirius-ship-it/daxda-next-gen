#!/usr/bin/env python3
"""
CLI Tool for Visualizing DAXDA Level 2 5D Chrono-Synchronicity Manifolds.
Renders ASCII timelines, exports SVG diagrams, or outputs JSON graph structures.
"""

import argparse
import json
import math
import os
import sys
from typing import Any, Dict, List

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.level2.chrono_5d import (
    CausalGraph5D,
    QuantumCausalLoopHarmonizer,
    RiemannianTemporalSpace5D,
    TemporalCoordinate5D,
)


def render_ascii_timeline(graph: CausalGraph5D, harmonizer: QuantumCausalLoopHarmonizer) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append("DAXDA LEVEL 2: 5D RIEMANNIAN TEMPORAL MANIFOLD ASCII PROJECTION")
    lines.append("Coordinates: (t, b, p, tau, omega)  |  Signature: (+, -, -, -, -)")
    lines.append("=" * 80)

    for nid, node in list(graph.nodes.items())[:12]:
        c = node.coordinate
        boundary = graph.space.classify_causal_relation(
            TemporalCoordinate5D(0, 0, 0, 0, 0), c
        )
        cone_symbol = ">>" if "FUTURE" in boundary.cone_type.value else ("<<" if "PAST" in boundary.cone_type.value else "<>")
        bar_len = int(min(20, max(1, c.t * 3)))
        time_bar = "—" * bar_len + "●"

        lines.append(
            f"[{nid:12s}] {cone_symbol} t={c.t:4.2f} | b={c.b:4.2f} | p={c.p:4.2f} | tau={c.tau:4.2f} | w={c.omega:4.2f} | {time_bar}"
        )

    lines.append("-" * 80)
    res = harmonizer.harmonize_loop("node_000000", max_branches=64)
    lines.append(f"Novikov Harmonization Status : {'CONSISTENT' if res.is_novikov_consistent else 'PARADOX'}")
    lines.append(f"Superposed Parallel Branches : {res.converged_branches_count} / {res.total_branches_evaluated}")
    lines.append(f"Iterations to Convergence    : {res.iterations_run} (Residual norm: {res.residual_norm:.2e})")
    lines.append(f"Geodesic Proper Distance     : {res.geodesic_distance:.4f}")
    lines.append("=" * 80)
    return "\n".join(lines)


def render_svg_diagram(graph: CausalGraph5D) -> str:
    svg_parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" width="1000" height="600">',
        '  <rect width="1000" height="600" fill="#07090e"/>',
        '  <text x="50" y="45" font-family="monospace" font-size="20" fill="#06b6d4" font-weight="bold">DAXDA Level 2: 5D Spacetime Manifold</text>',
        '  <text x="50" y="70" font-family="monospace" font-size="12" fill="#94a3b8">Metric: ds² = dt² - b² db² - p² dp² - dτ² - ω² dω²</text>',
    ]

    # Draw coordinate axes
    svg_parts.append('  <line x1="80" y1="500" x2="920" y2="500" stroke="#1e293b" stroke-width="2"/>')
    svg_parts.append('  <line x1="80" y1="500" x2="80" y2="120" stroke="#1e293b" stroke-width="2"/>')
    svg_parts.append('  <text x="910" y="520" font-family="monospace" font-size="12" fill="#64748b">Time (t)</text>')
    svg_parts.append('  <text x="30" y="130" font-family="monospace" font-size="12" fill="#64748b">Branch (b)</text>')

    # Draw nodes and branches
    nodes = list(graph.nodes.values())[:30]
    for i, node in enumerate(nodes):
        c = node.coordinate
        cx = 100 + (c.t / 10.0) * 800
        cy = 480 - (c.b * 320)
        r = 5 + (c.omega * 6)
        color = "#10b981" if c.p < 0.3 else ("#f59e0b" if c.p < 0.7 else "#ef4444")
        svg_parts.append(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}" opacity="0.85"/>')

        if i > 0:
            prev = nodes[i - 1]
            px = 100 + (prev.coordinate.t / 10.0) * 800
            py = 480 - (prev.coordinate.b * 320)
            svg_parts.append(f'  <line x1="{px:.1f}" y1="{py:.1f}" x2="{cx:.1f}" y2="{cy:.1f}" stroke="#0284c7" stroke-width="1.5" stroke-dasharray="4,2"/>')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def main():
    parser = argparse.ArgumentParser(description="DAXDA 5D Chrono Visualizer")
    parser.add_argument("--format", choices=["ascii", "svg", "json", "html"], default="ascii")
    parser.add_argument("--output", type=str, default=None, help="Output destination file")
    parser.add_argument("--nodes", type=int, default=50, help="Number of nodes to synthesize")
    args = parser.parse_args()

    graph = CausalGraph5D.generate_synthetic_graph(node_count=args.nodes, seed=42)
    harmonizer = QuantumCausalLoopHarmonizer(space=graph.space)

    if args.format == "ascii":
        output = render_ascii_timeline(graph, harmonizer)
        print(output)
    elif args.format == "svg":
        output = render_svg_diagram(graph)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Exported 5D Chrono SVG diagram to {args.output}")
        else:
            print(output)
    elif args.format == "json":
        data = {
            "node_count": len(graph.nodes),
            "edges_count": sum(len(el) for el in graph.edges.values()),
            "metric_signature": "(+, -, -, -, -)",
            "sample_nodes": [
                {
                    "id": n.node_id,
                    "t": n.coordinate.t,
                    "b": n.coordinate.b,
                    "p": n.coordinate.p,
                    "tau": n.coordinate.tau,
                    "omega": n.coordinate.omega,
                }
                for n in list(graph.nodes.values())[:10]
            ],
        }
        output = json.dumps(data, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Exported 5D Chrono JSON topology to {args.output}")
        else:
            print(output)
    elif args.format == "html":
        visualizer_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../daxda_guard/chrono_5d_manifold_visualizer.html")
        )
        print(f"5D WebGL Interactive Manifold Visualizer is available at:\nfile://{visualizer_path}")


if __name__ == "__main__":
    main()
