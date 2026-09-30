"""
Unit Tests for DAXDA EU AI Act Regulatory Evidence Profile & Evidence Package Builder (v1.1 / v1.2)
===================================================================================================
Verifies:
1. v1.1 Frozen Baseline Profile:
   - System Role terminology (PEP & Decision-Audit Infrastructure)
   - Classification Status NOT_YET_DETERMINED across all configurations
   - Legal determination authority boundary (PROVIDER / DEPLOYER / COUNSEL, DAXDA authority NONE)
   - Article 6 classification-support with profiling override gate
   - Article 5 prohibited practices: status NOT_ASSESSED, article_5_conformance None
   - Conformity assessment: status DETERMINATION_REQUIRED, candidate pathways, daxda_role EVIDENCE_SUPPORT
   - Article 49 / Article 71 registration and database separation with review triggers
   - Architectural taxonomy constraint (DAXDA shall never self-assign E5 or E6)
   - Mathematical configuration registry with decision_authority and self-modification boundary (False)
   - Article 13: daxda_decision_explanation vs upstream_model_explanation (OUT_OF_SCOPE)
   - Article 15: test_population (generalization False, separated empirical counts) & benchmark_provenance
   - Article 16, 17, 26, 43, 49/71, 72, 73 controls and actor separations
2. v1.2 Machine-Auditable Evidence Schema:
   - All 15 required fields present on every control record
   - Conformance with DAXDA_EU_AI_ACT_EVIDENCE_SCHEMA_v1.2.json
"""

import json
import pathlib
import pytest
from daxda_guard.canonical_clifford_trace import run_canonical_trace, CANONICAL_CASES
from daxda_guard.enterprise_adapter import DAXDAEnterpriseAdapter
from daxda_guard.eu_compliance_profile import (
    EUAIActComplianceProfileBuilder,
    HUMAN_OVERSIGHT_VERIFICATION_MATRIX,
    MATHEMATICAL_CONFIGURATION_REGISTRY,
    LEGAL_DETERMINATION_BOUNDARY,
    EVIDENCE_TAXONOMY,
    EVIDENCE_TAXONOMY_ARCHITECTURAL_CONSTRAINT
)

def test_eu_ai_act_compliance_profile_v11_freeze():
    """Verify v1.1 frozen baseline amendments and regulatory refinements across canonical fixtures."""
    for case in CANONICAL_CASES:
        trace = run_canonical_trace(
            case_id=case["case_id"],
            input_text=case["input_text"],
            M0_blades=case["M0_blades"],
            theta=case["theta"],
            rotor_plane=case["rotor_plane"],
            expected_disposition=case["expected_disposition"]
        )
        receipt = DAXDAEnterpriseAdapter.emit_receipt(trace)

        # 1. Build profile without Annex III categorization
        profile_std = EUAIActComplianceProfileBuilder.build_profile(trace, receipt)

        # Commercial & boundary statement checks
        assert "DAXDA converts runtime AI governance events into independently verifiable technical evidence" in profile_std["commercial_statement"]
        assert "DAXDA does not claim to be 'EU AI Act compliant'" in profile_std["legal_boundary_notice"]
        assert "does not make compliance automatic" in profile_std["legal_boundary_notice"]
        assert "does not certify AI systems" in profile_std["legal_boundary_notice"]

        # System Role terminology
        assert "System Role" not in profile_std["system_identification"] # key is system_role
        assert profile_std["system_identification"]["system_role"] == "AI Governance / Policy Enforcement Point / Decision-Audit Infrastructure"

        # Classification check: should strictly be ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED
        assert profile_std["regulatory_snapshot"]["classification_status"] == "ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED"
        assert profile_std["article_6_classification_support"]["classification_status"] == "ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED"
        assert profile_std["article_6_classification_support"]["classification_review"] == "ARTICLE_6_ASSESSMENT_REQUIRED"
        assert profile_std["article_6_classification_support"]["daxda_role"] == "CLASSIFICATION_SUPPORT_ONLY"
        assert profile_std["article_6_classification_support"]["article_6_3_profiling_override"] == "IF profiling_of_natural_persons == TRUE -> HIGH_RISK_REQUIRES_LEGAL_DOCUMENTATION"

        # Legal Determination Boundary
        legal_b = profile_std["legal_determination_boundary"]
        assert legal_b["legal_determination_authority"] == "PROVIDER / DEPLOYER / RELEVANT LEGAL ACTOR"
        assert legal_b["daxda_legal_role"] == "TECHNICAL_EVIDENCE_GENERATOR"
        assert legal_b["daxda_regulatory_decision_authority"] == "NONE"

        # Article 5 Prohibited Practices check: NOT_ASSESSED, not fake PASS
        art5 = profile_std["prohibited_practices_check"]
        assert art5["status"] == "NOT_ASSESSED"
        assert art5["article_5_conformance"] is None
        assert "REQUIRES_DEFINED_RULESET" in art5["assessment_method"]

        # Conformity assessment check: DETERMINATION_REQUIRED under Article 43
        ca = profile_std["conformity_assessment"]
        assert ca["status"] == "DETERMINATION_REQUIRED"
        assert ca["conformity_assessment_support"] == "TECHNICAL_EVIDENCE_AVAILABLE"
        assert ca["conformity_pathway"] == "DEPLOYMENT_AND_CLASSIFICATION_DEPENDENT"
        assert ca["applicable_article"] == "Article 43"
        assert ca["daxda_role"] == "EVIDENCE_SUPPORT"
        assert "does not determine" in ca["legal_boundary"]

        # Article 49 / 71 Registration & EU Database check
        reg = profile_std["registration_and_eu_database"]
        assert reg["registration_status"] == "NOT_DETERMINED"
        assert reg["registration_trigger"] == "ARTICLE_49_APPLICABILITY_REVIEW_REQUIRED"
        assert reg["eu_database"] == "ARTICLE_71_DATABASE_SCOPE"
        assert reg["registration_decision"] == "PROVIDER / AUTHORIZED_ACTOR RESPONSIBILITY"
        assert reg["daxda_role"] == "REGISTRATION_METADATA_SUPPORT"
        assert "Article 6 classification changes" in reg["review_trigger"]

        # Mathematical Configuration Registry: check Cl(4,1) vs Cl(16,4) and decision_authority
        math_reg = profile_std["mathematical_configuration"]
        assert math_reg["production_runtime"]["algebra"] == "Cl(4,1)"
        assert math_reg["production_runtime"]["basis_blades"] == 32
        assert math_reg["research_configuration"]["algebra"] == "Cl(16,4)"
        assert math_reg["research_configuration"]["blade_dimensions"] == 1048576
        assert math_reg["research_configuration"]["four_dimensional_combinations"] == 1820
        assert math_reg["equivalence_disclaimer"] == "No equivalence is implied between configurations."
        assert math_reg["decision_authority"]["production_gate"] == "Cl(4,1)"
        assert math_reg["decision_authority"]["research_configuration"] == "NON_AUTHORITATIVE"
        assert math_reg["decision_authority"]["research_can_modify_production_policy"] is False

        # 2. Build profile with high-risk Annex III categorization (e.g. Employment)
        profile_hr = EUAIActComplianceProfileBuilder.build_profile(
            trace, receipt, annex_iii_category="EMPLOYMENT_WORKER_MANAGEMENT"
        )
        # Classification remains ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED, with path flagged for assessment
        assert profile_hr["article_6_classification_support"]["classification_status"] == "ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED"
        assert profile_hr["article_6_classification_support"]["annex_iii_path"] == "REQUIRES_ASSESSMENT_FOR_EMPLOYMENT_WORKER_MANAGEMENT"
        assert profile_hr["article_6_classification_support"]["legal_determination"] == "PROVIDER / DEPLOYER / RELEVANT LEGAL ACTOR"

        # Check required article evidence fields
        evidence = profile_hr["article_controls_evidence"]
        assert evidence["article_9_risk_management"]["status_level"] == "E3 — INTERNALLY VERIFIED"

        # Article 10 tightened language
        expected_art10_phrase = (
            "DAXDA can record and evidence designated data-governance metadata; "
            "responsibility for applicable training, validation, and testing-data governance "
            "remains with the legally responsible actor under the relevant EU AI Act provisions and contractual allocation."
        )
        assert evidence["article_10_data_governance"]["boundary_note"] == expected_art10_phrase
        assert evidence["article_10_data_governance"]["status_level"] == "E2 — IMPLEMENTED"

        # Article 13: DAXDA decision explanation vs upstream model explanation
        art13 = evidence["article_13_transparency"]
        assert "daxda_decision_explanation" in art13
        assert "Dominant DAXDA channel" in art13["daxda_decision_explanation"]
        assert art13["upstream_model_explanation"]["status"] == "OUT_OF_SCOPE"

        # Article 14 9-dimension Human Oversight Matrix
        art14 = evidence["article_14_human_oversight"]
        matrix = art14["human_oversight_matrix"]
        assert len(matrix) == 9
        status_lookup = {item["dimension"]: item["verification_status"] for item in matrix}
        assert status_lookup["Limitation Awareness"] == "Machine-supported; human effectiveness unverified"
        assert status_lookup["Anomaly Detection"] == "Machine-supported; operator verification required"
        assert status_lookup["Output Interpretation"] == "Machine-supported; operator verification required"
        assert status_lookup["Pre-Action Intervention"] == "Machine-verified"
        assert status_lookup["Runtime Override"] == "Machine-verified; authorization workflow required"
        assert status_lookup["Immediate Interruption"] == "Machine-verified"
        assert status_lookup["Continued-Use Prevention"] == "Machine-verified"
        assert status_lookup["State Rollback"] == "Machine-verified"
        assert status_lookup["Consequence Awareness"] == "Customer workflow / human verification required"

        # Article 15: test_population and benchmark_provenance
        art15 = evidence["article_15_accuracy_cybersecurity"]
        tpop = art15["test_population"]
        assert tpop["population_type"] == "DEFINED_FIXTURE_CORPUS"
        assert tpop["population_size"] == 100
        assert tpop["generalization"] is False
        assert tpop["observed_false_releases"] == 0
        assert tpop["observed_false_blocks"] == 0
        assert tpop["population_error_rate_estimate"] == "NOT_COMPUTED"
        assert "Observed test result: 0 false releases in the defined test corpus (0/100)" in art15["boundary_note"]
        assert art15["benchmark_provenance"]["benchmark_method"] == "NUMPY_LINEAR_PERCENTILE"

        # Extended Articles: 16, 17, 26, 43, 49/71, 72, 73
        assert "article_16_provider_obligations" in evidence
        assert "article_17_quality_management" in evidence
        assert "daxda_technical_supplier" in evidence["article_17_quality_management"]["actors"]
        assert "article_26_deployer_obligations" in evidence
        assert "article_43_conformity_assessment" in evidence
        assert "article_49_71_registration_and_database" in evidence
        assert "article_72_post_market_monitoring" in evidence
        assert "article_73_serious_incident_reporting" in evidence

    print("\n[EU AI Act Profile Test v1.1] All legal and engineering freeze amendments verified.")


def test_eu_ai_act_evidence_package_v12_schema():
    """Verify v1.2 evidence package builder against all 15 required control fields, schema, and extended articles."""
    schema_path = pathlib.Path(__file__).parent.parent / "daxda_guard" / "schemas" / "DAXDA_EU_AI_ACT_EVIDENCE_SCHEMA_v1.2.json"
    assert schema_path.exists(), f"Schema file not found at {schema_path}"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Required fields for control record
    required_control_fields = schema["$defs"]["control_evidence_record"]["required"]
    assert len(required_control_fields) == 15
    expected_15_fields = [
        "article",
        "requirement",
        "actor",
        "daxda_control",
        "evidence_id",
        "evidence_hash",
        "test_corpus",
        "software_version",
        "environment",
        "status_level",
        "scope",
        "limitations",
        "independent_verification",
        "customer_responsibility",
        "regulatory_review_required"
    ]
    for field in expected_15_fields:
        assert field in required_control_fields

    # Generate evidence package for canonical case
    case = CANONICAL_CASES[0]
    trace = run_canonical_trace(
        case_id=case["case_id"],
        input_text=case["input_text"],
        M0_blades=case["M0_blades"],
        theta=case["theta"],
        rotor_plane=case["rotor_plane"],
        expected_disposition=case["expected_disposition"]
    )
    receipt = DAXDAEnterpriseAdapter.emit_receipt(trace)

    pkg = EUAIActComplianceProfileBuilder.build_v12_evidence_package(trace, receipt)

    # Validate package top-level structure
    assert pkg["schema_version"] == "1.2.0"
    assert pkg["system_identification"]["system_role"] == "AI Governance / Policy Enforcement Point / Decision-Audit Infrastructure"
    assert pkg["legal_determination_boundary"]["daxda_regulatory_decision_authority"] == "NONE"

    # Verify DAXDA_REGULATORY_EVIDENCE_MANIFEST
    manifest = pkg["regulatory_evidence_manifest"]
    assert manifest["profile_version"] == "v1.1"
    assert manifest["assessment_date"] == "2026-09-28"
    assert manifest["regulatory_source"] == "Regulation (EU) 2024/1689"
    assert "Consolidated text 2026-07-27" in manifest["regulatory_source_version"]
    assert manifest["classification_status"] == "ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED"
    assert manifest["production_engine"] == "Cl(4,1) 32 basis blades"
    assert manifest["research_engine"] == "Cl(16,4) NON-AUTHORITATIVE OFFLINE ONLY"
    assert manifest["authority_boundary"] == "RESEARCH_TO_PRODUCTION_SELF_MODIFICATION_PROHIBITED"
    assert manifest["legal_determination_authority"] == "PROVIDER / DEPLOYER / RELEVANT LEGAL ACTOR"
    assert manifest["daxda_regulatory_decision_authority"] == "NONE"
    assert len(manifest["evidence_items"]) == len(pkg["controls"])

    math_cfg = pkg["mathematical_configuration"]
    assert math_cfg["production_runtime"]["algebra"] == "Cl(4,1)"
    assert math_cfg["production_runtime"]["basis_blades"] == 32
    assert math_cfg["research_configuration"]["algebra"] == "Cl(16,4)"
    assert math_cfg["decision_authority"]["production_gate"] == "Cl(4,1)"
    assert math_cfg["decision_authority"]["research_can_modify_production_policy"] is False

    # Check architectural taxonomy constraint in evidence taxonomy
    tax_rule = pkg["evidence_taxonomy"]["architectural_constraint"]
    assert "DAXDA SHALL NEVER SELF-ASSIGN E5 OR E6" in tax_rule
    assert tax_rule == EVIDENCE_TAXONOMY_ARCHITECTURAL_CONSTRAINT

    # Validate extended controls (including Articles 9, 10, 11, 12, 13, 14, 15, 16, 17, 26, 43, 49/71, 72, 73)
    assert len(pkg["controls"]) >= 14

    articles_present = [ctrl["article"] for ctrl in pkg["controls"]]
    expected_articles = [
        "Article 9", "Article 10", "Article 11", "Article 12", "Article 13",
        "Article 14", "Article 15", "Article 16", "Article 17", "Article 26",
        "Article 43", "Article 49 / Article 71", "Article 72", "Article 73"
    ]
    for art in expected_articles:
        assert art in articles_present, f"Missing control for {art}"

    for ctrl in pkg["controls"]:
        for field in expected_15_fields:
            assert field in ctrl, f"Missing required field {field} in control {ctrl.get('article')}"
        assert len(ctrl["evidence_hash"]) == 64
        assert isinstance(ctrl["regulatory_review_required"], bool)
        assert isinstance(ctrl["environment"], dict)
        assert ctrl["environment"]["runtime_algebra"] == "Cl(4,1) (32 basis blades)"
        # Architectural constraint check: DAXDA shall never self-assign E5 or E6
        assert not ctrl["status_level"].startswith("E5")
        assert not ctrl["status_level"].startswith("E6")

    # Verify Article 17 actor separation in package
    art17_ctrl = next(c for c in pkg["controls"] if c["article"] == "Article 17")
    assert isinstance(art17_ctrl["actor"], list)
    assert "DAXDA_TECHNICAL_SUPPLIER" in art17_ctrl["actor"]
    assert "PROVIDER" in art17_ctrl["actor"]

    # Verify Article 16 actor separation in package
    art16_ctrl = next(c for c in pkg["controls"] if c["article"] == "Article 16")
    assert "DAXDA_TECHNICAL_SUPPLIER" in art16_ctrl["actor"]

    # Verify Article 49 / 71 registration in package
    art49_71_ctrl = next(c for c in pkg["controls"] if c["article"] == "Article 49 / Article 71")
    assert art49_71_ctrl["status_level"] == "E1 — SPECIFIED"

    print("\n[EU AI Act Evidence Package v1.2] All 15 required control fields, extended articles, and schema rules verified.")
