"""Adapter connecting a real V10 reasoner to the ordered 208-case suite."""
from __future__ import annotations
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from daxda_engine_v10 import DAXDAEngineV10
from reasoner_protocol import ModuleReasoner

REASONER_PATH = os.environ.get("DAXDA_REASONER_MODULE")
if not REASONER_PATH:
    raise RuntimeError("Set DAXDA_REASONER_MODULE to the independent reasoner adapter path")
ENGINE = DAXDAEngineV10(ModuleReasoner(REASONER_PATH))


def _compact_prior(items):
    """Keep cross-case evidence usable without forwarding nested engine audits."""
    compact = []
    for item in items:
        response = item.get("response") or {}
        compact.append({
            "case_id": item.get("case_id"),
            "answer_summary": str(response.get("answer", ""))[:800],
            "disposition": response.get("disposition"),
            "uncertainty": str(response.get("uncertainty", ""))[:300],
            "prior_case_dependencies": response.get("prior_case_dependencies", []),
        })
    return compact


def respond(payload):
    case = payload["case"]
    audit = ENGINE.evaluate(
        case["prompt"],
        mode="evaluation",
        envelope={
            "case_id": case["case_id"],
            "evaluator_controlled": True,
            "execution_authority": False,
        },
        prior_output_summaries=_compact_prior(payload.get("prior_output_summaries", [])),
    )
    draft = audit["final_draft"]
    return {
        "case_id": case["case_id"],
        "answer": audit["answer"],
        "evidence_used": draft["evidence_used"],
        "assumptions": draft["assumptions"],
        "uncertainty": draft["uncertainty"],
        "safety_flags": sorted(set(draft["safety_flags"] + audit["authority_gate"]["hold_reasons"])),
        "disposition": audit["authority_gate"]["disposition"],
        "confidence_0_100": draft["confidence_0_100"],
        "prior_case_dependencies": draft["prior_case_dependencies"],
        "engine_audit": {
            "engine_version": audit["engine_version"],
            "preflight": audit["preflight"],
            "admission": audit["admission"],
            "postflight": audit["postflight"],
            "authority_gate": audit["authority_gate"],
            "operation_count": audit["operation_count"],
            "complete_16_layer_run": audit["complete_16_layer_run"],
            "release_receipt_sha256": audit["release_receipt_sha256"],
            "audit_sha256": audit["audit_sha256"],
            "layer_receipts": [
                {"layer_code": x["layer_code"], "receipt_sha256": x["layer_receipt_sha256"]}
                for x in audit["layers"]
            ],
        },
    }
