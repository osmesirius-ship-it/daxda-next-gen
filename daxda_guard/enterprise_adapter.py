"""
DAXDA Enterprise Authorization Adapter
======================================
Translates internal Clifford multivector traces and authority gate evaluations
into standardized enterprise authorization receipts conforming to the
Blueprint Alliance (Okta, AWS, CrowdStrike, GCP), NIST TEVV, and EU AI Act specifications.
"""

import uuid
import datetime
import hashlib
import json
from typing import Dict, Any, Optional

class DAXDAEnterpriseAdapter:
    """
    Adapter converting internal DAXDA Clifford traces and gate evaluations
    into enterprise-standard DAXDAEnterpriseAuthorizationReceipt objects.
    """

    @staticmethod
    def emit_receipt(
        trace_data: Dict[str, Any],
        agent_id: str = "agent.enterprise.default",
        spiffe_id: str = "spiffe://prod.enterprise/ns/agents/sa/daxda-worker",
        model_family: str = "gpt-4o-2024-11-20",
        user_id: str = "principal.operator@enterprise.com",
        org_tenant_id: str = "org-tenant-01",
        task_id: Optional[str] = None,
        intent_description: Optional[str] = None,
        target_tool: str = "enterprise_action_api",
        action_verb: str = "EXECUTE",
        target_uri: str = "https://api.internal.enterprise/v1/action",
        privilege_level: str = "SCOPED_WRITE",
        customer_kms_key_id: str = "alias/customer-audit-signing-key"
    ) -> Dict[str, Any]:
        """
        Produce a validated enterprise authorization receipt from Clifford trace data.
        """
        gate = trace_data.get("gate_evaluation", {})
        disposition = trace_data.get("disposition", "BLOCK")
        
        # Map internal disposition to enterprise gate_decision
        if disposition == "RELEASE":
            gate_decision = "RELEASE"
            is_contained = False
            null_status = "STABLE_CONVERGENT"
            rollback_id = None
        elif disposition == "BLOCK":
            gate_decision = "BLOCK"
            is_contained = True
            null_status = "DISSIPATION_COLLAPSE"
            rollback_id = f"rb-{uuid.uuid4().hex[:12]}"
        else:
            gate_decision = "RELEASE_WITH_CAUTION"
            is_contained = False
            null_status = "STABLE_CONVERGENT"
            rollback_id = None

        # Extract dominant blade channel
        semantic_channels = trace_data.get("semantic_blade_channels", {})
        dominant_blade = "e1_trust"
        max_coeff = -1.0
        for blade, val in semantic_channels.items():
            if abs(val) > max_coeff:
                max_coeff = abs(val)
                dominant_blade = blade

        # Build mock customer KMS signature over the canonical trace SHA-256
        audit_sha256 = trace_data.get("tamper_evident_sha256", hashlib.sha256(json.dumps(trace_data, default=str).encode()).hexdigest())
        customer_kms_sig = f"kms-sig:{customer_kms_key_id}:{hashlib.sha256((audit_sha256 + customer_kms_key_id).encode()).hexdigest()[:32]}"

        receipt = {
            "receipt_id": str(uuid.uuid4()),
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "agent_identity": {
                "agent_id": agent_id,
                "runtime_spiffe_id": spiffe_id,
                "model_family": model_family,
                "version_hash": f"sha256:{hashlib.sha256(model_family.encode()).hexdigest()[:16]}"
            },
            "principal_identity": {
                "user_id": user_id,
                "delegated_session_id": str(uuid.uuid4()),
                "org_tenant_id": org_tenant_id
            },
            "task_scope": {
                "task_id": task_id or trace_data.get("case_id", f"task-{uuid.uuid4().hex[:8]}"),
                "intent_description": intent_description or trace_data.get("input_text", "General agent execution request"),
                "ephemeral_ttl_seconds": 300
            },
            "resource_scope": {
                "target_tool_or_api": target_tool,
                "action_verb": action_verb,
                "target_uri": target_uri
            },
            "privilege_level": privilege_level,
            "authority_channel_verdict": {
                "gate_decision": gate_decision,
                "confidence_cs": float(gate.get("coherence_S_M", 0.95)),
                "dominant_blade": dominant_blade,
                "null_horizon_status": null_status
            },
            "containment_state": {
                "is_contained": is_contained,
                "reversible_rollback_supported": True,
                "rollback_vector_id": rollback_id
            },
            "reproducibility": {
                "engine_version": trace_data.get("engine_version", "DAXDA-NEXTGEN/1.0.0"),
                "basis_signature": "Cl(4,1)[+1,+1,+1,+1,-1]",
                "audit_sha256": audit_sha256,
                "customer_kms_signature": customer_kms_sig
            }
        }

        return receipt
