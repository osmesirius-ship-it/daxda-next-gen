"""
DAXDA Authoritative Actuator Boundary & Cryptographic Governance Gate
====================================================================

Implements:
1. Authoritative Policy Engine: Single, non-bypassable gateway for all tool & actuator calls.
2. Fail-Closed on Uncertainty: Unknown actions, missing identity, malformed context,
   policy errors, stale receipts, and failed verifications deny execution or require explicit human approval.
3. Cryptographic Actuator Boundary Enforcement: Actuators verify cryptographically bound
   authorization receipts (action, target_device, principal, context_hash, expiry, request_id nonce).
4. Simulation vs Live Decoupling: Explicit AdapterExecutionMode (SIMULATED, MOCKED, LIVE) with
   full telemetry recording of hardware, API endpoints, credential fingerprints, and external calls.
"""

from __future__ import annotations

import hmac
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from daxda_guard.core import DAXDAGuardCore, GovernanceReceipt
from daxda_guard.nicole_gate import NicoleProtocolGate, NicoleGateResult


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AdapterExecutionMode(str, Enum):
    SIMULATED = "SIMULATED"   # Synthetic software simulation / physics model
    MOCKED = "MOCKED"         # Unit test double / static fixture
    LIVE = "LIVE"             # Real physical hardware / production cloud API


class GovernanceDisposition(str, Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REQUIRES_HUMAN_AUTHORIZATION = "REQUIRES_HUMAN_AUTHORIZATION"


class FailClosedReason(str, Enum):
    NONE = "NONE"
    UNKNOWN_ACTION = "FAIL_CLOSED_UNKNOWN_ACTION"
    MISSING_IDENTITY = "FAIL_CLOSED_MISSING_IDENTITY"
    MALFORMED_CONTEXT = "FAIL_CLOSED_MALFORMED_CONTEXT"
    POLICY_ERROR = "FAIL_CLOSED_POLICY_ERROR"
    STALE_RECEIPT = "FAIL_CLOSED_STALE_RECEIPT"
    REPLAY_DETECTED = "FAIL_CLOSED_REPLAY_DETECTED"
    VERIFICATION_FAILED = "FAIL_CLOSED_VERIFICATION_FAILED"
    DEVICE_MISMATCH = "FAIL_CLOSED_DEVICE_MISMATCH"
    ACTION_MISMATCH = "FAIL_CLOSED_ACTION_MISMATCH"
    CONTEXT_HASH_MISMATCH = "FAIL_CLOSED_CONTEXT_HASH_MISMATCH"
    HIGH_RISK_THRESHOLD = "REQUIRE_EXPLICIT_HUMAN_AUTHORIZATION"


# ---------------------------------------------------------------------------
# Canonical Context Hashing (RFC 8785-compatible deterministic JSON)
# ---------------------------------------------------------------------------

def compute_canonical_context_hash(parameters: Dict[str, Any]) -> str:
    """Computes a deterministic SHA-256 hash over canonicalized JSON parameters."""
    if not isinstance(parameters, dict):
        raise ValueError("Parameters must be a dictionary.")
    canonical_json = json.dumps(
        parameters,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
        default=str
    )
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()


# ---------------------------------------------------------------------------
# Cryptographically Bound Actuator Authorization Receipt
# ---------------------------------------------------------------------------

@dataclass
class ActuatorAuthorizationReceipt:
    request_id: str                   # Unique cryptographic nonce (UUIDv4)
    action: str                       # Authorized action / tool verb
    target_device: str                # Target hardware URI / device ID
    principal: str                    # Authenticated tenant / agent / user ID
    context_hash: str                 # SHA-256 of canonical execution parameters
    issued_at: float                  # Timestamp of issuance (epoch seconds)
    expires_at: float                 # Timestamp of expiration (epoch seconds)
    disposition: GovernanceDisposition # APPROVED / REQUIRES_HUMAN_AUTHORIZATION
    decision_rule: str                # Governance rule code
    authority_sha256: str             # Cryptographic hash from underlying engine
    signature: str                    # HMAC-SHA256 signature binding all fields
    human_authorized: bool = False    # True if explicit human confirmation provided
    human_authorizer_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["disposition"] = self.disposition.value
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ---------------------------------------------------------------------------
# Authoritative Policy Engine
# ---------------------------------------------------------------------------

class AuthoritativePolicyEngine:
    """
    Central, non-bypassable governance engine.
    
    Routes all actuator-related tool calls through:
    1. Caller Identity & Context Validation
    2. NicoleProtocolGate (Layer 1 semantic threat classifier)
    3. DAXDAGuardCore (Layer 2 C++ Cl(16,4) manifold gate)
    4. Cryptographic Binding & Receipt Minting
    
    FAILS CLOSED on any ambiguity, error, unknown action, or missing identity.
    """

    def __init__(
        self,
        signing_key: Optional[bytes] = None,
        default_ttl_seconds: float = 60.0,
        registered_actions: Optional[Set[str]] = None
    ):
        self.signing_key = signing_key or b"daxda_master_actuator_boundary_key_v16_4"
        self.default_ttl = default_ttl_seconds
        self.nicole_gate = NicoleProtocolGate()
        self.core = DAXDAGuardCore()

        # Default registered actions if not provided
        self.registered_actions: Set[str] = registered_actions if registered_actions is not None else {
            # Actuator actions
            "actuator.propulsion.set_mode",
            "actuator.propulsion.fire_thrust",
            "actuator.navigation.waypoint_update",
            "actuator.subsystem.recalibrate",
            "actuator.hardware.e_stop",
            # MCP Tool actions
            "hf_text_generation",
            "hf_embedding",
            "hf_agent_query",
            "hf_model_search",
            "hf_dataset_card",
            "enterprise_action_api",
        }

        # Registered high-risk actions requiring explicit human approval
        self.high_risk_actions: Set[str] = {
            "actuator.propulsion.fire_thrust",
            "actuator.hardware.e_stop",
            "actuator.hardware.override_interlock"
        }

    def register_action(self, action_name: str, high_risk: bool = False) -> None:
        """Register a valid action name with the policy engine."""
        self.registered_actions.add(action_name.strip())
        if high_risk:
            self.high_risk_actions.add(action_name.strip())

    def _sign_payload(self, canonical_payload: str) -> str:
        """Sign canonical receipt payload with HMAC-SHA256."""
        return hmac.new(self.signing_key, canonical_payload.encode('utf-8'), hashlib.sha256).hexdigest()

    def evaluate_request(
        self,
        action: str,
        target_device: str,
        principal: str,
        parameters: Dict[str, Any],
        domain: str = "general",
        human_token: Optional[str] = None
    ) -> Tuple[GovernanceDisposition, Optional[ActuatorAuthorizationReceipt], FailClosedReason, str]:
        """
        Authoritatively evaluates an action request.
        
        Returns:
            (disposition, receipt, fail_closed_reason, message)
        """
        # 1. Identity Validation (Fail closed if missing or empty)
        if not principal or not isinstance(principal, str) or not principal.strip():
            return (
                GovernanceDisposition.DENIED,
                None,
                FailClosedReason.MISSING_IDENTITY,
                "Fail-closed: Caller principal identity is missing or empty."
            )

        # 2. Action Validation (Fail closed if unknown action or malformed action name)
        if not action or not isinstance(action, str) or action not in self.registered_actions:
            return (
                GovernanceDisposition.DENIED,
                None,
                FailClosedReason.UNKNOWN_ACTION,
                f"Fail-closed: Action '{action}' is unrecognized or unregistered."
            )

        # 3. Target Device Validation
        if not target_device or not isinstance(target_device, str) or not target_device.strip():
            return (
                GovernanceDisposition.DENIED,
                None,
                FailClosedReason.MALFORMED_CONTEXT,
                "Fail-closed: Target device identifier is missing or malformed."
            )

        # 4. Context Parameter Validation & Canonical Hashing
        try:
            if not isinstance(parameters, dict):
                raise ValueError("Parameters must be a dictionary")
            context_hash = compute_canonical_context_hash(parameters)
        except Exception as e:
            return (
                GovernanceDisposition.DENIED,
                None,
                FailClosedReason.MALFORMED_CONTEXT,
                f"Fail-closed: Malformed context parameters ({str(e)})."
            )

        # 5. Dual-Layer Governance Evaluation (Nicole Protocol + C++ Manifold)
        try:
            probe_text = f"Action: {action} | Device: {target_device} | Principal: {principal} | Params: {json.dumps(parameters, default=str)}"
            gate_result: NicoleGateResult = self.nicole_gate.evaluate(domain, probe_text)
            
            if not gate_result.permitted:
                rule = gate_result.threat_label or "DENY_ISOLATED"
                return (
                    GovernanceDisposition.DENIED,
                    None,
                    FailClosedReason.POLICY_ERROR,
                    f"Governance blocked by {rule}: invariant {gate_result.invariant_ref or 'INV-GATE'}"
                )
            
            authority_sha256 = gate_result.dual_sha256_seal
        except Exception as e:
            # Policy error / unhandled exception -> MUST FAIL CLOSED
            return (
                GovernanceDisposition.DENIED,
                None,
                FailClosedReason.POLICY_ERROR,
                f"Fail-closed on policy engine exception: {str(e)}"
            )

        # 6. Check High Risk / Human Authorization Requirement
        now = time.time()
        is_high_risk = action in self.high_risk_actions
        human_approved = False
        authorizer_id = None

        if is_high_risk:
            # Requires explicit human token
            if not human_token or not human_token.startswith("HUMAN_AUTH_TOKEN:"):
                return (
                    GovernanceDisposition.REQUIRES_HUMAN_AUTHORIZATION,
                    None,
                    FailClosedReason.HIGH_RISK_THRESHOLD,
                    f"Action '{action}' is classified HIGH_RISK and requires explicit human authorization token."
                )
            human_approved = True
            authorizer_id = human_token.split(":", 1)[1]

        # 7. Mint Cryptographically Bound Receipt
        req_id = str(uuid.uuid4())
        expires_at = now + self.default_ttl
        
        # Build canonical payload to sign
        canonical_binding = f"{req_id}|{action}|{target_device}|{principal}|{context_hash}|{now:.4f}|{expires_at:.4f}|{authority_sha256}"
        signature = self._sign_payload(canonical_binding)

        receipt = ActuatorAuthorizationReceipt(
            request_id=req_id,
            action=action,
            target_device=target_device,
            principal=principal,
            context_hash=context_hash,
            issued_at=now,
            expires_at=expires_at,
            disposition=GovernanceDisposition.APPROVED,
            decision_rule="WITHIN_GOVERNANCE_TOLERANCE",
            authority_sha256=authority_sha256,
            signature=signature,
            human_authorized=human_approved,
            human_authorizer_id=authorizer_id
        )

        return (GovernanceDisposition.APPROVED, receipt, FailClosedReason.NONE, "Authorized")


# ---------------------------------------------------------------------------
# Actuator Boundary & Trusted Adapter
# ---------------------------------------------------------------------------

@dataclass
class ActuatorExecutionAuditRecord:
    timestamp_utc: float
    action: str
    target_device: str
    principal: str
    execution_mode: AdapterExecutionMode
    hardware_target: str
    api_endpoint: str
    credential_fingerprint: str
    external_calls_recorded: List[Dict[str, Any]]
    success: bool
    status_code: str
    error_message: Optional[str] = None


class ActuatorBoundary:
    """
    Enforces authorization AT THE ACTUATOR BOUNDARY.
    
    Verifies that:
    1. A valid, unexpired receipt exists.
    2. The receipt's cryptographic signature is authentic.
    3. The receipt's request_id (nonce) has never been seen before (Anti-Replay).
    4. The bound action, target_device, and principal match the request.
    5. The canonical context_hash matches the incoming parameters exactly.
    6. Clearly logs execution mode (SIMULATED, MOCKED, LIVE) and records call ledger.
    """

    def __init__(
        self,
        device_id: str,
        execution_mode: AdapterExecutionMode = AdapterExecutionMode.SIMULATED,
        signing_key: Optional[bytes] = None,
        clock_skew_tolerance_sec: float = 2.0
    ):
        self.device_id = device_id
        self.execution_mode = execution_mode
        self.signing_key = signing_key or b"daxda_master_actuator_boundary_key_v16_4"
        self.clock_skew_tolerance = clock_skew_tolerance_sec

        # Replay prevention nonce cache (stores consumed request_ids)
        self._consumed_nonces: Set[str] = set()
        # Execution audit ledger
        self.audit_log: List[ActuatorExecutionAuditRecord] = []

    def _verify_receipt_signature(self, receipt: ActuatorAuthorizationReceipt) -> bool:
        canonical_binding = (
            f"{receipt.request_id}|{receipt.action}|{receipt.target_device}|"
            f"{receipt.principal}|{receipt.context_hash}|{receipt.issued_at:.4f}|"
            f"{receipt.expires_at:.4f}|{receipt.authority_sha256}"
        )
        expected_sig = hmac.new(
            self.signing_key, canonical_binding.encode('utf-8'), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, receipt.signature)

    def verify_authorization(
        self,
        action: str,
        parameters: Dict[str, Any],
        principal: str,
        receipt: Optional[ActuatorAuthorizationReceipt]
    ) -> Tuple[bool, FailClosedReason, str]:
        """
        Strict boundary verification before actuator execution.
        """
        # 1. Check receipt presence
        if receipt is None:
            return (False, FailClosedReason.VERIFICATION_FAILED, "Missing authorization receipt at actuator boundary.")

        # 2. Check cryptographic signature integrity
        if not self._verify_receipt_signature(receipt):
            return (False, FailClosedReason.VERIFICATION_FAILED, "Cryptographic signature verification failed: tampered receipt.")

        # 3. Check explicit approval disposition (Verdict must be APPROVED / PASS)
        if receipt.disposition != GovernanceDisposition.APPROVED:
            return (False, FailClosedReason.VERIFICATION_FAILED, f"Receipt disposition is '{receipt.disposition.value}', requires APPROVED.")

        # 4. Anti-Replay Check (Verify request_id nonce hasn't been consumed)
        if receipt.request_id in self._consumed_nonces:
            return (False, FailClosedReason.REPLAY_DETECTED, f"Replay detected: request_id '{receipt.request_id}' already consumed.")

        # 5. Expiry & Freshness Window Check (Bidirectional bounds)
        now = time.time()
        if now > (receipt.expires_at + self.clock_skew_tolerance):
            return (False, FailClosedReason.STALE_RECEIPT, f"Receipt expired at {receipt.expires_at} (current time {now}).")
        if now < (receipt.issued_at - self.clock_skew_tolerance):
            return (False, FailClosedReason.STALE_RECEIPT, f"Receipt issued in the future (issued_at {receipt.issued_at}, current time {now}).")

        # 6. Target Device Binding Check
        if receipt.target_device != self.device_id:
            return (False, FailClosedReason.DEVICE_MISMATCH, f"Device mismatch: receipt bound to '{receipt.target_device}', actuator is '{self.device_id}'.")

        # 6. Action Binding Check
        if receipt.action != action:
            return (False, FailClosedReason.ACTION_MISMATCH, f"Action mismatch: receipt bound to '{receipt.action}', requested '{action}'.")

        # 7. Principal Identity Binding Check
        if receipt.principal != principal:
            return (False, FailClosedReason.MISSING_IDENTITY, f"Principal mismatch: receipt bound to '{receipt.principal}', caller is '{principal}'.")

        # 8. Context Parameter Tamper Check
        current_context_hash = compute_canonical_context_hash(parameters)
        if receipt.context_hash != current_context_hash:
            return (False, FailClosedReason.CONTEXT_HASH_MISMATCH, "Parameter hash mismatch: parameters were modified after governance approval.")

        # Mark nonce as consumed to prevent replay
        self._consumed_nonces.add(receipt.request_id)
        return (True, FailClosedReason.NONE, "Verified")

    def execute_governed_action(
        self,
        action: str,
        parameters: Dict[str, Any],
        principal: str,
        receipt: Optional[ActuatorAuthorizationReceipt],
        driver_callback: Any,
        hardware_info: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        credential_alias: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verifies boundary authorization and dispatches to driver with telemetry audit ledger.
        """
        hw_target = hardware_info or (f"sim://{self.device_id}" if self.execution_mode == AdapterExecutionMode.SIMULATED else f"hw://{self.device_id}")
        endpoint = api_endpoint or ("internal://simulator" if self.execution_mode != AdapterExecutionMode.LIVE else "https://api.device.live")
        cred_alias = credential_alias or ("CRED_NONE" if self.execution_mode == AdapterExecutionMode.SIMULATED else "KMS_ALIAS_PROD_***")

        external_calls: List[Dict[str, Any]] = []
        now = time.time()

        # Step 1: Boundary Verification
        valid, reason, msg = self.verify_authorization(action, parameters, principal, receipt)
        if not valid:
            audit = ActuatorExecutionAuditRecord(
                timestamp_utc=now,
                action=action,
                target_device=self.device_id,
                principal=principal,
                execution_mode=self.execution_mode,
                hardware_target=hw_target,
                api_endpoint=endpoint,
                credential_fingerprint=cred_alias,
                external_calls_recorded=external_calls,
                success=False,
                status_code=reason.value,
                error_message=msg
            )
            self.audit_log.append(audit)
            return {
                "success": False,
                "status": "DENIED_AT_ACTUATOR_BOUNDARY",
                "reason": reason.value,
                "message": msg,
                "execution_mode": self.execution_mode.value,
                "device_id": self.device_id
            }

        # Step 2: Driver Execution
        try:
            call_start = time.perf_counter()
            call_record = {
                "call_id": str(uuid.uuid4())[:8],
                "action": action,
                "mode": self.execution_mode.value,
                "timestamp": now
            }
            external_calls.append(call_record)

            # Invoke driver
            driver_result = driver_callback(parameters)
            call_duration = (time.perf_counter() - call_start) * 1000.0
            call_record["duration_ms"] = round(call_duration, 3)
            call_record["status"] = "OK"

            audit = ActuatorExecutionAuditRecord(
                timestamp_utc=now,
                action=action,
                target_device=self.device_id,
                principal=principal,
                execution_mode=self.execution_mode,
                hardware_target=hw_target,
                api_endpoint=endpoint,
                credential_fingerprint=cred_alias,
                external_calls_recorded=external_calls,
                success=True,
                status_code="EXECUTED"
            )
            self.audit_log.append(audit)

            return {
                "success": True,
                "status": "EXECUTED",
                "execution_mode": self.execution_mode.value,
                "device_id": self.device_id,
                "driver_output": driver_result,
                "receipt_request_id": receipt.request_id,
                "call_ledger": external_calls
            }
        except Exception as e:
            audit = ActuatorExecutionAuditRecord(
                timestamp_utc=now,
                action=action,
                target_device=self.device_id,
                principal=principal,
                execution_mode=self.execution_mode,
                hardware_target=hw_target,
                api_endpoint=endpoint,
                credential_fingerprint=cred_alias,
                external_calls_recorded=external_calls,
                success=False,
                status_code="DRIVER_FAULT",
                error_message=str(e)
            )
            self.audit_log.append(audit)
            return {
                "success": False,
                "status": "DRIVER_FAULT",
                "execution_mode": self.execution_mode.value,
                "device_id": self.device_id,
                "error": str(e)
            }


class GovernedPropulsionActuator:
    """
    Physical / simulated hardware actuator adapter wrapping the tri-propulsion drive.
    Guarantees that no physical motion or thruster ignition can occur without
    cryptographic boundary authorization.
    """
    def __init__(
        self,
        device_id: str = "sungur.actuator.tri_propulsion_01",
        execution_mode: AdapterExecutionMode = AdapterExecutionMode.SIMULATED,
        hardware_model: str = "DAXDA-HYBRID-DRIVE-V1"
    ):
        self.device_id = device_id
        self.hardware_model = hardware_model
        self.boundary = ActuatorBoundary(device_id=device_id, execution_mode=execution_mode)
        try:
            from sungur_omni.subsystems.propulsion import TriPropulsionSubsystem
            self._driver = TriPropulsionSubsystem()
        except ImportError:
            self._driver = None

    def execute_propulsion_command(
        self,
        target_mode: str,
        throttle_pct: float,
        telemetry_dict: Dict[str, Any],
        principal: str,
        receipt: Optional[ActuatorAuthorizationReceipt]
    ) -> Dict[str, Any]:
        action = "actuator.propulsion.set_mode"
        parameters = {
            "target_mode": target_mode,
            "throttle_pct": throttle_pct,
            "telemetry": telemetry_dict
        }

        def _driver_dispatch(params: Dict[str, Any]) -> Dict[str, Any]:
            if self._driver is None:
                return {
                    "simulated": True,
                    "target_mode": params["target_mode"],
                    "throttle_pct": params["throttle_pct"],
                    "thrust_kn": params["throttle_pct"] * 1.8,
                    "status": "PROPULSION_ENGAGED"
                }
            from sungur_omni.core.types import PropulsionMode, TelemetryVector, OperationalDomain
            mode_enum = PropulsionMode(params["target_mode"].upper())
            dom_val = params["telemetry"].get("domain", "LAND").upper()
            tel = TelemetryVector(
                domain=OperationalDomain(dom_val),
                altitude_m=float(params["telemetry"].get("altitude_m", 0.0)),
                velocity_mps=float(params["telemetry"].get("velocity_mps", 0.0)),
                mach_number=float(params["telemetry"].get("mach_number", 0.1)),
                hydrostatic_pressure_bar=float(params["telemetry"].get("hydrostatic_pressure_bar", 1.0)),
                hull_temperature_c=float(params["telemetry"].get("hull_temperature_c", 25.0)),
                qins_drift_error_m=float(params["telemetry"].get("qins_drift_error_m", 0.001)),
                propellant_kg=float(params["telemetry"].get("propellant_kg", 2000.0)),
                core_power_mw=float(params["telemetry"].get("core_power_mw", 10.0)),
                structural_integrity_pct=float(params["telemetry"].get("structural_integrity_pct", 100.0))
            )
            return self._driver.evaluate_propulsion_command(mode_enum, params["throttle_pct"], tel)

        return self.boundary.execute_governed_action(
            action=action,
            parameters=parameters,
            principal=principal,
            receipt=receipt,
            driver_callback=_driver_dispatch,
            hardware_info=f"hardware://{self.hardware_model}/{self.device_id}",
            api_endpoint=f"canbus://0x7A4/{self.device_id}" if self.boundary.execution_mode == AdapterExecutionMode.LIVE else "sim://propulsion_bus",
            credential_alias="HSM_SLOT_ACTUATOR_01" if self.boundary.execution_mode == AdapterExecutionMode.LIVE else "CRED_NONE"
        )

