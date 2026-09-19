#!/usr/bin/env python3
"""Run DAXDA recursive self-improvement and persist a local evidence packet."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from daxda_engine.recursive_self_improvement import RSIConfig, RecursiveSelfImprovementEngine


def main() -> int:
    cycles = 8
    if len(sys.argv) > 1:
        cycles = int(sys.argv[1])

    engine = RecursiveSelfImprovementEngine(RSIConfig(max_cycles=cycles))
    result = engine.run()
    payload = result.to_dict()
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()

    out_dir = ROOT / "reports" / "daxda_recursive_self_improvement"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    json_path = out_dir / f"rsi_{stamp}.json"
    md_path = out_dir / f"rsi_{stamp}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# DAXDA Recursive Self-Improvement",
        "",
        f"- **Generated:** {payload['generated_at']}",
        f"- **Receipt:** `{result.receipt_sha256}`",
        f"- **Kept cycles:** {result.kept_cycles}",
        f"- **Rolled back:** {result.rolled_back_cycles}",
        f"- **Blocked unsafe:** {result.blocked_cycles}",
        f"- **RSI rate:** {result.recursive_self_improvement_rate:.6f}",
        f"- **Active strategy:** `{result.active_genome.strategy_id}`",
        "",
        "## Better / Faster / Smarter",
        "",
        f"- **Better:** {result.better}",
        f"- **Faster:** {result.faster}",
        f"- **Smarter:** {result.smarter}",
        "",
        "## Fitness",
        "",
        "| Axis | Baseline | Final |",
        "|---|---|---|",
        f"| Quality | {result.baseline.quality:.4f} | {result.final.quality:.4f} |",
        f"| Speed | {result.baseline.speed:.4f} | {result.final.speed:.4f} |",
        f"| Smarts | {result.baseline.smarts:.4f} | {result.final.smarts:.4f} |",
        f"| Safety | {result.baseline.safety:.4f} | {result.final.safety:.4f} |",
        f"| Scalar | {result.baseline.scalar:.4f} | {result.final.scalar:.4f} |",
        f"| Train acc | {result.baseline.train_accuracy:.4f} | {result.final.train_accuracy:.4f} |",
        f"| Held-out acc | {result.baseline.held_out_accuracy:.4f} | {result.final.held_out_accuracy:.4f} |",
        f"| Benign acc | {result.baseline.benign_accuracy:.4f} | {result.final.benign_accuracy:.4f} |",
        f"| p99 latency ms | {result.baseline.p99_latency_ms:.4f} | {result.final.p99_latency_ms:.4f} |",
        "",
        "## Cycles",
        "",
        "| Cycle | Operator | Action | Δ quality | Δ held-out |",
        "|---|---|---|---|---|",
    ]
    for cycle in result.cycles:
        lines.append(
            f"| {cycle.cycle} | `{cycle.operator}` | `{cycle.action}` | "
            f"{cycle.quality_delta:+.4f} | {cycle.held_out_delta:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Learned overlay",
            "",
            f"- Suppress lemmas: `{', '.join(result.active_genome.extra_suppress_lemmas) or '—'}`",
            f"- Verification lemmas: `{', '.join(result.active_genome.extra_verification_lemmas) or '—'}`",
            f"- Short-circuit: `{result.active_genome.short_circuit_known_blocks}`",
            "",
            "Strategy overlays may escalate verdicts and never de-escalate them. "
            "Code-level promotion still requires PRADA and explicit human approval.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
