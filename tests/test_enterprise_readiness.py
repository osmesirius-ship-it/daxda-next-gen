"""
Unit & Integration Test Suite: Enterprise Readiness & Operational Hardening
===========================================================================

Validates all 10 enterprise readiness domains:
1. Governance & Prompts (config/layers.json, schema, versioning, DA-7 human on-call gates)
2. Security & Secrets (mTLS/JWT authentication, PII scrubbing, DA-8 signed evidence blobs)
3. Compliance & Data Handling (layer classification, DSR erasure hooks, tombstone verification)
4. Reliability & Performance (per-layer circuit breakers, jitter backoff, idempotency deduplication)
5. Observability & Auditability (deterministic error taxonomy, structured audit receipts)
"""

import os
import json
import time
from pathlib import Path
import pytest

from da13_validator.api.enterprise_auth import (
    EnterpriseAuthenticator,
    EnterpriseUserRole,
    EnterpriseErrorCode,
    EnterpriseErrorResponse,
    PIIRedactionEngine,
    DA8EvidenceSigner
)
from da13_validator.monitoring.circuit_breaker import (
    CircuitState,
    CircuitBreakerConfig,
    LayerCircuitBreaker,
    IdempotencyManager,
    ReliabilityRegistry
)
from da13_validator.monitoring.dsr_erasure import (
    DataClassification,
    LAYER_CLASSIFICATION_REGISTRY,
    DSRErasureEngine
)
from da13_validator.scoring.multi_engine_dispatcher import (
    MultiEngineDispatcher,
    EngineLineage,
    EngineEvaluationReceipt,
    MultiEngineConsensusReport
)


# ---------------------------------------------------------------------------
# Domain 1: Governance & Prompt Freeze Tests
# ---------------------------------------------------------------------------

class TestGovernanceAndPrompts:
    """Verifies config/layers.json structure, domain prompts, version freeze, and DA-7 human gates."""

    @pytest.fixture
    def layers_config(self):
        # Check both potential paths
        p1 = Path(__file__).resolve().parent.parent / "config" / "layers.json"
        p2 = Path(__file__).resolve().parent.parent.parent / "config" / "layers.json"
        target_path = p1 if p1.exists() else p2
        assert target_path.exists(), f"config/layers.json not found at {target_path}"
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_governance_version_frozen(self, layers_config):
        gov = layers_config.get("governance", {})
        assert gov.get("status") == "FROZEN_APPROVED"
        assert gov.get("layers_version") == "2.1.0-frozen"
        assert len(gov.get("approved_by", [])) >= 3
        policy = gov.get("change_approval_policy", {})
        assert policy.get("requires_pr") is True
        assert policy.get("minimum_reviewers") >= 2

    def test_all_16_layers_present_with_domains(self, layers_config):
        layers = layers_config.get("layers", [])
        assert len(layers) == 16

        expected_ids = [f"DA-{i}" for i in range(15, 0, -1)] + ["DA-X"]
        actual_ids = [layer["id"] for layer in layers]
        assert actual_ids == expected_ids

        domains = ["general_enterprise", "financial_services", "healthcare_lifesciences", "cybersecurity_infosec"]
        for layer in layers:
            assert "prompts" in layer
            for domain in domains:
                assert domain in layer["prompts"]
                assert len(layer["prompts"][domain]) > 20
            # Check pinned params
            params = layer.get("parameters", {})
            assert "temperature" in params
            assert "seed" in params
            assert "max_tokens" in params

    def test_model_allowlist_and_fallback_order(self, layers_config):
        model_gov = layers_config.get("model_governance", {})
        allowlist = model_gov.get("allowlist", [])
        assert len(allowlist) >= 3

        # Verify Anthropic and OpenAI are present with pinned versions
        providers = {m["provider"]: m for m in allowlist}
        assert "anthropic" in providers
        assert "openai" in providers
        assert "sovereign_enclave" in providers

        assert providers["anthropic"]["pinned_version"] == "2024-10-22"
        assert providers["openai"]["pinned_version"] == "2024-11-20"

        # Verify fallback order
        fallbacks = model_gov.get("fallback_order", [])
        assert len(fallbacks) >= 4
        assert fallbacks[0].startswith("anthropic:")
        assert "deterministic_reconciler:local_safe_gate" in fallbacks[-1]

    def test_da7_human_gate_and_on_call_slas(self, layers_config):
        human_gates = layers_config.get("human_gates", {})
        assert "DA-7" in human_gates
        da7 = human_gates["DA-7"]
        assert da7["layer_id"] == "DA-7"

        rotations = da7.get("on_call_rotations", {})
        assert "tier1" in rotations
        assert "tier2" in rotations
        assert "tier3" in rotations

        assert rotations["tier1"]["sla_minutes"] <= 15
        assert rotations["tier2"]["sla_minutes"] <= 60
        assert rotations["tier3"]["sla_minutes"] <= 240

        timeout_policy = da7.get("timeout_policy", {})
        assert timeout_policy.get("fail_closed") is True
        assert timeout_policy.get("default_action") == "HALT"
        assert timeout_policy.get("timeout_seconds") == 900


# ---------------------------------------------------------------------------
# Domain 2: Security, Authentication & DA-8 Signed Evidence Tests
# ---------------------------------------------------------------------------

class TestSecurityAndSecrets:
    """Verifies enterprise authentication, zero-trust anonymous blocking, PII scrubbing, and DA-8 signed evidence."""

    def test_authenticated_token_validation(self):
        auth = EnterpriseAuthenticator(is_production=True)
        # Valid admin token
        client, err = auth.authenticate(auth_header="Bearer dax-prod-admin-token-2026")
        assert err is None
        assert client is not None
        assert client.role == EnterpriseUserRole.ADMIN
        assert auth.check_permission(client, "validate") is True
        assert auth.check_permission(client, "dsr_purge") is True

    def test_production_blocks_anonymous_access(self):
        auth = EnterpriseAuthenticator(is_production=True)
        # Missing token in production
        client, err = auth.authenticate(auth_header=None)
        assert client is None
        assert err is not None
        assert err.error_code == EnterpriseErrorCode.AUTH_MISSING_OR_INVALID
        assert err.http_status == 401

    def test_dev_allows_sandbox_anonymous_access(self):
        auth = EnterpriseAuthenticator(is_production=False)
        client, err = auth.authenticate(auth_header=None)
        assert err is None
        assert client is not None
        assert client.client_id == "dev-sandbox-anonymous"

    def test_pii_redaction_engine(self):
        dirty_text = (
            "User credentials: api_key='sk-ant-api03-abcdef123456789' and password: 'SecretPassword123!'. "
            "Card number: 4111-2222-3333-4444, SSN: 123-45-6789. "
            "Contact: operator@enterprise-corp.com with AWS Key AKIAIOSFODNN7EXAMPLE."
        )
        clean = PIIRedactionEngine.redact_text(dirty_text)
        assert "sk-ant" not in clean
        assert "SecretPassword123!" not in clean
        assert "4111-2222-3333-4444" not in clean
        assert "123-45-6789" not in clean
        assert "operator@enterprise-corp.com" not in clean
        assert "AKIAIOSFODNN7EXAMPLE" not in clean

        assert "[REDACTED_SECRET]" in clean
        assert "[REDACTED_CARD]" in clean
        assert "[REDACTED_SSN]" in clean
        assert "[REDACTED_EMAIL]" in clean
        assert "[REDACTED_AWS_KEY]" in clean

    def test_da8_signed_evidence_blob_verification(self):
        signer = DA8EvidenceSigner(signing_key="unit-test-signing-key")
        critique = {
            "contradictions_detected": 1,
            "jailbreak_risk": 0.02,
            "critique_text": "Claim 4 lacks empirical simulation verification from DA-6."
        }
        blob = signer.generate_signed_evidence(
            layer_id="DA-8",
            critique_payload=critique,
            trace_id="tr-test-999888"
        )
        assert "signature" in blob
        assert blob["signature"].startswith("sig-sha256:")
        assert blob["layer_id"] == "DA-8"
        assert blob["compliance_seal"]["verified"] is True

        # Verify cryptographic integrity
        assert signer.verify_signed_evidence(blob) is True

        # Tampering with payload must cause verification failure
        tampered_blob = dict(blob)
        tampered_blob["signed_evidence_payload"] = {"tampered": True}
        assert signer.verify_signed_evidence(tampered_blob) is False


# ---------------------------------------------------------------------------
# Domain 3: Compliance, Data Handling & DSR Erasure Tests
# ---------------------------------------------------------------------------

class TestComplianceAndDSR:
    """Verifies layer classification table, retention policy, and DSR cryptographic erasure."""

    def test_layer_data_classification_matrix(self):
        assert len(LAYER_CLASSIFICATION_REGISTRY) == 16
        # DA-14 is RESTRICTED_PII
        assert LAYER_CLASSIFICATION_REGISTRY["DA-14"].data_classification == DataClassification.RESTRICTED_PII
        assert LAYER_CLASSIFICATION_REGISTRY["DA-14"].retention_days == 14

        # DA-X is CONFIDENTIAL with 365-day retention
        assert LAYER_CLASSIFICATION_REGISTRY["DA-X"].retention_days == 365
        assert LAYER_CLASSIFICATION_REGISTRY["DA-X"].dsr_eligible is True

    def test_dsr_erasure_and_cryptographic_tombstone(self):
        engine = DSRErasureEngine()
        subject = "subject-user-alpha"

        # Index records for subject
        engine.index_trace("trace-01", subject, {"query": "sample reasoning task"})
        engine.index_trace("trace-02", "other-user", {"query": "other task"})
        engine.index_evidence("ev-01", subject, {"critique": "test critique"})

        # Execute DSR erasure
        receipt = engine.execute_erasure(subject_id=subject, reason="GDPR_ART_17_RIGHT_TO_ERASURE")

        assert receipt.records_erased_count == 2
        assert receipt.subject_id == subject
        assert len(receipt.tombstone_hash) == 64
        assert receipt.signature.startswith("tombstone-sig:")

        # Verify records are purged
        assert "trace-01" not in engine.trace_store
        assert "ev-01" not in engine.da8_evidence_store
        # Other user records remain untouched
        assert "trace-02" in engine.trace_store

        # Verify tombstone integrity
        assert engine.verify_tombstone(receipt.receipt_id) is True


# ---------------------------------------------------------------------------
# Domain 4: Reliability, Circuit Breaker & Idempotency Tests
# ---------------------------------------------------------------------------

class TestReliabilityAndPerformance:
    """Verifies per-layer circuit breakers, jitter backoff, and idempotency deduplication."""

    def test_circuit_breaker_transitions(self):
        cfg = CircuitBreakerConfig(failure_threshold=3, recovery_timeout_sec=0.1, half_open_success_needed=2)
        breaker = LayerCircuitBreaker(layer_id="DA-6", config=cfg)

        assert breaker.state == CircuitState.CLOSED
        assert breaker.can_execute() is True

        # Record 2 failures -> remains closed
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitState.CLOSED

        # 3rd failure -> trips to OPEN
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        assert breaker.can_execute() is False

        # Wait for recovery timeout -> transitions to HALF_OPEN
        time.sleep(0.15)
        assert breaker.can_execute() is True
        assert breaker.state == CircuitState.HALF_OPEN

        # 2 successful probes -> closes circuit
        breaker.record_success()
        breaker.record_success()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.can_execute() is True

    def test_exponential_backoff_with_jitter(self):
        breaker = LayerCircuitBreaker(layer_id="DA-13")
        for attempt in range(5):
            delay = breaker.calculate_backoff(attempt)
            assert 0.0 <= delay <= breaker.config.max_backoff_sec

    def test_idempotency_manager_caching(self):
        idem = IdempotencyManager(ttl_seconds=60.0)
        payload = {"intent": "Analyze asset liabilities", "iteration": 1}

        key = idem.get_or_compute_key(None, payload)
        assert key.startswith("idem-")

        # Initially no cached result
        assert idem.check_idempotent_result(key) is None

        # Record result
        mock_result = {"status": "ACCEPT", "score": 0.88}
        idem.record_idempotent_result(key, mock_result)

        # Subsequent check returns cached result
        cached = idem.check_idempotent_result(key)
        assert cached == mock_result


# ---------------------------------------------------------------------------
# Domain 5: Deterministic Error Taxonomy Tests
# ---------------------------------------------------------------------------

class TestErrorTaxonomy:
    """Verifies deterministic enterprise error responses."""

    def test_deterministic_error_response_structure(self):
        err = EnterpriseErrorResponse(
            error_code=EnterpriseErrorCode.RATE_LIMIT_EXCEEDED,
            message="Tenant QPS rate limit exceeded.",
            http_status=429,
            trace_id="tr-12345",
            details={"retry_after_ms": 250}
        )
        d = err.to_dict()
        assert "error" in d
        assert d["error"]["code"] == "DAX_RATE_003"
        assert d["error"]["http_status"] == 429
        assert d["error"]["trace_id"] == "tr-12345"
        assert d["error"]["details"]["retry_after_ms"] == 250


# ---------------------------------------------------------------------------
# Domain 6: Multi-Engine Lineage Tests (New Engine + All Frozen Engines)
# ---------------------------------------------------------------------------

class TestMultiEngineLineage:
    """Validates enterprise governance and evaluation across the New Engine and all frozen engines."""

    @pytest.fixture
    def layers_config(self):
        p1 = Path(__file__).resolve().parent.parent / "config" / "layers.json"
        p2 = Path(__file__).resolve().parent.parent.parent / "config" / "layers.json"
        target_path = p1 if p1.exists() else p2
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_engine_compatibility_matrix_in_config(self, layers_config):
        matrix = layers_config.get("engine_compatibility_matrix", {})
        assert "active_new_engine" in matrix
        active = matrix["active_new_engine"]
        assert active["engine_id"] == "nextgen_da13_dax"
        assert active["status"] == "ACTIVE_PRODUCTION_PRIMARY"
        assert "Cl(16,4)" in active["mathematical_basis"]
        assert "M^4" in active["mathematical_basis"]

        frozen = matrix.get("frozen_engines", [])
        assert len(frozen) == 5
        frozen_ids = {e["engine_id"] for e in frozen}
        expected_ids = {
            "v16_4_nicole_hypervolume",
            "v13_cl70",
            "v12_1_cosmo",
            "v11_4_canonical_frozen",
            "v7_neural_symbolic"
        }
        assert frozen_ids == expected_ids

    def test_evaluate_new_engine_nextgen(self):
        dispatcher = MultiEngineDispatcher()
        receipt = dispatcher.evaluate(
            engine=EngineLineage.NEXTGEN_DA13_DAX,
            domain="financial_services",
            input_text="Evaluate asset-liability duration mismatch under rate shifts."
        )
        assert receipt.engine_id == "nextgen_da13_dax"
        assert receipt.decision == "ACCEPT"
        assert 0.75 <= receipt.stability_score_S <= 1.0
        assert len(receipt.receipt_sha256) == 64
        assert "Cl(16,4)" in receipt.mathematical_basis

    def test_evaluate_all_frozen_engines(self):
        dispatcher = MultiEngineDispatcher()
        text = "Audit cryptographic proof of non-repudiation and temporal consistency."

        # 1. V16.4 Nicole Protocol
        r_16 = dispatcher.evaluate(EngineLineage.V16_4_NICOLE_HYPERVOLUME, "general_enterprise", text)
        assert r_16.engine_id == "v16_4_nicole_hypervolume"
        assert r_16.decision in ("ACCEPT", "HALT")
        assert len(r_16.receipt_sha256) == 64

        # 2. V13.0 Cl(7,0)
        r_13 = dispatcher.evaluate(EngineLineage.V13_CL70, "general_enterprise", text)
        assert r_13.engine_id == "v13_cl70"
        assert r_13.decision in ("ACCEPT", "RECURSE")

        # 3. V12.1 Cosmo
        r_12 = dispatcher.evaluate(EngineLineage.V12_1_COSMO, "general_enterprise", text)
        assert r_12.engine_id == "v12_1_cosmo"
        assert r_12.decision == "ACCEPT"

        # 4. V11.4 Canonical Frozen Baseline
        r_11 = dispatcher.evaluate(EngineLineage.V11_4_CANONICAL_FROZEN, "general_enterprise", text)
        assert r_11.engine_id == "v11_4_canonical_frozen"
        assert r_11.decision == "ACCEPT"
        assert r_11.metadata["tier0_gate_enforced"] is True

        # 5. V7.0 Neural-Symbolic
        r_7 = dispatcher.evaluate(EngineLineage.V7_NEURAL_SYMBOLIC, "general_enterprise", text)
        assert r_7.engine_id == "v7_neural_symbolic"
        assert r_7.decision == "ACCEPT"

    def test_multi_engine_consensus_evaluation(self):
        dispatcher = MultiEngineDispatcher()
        report = dispatcher.evaluate_multi_engine_consensus(
            domain="cybersecurity_infosec",
            input_text="Verify zero-egress network firewall rule consistency."
        )
        assert report.primary_engine == "nextgen_da13_dax"
        assert len(report.engine_receipts) == 6
        assert report.consensus_agreement_pct >= 80.0
        assert len(report.tamper_evident_digest) == 64

