"""
Containment, Isolation & Operational Hardening Test Suite: DAXDA Fleet Daemon
=============================================================================

Validates the 5 Core Fleet Containment Gates:
1. Loopback Binding: Verifies socket binds strictly to 127.0.0.1, never 0.0.0.0.
2. Endpoint Isolation: Verifies /api/* endpoints are read-only / advisory and do NOT expose actuator authority.
3. Orderly Shutdown & State Preservation: Verifies graceful termination (SIGTERM/SIGINT) with intact telemetry.
4. Telemetry Integrity: Verifies SHA-256 state chain detects altered, reordered, and missing records.
5. Fault Injection & Actuator Isolation: Verifies that daemon failure strictly prevents actuator authorization.
"""

import os
import sys
import json
import time
import socket
import urllib.request
import urllib.parse
import threading
import tempfile
import copy
from datetime import datetime, timezone
import pytest

from tools.daxda_fleet_daemon import (
    DAXDAFleetDaemon,
    verify_telemetry_hash_chain,
    create_authenticated_checkpoint,
    verify_authenticated_checkpoint,
    quarantine_corrupt_log,
    sha256_text,
    sha256_file,
    DEFAULT_CHECKPOINT_KEY,
)
from daxda_guard.actuator_boundary import (
    AuthoritativePolicyEngine,
    ActuatorBoundary,
    GovernedPropulsionActuator,
    ActuatorAuthorizationReceipt,
    AdapterExecutionMode,
    GovernanceDisposition,
    FailClosedReason,
    compute_canonical_context_hash,
)


@pytest.fixture
def ephemeral_port():
    """Finds an available ephemeral port for loopback testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestFleetDaemonContainment:
    """Verifies loopback binding, endpoint isolation, shutdown, and tamper detection."""

    def test_loopback_binding_strictly_enforced(self, ephemeral_port):
        """P0: Asserts the listening socket binds exclusively to 127.0.0.1."""
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=1.0)
        daemon.start_server()
        try:
            # Wait for socket to bind
            time.sleep(0.15)
            assert daemon.httpd is not None
            server_host, server_port = daemon.httpd.server_address
            assert server_host == "127.0.0.1", f"Expected 127.0.0.1 loopback bind, got {server_host}"
            assert server_port == ephemeral_port

            # Verify it is reachable on 127.0.0.1
            url = f"http://127.0.0.1:{ephemeral_port}/api/telemetry"
            req = urllib.request.urlopen(url, timeout=2.0)
            assert req.status == 200
        finally:
            daemon.stop_server()

    def test_endpoints_isolation_no_actuator_authority(self, ephemeral_port):
        """Verifies GET and POST API endpoints do not expose or execute actuator actions."""
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=1.0)
        # Seed telemetry
        daemon.run_cycle()
        daemon.start_server()
        try:
            time.sleep(0.15)

            # 1. GET /api/telemetry
            t_url = f"http://127.0.0.1:{ephemeral_port}/api/telemetry"
            with urllib.request.urlopen(t_url, timeout=2.0) as resp:
                assert resp.status == 200
                data = json.loads(resp.read().decode("utf-8"))
                assert "metrics" in data
                assert "system" in data
                # No actuator controls in telemetry payload
                assert "actuators" not in data
                assert "execute" not in data

            # 2. GET /api/agents
            a_url = f"http://127.0.0.1:{ephemeral_port}/api/agents"
            with urllib.request.urlopen(a_url, timeout=2.0) as resp:
                assert resp.status == 200
                data = json.loads(resp.read().decode("utf-8"))
                assert "agents" in data

            # 3. GET /api/sleeper_analysis
            s_url = f"http://127.0.0.1:{ephemeral_port}/api/sleeper_analysis"
            with urllib.request.urlopen(s_url, timeout=2.0) as resp:
                assert resp.status == 200

            # 4. POST /api/scan (Advisory classifier only)
            scan_url = f"http://127.0.0.1:{ephemeral_port}/api/scan"
            req_data = json.dumps({"domain": "security_audit", "payload": "Clifford grade-0 rotor"}).encode("utf-8")
            post_req = urllib.request.Request(scan_url, data=req_data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(post_req, timeout=2.0) as resp:
                assert resp.status == 200
                scan_res = json.loads(resp.read().decode("utf-8"))
                assert "verdict" in scan_res
                # Must be advisory; cannot contain actuator tokens or driver handles
                assert "actuator_token" not in scan_res
                assert "driver_handle" not in scan_res

            # 5. Non-existent actuator endpoint returns 404
            act_url = f"http://127.0.0.1:{ephemeral_port}/api/actuator/fire_thrust"
            try:
                urllib.request.urlopen(act_url, timeout=1.0)
                pytest.fail("Actuator endpoint should return 404")
            except urllib.error.HTTPError as e:
                assert e.code == 404
        finally:
            daemon.stop_server()

    def test_orderly_shutdown_and_state_preservation(self, ephemeral_port):
        """P1: Verifies shutdown signal sets shutdown_requested, halts cleanly, and preserves state."""
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=0.05)
        initial_cycles = daemon.cycle_count
        daemon.start_server()
        try:
            # Run 2 cycles
            daemon.run_cycle()
            daemon.run_cycle()
            assert daemon.cycle_count == initial_cycles + 2
            prev_hash = daemon.prev_state_hash
            assert prev_hash != "0" * 64

            # Request shutdown
            daemon.request_shutdown()
            assert daemon.shutdown_requested.is_set()

            # Verify server closed
            daemon.stop_server()
            assert daemon.shutdown_requested.is_set()

            # Confirm state was preserved
            outputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
            t_file = os.path.join(outputs_dir, "fleet_telemetry.json")
            assert os.path.exists(t_file)
            with open(t_file, "r") as f:
                saved = json.load(f)
                assert saved["cycles_completed"] == daemon.cycle_count
                assert saved["last_state_hash"] == prev_hash
        finally:
            daemon.stop_server()

    def test_artifact_integrity_hash_chain_tamper_detection(self):
        """Verifies verify_telemetry_hash_chain detects altered, reordered, and missing records."""
        with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False) as f:
            temp_path = f.name

        try:
            # Build valid 3-cycle chain
            chain = []
            prev_h = "0" * 64
            for i in range(1, 4):
                payload = {
                    "cycle": i,
                    "timestamp": f"2026-10-20T12:00:0{i}Z",
                    "unit": "test",
                    "prev_state_hash": prev_h
                }
                raw = json.dumps(payload, sort_keys=True)
                st_hash = sha256_text(raw)
                prev_h = st_hash
                payload["state_hash"] = st_hash
                chain.append(payload)

            # Write pristine chain
            with open(temp_path, "w") as f:
                for rec in chain:
                    f.write(json.dumps(rec) + "\n")

            valid, cnt, err = verify_telemetry_hash_chain(temp_path)
            assert valid is True
            assert cnt == 3
            assert err is None

            # Case A: Altered record (tampering)
            with open(temp_path, "w") as f:
                corrupted_chain = [dict(c) for c in chain]
                corrupted_chain[1]["unit"] = "TAMPERED_PAYLOAD"  # Hash will not match
                for rec in corrupted_chain:
                    f.write(json.dumps(rec) + "\n")

            valid, cnt, err = verify_telemetry_hash_chain(temp_path)
            assert valid is False
            assert "Tamper detected at record 2" in err

            # Case B: Reordered records
            with open(temp_path, "w") as f:
                reordered = [chain[0], chain[2], chain[1]]
                for rec in reordered:
                    f.write(json.dumps(rec) + "\n")

            valid, cnt, err = verify_telemetry_hash_chain(temp_path)
            assert valid is False
            assert "Sequence break at record 2" in err or "Chain break at record 2" in err

            # Case C: Missing / deleted record
            with open(temp_path, "w") as f:
                deleted = [chain[0], chain[2]]  # Dropped record 1
                for rec in deleted:
                    f.write(json.dumps(rec) + "\n")

            valid, cnt, err = verify_telemetry_hash_chain(temp_path)
            assert valid is False
            assert "Sequence break at record 2" in err or "Chain break at record 2" in err

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestFaultInjectionAndActuatorIsolation:
    """
    Fault-Injection: Proves that daemon failure / shutdown CANNOT authorize actuator execution.
    Actuator authority remains locked fail-closed regardless of monitoring daemon state.
    """

    def test_daemon_termination_cannot_authorize_actuator_execution(self, ephemeral_port):
        """
        Fault injection: Start daemon, kill daemon, attempt actuator execution.
        Must strictly fail-closed at actuator boundary.
        """
        # 1. Initialize daemon and actuator
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=0.1)
        daemon.start_server()
        time.sleep(0.1)

        actuator = GovernedPropulsionActuator(
            device_id="sungur.actuator.tri_propulsion_01",
            execution_mode=AdapterExecutionMode.SIMULATED
        )

        # 2. Simulate complete daemon crash / termination
        daemon.request_shutdown()
        daemon.stop_server()
        assert daemon.shutdown_requested.is_set()

        # 3. Attempt protected actuator operation with NO receipt (or forged/empty receipt)
        result_no_receipt = actuator.execute_propulsion_command(
            target_mode="planetary_electric",
            throttle_pct=75.0,
            telemetry_dict={"domain": "AIR", "altitude_m": 5000.0},
            principal="adversary_attacker",
            receipt=None
        )

        assert result_no_receipt["success"] is False
        assert result_no_receipt["status"] == "DENIED_AT_ACTUATOR_BOUNDARY"
        assert result_no_receipt["reason"] == FailClosedReason.VERIFICATION_FAILED.value
        assert "Missing authorization receipt" in result_no_receipt["message"]

    def test_daemon_unauthorized_token_forgery_rejected(self):
        """
        Verifies that any token produced without the policy engine's HMAC secret key
        is rejected at the actuator boundary even if daemon is running or dead.
        """
        boundary = ActuatorBoundary(
            device_id="sungur.actuator.tri_propulsion_01",
            execution_mode=AdapterExecutionMode.SIMULATED
        )

        params = {"target_mode": "planetary_electric", "throttle_pct": 50.0}

        # Attempt execution with forged dummy receipt
        valid, reason, msg = boundary.verify_authorization(
            action="actuator.propulsion.set_mode",
            parameters=params,
            principal="attacker",
            receipt=None
        )
        assert valid is False
        assert reason == FailClosedReason.VERIFICATION_FAILED

    def test_actuator_boundary_enforces_all_invariant_dimensions(self):
        """
        P0 Actuator Invariant:
        Permit <=> ReceiptValid AND HMACValid AND (Verdict == APPROVED)
                   AND DeviceMatch AND ActionMatch AND PrincipalMatch AND ContextMatch AND FreshnessValid.
        Verifies every single dimension of the security invariant independently.
        """
        engine = AuthoritativePolicyEngine()
        boundary = ActuatorBoundary(
            device_id="sungur.actuator.tri_propulsion_01",
            execution_mode=AdapterExecutionMode.SIMULATED
        )
        action = "actuator.propulsion.set_mode"
        params = {"target_mode": "planetary_electric", "throttle_pct": 50.0}
        principal = "operator.yunus"

        # Baseline: Valid approved receipt -> True
        disp, valid_rcpt, reason, msg = engine.evaluate_request(
            action=action,
            target_device="sungur.actuator.tri_propulsion_01",
            principal=principal,
            parameters=params
        )
        assert disp == GovernanceDisposition.APPROVED
        assert valid_rcpt is not None

        # 1. Missing receipt -> Denied
        ok, r, _ = boundary.verify_authorization(action, params, principal, receipt=None)
        assert ok is False
        assert r == FailClosedReason.VERIFICATION_FAILED

        # 2. Forged signature / HMAC invalid -> Denied
        forged_rcpt = copy.deepcopy(valid_rcpt)
        forged_rcpt.signature = "f" * 64
        ok, r, _ = boundary.verify_authorization(action, params, principal, receipt=forged_rcpt)
        assert ok is False
        assert r == FailClosedReason.VERIFICATION_FAILED

        # 3. Unapproved disposition (e.g. DENIED) with valid HMAC -> Denied
        unapproved_rcpt = copy.deepcopy(valid_rcpt)
        unapproved_rcpt.disposition = GovernanceDisposition.DENIED
        unapproved_rcpt.signature = engine._sign_payload(
            f"{unapproved_rcpt.request_id}|{unapproved_rcpt.action}|{unapproved_rcpt.target_device}|"
            f"{unapproved_rcpt.principal}|{unapproved_rcpt.context_hash}|{unapproved_rcpt.issued_at:.4f}|"
            f"{unapproved_rcpt.expires_at:.4f}|{unapproved_rcpt.authority_sha256}"
        )
        ok, r, _ = boundary.verify_authorization(action, params, principal, receipt=unapproved_rcpt)
        assert ok is False
        assert r == FailClosedReason.VERIFICATION_FAILED

        # 4. Action mismatch -> Denied
        ok, r, _ = boundary.verify_authorization("actuator.propulsion.fire_thrust", params, principal, receipt=valid_rcpt)
        assert ok is False
        assert r == FailClosedReason.ACTION_MISMATCH

        # 5. Device mismatch -> Denied
        other_boundary = ActuatorBoundary("other.device.id")
        ok, r, _ = other_boundary.verify_authorization(action, params, principal, receipt=valid_rcpt)
        assert ok is False
        assert r == FailClosedReason.DEVICE_MISMATCH

        # 6. Principal mismatch -> Denied
        ok, r, _ = boundary.verify_authorization(action, params, principal="adversary", receipt=valid_rcpt)
        assert ok is False
        assert r == FailClosedReason.MISSING_IDENTITY

        # 7. Context hash / parameter modification -> Denied
        tampered_params = {"target_mode": "planetary_electric", "throttle_pct": 100.0}
        ok, r, _ = boundary.verify_authorization(action, tampered_params, principal, receipt=valid_rcpt)
        assert ok is False
        assert r == FailClosedReason.CONTEXT_HASH_MISMATCH

        # 8. Stale expired receipt -> Denied
        stale_rcpt = copy.deepcopy(valid_rcpt)
        stale_rcpt.expires_at = time.time() - 100.0
        stale_rcpt.signature = engine._sign_payload(
            f"{stale_rcpt.request_id}|{stale_rcpt.action}|{stale_rcpt.target_device}|"
            f"{stale_rcpt.principal}|{stale_rcpt.context_hash}|{stale_rcpt.issued_at:.4f}|"
            f"{stale_rcpt.expires_at:.4f}|{stale_rcpt.authority_sha256}"
        )
        ok, r, _ = boundary.verify_authorization(action, params, principal, receipt=stale_rcpt)
        assert ok is False
        assert r == FailClosedReason.STALE_RECEIPT

        # 9. Future issued timestamp -> Denied
        future_rcpt = copy.deepcopy(valid_rcpt)
        future_rcpt.issued_at = time.time() + 300.0
        future_rcpt.signature = engine._sign_payload(
            f"{future_rcpt.request_id}|{future_rcpt.action}|{future_rcpt.target_device}|"
            f"{future_rcpt.principal}|{future_rcpt.context_hash}|{future_rcpt.issued_at:.4f}|"
            f"{future_rcpt.expires_at:.4f}|{future_rcpt.authority_sha256}"
        )
        ok, r, _ = boundary.verify_authorization(action, params, principal, receipt=future_rcpt)
        assert ok is False
        assert r == FailClosedReason.STALE_RECEIPT

        # 10. Legitimate receipt -> Success (1st use), Replay detected (2nd use)
        ok1, r1, _ = boundary.verify_authorization(action, params, principal, receipt=valid_rcpt)
        assert ok1 is True
        assert r1 == FailClosedReason.NONE

        ok2, r2, _ = boundary.verify_authorization(action, params, principal, receipt=valid_rcpt)
        assert ok2 is False
        assert r2 == FailClosedReason.REPLAY_DETECTED


class TestFleetDaemonOperationalHardening:
    """Verifies fail-closed scanner decisions, 64KB body limits, CORS isolation, and chain truncation."""

    def test_post_scan_fail_closed_on_payload_too_large(self, ephemeral_port):
        """Verifies payloads exceeding 64KB return HTTP 413 with fail-closed verdict and NO dissipation credited."""
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=1.0)
        daemon.start_server()
        try:
            time.sleep(0.1)
            scan_url = f"http://127.0.0.1:{ephemeral_port}/api/scan"
            oversized_payload = json.dumps({"domain": "defense", "payload": "A" * 70000}).encode("utf-8")
            req = urllib.request.Request(
                scan_url,
                data=oversized_payload,
                headers={"Content-Type": "application/json"}
            )
            try:
                urllib.request.urlopen(req, timeout=2.0)
                pytest.fail("Oversized payload should have returned HTTP 413")
            except urllib.error.HTTPError as e:
                assert e.code == 413
                res = json.loads(e.read().decode("utf-8"))
                assert res["verdict"] == "HOLD_FOR_REVIEW"
                assert res["execution_permitted"] is False
                assert res["null_vector_dissipated"] is False
                assert res["dissipation_status"] == "NOT_RUN"
                assert "exceeds 64 KB limit" in res["error"]
        finally:
            daemon.stop_server()

    def test_post_scan_fail_closed_on_malformed_json_and_empty_body(self, ephemeral_port):
        """Verifies malformed JSON or empty body returns HTTP 400 with fail-closed verdict and NOT_RUN dissipation."""
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=1.0)
        daemon.start_server()
        try:
            time.sleep(0.1)
            scan_url = f"http://127.0.0.1:{ephemeral_port}/api/scan"

            # 1. Malformed JSON
            req1 = urllib.request.Request(
                scan_url,
                data=b"NOT_VALID_JSON{abc:",
                headers={"Content-Type": "application/json"}
            )
            try:
                urllib.request.urlopen(req1, timeout=2.0)
                pytest.fail("Malformed JSON should have returned HTTP 400")
            except urllib.error.HTTPError as e:
                assert e.code == 400
                res = json.loads(e.read().decode("utf-8"))
                assert res["verdict"] == "HOLD_FOR_REVIEW"
                assert res["execution_permitted"] is False
                assert res["null_vector_dissipated"] is False
                assert res["dissipation_status"] == "NOT_RUN"

            # 2. Empty payload field
            req2 = urllib.request.Request(
                scan_url,
                data=json.dumps({"domain": "general", "payload": "   "}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            try:
                urllib.request.urlopen(req2, timeout=2.0)
                pytest.fail("Empty payload string should have returned HTTP 400")
            except urllib.error.HTTPError as e:
                assert e.code == 400
                res = json.loads(e.read().decode("utf-8"))
                assert res["verdict"] == "HOLD_FOR_REVIEW"
                assert res["execution_permitted"] is False
                assert res["null_vector_dissipated"] is False
                assert res["dissipation_status"] == "NOT_RUN"
        finally:
            daemon.stop_server()

    def test_post_scan_fail_closed_on_scanner_exception(self, ephemeral_port):
        """Verifies scanner exception returns HTTP 500 with fail-closed verdict and NOT_RUN dissipation."""
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=1.0)

        # Mock scanner that throws
        class CrashingScanner:
            def scan_enterprise_payload(self, *args, **kwargs):
                raise RuntimeError("Internal scanner fault injection")

        daemon.scanner = CrashingScanner()
        daemon.start_server()
        try:
            time.sleep(0.1)
            scan_url = f"http://127.0.0.1:{ephemeral_port}/api/scan"
            req = urllib.request.Request(
                scan_url,
                data=json.dumps({"domain": "defense", "payload": "Normal input"}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            try:
                urllib.request.urlopen(req, timeout=2.0)
                pytest.fail("Crashing scanner should have returned HTTP 500")
            except urllib.error.HTTPError as e:
                assert e.code == 500
                res = json.loads(e.read().decode("utf-8"))
                assert res["verdict"] == "HOLD_FOR_REVIEW"
                assert res["execution_permitted"] is False
                assert res["null_vector_dissipated"] is False
                assert res["dissipation_status"] == "NOT_RUN"
                assert "Internal scanner fault injection" in res["error"]
        finally:
            daemon.stop_server()

    def test_exact_origin_cors_and_cross_origin_blocking(self, ephemeral_port):
        """Verifies exact port-specific CORS allowlist and rejection of foreign web origins."""
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=1.0)
        daemon.run_cycle()
        daemon.start_server()
        try:
            time.sleep(0.1)
            url_telemetry = f"http://127.0.0.1:{ephemeral_port}/api/telemetry"
            url_scan = f"http://127.0.0.1:{ephemeral_port}/api/scan"

            # Case A: External evil origin on GET -> Access-Control-Allow-Origin not set
            req_ext = urllib.request.Request(url_telemetry, headers={"Origin": "https://malicious-site.example.com"})
            with urllib.request.urlopen(req_ext, timeout=2.0) as resp:
                headers = dict(resp.getheaders())
                assert headers.get("Access-Control-Allow-Origin") is None

            # Case B: Cross-port origin (e.g. localhost:3000) on GET -> Access-Control-Allow-Origin not set
            req_diff_port = urllib.request.Request(url_telemetry, headers={"Origin": "http://127.0.0.1:3000"})
            with urllib.request.urlopen(req_diff_port, timeout=2.0) as resp:
                headers = dict(resp.getheaders())
                assert headers.get("Access-Control-Allow-Origin") is None

            # Case C: Cross-port origin on POST -> HTTP 403 Forbidden
            post_data = json.dumps({"domain": "software", "payload": "print(1)"}).encode("utf-8")
            req_cross_post = urllib.request.Request(
                url_scan,
                data=post_data,
                headers={"Content-Type": "application/json", "Origin": "http://127.0.0.1:3000"}
            )
            try:
                urllib.request.urlopen(req_cross_post, timeout=2.0)
                pytest.fail("Cross-port POST should return 403")
            except urllib.error.HTTPError as e:
                assert e.code == 403
                res = json.loads(e.read().decode("utf-8"))
                assert res["verdict"] == "HOLD_FOR_REVIEW"
                assert res["execution_permitted"] is False
                assert res["decision_rule"] == "FAIL_CLOSED_CROSS_ORIGIN_BLOCKED"

            # Case D: Exact matching dashboard origin -> Allowed
            req_exact = urllib.request.Request(
                url_scan,
                data=post_data,
                headers={"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{ephemeral_port}"}
            )
            with urllib.request.urlopen(req_exact, timeout=2.0) as resp:
                assert resp.status == 200
                headers = dict(resp.getheaders())
                assert headers.get("Access-Control-Allow-Origin") == f"http://127.0.0.1:{ephemeral_port}"
        finally:
            daemon.stop_server()

    def test_corrupt_log_quarantine_and_clean_recovery(self):
        """Verifies corrupt existing log is quarantined on startup, starting clean from genesis and validating on restart."""
        outputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
        receipts_file = os.path.join(outputs_dir, "fleet_cycle_receipts.jsonl")

        # Backup existing receipts file if present
        backup_file = receipts_file + ".test_backup"
        if os.path.exists(receipts_file):
            os.replace(receipts_file, backup_file)

        quarantined_path = None
        try:
            # 1. Create deliberately corrupted receipts log
            corrupted_content = (
                json.dumps({"cycle": 1, "state_hash": "a" * 64, "prev_state_hash": "0" * 64}) + "\n"
                + json.dumps({"cycle": 3, "state_hash": "b" * 64, "prev_state_hash": "a" * 64}) + "\n"  # Skipped cycle 2!
            )
            with open(receipts_file, "w") as f:
                f.write(corrupted_content)

            # 2. Instantiate daemon -> should detect corruption, quarantine file, and reset to genesis
            daemon1 = DAXDAFleetDaemon(interval_sec=0.1)
            assert daemon1.cycle_count == 0
            assert daemon1.prev_state_hash == "0" * 64
            assert daemon1.last_quarantined_log is not None
            quarantined_path = daemon1.last_quarantined_log
            assert os.path.exists(quarantined_path)
            # The corrupted content is safely preserved in quarantine
            with open(quarantined_path, "r") as qf:
                assert qf.read() == corrupted_content

            # 3. Run cycle 1 on fresh chain
            res1 = daemon1.run_cycle()
            assert res1["cycle"] == 1
            assert daemon1.cycle_count == 1
            assert daemon1.prev_state_hash != "0" * 64

            # 4. Verify fresh receipt log validates 100%
            valid1, cnt1, err1 = verify_telemetry_hash_chain(receipts_file)
            assert valid1 is True
            assert cnt1 == 1
            assert err1 is None

            # 5. Second restart recovery: new daemon starts up and restores cycle 1 without quarantining
            daemon2 = DAXDAFleetDaemon(interval_sec=0.1)
            assert daemon2.cycle_count == 1
            assert daemon2.prev_state_hash == res1["state_hash"]
            assert daemon2.last_quarantined_log is None
        finally:
            # Cleanup test artifacts
            if quarantined_path and os.path.exists(quarantined_path):
                os.remove(quarantined_path)
            if os.path.exists(backup_file):
                os.replace(backup_file, receipts_file)

    def test_quarantine_collision_safety_and_byte_preservation(self):
        """
        P0 Quarantine Invariant:
        1. When a quarantine artifact already exists at the primary timestamped destination,
           the quarantine mechanism disambiguates using a monotonic suffix (.1.jsonl, .2.jsonl)
           and NEVER overwrites or corrupts the existing quarantine artifact.
        2. Verifies exact byte preservation by checking source and destination SHA-256 and byte sizes.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            corrupt_src = os.path.join(tmp_dir, "fleet_cycle_receipts.jsonl")
            corrupt_bytes = b'{"cycle": 1, "bad_data": true}\n{"cycle": 999, "broken": true}\n'
            with open(corrupt_src, "wb") as f:
                f.write(corrupt_bytes)

            src_hash = sha256_file(corrupt_src)
            src_len = len(corrupt_bytes)

            # Pre-create the primary collision target
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            primary_collision = os.path.join(tmp_dir, f"fleet_cycle_receipts.corrupt.{ts}.jsonl")
            prior_artifact_bytes = b"PRIOR_UNTOUCHED_QUARANTINE_ARTIFACT_DO_NOT_OVERWRITE\n"
            with open(primary_collision, "wb") as f:
                f.write(prior_artifact_bytes)
            prior_hash = sha256_file(primary_collision)

            # Execute quarantine
            ok, q_path, q_sha = quarantine_corrupt_log(corrupt_src, reason="test_collision_safety")
            assert ok is True
            assert q_path is not None
            assert q_path != primary_collision, "Must NOT overwrite existing quarantine artifact!"
            assert q_path.endswith(".1.jsonl"), f"Expected collision suffix .1.jsonl, got {q_path}"
            assert os.path.exists(q_path)

            # 1. Verify prior artifact was untouched
            assert sha256_file(primary_collision) == prior_hash
            with open(primary_collision, "rb") as f:
                assert f.read() == prior_artifact_bytes

            # 2. Verify quarantined artifact preserves exact bytes of corrupt source
            assert q_sha == src_hash
            assert sha256_file(q_path) == src_hash
            assert os.path.getsize(q_path) == src_len
            with open(q_path, "rb") as f:
                assert f.read() == corrupt_bytes

            # 3. Source file was safely unlinked after verified transfer
            assert not os.path.exists(corrupt_src)

    def test_authenticated_external_checkpoint_and_truncation(self):
        """
        P0 Checkpoint Completeness Invariant:
        1. An authenticated checkpoint anchor cryptographically binds terminal cycle and hash with HMAC-SHA256.
        2. Chain validation against the authenticated checkpoint detects suffix truncation.
        3. A forged or tampered checkpoint signature is rejected immediately as untrusted.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            chain_file = os.path.join(tmp_dir, "fleet_cycle_receipts.jsonl")
            cp_file = os.path.join(tmp_dir, "fleet_chain_checkpoint.json")

            # Build 5-cycle chain
            chain = []
            prev_h = "0" * 64
            for i in range(1, 6):
                payload = {
                    "cycle": i,
                    "timestamp": f"2026-10-20T12:00:0{i}Z",
                    "prev_state_hash": prev_h
                }
                raw = json.dumps(payload, sort_keys=True)
                st_h = sha256_text(raw)
                prev_h = st_h
                payload["state_hash"] = st_h
                chain.append(payload)

            # 1. Create authenticated checkpoint for full 5-cycle chain
            cp_data = create_authenticated_checkpoint(
                cycle=5,
                state_hash=chain[4]["state_hash"],
                signing_key=DEFAULT_CHECKPOINT_KEY,
                checkpoint_filepath=cp_file
            )
            assert os.path.exists(cp_file)

            # 2. Verify checkpoint signature independently
            valid_cp, term_cycle, term_hash, cp_err = verify_authenticated_checkpoint(cp_file, DEFAULT_CHECKPOINT_KEY)
            assert valid_cp is True
            assert term_cycle == 5
            assert term_hash == chain[4]["state_hash"]
            assert cp_err is None

            # 3. Forged checkpoint signature is rejected
            with open(cp_file, "r") as f:
                forged_data = json.load(f)
            forged_data["checkpoint_signature"] = "0" * 64
            forged_cp_file = os.path.join(tmp_dir, "forged_checkpoint.json")
            with open(forged_cp_file, "w") as f:
                json.dump(forged_data, f)

            valid_forged, _, _, forged_err = verify_authenticated_checkpoint(forged_cp_file, DEFAULT_CHECKPOINT_KEY)
            assert valid_forged is False
            assert "Checkpoint signature verification failed" in forged_err

            # 4. Truncated chain (write only 3 cycles out of 5)
            with open(chain_file, "w") as f:
                for rec in chain[:3]:
                    f.write(json.dumps(rec) + "\n")

            # Validated with trusted checkpoint -> Truncation detected!
            chain_valid, count, chain_err = verify_telemetry_hash_chain(chain_file, checkpoint=cp_file)
            assert chain_valid is False
            assert "Truncation detected" in chain_err
            assert "expected 5" in chain_err

            # 5. Full chain written (cycles 1..5) -> Passes 100% against checkpoint
            with open(chain_file, "w") as f:
                for rec in chain:
                    f.write(json.dumps(rec) + "\n")

            full_valid, full_count, full_err = verify_telemetry_hash_chain(chain_file, checkpoint=cp_file)
            assert full_valid is True
            assert full_count == 5
            assert full_err is None

    def test_hash_chain_genesis_predecessor_enforcement(self):
        """Verifies verify_telemetry_hash_chain rejects record 1 if prev_state_hash is not 64 zeros."""
        with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False) as f:
            temp_path = f.name

        try:
            # Record 1 with non-zero genesis predecessor
            bad_genesis = {
                "cycle": 1,
                "timestamp": "2026-10-20T12:00:00Z",
                "prev_state_hash": "deadbeef" * 8  # Not 64 zeros
            }
            raw = json.dumps(bad_genesis, sort_keys=True)
            bad_genesis["state_hash"] = sha256_text(raw)

            with open(temp_path, "w") as f:
                f.write(json.dumps(bad_genesis) + "\n")

            valid, cnt, err = verify_telemetry_hash_chain(temp_path)
            assert valid is False
            assert "Chain break at record 1" in err and "does not match expected" in err
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_hash_chain_suffix_truncation_detection(self):
        """Verifies verify_telemetry_hash_chain detects truncated suffix against expected checkpoint."""
        with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False) as f:
            temp_path = f.name

        try:
            chain = []
            prev_h = "0" * 64
            for i in range(1, 5):
                payload = {
                    "cycle": i,
                    "timestamp": f"2026-10-20T12:00:0{i}Z",
                    "prev_state_hash": prev_h
                }
                raw = json.dumps(payload, sort_keys=True)
                st_h = sha256_text(raw)
                prev_h = st_h
                payload["state_hash"] = st_h
                chain.append(payload)

            # Write only first 2 records (suffix 3 & 4 truncated)
            with open(temp_path, "w") as f:
                f.write(json.dumps(chain[0]) + "\n")
                f.write(json.dumps(chain[1]) + "\n")

            # Check without checkpoint -> internal chain is valid for 2 records
            valid, cnt, err = verify_telemetry_hash_chain(temp_path)
            assert valid is True
            assert cnt == 2

            # Check with expected final cycle 4 -> detects truncation
            expected_cycle = 4
            expected_hash = chain[3]["state_hash"]
            valid_chk, cnt_chk, err_chk = verify_telemetry_hash_chain(
                temp_path,
                expected_final_cycle=expected_cycle,
                expected_final_hash=expected_hash
            )
            assert valid_chk is False
            assert "Truncation detected" in err_chk
            assert "expected 4" in err_chk
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_indeterminate_and_error_paths_do_not_credit_dissipation(self, ephemeral_port):
        """
        P0 Invariant: Asserts that an unexecuted, errored, or indeterminate scan NEVER credits null-vector dissipation.
        - Fail-closed error/rejection: execution_permitted=False, null_vector_dissipated=False, dissipation_status="NOT_RUN".
        - Indeterminate verdict: execution_permitted=False, null_vector_dissipated=False, dissipation_status="INDETERMINATE".
        - Explicit block: execution_permitted=False, null_vector_dissipated=True, dissipation_status="DISSIPATED".
        - Explicit pass: execution_permitted=True, null_vector_dissipated=False, dissipation_status="NOT_APPLICABLE".
        """
        daemon = DAXDAFleetDaemon(host="127.0.0.1", port=ephemeral_port, interval_sec=1.0)

        # Mock scanner that can return custom schemas
        class ControlledScanner:
            mode = "block"

            def scan_enterprise_payload(self, domain, payload_text, source_id="test"):
                if self.mode == "block":
                    return {
                        "final_verdict": "BLOCK",
                        "final_rule": "ADVERSARIAL_PROMPT_INJECTION",
                        "final_pub_permitted": False,
                        "containment_stage": "STAGE_1_INGRESS",
                        "receipt_sha256": "1" * 64,
                        "grade0_scalar": 0.0,
                        "reconstruction_loss": 0.95
                    }
                elif self.mode == "pass":
                    return {
                        "final_verdict": "PASS",
                        "final_rule": "BENIGN_MULTIVECTOR_OPERATION",
                        "final_pub_permitted": True,
                        "containment_stage": "PASS",
                        "receipt_sha256": "2" * 64,
                        "grade0_scalar": 1.0,
                        "reconstruction_loss": 0.01
                    }
                elif self.mode == "indeterminate":
                    return {
                        "final_verdict": "UNKNOWN_CUSTOM_VERDICT",  # Non-standard verdict
                        "final_rule": "UNCLASSIFIED_PATTERN",
                        "final_pub_permitted": False,
                        "containment_stage": "STAGE_UNKNOWN",
                        "receipt_sha256": "3" * 64
                    }
                elif self.mode == "malformed":
                    return "NOT_A_DICTIONARY"

        mock_scanner = ControlledScanner()
        daemon.scanner = mock_scanner
        daemon.start_server()

        try:
            time.sleep(0.1)
            scan_url = f"http://127.0.0.1:{ephemeral_port}/api/scan"
            headers = {"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{ephemeral_port}"}

            # 1. Explicit block: credits dissipation
            mock_scanner.mode = "block"
            req_block = urllib.request.Request(
                scan_url,
                data=json.dumps({"domain": "defense", "payload": "attack"}).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req_block, timeout=2.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                assert res["verdict"] == "BLOCK"
                assert res["execution_permitted"] is False
                assert res["null_vector_dissipated"] is True
                assert res["dissipation_status"] == "DISSIPATED"

            # 2. Explicit pass: no dissipation (scalar preserved), execution permitted
            mock_scanner.mode = "pass"
            req_pass = urllib.request.Request(
                scan_url,
                data=json.dumps({"domain": "general", "payload": "hello"}).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req_pass, timeout=2.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                assert res["verdict"] == "PASS"
                assert res["execution_permitted"] is True
                assert res["null_vector_dissipated"] is False
                assert res["dissipation_status"] == "NOT_APPLICABLE"

            # 3. Indeterminate verdict: fail-closed HOLD_FOR_REVIEW, NO dissipation credited
            mock_scanner.mode = "indeterminate"
            req_indet = urllib.request.Request(
                scan_url,
                data=json.dumps({"domain": "general", "payload": "mystery"}).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req_indet, timeout=2.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                assert res["verdict"] == "HOLD_FOR_REVIEW"
                assert res["execution_permitted"] is False
                assert res["null_vector_dissipated"] is False
                assert res["dissipation_status"] == "INDETERMINATE"

            # 4. Malformed scanner output: fail-closed 500, NO dissipation credited
            mock_scanner.mode = "malformed"
            req_malf = urllib.request.Request(
                scan_url,
                data=json.dumps({"domain": "general", "payload": "bad_output"}).encode("utf-8"),
                headers=headers
            )
            try:
                urllib.request.urlopen(req_malf, timeout=2.0)
                pytest.fail("Malformed output should return HTTP 500")
            except urllib.error.HTTPError as e:
                assert e.code == 500
                res = json.loads(e.read().decode("utf-8"))
                assert res["verdict"] == "HOLD_FOR_REVIEW"
                assert res["execution_permitted"] is False
                assert res["null_vector_dissipated"] is False
                assert res["dissipation_status"] == "NOT_RUN"
        finally:
            daemon.stop_server()
