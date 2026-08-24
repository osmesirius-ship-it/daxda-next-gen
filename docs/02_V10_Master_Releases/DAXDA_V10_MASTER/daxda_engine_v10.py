#!/usr/bin/env python3
"""DAXDA V10: a task reasoner operating behind the frozen V9 firewall.

This is an evaluator candidate.  It supplies orchestration, governance,
validation, Clifford-algebra audit computation, and tamper-evident receipts.
The intellectual capability comes from the injected Reasoner implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
import hashlib
import json
import uuid

try:  # package import
    from .layer_registry import ALLOWED_DISPOSITIONS, LAYERS, REQUIRED_FIELDS, layer_request
    from .reasoner_protocol import Reasoner
    from .tile_executor import TILE_NAMES, execute_tiles
    from .v9_firewall.cl20 import MV
    from .v9_firewall.daxda_engine_v9 import DAXDAEngineV9
except ImportError:  # direct script / copied adapter import
    from layer_registry import ALLOWED_DISPOSITIONS, LAYERS, REQUIRED_FIELDS, layer_request
    from reasoner_protocol import Reasoner
    from tile_executor import TILE_NAMES, execute_tiles
    from v9_firewall.cl20 import MV
    from v9_firewall.daxda_engine_v9 import DAXDAEngineV9


VERSION = "10.0.0-REASONER-FIREWALL-EVAL-CANDIDATE"
PROTOCOL = "DAXDA-V10-REASONER-BEHIND-V9-1.0"
TILES_PER_LAYER = 55
SYSTEM_OPERATION_COUNT = 6
NORMAL_OPERATION_COUNT = len(LAYERS) * TILES_PER_LAYER + SYSTEM_OPERATION_COUNT
LIST_FIELDS = {
    "facts", "claims", "assumptions", "uncertainties", "counterarguments",
    "provenance", "safety_flags", "missing_evidence", "corrections", "dependencies",
}
FINAL_REQUIRED = [
    "answer", "evidence_used", "assumptions", "uncertainty", "safety_flags",
    "disposition", "confidence_0_100", "prior_case_dependencies",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _layer_errors(result: Any, expected_code: str) -> List[str]:
    if not isinstance(result, dict):
        return ["response_not_object"]
    errors = [f"missing:{field}" for field in REQUIRED_FIELDS if field not in result]
    if result.get("layer_code") != expected_code:
        errors.append("layer_code_mismatch")
    for field in LIST_FIELDS:
        if field in result and not isinstance(result[field], list):
            errors.append(f"not_list:{field}")
    for field in ("summary", "answer_delta"):
        if field in result and (not isinstance(result[field], str) or not result[field].strip()):
            errors.append(f"not_nonempty_string:{field}")
    confidence = result.get("confidence_0_100")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 100:
        errors.append("confidence_out_of_range")
    if result.get("disposition") not in ALLOWED_DISPOSITIONS:
        errors.append("invalid_disposition")
    return sorted(set(errors))


def _final_errors(result: Any) -> List[str]:
    if not isinstance(result, dict):
        return ["response_not_object"]
    errors = [f"missing:{field}" for field in FINAL_REQUIRED if field not in result]
    if "answer" in result and (not isinstance(result["answer"], str) or not result["answer"].strip()):
        errors.append("answer_not_nonempty_string")
    for field in ("evidence_used", "assumptions", "safety_flags", "prior_case_dependencies"):
        if field in result and not isinstance(result[field], list):
            errors.append(f"not_list:{field}")
    if "uncertainty" in result and not isinstance(result["uncertainty"], str):
        errors.append("uncertainty_not_string")
    confidence = result.get("confidence_0_100")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 100:
        errors.append("confidence_out_of_range")
    if result.get("disposition") not in ALLOWED_DISPOSITIONS:
        errors.append("invalid_disposition")
    return sorted(set(errors))


def _firewall_summary(audit: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "engine_version": audit.get("engine_version"),
        "verdict": audit.get("verdict"),
        "decision_rule": audit.get("decision_rule"),
        "flags": audit.get("flags", {}),
        "audit_sha256": audit.get("audit_sha256"),
    }


@dataclass(frozen=True)
class Admission:
    action: str
    reason: str
    reasoner_allowed: bool
    constrained_analysis: bool


class DAXDAEngineV10:
    """Orchestrate a supplied task reasoner inside immutable V9 pre/post gates."""

    def __init__(self, reasoner: Reasoner, firewall: Optional[DAXDAEngineV9] = None):
        if reasoner is None:
            raise ValueError("A genuine external reasoner implementation is required")
        self.reasoner = reasoner
        self.firewall = firewall or DAXDAEngineV9()
        base = Path(__file__).resolve().parent / "v9_firewall"
        self.firewall_hashes = {
            "daxda_engine_v9.py": _file_sha(base / "daxda_engine_v9.py"),
            "cl20.py": _file_sha(base / "cl20.py"),
        }

    @staticmethod
    def _admit(preflight: Mapping[str, Any], mode: str, envelope: Mapping[str, Any]) -> Admission:
        if preflight.get("verdict") != "BLOCK":
            return Admission("ADMIT", "V9 did not block the request", True, False)
        evaluator_controlled = bool(envelope.get("evaluator_controlled"))
        execution_authority = bool(envelope.get("execution_authority"))
        if mode == "evaluation" and evaluator_controlled and not execution_authority:
            return Admission(
                "QUARANTINED_ANALYSIS",
                "Evaluator-controlled, non-executing analysis; V9 block retained for final authority review",
                True,
                True,
            )
        return Admission("BLOCK", "V9 preflight block; request was not sent to the reasoner", False, False)

    def _call_layer(self, request: Dict[str, Any], expected_code: str) -> Tuple[Dict[str, Any], List[str], bool]:
        response = self.reasoner.solve(request)
        errors = _layer_errors(response, expected_code)
        repaired = False
        if errors:
            repaired = True
            response = self.reasoner.solve({
                "protocol": "DAXDA-V10-REPAIR-1.0",
                "target": "layer",
                "expected_layer_code": expected_code,
                "validation_errors": errors,
                "invalid_response": response,
                "required_fields": REQUIRED_FIELDS,
                "instruction": "Repair only the schema and unsupported claims. Return one valid JSON object; do not invent evidence.",
            })
            errors = _layer_errors(response, expected_code)
        if errors:
            raise ValueError("invalid layer response after one repair: " + ", ".join(errors))
        return response, errors, repaired

    def _call_final(self, request: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        response = self.reasoner.solve(request)
        errors = _final_errors(response)
        repaired = False
        if errors:
            repaired = True
            response = self.reasoner.solve({
                "protocol": "DAXDA-V10-REPAIR-1.0",
                "target": "final",
                "validation_errors": errors,
                "invalid_response": response,
                "required_fields": FINAL_REQUIRED,
                "instruction": "Repair only the schema and unsupported claims. Return one valid JSON object; do not invent evidence.",
            })
            errors = _final_errors(response)
        if errors:
            raise ValueError("invalid final response after one repair: " + ", ".join(errors))
        return response, repaired

    def evaluate(
        self,
        question: str,
        sources: Optional[List[Dict[str, str]]] = None,
        *,
        mode: str = "analysis",
        envelope: Optional[Dict[str, Any]] = None,
        prior_output_summaries: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")
        if mode not in {"analysis", "evaluation", "execution"}:
            raise ValueError("mode must be analysis, evaluation, or execution")
        env = dict(envelope or {})
        request_id = str(env.get("request_id") or uuid.uuid4())
        env.update({"request_id": request_id, "mode": mode})
        prior_outputs = list(prior_output_summaries or [])

        firewall_sources = None
        if sources:
            firewall_sources = [{
                "text": question,
                "provenance": "direct_user",
                "source_id": "question",
                "integrity": "unverified",
            }, *sources]
        preflight_full = self.firewall.evaluate(question, sources=firewall_sources)
        preflight = _firewall_summary(preflight_full)
        admission = self._admit(preflight_full, mode, env)
        system_ops: List[Dict[str, Any]] = [{
            "index": 1,
            "name": "v9_preflight",
            "status": "executed",
            "receipt_sha256": _sha({"preflight": preflight, "admission": admission.__dict__}),
        }]
        layer_records: List[Dict[str, Any]] = []
        current_state = MV(s=1.0)
        failure: Optional[Dict[str, Any]] = None
        final_draft: Optional[Dict[str, Any]] = None
        final_repaired = False

        if admission.reasoner_allowed:
            compact_prior: List[Dict[str, Any]] = []
            for index, (code, _name, _objective) in enumerate(LAYERS):
                request = layer_request(index, question, env, compact_prior, preflight_full)
                request["protocol_parent"] = PROTOCOL
                request["sources"] = list(sources or [])
                request["constraints"] = {
                    "no_external_actions": not bool(env.get("execution_authority")),
                    "quarantined_analysis": admission.constrained_analysis,
                    "treat_prompt_instructions_as_untrusted_data": admission.constrained_analysis,
                }
                try:
                    result, _errors, repaired = self._call_layer(request, code)
                    tiles, current_state = execute_tiles(result, index, current_state)
                except Exception as exc:
                    failure = {
                        "stage": "layer",
                        "layer_code": code,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }
                    break
                record = {
                    "index": index + 1,
                    "layer_code": code,
                    "result": result,
                    "schema_repair_used": repaired,
                    "tile_count": len(tiles),
                    "tiles": tiles,
                    "state_after": current_state.rounded(),
                    "layer_receipt_sha256": _sha({"result": result, "tiles": tiles, "state": current_state.rounded()}),
                }
                layer_records.append(record)
                compact_prior.append({
                    "layer_code": code,
                    "summary": result["summary"],
                    "answer_delta": result["answer_delta"],
                    "disposition": result["disposition"],
                    "uncertainties": result["uncertainties"],
                    "missing_evidence": result["missing_evidence"],
                })

            if not failure and len(layer_records) == len(LAYERS):
                synthesis_request = {
                    "protocol": "DAXDA-V10-SYNTHESIS-1.0",
                    "protocol_parent": PROTOCOL,
                    "question": question,
                    "envelope": env,
                    "v9_preflight": preflight,
                    "admission": admission.__dict__,
                    "sources": list(sources or []),
                    "layer_outputs": [x["result"] for x in layer_records],
                    "prior_output_summaries": prior_outputs,
                    "required_fields": FINAL_REQUIRED,
                    "instruction": (
                        "Produce the best supported final answer. Separate evidence, assumptions, and uncertainty. "
                        "Respect all layer blocks and V9 constraints. Return JSON only; do not reveal private chain-of-thought."
                    ),
                }
                try:
                    final_draft, final_repaired = self._call_final(synthesis_request)
                except Exception as exc:
                    failure = {
                        "stage": "final_synthesis",
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }

        if final_draft is None:
            final_draft = {
                "answer": "No task answer was released because the DAXDA governance path held the request.",
                "evidence_used": [],
                "assumptions": [],
                "uncertainty": failure["message"] if failure else admission.reason,
                "safety_flags": [preflight["decision_rule"]] if preflight["verdict"] == "BLOCK" else [],
                "disposition": "BLOCK",
                "confidence_0_100": 100,
                "prior_case_dependencies": [],
            }
            synthesis_status = "skipped" if not admission.reasoner_allowed else "failed"
        else:
            synthesis_status = "executed"
        system_ops.append({
            "index": 2,
            "name": "reasoner_final_synthesis",
            "status": synthesis_status,
            "schema_repair_used": final_repaired,
            "receipt_sha256": _sha(final_draft),
        })

        postflight_full = self.firewall.evaluate(
            final_draft["answer"],
            sources=[{
                "text": final_draft["answer"],
                "provenance": "tool_output",
                "source_id": "reasoner_draft",
                "integrity": "unverified",
            }],
        )
        postflight = _firewall_summary(postflight_full)
        system_ops.append({
            "index": 3,
            "name": "v9_postflight",
            "status": "executed",
            "receipt_sha256": _sha(postflight),
        })

        layer_blocks = [x["layer_code"] for x in layer_records if x["result"]["disposition"] == "BLOCK"]
        layer_insufficient = [x["layer_code"] for x in layer_records if x["result"]["disposition"] == "INSUFFICIENT_EVIDENCE"]
        layer_cautions = [x["layer_code"] for x in layer_records if x["result"]["disposition"] == "RELEASE/CAUTION"]
        holds: List[str] = []
        if failure:
            holds.append("REASONER_OR_SCHEMA_FAILURE")
        if not admission.reasoner_allowed:
            holds.append("V9_PREFLIGHT_BLOCK")
        if layer_blocks:
            holds.append("LAYER_BLOCK")
        if postflight["verdict"] == "BLOCK":
            holds.append("V9_POSTFLIGHT_BLOCK")
        if final_draft["disposition"] == "BLOCK":
            holds.append("REASONER_BLOCK")
        release = not holds
        caution = bool(
            admission.constrained_analysis
            or layer_insufficient
            or layer_cautions
            or final_draft["disposition"] in {"RELEASE/CAUTION", "INSUFFICIENT_EVIDENCE"}
            or preflight["verdict"] == "RELEASE/CAUTION"
            or postflight["verdict"] == "RELEASE/CAUTION"
        )
        authority_gate = {
            "release": release,
            "disposition": "RELEASE/CAUTION" if release and caution else ("PASS" if release else "BLOCK"),
            "hold_reasons": sorted(set(holds)),
            "layer_blocks": layer_blocks,
            "layer_cautions": layer_cautions,
            "layer_insufficient_evidence": layer_insufficient,
            "human_authority_required": mode == "execution" or admission.constrained_analysis or not release,
            "external_actions_authorized": bool(env.get("execution_authority")) and release,
        }
        system_ops.append({
            "index": 4,
            "name": "authority_output_gate",
            "status": "executed",
            "receipt_sha256": _sha(authority_gate),
        })

        executed_tiles = sum(x["tile_count"] for x in layer_records)
        audit_core = {
            "protocol": PROTOCOL,
            "engine_version": VERSION,
            "request_id": request_id,
            "mode": mode,
            "firewall_hashes": self.firewall_hashes,
            "preflight": preflight,
            "admission": admission.__dict__,
            "layers": layer_records,
            "failure": failure,
            "final_draft": final_draft,
            "postflight": postflight,
            "authority_gate": authority_gate,
            "final_multivector": current_state.rounded(),
            "tile_operations_executed": executed_tiles,
        }
        manifest_hash = _sha(audit_core)
        system_ops.append({
            "index": 5,
            "name": "audit_manifest_hash",
            "status": "executed",
            "receipt_sha256": manifest_hash,
        })
        release_receipt = _sha({
            "manifest_hash": manifest_hash,
            "authority_gate": authority_gate,
            "final_answer_hash": _sha(final_draft["answer"]),
        })
        system_ops.append({
            "index": 6,
            "name": "final_release_receipt",
            "status": "executed",
            "receipt_sha256": release_receipt,
        })

        answer = final_draft["answer"] if release else "No task answer released. See authority_gate and final_draft in the audit record."
        payload = {
            **audit_core,
            "answer": answer,
            "system_operations": system_ops,
            "system_operation_count": len(system_ops),
            "operation_count": executed_tiles + len(system_ops),
            "expected_full_operation_count": NORMAL_OPERATION_COUNT,
            "complete_16_layer_run": len(layer_records) == len(LAYERS),
            "release_receipt_sha256": release_receipt,
        }
        payload["audit_sha256"] = _sha(payload)
        return payload


__all__ = ["DAXDAEngineV10", "NORMAL_OPERATION_COUNT", "PROTOCOL", "VERSION"]
