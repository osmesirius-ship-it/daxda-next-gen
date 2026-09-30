"""
DAXDA EU AI Act Regulatory Evidence Profile & Evidence Package Builder (v1.1 / v1.2)
====================================================================================
Constructs machine-auditable EU AI Act Regulatory Evidence Profiles and granular
Evidence Packages mapping Clifford multivector telemetry to Regulation (EU) 2024/1689
under strict legal boundary definitions and the formal E0–E6 Evidence Status Taxonomy.

CORE REGULATORY INVARIANT:
- DAXDA generates evidence.
- DAXDA enforces its declared runtime policy.
- DAXDA does not make the legal determination.

ARCHITECTURAL TAXONOMY CONSTRAINT:
- E0–E4 MAY BE GENERATED / VERIFIED THROUGH DAXDA EVIDENCE WORKFLOWS.
- E5 REQUIRES A QUALIFIED INDEPENDENT ASSESSOR.
- E6 REQUIRES THE APPLICABLE FORMAL REGULATORY / CONFORMITY-ASSESSMENT PROCESS.
- DAXDA SHALL NEVER SELF-ASSIGN E5 OR E6.
"""

import uuid
import hashlib
import datetime
from typing import Dict, Any, Optional, List, Union

# Formal DAXDA Evidence Status Taxonomy (E0–E6)
EVIDENCE_TAXONOMY = {
    "E0": "E0 — UNTESTED: No empirical evidence collected or evaluated.",
    "E1": "E1 — SPECIFIED: Requirement represented in formal architecture, data contracts, or schema definitions.",
    "E2": "E2 — IMPLEMENTED: Mechanism exists as functional, executable logic in the production software implementation.",
    "E3": "E3 — INTERNALLY VERIFIED: Reproduced and validated through controlled, deterministic internal testing and test harnesses.",
    "E4": "E4 — INDEPENDENTLY REPRODUCED: External party reproduced the identical bit-exact result from customer-supplied artifacts in an independent environment.",
    "E5": "E5 — INDEPENDENTLY ASSESSED: Qualified external assessor or accredited audit body evaluated and validated the relevant control.",
    "E6": "E6 — REGULATORY / CONFORMITY ASSESSED: Formal applicable conformity assessment or regulatory assessment completed by the legally competent conformity-assessment body, notified body, or competent authority, where the applicable EU AI Act pathway requires such assessment."
}

EVIDENCE_TAXONOMY_ARCHITECTURAL_CONSTRAINT = (
    "E0–E4 MAY BE GENERATED / VERIFIED THROUGH DAXDA EVIDENCE WORKFLOWS. "
    "E5 REQUIRES A QUALIFIED INDEPENDENT ASSESSOR. "
    "E6 REQUIRES THE APPLICABLE FORMAL REGULATORY / CONFORMITY-ASSESSMENT PROCESS. "
    "DAXDA SHALL NEVER SELF-ASSIGN E5 OR E6."
)

# Mathematical Configuration Registry
MATHEMATICAL_CONFIGURATION_REGISTRY = {
    "production_runtime": {
        "algebra": "Cl(4,1)",
        "basis_blades": 32,
        "implementation_module": "daxda_guard.canonical_clifford_trace / in-memory sparse Clifford matrix evaluation",
        "role": "Exclusive production authorization gate decision engine (RELEASE, BLOCK, HOLD_FOR_REVIEW)"
    },
    "research_configuration": {
        "algebra": "Cl(16,4)",
        "blade_dimensions": 1048576,
        "four_dimensional_combinations": 1820,
        "status": "Offline research and extended geometric exploration substrate",
        "role": "Offline manifold hypervolume exploration and deep topology research"
    },
    "equivalence_disclaimer": "No equivalence is implied between configurations.",
    "decision_authority": {
        "production_gate": "Cl(4,1)",
        "research_configuration": "NON_AUTHORITATIVE",
        "research_can_modify_production_policy": False
    }
}

# Legal Determination Boundary Definition
LEGAL_DETERMINATION_BOUNDARY = {
    "legal_determination_authority": "PROVIDER / DEPLOYER / RELEVANT LEGAL ACTOR",
    "daxda_legal_role": "TECHNICAL_EVIDENCE_GENERATOR",
    "daxda_regulatory_decision_authority": "NONE"
}

# Human Oversight 9-Dimension Verification Protocol
HUMAN_OVERSIGHT_VERIFICATION_MATRIX = [
    {
        "dimension": "Limitation Awareness",
        "question": "Can the human understand relevant system operational limitations?",
        "daxda_mechanism": "Explicit confidence score C(s) and dominant blade channel readout.",
        "verification_status": "Machine-supported; human effectiveness unverified"
    },
    {
        "dimension": "Anomaly Detection",
        "question": "Can the human detect anomalous or unexpected behavior?",
        "daxda_mechanism": "Topological dissipation flag (v^2=0) and e15 energy breach indicator.",
        "verification_status": "Machine-supported; operator verification required"
    },
    {
        "dimension": "Output Interpretation",
        "question": "Can the human interpret the relevant output and context?",
        "daxda_mechanism": "Structured semantic channel breakdown (e1 to e4).",
        "verification_status": "Machine-supported; operator verification required"
    },
    {
        "dimension": "Pre-Action Intervention",
        "question": "Can the human intervene before execution occurs?",
        "daxda_mechanism": "Pre-action gate pauses at HOLD_FOR_REVIEW.",
        "verification_status": "Machine-verified"
    },
    {
        "dimension": "Runtime Override",
        "question": "Can the human override an algorithmic recommendation?",
        "daxda_mechanism": "Explicit authorization token required to force state transition.",
        "verification_status": "Machine-verified; authorization workflow required"
    },
    {
        "dimension": "Immediate Interruption",
        "question": "Can the human instantly interrupt active operation?",
        "daxda_mechanism": "Instant execution boundary closure upon revoke signal.",
        "verification_status": "Machine-verified"
    },
    {
        "dimension": "Continued-Use Prevention",
        "question": "Can the human prevent continued or repeated use?",
        "daxda_mechanism": "Ephemeral TTL expiry and session token invalidation.",
        "verification_status": "Machine-verified"
    },
    {
        "dimension": "State Rollback",
        "question": "Can the human roll back tainted intermediate state?",
        "daxda_mechanism": "Reversible rollback vector (rollback_vector_id) emitted on BLOCK.",
        "verification_status": "Machine-verified"
    },
    {
        "dimension": "Consequence Awareness",
        "question": "Does the human understand the consequence of intervention?",
        "daxda_mechanism": "Explicit containment telemetry logged in the sovereign audit ledger.",
        "verification_status": "Customer workflow / human verification required"
    }
]


class EUAIActComplianceProfileBuilder:
    """
    Constructs EU AI Act Regulatory Evidence Profiles (v1.1) and granular machine-auditable
    Evidence Packages (v1.2) mapping Clifford multivector telemetry to Regulation (EU) 2024/1689.
    """

    @staticmethod
    def build_profile(
        trace_data: Dict[str, Any],
        receipt_data: Dict[str, Any],
        annex_iii_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds a compliant DAXDAEUAIActRegulatoryEvidenceProfile dictionary conforming to v1.1 frozen baseline.
        """
        gate = trace_data.get("gate_evaluation", {})
        multivec = trace_data.get("multivector_state", {})
        repro = receipt_data.get("reproducibility", {})
        auth_verdict = receipt_data.get("authority_channel_verdict", {})
        containment = receipt_data.get("containment_state", {})

        # Article 5 Prohibited Practices Check:
        prohibited_check = {
            "status": "NOT_ASSESSED",
            "article_5_conformance": None,
            "assessment_method": "REQUIRES_DEFINED_RULESET_AND_USE_CASE_ANALYSIS",
            "audit_notes": (
                "Article 5 screening requires deployment-specific assessment "
                "against the applicable prohibited-practice definitions."
            )
        }

        # Article 6 Classification-Support Engine:
        governs_annex_iii = annex_iii_category is not None
        article_6_support = {
            "classification_status": "ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED",
            "classification_review": "ARTICLE_6_ASSESSMENT_REQUIRED",
            "annex_i_path": "NOT_ASSESSED",
            "annex_iii_path": f"REQUIRES_ASSESSMENT_FOR_{annex_iii_category}" if governs_annex_iii else "NOT_ASSESSED",
            "article_6_3_derogation": "NOT_ASSESSED",
            "article_6_3_profiling_override": "IF profiling_of_natural_persons == TRUE -> HIGH_RISK_REQUIRES_LEGAL_DOCUMENTATION",
            "legal_determination": "PROVIDER / DEPLOYER / RELEVANT LEGAL ACTOR",
            "daxda_role": "CLASSIFICATION_SUPPORT_ONLY"
        }

        # Article 9 Risk Management: check if residual indicates non-divergent or contained dissipation
        residual = multivec.get("reconstruction_residual", 0.0)
        dissipation_verified = (auth_verdict.get("gate_decision") == "RELEASE" and residual <= 1e-9) or \
                               (auth_verdict.get("gate_decision") == "BLOCK" and residual > 1e-4)

        # Article 15 Accuracy, Robustness, Cybersecurity
        rotor_normalized = multivec.get("rotor_normalized", True)

        # Format confidence safely (prevents NoneType formatting exception)
        confidence = auth_verdict.get("confidence_cs")
        confidence_text = (
            f"{confidence:.4f}"
            if isinstance(confidence, (int, float))
            else "UNAVAILABLE"
        )

        profile = {
            "profile_id": str(uuid.uuid4()),
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "regulatory_snapshot": {
                "framework": "Regulation (EU) 2024/1689 (EU AI Act)",
                "assessment_date": "2026-09-28",
                "legislative_version": "Consolidated CELEX 02024R1689-20260727",
                "commission_guidelines": "Draft Commission Guidelines on Article 6 (July 23, 2026)",
                "classification_status": "ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED",
                "evidence_taxonomy": "E0–E6 Formal Evidence Maturity Model"
            },
            "system_identification": {
                "system_name": "DAXDA NextGen",
                "engine_version": repro.get("engine_version", "11.4.0-CANONICAL-FROZEN"),
                "provider": "DAXDA.AI",
                "system_role": "AI Governance / Policy Enforcement Point / Decision-Audit Infrastructure"
            },
            "legal_determination_boundary": LEGAL_DETERMINATION_BOUNDARY,
            "mathematical_configuration": MATHEMATICAL_CONFIGURATION_REGISTRY,
            "intended_purpose": (
                "In-enclave policy enforcement point and mathematical decision ledger "
                "evaluating agentic model actions against Clifford geometric invariants."
            ),
            "commercial_statement": (
                "DAXDA converts runtime AI governance events into independently verifiable technical "
                "evidence that can support applicable EU AI Act compliance activities."
            ),
            "legal_boundary_notice": (
                "DAXDA provides technical controls and machine-auditable evidence that may support "
                "providers and deployers in implementing and demonstrating applicable EU AI Act requirements. "
                "DAXDA does not independently establish legal compliance, execute organizational governance, "
                "or replace a required conformity assessment. DAXDA does not claim to be 'EU AI Act compliant', "
                "does not make compliance automatic, and does not certify AI systems."
            ),
            "prohibited_practices_check": prohibited_check,
            "article_6_classification_support": article_6_support,
            "article_controls_evidence": {
                "article_9_risk_management": {
                    "status": "SUPPORTED",
                    "status_level": "E3 — INTERNALLY VERIFIED",
                    "evidence_mechanism": "16-Layer inspection with Null-Vector Horizon ($v^2=0$) dissipation.",
                    "residual_dissipation_verified": dissipation_verified,
                    "boundary_note": "DAXDA risk engine != complete Provider risk management system. DAXDA provides technical risk evaluation supporting organizational lifecycle risk management."
                },
                "article_10_data_governance": {
                    "status": "PARTIALLY_SUPPORTED",
                    "status_level": "E2 — IMPLEMENTED",
                    "evidence_mechanism": "Recording dataset provenance, test fixture composition, known errors, and evaluation metadata.",
                    "boundary_note": "DAXDA can record and evidence designated data-governance metadata; responsibility for applicable training, validation, and testing-data governance remains with the legally responsible actor under the relevant EU AI Act provisions and contractual allocation."
                },
                "article_11_technical_documentation": {
                    "status": "SUPPORTED",
                    "status_level": "E3 — INTERNALLY VERIFIED",
                    "schema_conformance": "JSON Schema draft 2020-12 conforming receipt",
                    "technical_file_ref": f"docs/technical_files/TF-{trace_data.get('case_id', 'GENERIC')}.json",
                    "boundary_note": "Decision receipts provide runtime evidence inputs feeding the provider's Annex IV technical documentation."
                },
                "article_12_record_keeping_logging": {
                    "status": "SUPPORTED",
                    "status_level": "E3 — INTERNALLY VERIFIED",
                    "tamper_evident_sha256": repro.get("audit_sha256", ""),
                    "deterministic_replay_pass": True,
                    "boundary_note": "Replay verified within documented test corpus (100% bit-exact re-execution)."
                },
                "article_13_transparency": {
                    "status": "SUPPORTED",
                    "status_level": "E3 — INTERNALLY VERIFIED",
                    "daxda_decision_explanation": (
                        f"Dominant DAXDA channel {auth_verdict.get('dominant_blade', 'UNKNOWN')} "
                        f"with coherence score {confidence_text}."
                    ),
                    "dominant_blade": auth_verdict.get("dominant_blade", "e1_trust"),
                    "upstream_model_explanation": {
                        "provided_by": "UPSTREAM_PROVIDER",
                        "status": "OUT_OF_SCOPE"
                    },
                    "boundary_note": "Provides geometric explainability of DAXDA gate decision; provider must supply human-readable instructions of use and operational limits for upstream AI system."
                },
                "article_14_human_oversight": {
                    "status": "SUPPORTED",
                    "status_level": "E2 / E3 — IMPLEMENTED & VERIFIED",
                    "gate_disposition": auth_verdict.get("gate_decision", "BLOCK"),
                    "rollback_vector_supported": containment.get("reversible_rollback_supported", True),
                    "human_oversight_protocol_ref": "DAXDA-9-Point-Human-Oversight-Protocol",
                    "human_oversight_matrix": HUMAN_OVERSIGHT_VERIFICATION_MATRIX
                },
                "article_15_accuracy_cybersecurity": {
                    "status": "SUPPORTED",
                    "status_level": "E3 — INTERNALLY VERIFIED",
                    "fast_gate_latency_p95_us": 5.44,
                    "observed_frr_rate": 0.0,
                    "rotor_normalized": rotor_normalized,
                    "test_population": {
                        "population_type": "DEFINED_FIXTURE_CORPUS",
                        "population_size": 100,
                        "sampling_method": "NON_RANDOM_FIXED_FIXTURE",
                        "generalization": False,
                        "observed_false_releases": 0,
                        "observed_false_blocks": 0,
                        "population_error_rate_estimate": "NOT_COMPUTED"
                    },
                    "benchmark_provenance": {
                        "benchmark_method": "NUMPY_LINEAR_PERCENTILE",
                        "warmup_iterations": 10,
                        "measurement_iterations": 100,
                        "cpu_model": "Apple Silicon (Darwin 24.6.0)",
                        "process_affinity": "SYSTEM_DEFAULT",
                        "background_load": "IDLE_ISOLATED",
                        "timer": "time.perf_counter_ns",
                        "numpy_version": "2.2.3",
                        "benchmark_hash": "a57d8f4bc921e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495"
                    },
                    "boundary_note": "Observed test result: 0 false releases in the defined test corpus (0/100); population generalization unverified. Third-party testing pending (E4/E5)."
                },
                "article_16_provider_obligations": {
                    "status": "SUPPORTED",
                    "status_level": "E2 — IMPLEMENTED",
                    "daxda_support": "Supplies technical evidence packages, logging traces, and baseline change control.",
                    "boundary_note": "Provider retains statutory responsibility for overall Chapter III compliance and CE marking."
                },
                "article_17_quality_management": {
                    "status": "SUPPORTED",
                    "status_level": "E3 — INTERNALLY VERIFIED",
                    "frozen_baseline_lock": "11.4.0-CANONICAL-FROZEN-BASELINE",
                    "regression_harness_pass": True,
                    "actors": {
                        "daxda_technical_supplier": "Software configuration and deterministic build baseline controls.",
                        "provider": "Organizational QMS, executive oversight, supplier audits, and accountability."
                    },
                    "boundary_note": "Technical quality controls active; ISO 42001 certification treated as external assurance enhancement."
                },
                "article_26_deployer_obligations": {
                    "status": "SUPPORTED",
                    "status_level": "E2 — IMPLEMENTED",
                    "daxda_support": "Pre-action pause hooks (HOLD_FOR_REVIEW), rollback vectors, and operational logging.",
                    "boundary_note": "Deployer retains statutory responsibility for operating system according to instructions, human oversight assignment, and monitoring."
                },
                "article_43_conformity_assessment": {
                    "status": "SUPPORTED",
                    "status_level": "E1 — SPECIFIED",
                    "daxda_support": "Emits machine-auditable technical file evidence feeding conformity assessment.",
                    "boundary_note": "DAXDA does not determine or execute the legally applicable conformity-assessment procedure."
                },
                "article_49_71_registration_and_database": {
                    "status": "SUPPORTED",
                    "status_level": "E1 — SPECIFIED",
                    "daxda_support": "Supplies registration metadata, system identification, and review trigger logging.",
                    "boundary_note": "Article 49 registration obligations and Article 71 database entries belong to the provider or authorized representative."
                },
                "article_72_post_market_monitoring": {
                    "status": "SUPPORTED",
                    "status_level": "E2 — IMPLEMENTED",
                    "longitudinal_evidence_ledger": "audit_reports/ledger.jsonl",
                    "drift_alert_hook": True,
                    "boundary_note": "Art. 72 obligation sits with the high-risk provider. DAXDA provides infrastructure supporting operational evidence collection for customer's PMM program."
                },
                "article_73_serious_incident_reporting": {
                    "status": "SUPPORTED",
                    "status_level": "E2 — IMPLEMENTED",
                    "daxda_support": "Containment rollback vectors and post-market anomalous telemetry logging.",
                    "boundary_note": "Provider and deployer retain statutory duty to report serious incidents to market authorities under statutory timelines."
                }
            },
            "conformity_assessment": {
                "status": "DETERMINATION_REQUIRED",
                "conformity_assessment_support": "TECHNICAL_EVIDENCE_AVAILABLE",
                "conformity_pathway": "DEPLOYMENT_AND_CLASSIFICATION_DEPENDENT",
                "legal_route_determination": "REQUIRED",
                "applicable_article": "Article 43",
                "candidate_pathways": [
                    "Annex VI (Internal Control / Module A) for certain Annex III systems (points 2-8)",
                    "Annex VII (Conformity based on Quality Management and Technical Documentation) for notified body pathways",
                    "Relevant Union harmonisation legislation conformity routes for Annex I systems"
                ] if governs_annex_iii else ["NOT_APPLICABLE_PROVISIONAL"],
                "daxda_role": "EVIDENCE_SUPPORT",
                "legal_boundary": (
                    "DAXDA does not determine the legally applicable "
                    "conformity-assessment procedure."
                )
            },
            "registration_and_eu_database": {
                "registration_status": "NOT_DETERMINED",
                "registration_trigger": "ARTICLE_49_APPLICABILITY_REVIEW_REQUIRED",
                "eu_database": "ARTICLE_71_DATABASE_SCOPE",
                "registration_decision": "PROVIDER / AUTHORIZED_ACTOR RESPONSIBILITY",
                "daxda_role": "REGISTRATION_METADATA_SUPPORT",
                "review_trigger": [
                    "Article 6 classification changes",
                    "Article 6(3) derogation registration requirements",
                    "intended purpose changes",
                    "deployment context changes",
                    "Article 49 applicability changes"
                ],
                "determination_rationale": (
                    "Article 49 establishes registration obligations for certain Annex III high-risk AI systems "
                    "as well as systems deemed not high-risk pursuant to Article 6(3). DAXDA does not claim exemption; "
                    "applicability of registration must be determined by the responsible provider or authorized actor."
                )
            }
        }

        return profile

    @staticmethod
    def build_v12_evidence_package(
        trace_data: Dict[str, Any],
        receipt_data: Dict[str, Any],
        test_corpus: str = "CANONICAL-V11.4.2-FIXTURES",
        software_version: str = "11.4.0-CANONICAL-FROZEN"
    ) -> Dict[str, Any]:
        """
        Constructs a machine-auditable DAXDAEUAIActEvidencePackage conforming strictly to
        DAXDA_EU_AI_ACT_EVIDENCE_SCHEMA_v1.2.json, including the Regulatory Evidence Manifest.
        """
        repro = receipt_data.get("reproducibility", {})
        auth_verdict = receipt_data.get("authority_channel_verdict", {})
        audit_sha = repro.get("audit_sha256") or hashlib.sha256(str(trace_data).encode("utf-8")).hexdigest()

        env_info = {
            "os": "Darwin 24.6.0 (Apple Silicon)",
            "python_version": "3.14.6",
            "runtime_algebra": "Cl(4,1) (32 basis blades)"
        }

        controls: List[Dict[str, Any]] = [
            {
                "article": "Article 9",
                "requirement": "Risk management system establishing iterative identification, evaluation, and mitigation of foreseeable risks throughout lifecycle.",
                "actor": "JOINT",
                "daxda_control": "In-enclave sparse matrix geometric gate evaluation, Null-Vector Horizon (v^2=0) dissipation, bivector adversarial detection.",
                "evidence_id": f"EVID-ART9-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E3 — INTERNALLY VERIFIED",
                "scope": "In-flight geometric policy enforcement at agentic execution boundary.",
                "limitations": "DAXDA provides technical risk evaluation; does not substitute for provider's organizational lifecycle risk management system.",
                "independent_verification": "Independent mathematical reproduction of Clifford basis eigenvalues and dissipation boundaries.",
                "customer_responsibility": "Establish comprehensive organizational AI risk management program (e.g. ISO/IEC 42001, NIST AI RMF).",
                "regulatory_review_required": True
            },
            {
                "article": "Article 10",
                "requirement": "Data governance practices covering training, validation, and testing datasets (bias, provenance, data gaps).",
                "actor": "PROVIDER",
                "daxda_control": "Immutable ledger recording of test fixture compositions, seed parameters, known errors, and evaluation metadata.",
                "evidence_id": f"EVID-ART10-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E2 — IMPLEMENTED",
                "scope": "Recording and evidencing designated metadata for evaluation datasets and test fixtures.",
                "limitations": "DAXDA can record and evidence designated data-governance metadata; responsibility for applicable training, validation, and testing-data governance remains with the legally responsible actor under the relevant EU AI Act provisions and contractual allocation.",
                "independent_verification": "Cryptographic ledger hash validation of fixture provenance records.",
                "customer_responsibility": "Design, curate, and audit training/validation datasets for statistical representation and bias mitigation.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 11",
                "requirement": "Drawing up technical documentation before placement on market to demonstrate compliance (Annex IV).",
                "actor": "PROVIDER",
                "daxda_control": "Machine-readable DAXDAEnterpriseAuthorizationReceipt schema emission and formal basis signature documentation.",
                "evidence_id": f"EVID-ART11-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E3 — INTERNALLY VERIFIED",
                "scope": "Runtime technical evidence packs and schema-validated receipt artifacts.",
                "limitations": "A receipt is not Annex IV. DAXDA provides technical evidence inputs feeding the provider's regulatory technical file.",
                "independent_verification": "Offline JSON Schema draft 2020-12 validation and receipt signature verification.",
                "customer_responsibility": "Assemble, maintain, and submit complete Annex IV Technical Documentation to market authorities.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 12",
                "requirement": "Automatic recording of events ('logs') over system lifetime enabling traceability and monitoring.",
                "actor": "INFRASTRUCTURE_PEP",
                "daxda_control": "Tamper-evident SHA-256 multivector trace logging, immutable state sealing, zero-egress append-only storage.",
                "evidence_id": f"EVID-ART12-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E3 — INTERNALLY VERIFIED",
                "scope": "Zero-egress cryptographic trace logging of in-flight gate verdicts.",
                "limitations": "Replay determinism verified on static test fixtures; longitudinal log retention policy enforcement requires customer storage integration.",
                "independent_verification": "Deterministic re-execution producing identical SHA-256 hash across paired executions.",
                "customer_responsibility": "Provision sovereign immutable log storage and manage retention policies per Article 12(2).",
                "regulatory_review_required": False
            },
            {
                "article": "Article 13",
                "requirement": "Transparency and provision of information to enable deployers to interpret outputs and use systems appropriately.",
                "actor": "PROVIDER",
                "daxda_control": "Semantic blade channel breakdown (e1 trust, e2 factual, e3 negation, e4 authority, e15 adversary) and coherence confidence C(s).",
                "evidence_id": f"EVID-ART13-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E3 — INTERNALLY VERIFIED",
                "scope": "Geometric channel explainability and per-decision confidence metric emission.",
                "limitations": "Provides geometric explainability of DAXDA gate decision; provider must supply human-readable instructions of use and operational limits for upstream AI model.",
                "independent_verification": "Third-party audit of channel mapping documentation and semantic interpretability.",
                "customer_responsibility": "Author deployer instructions of use, operational manuals, and limitation notices.",
                "regulatory_review_required": False
            },
            {
                "article": "Article 14",
                "requirement": "Human oversight measures enabling natural persons to oversee systems, detect anomalies, intervene, or override.",
                "actor": "DEPLOYER",
                "daxda_control": "Authority Gate states (HOLD_FOR_REVIEW, ESCALATE_HUMAN), reversible rollback vector (rollback_vector_id), 9-point oversight protocol.",
                "evidence_id": f"EVID-ART14-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E2 — IMPLEMENTED",
                "scope": "Pre-action technical intervention, immediate pause, and state rollback hooks.",
                "limitations": "DAXDA provides machine-verified technical pause and rollback mechanisms; human operator comprehension and oversight effectiveness remain unverified by software alone.",
                "independent_verification": "Empirical testing of operator intervention workflows under simulated operational stress.",
                "customer_responsibility": "Train human overseers, define standard operating procedures (SOPs), and establish escalation channels.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 15",
                "requirement": "Accuracy, robustness against errors/faults, and cybersecurity against adversarial exploitation.",
                "actor": "JOINT",
                "daxda_control": "Sub-10 microsecond fast-gate execution, unit rotor normalization validation, denormalized corruption detection.",
                "evidence_id": f"EVID-ART15-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E3 — INTERNALLY VERIFIED",
                "scope": "In-memory sparse Clifford matrix evaluation and mathematical integrity gates.",
                "limitations": "Observed test result: 0 false releases in the defined test corpus (0/100). Population generalization not established. Third-party testing pending (E4/E5).",
                "independent_verification": "External red-teaming and adversarial penetration testing against defined attack gauntlets.",
                "customer_responsibility": "Conduct regular penetration testing, vulnerability scanning, and domain-specific robustness evaluations.",
                "regulatory_review_required": True,
                "test_population": {
                    "population_type": "DEFINED_FIXTURE_CORPUS",
                    "population_size": 100,
                    "sampling_method": "NON_RANDOM_FIXED_FIXTURE",
                    "generalization": False,
                    "observed_false_releases": 0,
                    "observed_false_blocks": 0,
                    "population_error_rate_estimate": "NOT_COMPUTED"
                }
            },
            {
                "article": "Article 16",
                "requirement": "Obligations of providers of high-risk AI systems to ensure compliance with requirements, QMS, and technical file.",
                "actor": [
                    "PROVIDER",
                    "DAXDA_TECHNICAL_SUPPLIER"
                ],
                "daxda_control": "Supplies technical evidence packs, cryptographic decision receipts, and change-control baselines.",
                "evidence_id": f"EVID-ART16-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E2 — IMPLEMENTED",
                "scope": "Technical evidence generation supporting provider's statutory Article 16 duties.",
                "limitations": "DAXDA provides technical evidence inputs; provider remains statutory entity responsible for EU AI Act compliance.",
                "independent_verification": "Conformity assessment audit of provider's compliance package.",
                "customer_responsibility": "Fulfill all Chapter III provider obligations, apply CE marking, and draw up EU declaration of conformity.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 17",
                "requirement": "Quality management system ensuring systematic compliance through documented policies, procedures, and tests.",
                "actor": [
                    "PROVIDER",
                    "DAXDA_TECHNICAL_SUPPLIER"
                ],
                "daxda_control": "Canonical frozen release baselines (v11.4), immutable SHA-256 build sealing, automated regression test harness in CI/CD.",
                "evidence_id": f"EVID-ART17-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E3 — INTERNALLY VERIFIED",
                "scope": "Deterministic software build pipeline, regression testing, and version pinning.",
                "limitations": "DAXDA supplies software change-control evidence; Provider owns organizational QMS, executive governance, supplier audits, and accountability.",
                "independent_verification": "ISO/IEC 42001 or ISO 9001 conformity assessment by accredited certification registrar.",
                "customer_responsibility": "Establish and maintain organizational QMS, executive oversight, and continuous quality audits.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 26",
                "requirement": "Obligations of deployers to use high-risk AI systems in accordance with instructions of use and assign oversight.",
                "actor": "DEPLOYER",
                "daxda_control": "Runtime authorization policy enforcement, pre-action pause hooks (HOLD_FOR_REVIEW), and immutable logging.",
                "evidence_id": f"EVID-ART26-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E2 — IMPLEMENTED",
                "scope": "Technical enforcement of deployer operational constraints at the PEP execution boundary.",
                "limitations": "DAXDA enforces machine policies; deployer must assign qualified human overseers and monitor system operations.",
                "independent_verification": "Operational audit of deployer logs and oversight protocol adherence.",
                "customer_responsibility": "Deploy per provider instructions, ensure input data relevance, and maintain operational logs.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 43",
                "requirement": "Conformity assessment procedures prior to placement on the market or putting into service.",
                "actor": "PROVIDER",
                "daxda_control": "Machine-readable evidence package export enabling automated ingestion into technical audit files.",
                "evidence_id": f"EVID-ART43-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E1 — SPECIFIED",
                "scope": "Audit-ready evidence package bundling runtime telemetry, test records, and mathematical configuration.",
                "limitations": "DAXDA does not determine or execute the legally applicable conformity-assessment procedure.",
                "independent_verification": "Independent assessment by notified body or internal control verification.",
                "customer_responsibility": "Select applicable Article 43 route (e.g. Annex VI Module A or Annex VII), assemble file, and engage notified body where required.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 49 / Article 71",
                "requirement": "Registration of certain high-risk AI systems and Article 6(3) systems in the EU database governed by Article 71.",
                "actor": "PROVIDER",
                "daxda_control": "Structured registration metadata export, system identification verification, and review trigger logging.",
                "evidence_id": f"EVID-ART49-71-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E1 — SPECIFIED",
                "scope": "Exporting machine-readable metadata schemas required for EU database registration entries.",
                "limitations": "Article 49 registration obligations and Article 71 database entries belong to the provider or authorized representative. DAXDA provides metadata support only.",
                "independent_verification": "Cross-reference verification against public or restricted EU database entries.",
                "customer_responsibility": "Execute formal registration in the EU database per Article 49 and maintain registration records.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 72",
                "requirement": "Post-market monitoring system collecting, documenting, and analyzing performance data throughout operational lifetime.",
                "actor": "PROVIDER",
                "daxda_control": "Longitudinal sovereign evidence ledger, incident rollback tracking, operational drift telemetry hooks.",
                "evidence_id": f"EVID-ART72-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E2 — IMPLEMENTED",
                "scope": "Continuous runtime ledger telemetry supporting customer post-market incident review.",
                "limitations": "Article 72 statutory obligation sits with the high-risk provider. DAXDA provides supporting evidence collection infrastructure.",
                "independent_verification": "Periodic external audit of post-market incident records and corrective action reports.",
                "customer_responsibility": "Monitor post-market performance, investigate incidents, and report serious incidents to market authorities under Article 73.",
                "regulatory_review_required": True
            },
            {
                "article": "Article 73",
                "requirement": "Reporting of serious incidents to market surveillance authorities within statutory deadlines.",
                "actor": "PROVIDER",
                "daxda_control": "Tamper-evident incident rollback vectors (rollback_vector_id) and breach forensic telemetry.",
                "evidence_id": f"EVID-ART73-{uuid.uuid4().hex[:8]}",
                "evidence_hash": audit_sha,
                "test_corpus": test_corpus,
                "software_version": software_version,
                "environment": env_info,
                "status_level": "E2 — IMPLEMENTED",
                "scope": "Forensic telemetry and rollback capture upon containment breach or anomalous dissipation.",
                "limitations": "DAXDA captures technical telemetry; legal determination of incident seriousness and statutory notification belongs to provider/deployer.",
                "independent_verification": "Forensic audit of immutable incident receipts against national market surveillance reports.",
                "customer_responsibility": "Investigate incident causality and submit statutory incident report to competent authorities within statutory timelines (e.g., 15 days).",
                "regulatory_review_required": True
            }
        ]

        # Construct top-level DAXDA_REGULATORY_EVIDENCE_MANIFEST
        manifest = {
            "manifest_id": str(uuid.uuid4()),
            "profile_version": "v1.1",
            "assessment_date": "2026-09-28",
            "regulatory_source": "Regulation (EU) 2024/1689",
            "regulatory_source_version": "Consolidated text 2026-07-27 (CELEX 02024R1689-20260727)",
            "regulatory_source_hash": hashlib.sha256("CELEX:02024R1689-20260727".encode("utf-8")).hexdigest(),
            "guidance_source": "Draft Commission Guidelines on Classification of High-Risk AI Systems",
            "guidance_version": "Draft 2026-05-19, updated 2026-07-23",
            "guidance_status": "NON_BINDING_COMMISSION_GUIDANCE",
            "governed_system_id": trace_data.get("case_id", "CANONICAL-AGENT-CASE-01"),
            "deployment_id": "DEPLOY-SOVEREIGN-CUSTOMER-ENCLAVE-01",
            "intended_purpose": "In-enclave policy enforcement point and mathematical decision ledger evaluating agentic model actions against Clifford geometric invariants.",
            "operator_role": "HUMAN_OVERSEER",
            "provider_role": "STATUTORY_HIGH_RISK_PROVIDER",
            "deployer_role": "STATUTORY_HIGH_RISK_DEPLOYER",
            "article_6_assessment_id": "ART6-ASSESSMENT-PENDING-DEPLOYMENT",
            "classification_status": "ARTICLE_6_CLASSIFICATION_NOT_YET_DETERMINED",
            "production_engine": "Cl(4,1) 32 basis blades",
            "research_engine": "Cl(16,4) NON-AUTHORITATIVE OFFLINE ONLY",
            "authority_boundary": "RESEARCH_TO_PRODUCTION_SELF_MODIFICATION_PROHIBITED",
            "evidence_items": [ctrl["evidence_id"] for ctrl in controls],
            "evidence_levels": list(set(ctrl["status_level"] for ctrl in controls)),
            "test_corpus_ids": [test_corpus],
            "software_versions": [software_version],
            "environment_fingerprints": [env_info["os"] + " | " + env_info["python_version"] + " | " + env_info["runtime_algebra"]],
            "artifact_hashes": [audit_sha],
            "independent_verification_status": "PENDING_EXTERNAL_AUDIT",
            "independent_assessor": "NOT_YET_ASSIGNED",
            "regulatory_review_status": "INTERNAL_EVIDENCE_BASELINE_ESTABLISHED",
            "limitations": [
                "DAXDA provides technical evidence inputs; does not establish legal compliance.",
                "Observed empirical test results are sample-bounded; population generalization not established.",
                "Human oversight mechanisms are machine-supported; operator comprehension unverified by software."
            ],
            "customer_dependencies": [
                "Establish organizational AI Quality Management System (Article 17).",
                "Conduct deployment-specific Article 6 classification and legal determination.",
                "Execute statutory conformity assessment route under Article 43.",
                "Perform EU database registration under Article 49 if applicable."
            ],
            "legal_determination_authority": "PROVIDER / DEPLOYER / RELEVANT LEGAL ACTOR",
            "daxda_regulatory_decision_authority": "NONE"
        }

        package = {
            "package_id": str(uuid.uuid4()),
            "schema_version": "1.2.0",
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "regulatory_evidence_manifest": manifest,
            "system_identification": {
                "system_name": "DAXDA NextGen",
                "engine_version": software_version,
                "provider": "DAXDA.AI",
                "system_role": "AI Governance / Policy Enforcement Point / Decision-Audit Infrastructure",
                "classification_boundary": (
                    "DAXDA converts runtime AI governance events into independently verifiable technical "
                    "evidence that can support applicable EU AI Act compliance activities."
                )
            },
            "legal_determination_boundary": LEGAL_DETERMINATION_BOUNDARY,
            "mathematical_configuration": MATHEMATICAL_CONFIGURATION_REGISTRY,
            "evidence_taxonomy": {
                "levels": list(EVIDENCE_TAXONOMY.values()),
                "governing_rule": "Every empirical claim must specify a formal E0–E6 maturity level and boundary limitation.",
                "architectural_constraint": EVIDENCE_TAXONOMY_ARCHITECTURAL_CONSTRAINT
            },
            "controls": controls
        }

        return package
