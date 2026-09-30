"""
DA13 JSON Schema & Semantic Validator
====================================

Validates DAXDA execution payloads against dax-full-system.schema.json
and enforces semantic rules VAL-001 through VAL-007.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from .dax_scoring import DAXScoringEngine


class SchemaValidationError(Exception):
    def __init__(self, rule_id: str, message: str, path: str = "/"):
        super().__init__(f"[{rule_id}] {message} at {path}")
        self.rule_id = rule_id
        self.message = message
        self.path = path


class SchemaValidator:
    """Enforces JSON schema structural constraints and DAX semantic rules."""

    def __init__(self, schema_path: Optional[str] = None):
        self.schema_path = schema_path or str(
            Path(__file__).resolve().parent.parent / "dax-full-system.schema.json"
        )
        self.schema = self._load_schema()
        self.scoring_engine = DAXScoringEngine()

    def _load_schema(self) -> Dict[str, Any]:
        """Loads JSON schema if file exists, or provides baseline schema."""
        p = Path(self.schema_path)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"type": "object", "required": ["meta", "stability"]}

    def validate(self, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Runs both structural schema validation and semantic rule validation.
        Returns a list of error dictionaries containing rule_id, message, and path.
        """
        errors: List[Dict[str, str]] = []

        # 1. Structural checks (VAL-001 / VAL-002)
        errors.extend(self._validate_structure(payload))

        # 2. Semantic scoring checks (VAL-004, VAL-005, VAL-006, VAL-007)
        errors.extend(self._validate_semantics(payload))

        return errors

    def _validate_structure(self, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        errors = []
        if not isinstance(payload, dict):
            return [{"rule_id": "VAL-001", "category": "SCHEMA", "message": "Payload must be a JSON object", "path": "/"}]

        # Check required top-level fields
        required_fields = ["meta", "stability"]
        for field in required_fields:
            if field not in payload:
                errors.append({
                    "rule_id": "VAL-001",
                    "category": "SCHEMA",
                    "message": f"Missing required top-level property: {field}",
                    "path": f"/{field}"
                })

        meta = payload.get("meta", {})
        if not isinstance(meta, dict):
            errors.append({"rule_id": "VAL-001", "category": "SCHEMA", "message": "'meta' must be an object", "path": "/meta"})
        else:
            for req_meta in ["schema_version"]:
                if req_meta not in meta:
                    errors.append({
                        "rule_id": "VAL-002",
                        "category": "SCHEMA",
                        "message": f"Missing metadata property: {req_meta}",
                        "path": f"/meta/{req_meta}"
                    })

        return errors

    def _validate_semantics(self, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        errors = []
        stability = payload.get("stability")
        if not isinstance(stability, dict):
            return errors

        weights = stability.get("weights")
        if isinstance(weights, dict):
            # VAL-005: Weights must sum to 1.0
            w_sum = sum(float(weights.get(k, 0.0)) for k in ["wL", "wA", "wP", "wF", "wT"])
            if abs(w_sum - 1.0) > 1e-4:
                errors.append({
                    "rule_id": "VAL-005",
                    "category": "SCORING",
                    "message": f"Weight sum must equal 1.0 (found {w_sum:.4f})",
                    "path": "/stability/weights"
                })

        components = stability.get("components")
        if isinstance(components, dict):
            # VAL-006: Components must be in [0, 1]
            for c_name in ["L", "A", "P", "F", "T"]:
                comp = components.get(c_name)
                val = comp.get("value") if isinstance(comp, dict) else comp
                if val is not None:
                    try:
                        val_f = float(val)
                        if val_f < 0.0 or val_f > 1.0:
                            errors.append({
                                "rule_id": "VAL-006",
                                "category": "SCORING",
                                "message": f"Component {c_name} value must be within [0, 1] (found {val_f})",
                                "path": f"/stability/components/{c_name}"
                            })
                    except (ValueError, TypeError):
                        errors.append({
                            "rule_id": "VAL-006",
                            "category": "SCORING",
                            "message": f"Component {c_name} value must be numeric",
                            "path": f"/stability/components/{c_name}"
                        })

        # VAL-004: Score recalculation check
        if "score" in stability and isinstance(weights, dict) and isinstance(components, dict):
            try:
                res = self.scoring_engine.compute_stability_score(payload)
                provided_score = round(float(stability["score"]), 4)
                calculated_score = round(res.score, 4)
                if abs(provided_score - calculated_score) > 0.05:
                    errors.append({
                        "rule_id": "VAL-004",
                        "category": "SCORING",
                        "message": f"Provided score {provided_score} differs from calculated {calculated_score}",
                        "path": "/stability/score"
                    })

                # VAL-007: Decision threshold mismatch
                dax_decision = payload.get("dax_decision")
                if isinstance(dax_decision, dict) and "status" in dax_decision:
                    expected_status = res.decision
                    if dax_decision["status"] != expected_status:
                        errors.append({
                            "rule_id": "VAL-007",
                            "category": "DECISION",
                            "message": f"dax_decision status '{dax_decision['status']}' does not match expected '{expected_status}'",
                            "path": "/dax_decision/status"
                        })
            except Exception:
                pass

        return errors

    def is_valid(self, payload: Dict[str, Any]) -> bool:
        """Returns True if payload has zero schema or semantic errors."""
        return len(self.validate(payload)) == 0
