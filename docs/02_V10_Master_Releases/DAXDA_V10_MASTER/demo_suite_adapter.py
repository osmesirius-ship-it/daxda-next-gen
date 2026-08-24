"""208-suite wiring smoke test using the non-capability demo fixture."""
from __future__ import annotations
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from daxda_engine_v10 import DAXDAEngineV10
from reasoner_protocol import ModuleReasoner

ENGINE = DAXDAEngineV10(ModuleReasoner(str(ROOT / "demo_reasoner.py")))


def _compact_prior(items):
    return [{
        "case_id": item.get("case_id"),
        "answer_summary": str((item.get("response") or {}).get("answer", ""))[:800],
        "disposition": (item.get("response") or {}).get("disposition"),
    } for item in items]


def respond(payload):
    case = payload["case"]
    audit = ENGINE.evaluate(
        case["prompt"],
        mode="evaluation",
        envelope={"case_id": case["case_id"], "evaluator_controlled": True, "execution_authority": False},
        prior_output_summaries=_compact_prior(payload.get("prior_output_summaries", [])),
    )
    draft = audit["final_draft"]
    return {
        "case_id": case["case_id"],
        "answer": audit["answer"],
        "evidence_used": draft["evidence_used"],
        "assumptions": draft["assumptions"],
        "uncertainty": draft["uncertainty"],
        "safety_flags": draft["safety_flags"],
        "disposition": audit["authority_gate"]["disposition"],
        "confidence_0_100": draft["confidence_0_100"],
        "prior_case_dependencies": draft["prior_case_dependencies"],
        "engine_audit": {
            "engine_version": audit["engine_version"],
            "operation_count": audit["operation_count"],
            "complete_16_layer_run": audit["complete_16_layer_run"],
            "audit_sha256": audit["audit_sha256"],
        },
    }
