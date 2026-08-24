"""Deterministic structural fixture.  This is NOT a capability reasoner."""
from __future__ import annotations
from typing import Any, Dict


def _layer_response(request: Dict[str, Any]) -> Dict[str, Any]:
    code = request["layer_code"]
    objective = request["objective"]
    constrained = bool(request.get("constraints", {}).get("quarantined_analysis"))
    return {
        "layer_code": code,
        "summary": f"Structural fixture executed {code}: {objective}",
        "answer_delta": f"Recorded the {code} governance checkpoint; no substantive inference was attempted.",
        "facts": [{"statement": "This response came from the bundled structural fixture.", "status": "verified"}],
        "claims": [{"statement": "A genuine external reasoner is still required.", "status": "verified"}],
        "assumptions": ["The caller is testing orchestration rather than capability."],
        "uncertainties": ["No task-level reasoning or external evidence verification was performed."],
        "counterarguments": ["Passing structural checks does not establish reasoning quality."],
        "provenance": [{"source_id": "demo_reasoner.py", "status": "local_fixture"}],
        "safety_flags": ["QUARANTINED_ANALYSIS"] if constrained else [],
        "missing_evidence": ["Independent task-relevant evidence"],
        "corrections": [],
        "dependencies": [request["prior_layers"][-1]["layer_code"]] if request.get("prior_layers") else [],
        "confidence_0_100": 100,
        "disposition": "INSUFFICIENT_EVIDENCE",
    }


def _final_response(request: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "answer": (
            "Structural orchestration completed, but no substantive task answer is claimed. "
            "Connect an independently controlled, genuine reasoner and rerun the sealed evaluation suite."
        ),
        "evidence_used": ["Bundled structural fixture only"],
        "assumptions": ["This run is a software integration test."],
        "uncertainty": "Task-solving quality was not evaluated by the structural fixture.",
        "safety_flags": [],
        "disposition": "INSUFFICIENT_EVIDENCE",
        "confidence_0_100": 100,
        "prior_case_dependencies": [],
    }


def solve(request: Dict[str, Any]) -> Dict[str, Any]:
    protocol = request.get("protocol")
    if protocol == "DAXDA-V10-LAYER-REQUEST-1.0":
        return _layer_response(request)
    if protocol == "DAXDA-V10-SYNTHESIS-1.0":
        return _final_response(request)
    if protocol == "DAXDA-V10-REPAIR-1.0":
        invalid = request.get("invalid_response")
        if isinstance(invalid, dict):
            return invalid
        return {}
    raise ValueError(f"Unsupported protocol: {protocol!r}")

