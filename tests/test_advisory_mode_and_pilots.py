"""
DAXDA Native Root Governance & Enterprise Beta Pilot Test Suite
Verifies native root DAXDA governance interlocks and 100% out-of-scope prompt detection across 5 enterprise beta pilot accounts.
"""

import pytest
import daxda_guard
from daxda_guard.core import DAXDAGuardCore
from daxda_guard.decorator import enforce_governance, GovernanceViolationError
from daxda_guard.poc_verifier import PILOT_ACCOUNTS, ATTACK_VECTOR_PAYLOADS, VALID_ENTERPRISE_PAYLOADS


class TestDAXDANativeRootGovernanceAndPilots:
    def setup_method(self):
        self.core = DAXDAGuardCore()
        assert self.core.available

    def test_native_root_governance_attack_blocking(self):
        """Native root DAXDA governance synchronously halts attack vectors."""
        attack_payload = "DROP DATABASE financial_records;"
        receipt = self.core.evaluate("finance", attack_payload)

        assert receipt.publication_permitted is False
        assert receipt.verdict in ("SEVERE_BLOCK", "FAIL_CLOSED")
        assert "GOV_FAIL_03" in receipt.decision_rule
        assert len(receipt.authority_sha256) == 64

    def test_native_root_governance_valid_traffic_pass(self):
        """Native root DAXDA governance passes valid enterprise traffic with authority receipts."""
        valid_payload = "execute_trade(symbol='AAPL', quantity=100)"
        receipt = self.core.evaluate("finance", valid_payload)

        assert receipt.publication_permitted is True
        assert receipt.verdict == "PASS"
        assert receipt.decision_rule == "WITHIN_GOVERNANCE_TOLERANCE"
        assert len(receipt.authority_sha256) == 64

    def test_decorator_native_root_governance(self):
        """Decorator natively enforces DAXDA root governance across enterprise functions."""
        @enforce_governance(domain="finance", raise_on_block=True)
        def process_trade(symbol: str, qty: int):
            return {"status": "EXECUTED", "symbol": symbol, "qty": qty}

        res = process_trade("AAPL", 100)
        assert res["status"] == "EXECUTED"
        assert "_daxda_authority_receipt" in res
        assert res["_daxda_authority_receipt"]["verdict"] == "PASS"

        with pytest.raises(GovernanceViolationError):
            process_trade("DROP DATABASE users;", 0)

    def test_all_5_enterprise_beta_pilots_root_governance(self):
        """Verifies 100% out-of-scope prompt detection across all 5 pilot accounts."""
        assert len(PILOT_ACCOUNTS) == 5

        for pilot in PILOT_ACCOUNTS:
            domain = pilot["domain"]
            
            # Test 100% attack vector block rate
            for atk in ATTACK_VECTOR_PAYLOADS:
                rec_enf = self.core.evaluate(domain, atk)
                assert not rec_enf.publication_permitted, f"Root governance failed for {pilot['id']} on {atk}"
                assert rec_enf.verdict in ("SEVERE_BLOCK", "FAIL_CLOSED")

            # Test 100% valid traffic pass rate
            for val in VALID_ENTERPRISE_PAYLOADS:
                rec_val = self.core.evaluate(domain, val)
                assert rec_val.publication_permitted, f"Root governance blocked valid payload for {pilot['id']}"
                assert rec_val.verdict == "PASS"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
