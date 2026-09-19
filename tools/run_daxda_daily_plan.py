#!/usr/bin/env python3
"""Run one dated DAXDA 90-day plan item and persist local evidence."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

from daxda_engine.engine_v12_1 import DAXDAEngineV12_1
from daxda_guard.core import DAXDAGuardCore


ROOT = Path(__file__).resolve().parents[1]
START = date(2026, 9, 17)
END = date(2026, 12, 15)
EVIDENCE_DIR = ROOT / "reports" / "daxda_daily_execution"

PHASES = [
    (1, 10, "Baseline and evidence inventory"),
    (11, 20, "Engine and semantic analysis hardening"),
    (21, 30, "Guard and containment controls"),
    (31, 40, "Scientific protocol and auditability"),
    (41, 50, "SDK, mobile, and deployment integration"),
    (51, 60, "Performance and distributed validation"),
    (61, 70, "End-to-end orchestration"),
    (71, 80, "Adversarial review and claims audit"),
    (81, 90, "Release decision and next-cycle planning"),
]


def phase_for(day_number: int) -> str:
    for first, last, name in PHASES:
        if first <= day_number <= last:
            return name
    raise ValueError(f"Day number outside plan: {day_number}")


def activity_for(day_number: int, phase: str) -> str:
    return (
        f"Execute Day {day_number} of the DAXDA 90-day plan: "
        f"{phase}. Record command output, test results, structured receipts, "
        "review evidence, and blockers without changing safety thresholds."
    )


def run_tests(day_number: int) -> dict:
    if day_number not in {3, 21, 31, 51, 61, 71, 81, 90}:
        return {"scheduled": False, "status": "not_scheduled"}
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/test_advisory_mode_and_pilots.py",
        "tests/test_governed_authority_gate.py",
        "tests/test_audit_generator.py",
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "scheduled": True,
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-2000:],
    }


def main() -> int:
    today = date.today()
    if today < START:
        print(f"Plan has not started; first scheduled date is {START}.")
        return 0
    if today > END:
        print(f"Plan completed on {END}.")
        return 0

    day_number = (today - START).days + 1
    phase = phase_for(day_number)
    activity = activity_for(day_number, phase)
    started = time.perf_counter()
    engine_result = DAXDAEngineV12_1().evaluate(activity)
    guard_receipt = DAXDAGuardCore().evaluate("governance", activity)
    tests = run_tests(day_number)
    elapsed = time.perf_counter() - started

    evidence = {
        "date": today.isoformat(),
        "day_number": day_number,
        "phase": phase,
        "activity": activity,
        "engine": engine_result,
        "guard_receipt": guard_receipt.__dict__,
        "tests": tests,
        "runtime": {
            "python": sys.version,
            "os": platform.platform(),
            "cwd": str(ROOT),
        },
        "elapsed_seconds": elapsed,
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    output = EVIDENCE_DIR / f"day_{day_number:02d}_{today.isoformat()}.json"
    output.write_text(json.dumps(evidence, indent=2, default=str), encoding="utf-8")
    summary = EVIDENCE_DIR / f"day_{day_number:02d}_{today.isoformat()}.md"
    summary.write_text(
        "\n".join(
            [
                f"# DAXDA Daily Execution — Day {day_number}",
                "",
                f"- **Date:** {today.isoformat()}",
                f"- **Phase:** {phase}",
                f"- **Engine:** `{engine_result['verdict']}` / `{engine_result['decision_rule']}`",
                f"- **Guard:** `{guard_receipt.verdict}` / `{guard_receipt.decision_rule}`",
                f"- **Receipt:** `{guard_receipt.authority_sha256}`",
                f"- **Tests:** `{tests['status']}`",
                f"- **JSON evidence:** `{output}`",
                "",
                "This is local execution evidence, not a certification or proof of universal safety.",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"day": day_number, "date": today.isoformat(), "evidence": str(output)}, indent=2))
    return 0 if tests["status"] != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
