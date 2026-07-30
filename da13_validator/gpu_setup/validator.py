import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jsonschema import Draft202012Validator


class ValidationErrorWithRule(Exception):
    def __init__(self, rule_id: str, message: str):
        super().__init__(message)
        self.rule_id = rule_id
        self.message = message


def load_schema(schema_path: str) -> Dict[str, Any]:
    return json.loads(Path(schema_path).read_text(encoding="utf-8"))


def schema_validate(payload: Dict[str, Any], schema: Dict[str, Any]) -> List[Dict[str, str]]:
    validator = Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(payload), key=lambda e: e.path):
        errors.append(
            {
                "rule_id": "VAL-001",
                "category": "SCHEMA",
                "message": err.message,
                "path": "/" + "/".join(str(p) for p in err.path),
            }
        )
    return errors


def recompute_score(payload: Dict[str, Any]) -> Dict[str, float]:
    s = payload["stability"]
    w = s["weights"]
    c = s["components"]
    score = (
        w["wL"] * c["L"]["value"]
        + w["wA"] * c["A"]["value"]
        + w["wP"] * c["P"]["value"]
        + w["wF"] * c["F"]["value"]
        + w["wT"] * c["T"]["value"]
    )
    return {"score": round(score, 6)}


def expected_decision(payload: Dict[str, Any]) -> str:
    st = payload["stability"]
    score = st["score"]
    c = st["components"]
    iteration = payload["meta"]["current_iteration"]
    max_iterations = payload["meta"]["max_iterations"]

    if iteration > max_iterations:
        return "HALT"
    if c["F"]["value"] < 0.50 or c["T"]["value"] < 0.60:
        return "RECURSE"
    if score >= st["threshold"]:
        return "ACCEPT"
    if score >= 0.55:
        return "RECURSE"
    return "HALT"


def semantic_validate(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []

    # VAL-005
    weights = payload["stability"]["weights"]
    w_sum = weights["wL"] + weights["wA"] + weights["wP"] + weights["wF"] + weights["wT"]
    if abs(w_sum - 1.0) > 1e-9:
        errors.append(
            {
                "rule_id": "VAL-005",
                "category": "SCORING",
                "message": "Weight sum must equal 1",
                "path": "/stability/weights",
            }
        )

    # VAL-004
    recomputed = recompute_score(payload)["score"]
    provided = round(payload["stability"]["score"], 6)
    if recomputed != provided:
        errors.append(
            {
                "rule_id": "VAL-004",
                "category": "SCORING",
                "message": "Stability score does not match recomputed score",
                "path": "/stability/score",
            }
        )

    # VAL-007
    exp_decision = expected_decision(payload)
    if payload["dax_decision"]["status"] != exp_decision:
        errors.append(
            {
                "rule_id": "VAL-007",
                "category": "DECISION",
                "message": f"Decision mismatch; expected {exp_decision}",
                "path": "/dax_decision/status",
            }
        )

    # VAL-009
    if payload["dax_decision"]["status"] == "RECURSE" and "mutation_contract" not in payload["recursion"]:
        errors.append(
            {
                "rule_id": "VAL-009",
                "category": "RECURSION",
                "message": "RECURSE requires mutation_contract",
                "path": "/recursion/mutation_contract",
            }
        )

    # VAL-010
    if payload["meta"]["current_iteration"] > payload["meta"]["max_iterations"]:
        errors.append(
            {
                "rule_id": "VAL-010",
                "category": "RECURSION",
                "message": "Iteration exceeds max_iterations",
                "path": "/meta/current_iteration",
            }
        )

    return errors


def validate_payload(payload: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    errors = schema_validate(payload, schema)
    if not errors:
        errors.extend(semantic_validate(payload))

    ok = len(errors) == 0
    report = {
        "validation_status": "PASS" if ok else "FAIL",
        "errors": errors,
        "expected_decision": expected_decision(payload) if not errors or payload.get("dax_decision") else None,
        "actual_decision": payload.get("dax_decision", {}).get("status"),
        "action": "EMIT" if ok else "HALT",
    }
    return ok, report
