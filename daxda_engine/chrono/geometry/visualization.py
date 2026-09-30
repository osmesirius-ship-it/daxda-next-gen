"""
DAXDA Chrono-Synchronicity Mapping: Temporal Relationship Visualization
Generates ASCII timeline graphs, SVG causal network diagrams, and JSON manifold structures.
"""

from __future__ import annotations
import json
from typing import Dict, List, Optional, Any, Set
from daxda_engine.chrono.geometry.temporal_space import TemporalSpace, TemporalState
from daxda_engine.chrono.geometry.retrocausal_engine import RetrocausalInfluence
from daxda_engine.chrono.geometry.synchronicity import SynchronicityEvent


class TemporalVisualizer:
    """
    Renders temporal manifolds, causal graphs, retrocausal influence fields,
    and synchronicity bridges in multiple formats.
    """

    def __init__(self, space: TemporalSpace):
        self.space = space

    def render_ascii_timeline(self, limit: int = 20) -> str:
        """Render a terminal ASCII visualization of the temporal timeline and branches."""
        self.space._ensure_time_sorted()
        items = self.space._time_index[:limit]
        if not items:
            return "[Empty Temporal Space]"

        lines: List[str] = [
            "==================================================================",
            "                 DAXDA CHRONO-TEMPORAL TIMELINE                   ",
            "==================================================================",
            " TIME (t) | BRANCH (b) | PARALLEL (p) | STATE ID     | CONSTRAINTS",
            "------------------------------------------------------------------"
        ]

        for t_val, sid in items:
            st = self.space.get_state(sid)
            if not st:
                continue
            c = st.coordinate
            n_preds = len(st.predecessors)
            n_succs = len(st.successors)
            n_retro = len(st.retrocausal_influences)
            
            branch_marker = f"B:{c.b:+.1f}"
            parallel_marker = f"P:{c.p:+.1f}"
            c_tag = f"<-{n_preds} | ->{n_succs} | <~{n_retro}"
            lines.append(f" {c.t:8.2f} | {branch_marker:10} | {parallel_marker:12} | {sid[:12]:12} | {c_tag}")

        lines.append("==================================================================")
        return "\n".join(lines)

    def export_graph_json(
        self,
        retro_influences: Optional[List[RetrocausalInfluence]] = None,
        sync_events: Optional[List[SynchronicityEvent]] = None,
    ) -> Dict[str, Any]:
        """Export temporal state graph as node-link JSON for graph visualization."""
        nodes = []
        links = []

        for sid, st in self.space._states.items():
            nodes.append({
                "id": sid,
                "t": st.coordinate.t,
                "b": st.coordinate.b,
                "p": st.coordinate.p,
                "tau": st.coordinate.tau,
                "vector": st.decision_vector[:4] if st.decision_vector else [],
                "state_hash": st.state_hash[:12],
            })
            for succ_id in st.successors:
                links.append({
                    "source": sid,
                    "target": succ_id,
                    "type": "causal_forward",
                    "color": "#34d399",  # Emerald Green
                })

        if retro_influences:
            for r in retro_influences:
                links.append({
                    "source": r.source_state_id,
                    "target": r.target_state_id,
                    "type": "retrocausal_backward",
                    "strength": r.influence_strength,
                    "color": "#c084fc",  # Purple
                })

        if sync_events:
            for s in sync_events:
                links.append({
                    "source": s.state_a_id,
                    "target": s.state_b_id,
                    "type": "synchronicity_acausal",
                    "score": s.synchronicity_score,
                    "color": "#38bdf8",  # Sky Blue
                })

        return {
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(links),
                "dimension": self.space.dimension.name,
            },
            "nodes": nodes,
            "links": links,
        }

    def render_svg_diagram(
        self,
        width: int = 900,
        height: int = 500,
        retro_influences: Optional[List[RetrocausalInfluence]] = None,
        sync_events: Optional[List[SynchronicityEvent]] = None,
    ) -> str:
        """Render standalone SVG diagram of the temporal manifold."""
        graph = self.export_graph_json(retro_influences, sync_events)
        nodes = graph["nodes"]
        links = graph["links"]

        if not nodes:
            return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><text x="50" y="50" fill="white">Empty Manifold</text></svg>'

        t_min = min(n["t"] for n in nodes)
        t_max = max(n["t"] for n in nodes)
        t_span = max(1.0, t_max - t_min)

        b_min = min(n["b"] for n in nodes)
        b_max = max(n["b"] for n in nodes)
        b_span = max(1.0, b_max - b_min)

        pad = 60
        node_coords = {}
        for n in nodes:
            x = pad + ((n["t"] - t_min) / t_span) * (width - 2 * pad)
            y = height / 2.0 + ((n["b"] - b_min) / b_span - 0.5) * (height - 2 * pad)
            node_coords[n["id"]] = (x, y)

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
            '  <defs>',
            '    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">',
            '      <stop offset="0%" stop-color="#0b0f19" />',
            '      <stop offset="100%" stop-color="#111827" />',
            '    </linearGradient>',
            '    <marker id="arrow-green" viewBox="0 0 10 10" refX="15" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#34d399"/></marker>',
            '    <marker id="arrow-purple" viewBox="0 0 10 10" refX="15" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#c084fc"/></marker>',
            '  </defs>',
            f'  <rect width="{width}" height="{height}" fill="url(#bg)" />',
            f'  <text x="{pad}" y="35" font-family="monospace" font-size="16" fill="#38bdf8" font-weight="bold">DAXDA Chrono-Synchronicity Geometric Manifold</text>',
        ]

        # Draw links
        for link in links:
            s_coord = node_coords.get(link["source"])
            t_coord = node_coords.get(link["target"])
            if not s_coord or not t_coord:
                continue

            x1, y1 = s_coord
            x2, y2 = t_coord
            color = link.get("color", "#9ca3af")
            ltype = link.get("type", "forward")

            if ltype == "causal_forward":
                svg_parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="2" marker-end="url(#arrow-green)" />')
            elif ltype == "retrocausal_backward":
                svg_parts.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="2.5" stroke-dasharray="6,4" marker-end="url(#arrow-purple)" />')
            elif ltype == "synchronicity_acausal":
                cx = (x1 + x2) / 2.0
                cy = min(y1, y2) - 30
                svg_parts.append(f'  <path d="M {x1:.1f} {y1:.1f} Q {cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" stroke="{color}" stroke-width="1.8" stroke-dasharray="3,3" fill="none" />')

        # Draw nodes
        for n in nodes:
            x, y = node_coords[n["id"]]
            svg_parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#0284c7" stroke="#38bdf8" stroke-width="2" />')
            svg_parts.append(f'  <text x="{x + 8:.1f}" y="{y + 4:.1f}" font-family="monospace" font-size="10" fill="#e2e8f0">{n["id"][:6]}</text>')

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)
