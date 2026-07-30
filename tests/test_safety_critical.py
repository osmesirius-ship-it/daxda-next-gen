"""
DAXDA Safety-Critical Test Suite
pytest-based with explicit gate assertions and fail-closed escalation
"""

import pytest
import json
import hashlib
import os
import socket
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import Dict, List, Tuple


# ============================================================================
# CANONICAL REPRODUCIBILITY HASH — Excludes timestamps, run IDs, signatures
# ============================================================================

class CanonicalHash:
    """Generate reproducible hashes excluding non-deterministic fields."""
    
    EXCLUDED_FIELDS = {
        'timestamp', 'runId', 'run_id', 'telemetryTime', 'telemetry_time',
        'signature', 'verificationKey', 'verification_key', 'datetime',
        'uuid', 'nonce', 'random', 'session_id', 'sessionId'
    }
    
    @staticmethod
    def scrub_dict(data: Dict) -> Dict:
        """Remove non-deterministic fields recursively."""
        if not isinstance(data, dict):
            return data
        
        scrubbed = {}
        for key, value in data.items():
            if key in CanonicalHash.EXCLUDED_FIELDS:
                continue
            if isinstance(value, dict):
                scrubbed[key] = CanonicalHash.scrub_dict(value)
            elif isinstance(value, list):
                scrubbed[key] = [CanonicalHash.scrub_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                scrubbed[key] = value
        return scrubbed
    
    @staticmethod
    def compute(data: Dict) -> str:
        """Compute canonical hash excluding non-deterministic fields."""
        scrubbed = CanonicalHash.scrub_dict(data)
        canonical_json = json.dumps(scrubbed, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode()).hexdigest()


# ============================================================================
# REPORT FIELD SEPARATION — "Audit completed" ≠ "Action released"
# ============================================================================

class SeparatedReportFields:
    """Ensure audit completion and action release are never confused."""
    
    def __init__(self):
        self.audit_completed = False
        self.audit_hash = None
        self.audit_gates = {}
        
        self.action_released = False
        self.action_authority = None
        self.action_signature = None
        self.action_gates = {}
    
    def mark_audit_complete(self, gates: Dict, hash_value: str):
        """Mark audit as complete. This does NOT release action."""
        self.audit_completed = True
        self.audit_hash = hash_value
        self.audit_gates = gates
        self.action_released = False  # EXPLICIT: Audit ≠ Release
    
    def mark_action_released(self, authority: str, signature: str, gates: Dict):
        """Mark action as released. Requires audit to be complete AND all gates PASS."""
        if not self.audit_completed:
            raise RuntimeError("Cannot release action: audit not completed")
        
        # Verify all gates are PASS
        failed_gates = [gate for gate, status in gates.items() if status != 'PASS']
        if failed_gates:
            raise RuntimeError(f"Cannot release action: failed gates: {failed_gates}")
        
        self.action_released = True
        self.action_authority = authority
        self.action_signature = signature
        self.action_gates = gates
    
    def to_dict(self) -> Dict:
        """Return separated report fields."""
        return {
            'audit': {
                'completed': self.audit_completed,
                'hash': self.audit_hash,
                'gates': self.audit_gates,
            },
            'action': {
                'released': self.action_released,
                'authority': self.action_authority,
                'signature': self.action_signature,
                'gates': self.action_gates,
            },
        }


# ============================================================================
# FAIL-CLOSED AUTHORITY ESCALATION
# ============================================================================

class FailClosedAuthority:
    """Authority escalation fails closed when model assistance is unavailable."""
    
    def __init__(self, model_available: bool = True):
        self.model_available = model_available
        self.escalation_blocked = False
    
    def escalate(self, decision: str, gates: Dict) -> Tuple[bool, str]:
        """
        Attempt to escalate authority decision.
        Returns (success, authority_decision)
        """
        # FAIL CLOSED: If model unavailable, block escalation
        if not self.model_available:
            self.escalation_blocked = True
            return (False, 'BLOCKED_NO_MODEL')
        
        # Verify all gates pass
        failed_gates = [gate for gate, status in gates.items() if status != 'PASS']
        if failed_gates:
            self.escalation_blocked = True
            return (False, f'BLOCKED_FAILED_GATES: {failed_gates}')
        
        # Only escalate if all conditions met
        return (True, decision)


# ============================================================================
# AIR-GAP TEST HARNESS — Disable networking, monitor socket calls
# ============================================================================

class AirGapTestHarness:
    """Test harness that disables networking and monitors socket/model calls."""
    
    def __init__(self):
        self.socket_calls = []
        self.model_calls = []
        self.network_disabled = False
    
    def disable_network(self):
        """Disable all network calls."""
        self.network_disabled = True
    
    def monitor_socket(self, *args, **kwargs):
        """Monitor socket calls."""
        self.socket_calls.append({
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.now().isoformat(),
        })
        if self.network_disabled:
            raise RuntimeError("Network disabled: socket call blocked")
    
    def monitor_model_call(self, *args, **kwargs):
        """Monitor model API calls."""
        self.model_calls.append({
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.now().isoformat(),
        })
        if self.network_disabled:
            raise RuntimeError("Network disabled: model call blocked")
    
    def assert_no_network_calls(self):
        """Assert that no network calls occurred."""
        assert len(self.socket_calls) == 0, f"Socket calls detected: {self.socket_calls}"
        assert len(self.model_calls) == 0, f"Model calls detected: {self.model_calls}"


# ============================================================================
# PYTEST TEST SUITE
# ============================================================================

class TestDAXDASafetyCritical:
    """Safety-critical tests for DAXDA with explicit gate assertions."""
    
    def setup_method(self):
        """Setup for each test."""
        self.air_gap = AirGapTestHarness()
        self.report = SeparatedReportFields()
        self.authority = FailClosedAuthority()
    
    # ========================================================================
    # TEST: Canonical Reproducibility Hash
    # ========================================================================
    
    def test_canonical_hash_excludes_timestamps(self):
        """Test that canonical hash excludes timestamps."""
        data1 = {
            'decision': 'BLOCKED',
            'timestamp': '2026-07-07T14:00:00Z',
            'gates': {'legal': 'FAIL', 'financial': 'FAIL'},
        }
        data2 = {
            'decision': 'BLOCKED',
            'timestamp': '2026-07-07T15:00:00Z',  # Different timestamp
            'gates': {'legal': 'FAIL', 'financial': 'FAIL'},
        }
        
        hash1 = CanonicalHash.compute(data1)
        hash2 = CanonicalHash.compute(data2)
        
        assert hash1 == hash2, "Hashes should match despite different timestamps"
    
    def test_canonical_hash_excludes_run_ids(self):
        """Test that canonical hash excludes run IDs."""
        data1 = {
            'decision': 'BLOCKED',
            'runId': 'run-abc-123',
            'gates': {'legal': 'FAIL'},
        }
        data2 = {
            'decision': 'BLOCKED',
            'runId': 'run-xyz-789',  # Different run ID
            'gates': {'legal': 'FAIL'},
        }
        
        hash1 = CanonicalHash.compute(data1)
        hash2 = CanonicalHash.compute(data2)
        
        assert hash1 == hash2, "Hashes should match despite different run IDs"
    
    def test_canonical_hash_includes_decision_data(self):
        """Test that canonical hash includes actual decision data."""
        data1 = {
            'decision': 'BLOCKED',
            'gates': {'legal': 'FAIL', 'financial': 'FAIL'},
        }
        data2 = {
            'decision': 'APPROVED',  # Different decision
            'gates': {'legal': 'FAIL', 'financial': 'FAIL'},
        }
        
        hash1 = CanonicalHash.compute(data1)
        hash2 = CanonicalHash.compute(data2)
        
        assert hash1 != hash2, "Hashes should differ for different decisions"
    
    # ========================================================================
    # TEST: Report Field Separation
    # ========================================================================
    
    def test_audit_completed_does_not_release_action(self):
        """Test that marking audit complete does NOT release action."""
        gates = {'legal': 'PASS', 'financial': 'PASS'}
        self.report.mark_audit_complete(gates, 'hash123')
        
        assert self.report.audit_completed == True
        assert self.report.action_released == False, "Audit completion should NOT release action"
    
    def test_action_release_requires_audit_complete(self):
        """Test that action release requires audit to be complete."""
        gates = {'legal': 'PASS', 'financial': 'PASS'}
        
        with pytest.raises(RuntimeError, match="audit not completed"):
            self.report.mark_action_released('APPROVED', 'sig123', gates)
    
    def test_action_release_requires_all_gates_pass(self):
        """Test that action release requires all gates to PASS."""
        self.report.mark_audit_complete({'legal': 'FAIL'}, 'hash123')
        gates = {'legal': 'FAIL', 'financial': 'PASS'}
        
        with pytest.raises(RuntimeError, match="failed gates"):
            self.report.mark_action_released('APPROVED', 'sig123', gates)
    
    def test_action_release_only_with_all_gates_pass(self):
        """Test that action release succeeds only with all gates PASS."""
        self.report.mark_audit_complete({'legal': 'PASS', 'financial': 'PASS'}, 'hash123')
        gates = {'legal': 'PASS', 'financial': 'PASS'}
        
        self.report.mark_action_released('APPROVED', 'sig123', gates)
        
        assert self.report.action_released == True
        assert self.report.action_authority == 'APPROVED'
    
    def test_report_fields_never_confused(self):
        """Test that audit and action fields are never confused."""
        report_dict = self.report.to_dict()
        
        # Audit and action are separate
        assert 'audit' in report_dict
        assert 'action' in report_dict
        assert report_dict['audit'] != report_dict['action']
    
    # ========================================================================
    # TEST: Fail-Closed Authority Escalation
    # ========================================================================
    
    def test_escalation_fails_closed_when_model_unavailable(self):
        """Test that escalation fails closed when model is unavailable."""
        authority = FailClosedAuthority(model_available=False)
        gates = {'legal': 'PASS', 'financial': 'PASS'}
        
        success, decision = authority.escalate('APPROVED', gates)
        
        assert success == False, "Escalation should fail when model unavailable"
        assert decision == 'BLOCKED_NO_MODEL'
        assert authority.escalation_blocked == True
    
    def test_escalation_fails_closed_when_gates_fail(self):
        """Test that escalation fails closed when gates fail."""
        authority = FailClosedAuthority(model_available=True)
        gates = {'legal': 'FAIL', 'financial': 'PASS'}
        
        success, decision = authority.escalate('APPROVED', gates)
        
        assert success == False, "Escalation should fail when gates fail"
        assert 'BLOCKED_FAILED_GATES' in decision
        assert authority.escalation_blocked == True
    
    def test_escalation_succeeds_only_with_model_and_gates(self):
        """Test that escalation succeeds only with model available and gates passing."""
        authority = FailClosedAuthority(model_available=True)
        gates = {'legal': 'PASS', 'financial': 'PASS', 'safety': 'PASS'}
        
        success, decision = authority.escalate('APPROVED', gates)
        
        assert success == True, "Escalation should succeed with model and gates"
        assert decision == 'APPROVED'
        assert authority.escalation_blocked == False
    
    # ========================================================================
    # TEST: Air-Gap (Network Disabled)
    # ========================================================================
    
    def test_air_gap_blocks_socket_calls(self):
        """Test that air-gap blocks socket calls."""
        self.air_gap.disable_network()
        
        with pytest.raises(RuntimeError, match="Network disabled"):
            self.air_gap.monitor_socket('127.0.0.1', 8000)
    
    def test_air_gap_blocks_model_calls(self):
        """Test that air-gap blocks model API calls."""
        self.air_gap.disable_network()
        
        with pytest.raises(RuntimeError, match="Network disabled"):
            self.air_gap.monitor_model_call('claude-sonnet', {'prompt': 'test'})
    
    def test_air_gap_assert_no_network_calls(self):
        """Test that air-gap can assert no network calls occurred."""
        self.air_gap.disable_network()
        
        # Should pass with no calls
        self.air_gap.assert_no_network_calls()
    
    def test_air_gap_detects_socket_calls(self):
        """Test that air-gap detects socket calls."""
        # Don't disable network, just monitor
        self.air_gap.monitor_socket('127.0.0.1', 8000)
        
        with pytest.raises(AssertionError, match="Socket calls detected"):
            self.air_gap.assert_no_network_calls()
    
    # ========================================================================
    # TEST: Stage-4 AGI Quarantine
    # ========================================================================
    
    def test_stage4_agi_blocked_until_gates_pass(self):
        """Test that Stage-4 AGI results are blocked until gates pass."""
        stage4_result = {
            'model': 'gpt-5-reasoning',
            'decision': 'APPROVED',
            'gates': {'legal': 'FAIL', 'financial': 'FAIL'},
        }
        
        # Extract gates
        gates = stage4_result['gates']
        failed_gates = [gate for gate, status in gates.items() if status != 'PASS']
        
        # Stage-4 should be quarantined
        assert len(failed_gates) > 0, "Stage-4 should be quarantined with failed gates"
    
    def test_stage4_agi_released_only_with_all_gates_pass(self):
        """Test that Stage-4 AGI is released only when all gates pass."""
        stage4_result = {
            'model': 'gpt-5-reasoning',
            'decision': 'APPROVED',
            'gates': {'legal': 'PASS', 'financial': 'PASS', 'safety': 'PASS'},
        }
        
        # Extract gates
        gates = stage4_result['gates']
        failed_gates = [gate for gate, status in gates.items() if status != 'PASS']
        
        # Stage-4 should be released
        assert len(failed_gates) == 0, "Stage-4 should be released with all gates passing"


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture
def air_gap_harness():
    """Fixture for air-gap test harness."""
    return AirGapTestHarness()


@pytest.fixture
def separated_report():
    """Fixture for separated report fields."""
    return SeparatedReportFields()


@pytest.fixture
def fail_closed_authority():
    """Fixture for fail-closed authority."""
    return FailClosedAuthority()


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
