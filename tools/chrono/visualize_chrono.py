#!/usr/bin/env python3
"""
CLI Tool for Visualizing DAXDA Chrono-Synchronicity Manifolds.
Renders ASCII timelines, exports SVG diagrams, or outputs JSON graph structures.
"""

import sys
import os
import argparse
from typing import Tuple, List, Any

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from daxda_engine.chrono.geometry.temporal_space import (
    TemporalCoordinate,
    TemporalState,
    TemporalSpace,
)
from daxda_engine.chrono.geometry.retrocausal_engine import RetrocausalEngine
from daxda_engine.chrono.geometry.synchronicity import SynchronicityDetector
from daxda_engine.chrono.geometry.visualization import TemporalVisualizer



def populate_demo_space() -> Tuple[TemporalSpace, List[Any], List[Any]]:
    space = TemporalSpace()
    # Create main trunk states
    s1 = TemporalState(state_id="alpha_init", coordinate=TemporalCoordinate(t=10.0, b=0.0), decision_vector=[0.2, 0.4, 0.8])
    s2 = TemporalState(state_id="alpha_step1", coordinate=TemporalCoordinate(t=12.0, b=0.0), decision_vector=[0.25, 0.42, 0.78])
    s3 = TemporalState(state_id="alpha_branch_A", coordinate=TemporalCoordinate(t=14.0, b=1.0), decision_vector=[0.3, 0.5, 0.7])
    s4 = TemporalState(state_id="alpha_branch_B", coordinate=TemporalCoordinate(t=14.5, b=-1.0), decision_vector=[0.1, 0.2, 0.9])
    s_term = TemporalState(state_id="omega_terminal", coordinate=TemporalCoordinate(t=20.0, b=0.0), decision_vector=[0.35, 0.45, 0.75])

    s1.successors.add(s2.state_id)
    s2.successors.add(s3.state_id)
    s2.successors.add(s4.state_id)
    s3.successors.add(s_term.state_id)
    s4.successors.add(s_term.state_id)

    space.add_state(s1)
    space.add_state(s2)
    space.add_state(s3)
    space.add_state(s4)
    space.add_state(s_term)

    retro = RetrocausalEngine(space)
    infl = [retro.compute_retrocausal_influence(s_term, s2)]

    sync = SynchronicityDetector(space)
    evs = sync.scan_recent_window(t_center=14.0, window_radius=2.0)

    return space, infl, evs


def main():
    parser = argparse.ArgumentParser(description="DAXDA Chrono-Synchronicity Manifold Visualizer")
    parser.add_argument("--format", choices=["ascii", "svg", "json"], default="ascii", help="Output format")
    parser.add_argument("--output", type=str, default=None, help="Output file path (for svg/json)")
    args = parser.parse_args()

    space, infl, sync_evs = populate_demo_space()
    viz = TemporalVisualizer(space)

    if args.format == "ascii":
        output_str = viz.render_ascii_timeline()
        print(output_str)
    elif args.format == "svg":
        output_str = viz.render_svg_diagram(retro_influences=infl, sync_events=sync_evs)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output_str)
            print(f"SVG written to {args.output}")
        else:
            print(output_str[:300] + "... (truncated SVG)")
    elif args.format == "json":
        graph_data = viz.export_graph_json(retro_influences=infl, sync_events=sync_evs)
        import json
        output_str = json.dumps(graph_data, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output_str)
            print(f"JSON written to {args.output}")
        else:
            print(output_str)


if __name__ == "__main__":
    main()
