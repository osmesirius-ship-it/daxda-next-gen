"""
DAXDA Guard Self-Service Risk Audit Generator Automated Test Suite
Verifies 1,000+ word report generation in < 5.0 seconds SLA with SHA-256 compliance receipts.
"""

import os
import pytest
from daxda_guard.audit_generator import RiskAuditReportGenerator


class TestSelfServiceRiskAuditGenerator:
    def setup_method(self):
        self.generator = RiskAuditReportGenerator()
        self.output_dir = "test_audit_reports"

    def test_audit_generator_word_count_and_sla(self):
        res = self.generator.generate_report(
            company_name="JPMorgan Chase Test",
            num_scans=60,
            output_dir=self.output_dir
        )

        assert res["sla_passed"]
        assert res["word_count"] >= 1000, f"Report word count was {res['word_count']} (expected >= 1000)"
        assert res["elapsed_sec"] < 5.0, f"Report generation took {res['elapsed_sec']:.3f} s (expected < 5.0 s)"

        assert os.path.exists(res["markdown_path"])
        assert os.path.exists(res["html_path"])

    def test_audit_report_contains_sha256_receipts_and_regulatory_signoffs(self):
        res = self.generator.generate_report(
            company_name="Lockheed Martin Avionics",
            num_scans=30,
            output_dir=self.output_dir
        )

        with open(res["markdown_path"], "r", encoding="utf-8") as f:
            md_text = f.read()

        assert "Federal Reserve SR 11-7" in md_text
        assert "ITAR / FedRAMP High Air-Gap" in md_text
        assert "European Union (EU) AI Act Article 14" in md_text
        assert "GOV_FAIL_01" in md_text
        assert "GOV_FAIL_04" in md_text
        assert "SHA-256" in md_text
        assert len(md_text.split()) >= 1000

    def test_html_report_rendering(self):
        res = self.generator.generate_report(
            company_name="Goldman Sachs Trading",
            num_scans=20,
            output_dir=self.output_dir
        )

        with open(res["html_path"], "r", encoding="utf-8") as f:
            html_text = f.read()

        assert "<!DOCTYPE html>" in html_text
        assert "Goldman Sachs Trading" in html_text
        assert "badge pass" in html_text
        assert "badge block" in html_text
        assert "DAXDA GUARD v1.0.0 EXECUTIVE AUDIT SEAL" in html_text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
