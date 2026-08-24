#!/usr/bin/env python3
"""
DAX Prospective Evidence Packet Builder & Corpus Generator (dax_evidence_packet_builder.py)
===========================================================================================
Generates 200 complete, multi-document evidence packets with realistic dockets, filings,
game logs, regulatory transcripts, corporate filings, and scientific replication protocols.

Domains & Case Distribution (Total N = 200):
  1. LEGAL_DECISIONS (50 cases): Court dockets, motions to suppress/dismiss, precedent citations.
  2. SPORTS_OUTCOMES (50 cases): Team records, injury reports, H2H stats, weather, T0 cutoffs.
  3. REGULATORY_DECISIONS (25 cases): FDA advisory committee summaries, SEC/FTC merger dockets.
  4. CORPORATE_EVENTS (25 cases): M&A tender offers, earnings guidance, proxy battles.
  5. SCIENTIFIC_REPLICATION (25 cases): Original paper stats, sample sizes, replication protocols.
  6. STRUCTURED_SYNTHETIC (25 cases): Formally specified state-transition logic graphs.
"""

from __future__ import annotations
import json
import os
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


@dataclass
class DocketEntry:
    entry_number: int
    date: str
    filing_type: str
    filed_by: str
    summary: str


@dataclass
class CaseEvidencePacket:
    case_id: str
    domain: str
    title: str
    cutoff_time: str
    outcome_categories: Dict[str, str]
    actual_outcome: str
    docket_entries: List[DocketEntry]
    background_facts: str
    procedural_posture: str
    legal_or_domain_precedents: List[str]
    supporting_exhibits: List[Dict[str, str]]
    base_rate_prior: Dict[str, float]
    sha256_snapshot_hash: str = ""

    def __post_init__(self):
        if not self.sha256_snapshot_hash:
            raw = f"{self.case_id}:{self.cutoff_time}:{self.background_facts}:{self.procedural_posture}"
            self.sha256_snapshot_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_full_text(self) -> str:
        docket_str = "\n".join([f"  [{e.entry_number}] {e.date} | {e.filing_type} ({e.filed_by}): {e.summary}" for e in self.docket_entries])
        exhibits_str = "\n".join([f"  - Exhibit {ex['id']}: {ex['title']} - {ex['description']}" for ex in self.supporting_exhibits])
        precedents_str = "\n".join([f"  - {p}" for p in self.legal_or_domain_precedents])
        
        return f"""================================================================================
CASE EVIDENCE PACKET [T0 CUTOFF: {self.cutoff_time}]
ID: {self.case_id} | Domain: {self.domain}
Title: {self.title}
================================================================================

1. PROCEDURAL POSTURE & BACKGROUND:
{self.procedural_posture}

2. STATEMENT OF FACTS:
{self.background_facts}

3. DOCKET HISTORY UP TO T0:
{docket_str}

4. DOMAIN PRECEDENTS & GOVERNING RULES:
{precedents_str}

5. SUPPORTING EXHIBITS & EVIDENCE ATTACHMENTS:
{exhibits_str}

6. OUTCOME CATEGORIES TO FORECAST:
{json.dumps(self.outcome_categories, indent=2)}
"""


class EvidenceCorpusGenerator:
    def __init__(self):
        pass

    def build_legal_case(self, idx: int) -> CaseEvidencePacket:
        cid = f"LEGAL-{idx:03d}"
        cutoff = "2026-09-05T17:00:00-04:00"
        
        outcomes = {
            "A": "Motion Granted in Full",
            "B": "Motion Granted in Part / Denied in Part",
            "C": "Motion Denied in Full",
            "D": "Case Dismissed / Settlement Approved",
            "E": "Interlocutory Appeal / Stay Granted"
        }
        
        # Ground truth distribution
        if idx % 5 in [1, 2, 3]:
            actual = "C"
        elif idx % 5 == 4:
            actual = "A"
        else:
            actual = "B"

        dockets = [
            DocketEntry(1, "2026-08-01", "COMPLAINT", "Plaintiff", "Filed civil complaint alleging breach of fiduciary duty and violation of federal securities law."),
            DocketEntry(2, "2026-08-10", "SUMMONS RETURNED", "Clerk", "Summons executed on corporate defendants."),
            DocketEntry(3, "2026-08-20", "MOTION TO DISMISS", "Defendants", "Defendants filed Rule 12(b)(6) motion to dismiss for failure to state a claim under heightened Rule 9(b) pleading standards."),
            DocketEntry(4, "2026-08-28", "OPPOSITION TO MOTION TO DISMISS", "Plaintiff", "Plaintiff filed opposition brief citing internal emails and board meeting minutes."),
            DocketEntry(5, "2026-09-02", "REPLY BRIEF", "Defendants", "Defendants filed reply asserting scienter was inadequately pled under PSLRA safe harbor provisions.")
        ]

        posture = f"District Court Civil Action No. 26-CV-{1000+idx}. Defendant's Rule 12(b)(6) Motion to Dismiss pending before District Judge."
        facts = f"Plaintiff shareholders allege that Defendant Corporation made materially misleading statements regarding Q2 commercial revenue projections. Defendants contend statements constituted forward-looking expressions covered by PSLRA safe harbor provisions. The evidentiary record at cutoff T0 consists of public disclosure statements, regulatory SEC Form 8-K filings, and sworn officer declarations."
        precedents = [
            "Tellabs, Inc. v. Makor Issues & Rights, Ltd., 551 U.S. 308 (2007) (Strong inference of scienter required)",
            "Omnicare, Inc. v. Laborers Dist. Council Constr. Industry Pension Fund, 575 U.S. 175 (2015) (Opinion statement liability standards)",
            "Matrixx Initiatives, Inc. v. Siracusano, 563 U.S. 27 (2011) (Materiality of adverse event reports)"
        ]
        exhibits = [
            {"id": "A", "title": "SEC Form 10-Q", "description": "Quarterly report for period ending June 30, 2026."},
            {"id": "B", "title": "Internal Email Matrix", "description": "Email thread between CFO and VP of Sales regarding pipeline conversion rates."},
            {"id": "C", "title": "Analyst Call Transcript", "description": "Transcript of Q2 earnings conference call."}
        ]
        base_rate = {"A": 0.18, "B": 0.27, "C": 0.46, "D": 0.05, "E": 0.04}

        return CaseEvidencePacket(
            case_id=cid,
            domain="LEGAL_DECISIONS",
            title=f"In re Corporate Securities Litigation (Case #{idx})",
            cutoff_time=cutoff,
            outcome_categories=outcomes,
            actual_outcome=actual,
            docket_entries=dockets,
            background_facts=facts,
            procedural_posture=posture,
            legal_or_domain_precedents=precedents,
            supporting_exhibits=exhibits,
            base_rate_prior=base_rate
        )

    def build_sports_case(self, idx: int) -> CaseEvidencePacket:
        cid = f"SPORT-{idx:03d}"
        cutoff = "2026-09-05T17:00:00-04:00"

        outcomes = {
            "A": "Home Team Win (Margin > 5)",
            "B": "Home Team Win (Margin 1-5)",
            "C": "Away Team Win (Margin 1-5)",
            "D": "Away Team Win (Margin > 5)",
            "E": "Draw / Extra Time Decision"
        }

        if idx % 4 == 1:
            actual = "A"
        elif idx % 4 == 2:
            actual = "B"
        elif idx % 4 == 3:
            actual = "C"
        else:
            actual = "D"

        dockets = [
            DocketEntry(1, "2026-08-25", "REGULAR SEASON GAME 1", "Home Team", "Home team won 104-98 vs Conference Opponent."),
            DocketEntry(2, "2026-08-28", "REGULAR SEASON GAME 2", "Away Team", "Away team won 112-110 in overtime."),
            DocketEntry(3, "2026-09-01", "INJURY REPORT", "League Medical", "Starting All-Pro point guard listed as Questionable (Hamstring tightness)."),
            DocketEntry(4, "2026-09-04", "SHOOTAROUND PRACTICE", "Coaching Staff", "Head Coach confirmed starting lineup adjustment for Game 3.")
        ]

        posture = f"National League Matchup #{idx}. Pre-game cutoff T0."
        facts = f"Home Team (12-4, 8-1 at home) hosts Away Team (10-6, 4-4 away). Home Team ranks #3 in offensive efficiency (116.4 ratings) and #7 in defensive rating (108.2). Away Team ranks #12 in offensive efficiency and #2 in defensive rating. Weather conditions: Indoor stadium, zero environmental impact."
        precedents = [
            "Historical Home Court Advantage: Home teams win 61.2% in head-to-head matchups when rest days = 2.",
            "Injury Impact Index: Absence of starting point guard reduces expected offensive output by 4.2 points per 100 possessions."
        ]
        exhibits = [
            {"id": "1", "title": "Advanced Synergy Tracking", "description": "Pace and shot quality metrics past 10 games."},
            {"id": "2", "title": "Head-to-Head History", "description": "Home Team leads series 7-3 over past 3 seasons."}
        ]
        base_rate = {"A": 0.42, "B": 0.22, "C": 0.20, "D": 0.14, "E": 0.02}

        return CaseEvidencePacket(
            case_id=cid,
            domain="SPORTS_OUTCOMES",
            title=f"Professional Championship Matchup #{idx}",
            cutoff_time=cutoff,
            outcome_categories=outcomes,
            actual_outcome=actual,
            docket_entries=dockets,
            background_facts=facts,
            procedural_posture=posture,
            legal_or_domain_precedents=precedents,
            supporting_exhibits=exhibits,
            base_rate_prior=base_rate
        )

    def build_regulatory_case(self, idx: int) -> CaseEvidencePacket:
        cid = f"REGUL-{idx:03d}"
        cutoff = "2026-09-05T17:00:00-04:00"

        outcomes = {
            "A": "Approval Granted Without Complete Response Letter",
            "B": "Approval Granted With Black Box Warning / REMS Requirement",
            "C": "Complete Response Letter Issued (PDUFA Delayed)",
            "D": "Regulatory Enforcement Action / Advisory Block",
            "E": "Application Withdrawn by Sponsor"
        }

        actual = "A" if idx % 3 != 0 else "C"

        dockets = [
            DocketEntry(1, "2026-03-15", "NDA SUBMISSION", "Biotech Sponsor", "Filed New Drug Application for novel oncology agent DAX-402."),
            DocketEntry(2, "2026-05-10", "PRIORITY REVIEW GRANTED", "FDA CDER", "Granted 6-month priority review with PDUFA target date of Sept 15, 2026."),
            DocketEntry(3, "2026-08-12", "ADVISORY COMMITTEE MEETING", "FDA Oncologic Drugs Advisory Committee", "AdCom voted 11-2 that benefit-risk profile supports approval for primary indication.")
        ]

        posture = f"FDA PDUFA Review Docket NDA #218-{idx:03d}. Post-AdCom review phase prior to final decision."
        facts = f"Sponsor submitted Phase 3 global randomized double-blind trial results (N=840) demonstrating statistically significant overall survival benefit (HR 0.68, 95% CI 0.54-0.84, p < 0.001) compared to standard of care. Secondary endpoints met. Grade 3/4 adverse events observed in 14.2% of arm vs 11.1% in control."
        precedents = [
            "FDA Guidance for Industry: Clinical Trial Endpoints for Approval of Cancer Drugs.",
            "Historical FDA AdCom Concurrence Rate: FDA aligns with positive AdCom votes in 87.4% of oncology applications."
        ]
        exhibits = [
            {"id": "1", "title": "Phase 3 Primary Endpoint Kaplan-Meier Curve", "description": "Overall Survival curves showing clear early divergence at Month 3."},
            {"id": "2", "title": "AdCom Transcript Summary", "description": "Key panel member comments supporting efficacy in intention-to-treat population."}
        ]
        base_rate = {"A": 0.65, "B": 0.20, "C": 0.10, "D": 0.04, "E": 0.01}

        return CaseEvidencePacket(
            case_id=cid,
            domain="REGULATORY_DECISIONS",
            title=f"FDA NDA Review Docket #{idx}",
            cutoff_time=cutoff,
            outcome_categories=outcomes,
            actual_outcome=actual,
            docket_entries=dockets,
            background_facts=facts,
            procedural_posture=posture,
            legal_or_domain_precedents=precedents,
            supporting_exhibits=exhibits,
            base_rate_prior=base_rate
        )

    def build_corporate_case(self, idx: int) -> CaseEvidencePacket:
        cid = f"CORPO-{idx:03d}"
        cutoff = "2026-09-05T17:00:00-04:00"

        outcomes = {
            "A": "Merger Completed on Original Terms",
            "B": "Merger Price Revised Upward / Sweetened Offer",
            "C": "Regulatory Divestiture Required Before Closing",
            "D": "Deal Terminated / Breakup Fee Paid",
            "E": "Hostile Counter-Bidding War Initiated"
        }

        actual = "A" if idx % 2 == 1 else "B"

        dockets = [
            DocketEntry(1, "2026-06-01", "DEFINITIVE MERGER AGREEMENT", "Acquirer & Target", "Announced $4.2B all-cash acquisition at $65.00/share (38% premium)."),
            DocketEntry(2, "2026-07-15", "HSR SECOND REQUEST", "FTC Bureau of Competition", "Issued Request for Additional Information under Hart-Scott-Rodino Act."),
            DocketEntry(3, "2026-08-25", "SHAREHOLDER VOTE", "Target Corporation", "94.2% of voting shares voted in favor of merger adoption.")
        ]

        posture = f"SEC Schedule 14A Proxy & FTC HSR Antitrust Review for Deal #{idx}."
        facts = f"Acquirer Corporation (Market Cap $28B) agreed to acquire Target Corp (Market Cap $3.8B) in the specialized medical device sector. Combined market share in regional target sub-markets estimated at 31%. Both parties have certified substantial compliance with FTC Second Request."
        precedents = [
            "FTC Horizontal Merger Guidelines (Market concentration & HHI calculation standards).",
            "Precedent Medical Device Transactions: Remedies accepted in 78% of similar HHI overlap cases."
        ]
        exhibits = [
            {"id": "1", "title": "SEC Schedule 14A Proxy Statement", "description": "Background of the merger & fairness opinion by Independent Financial Advisor."},
            {"id": "2", "title": "HSR Compliance Certificate", "description": "Formal certification of document production to FTC."}
        ]
        base_rate = {"A": 0.55, "B": 0.25, "C": 0.15, "D": 0.04, "E": 0.01}

        return CaseEvidencePacket(
            case_id=cid,
            domain="CORPORATE_EVENTS",
            title=f"M&A Acquisition Docket #{idx}",
            cutoff_time=cutoff,
            outcome_categories=outcomes,
            actual_outcome=actual,
            docket_entries=dockets,
            background_facts=facts,
            procedural_posture=posture,
            legal_or_domain_precedents=precedents,
            supporting_exhibits=exhibits,
            base_rate_prior=base_rate
        )

    def build_scientific_case(self, idx: int) -> CaseEvidencePacket:
        cid = f"SCIEN-{idx:03d}"
        cutoff = "2026-09-05T17:00:00-04:00"

        outcomes = {
            "A": "Primary Effect Confirmed (Effect Size within 80% CI of Original)",
            "B": "Partial Confirmation (Statistically Significant but Attenuated)",
            "C": "Null Hypothesis Retained (Effect Size Non-Significant / p > 0.05)",
            "D": "Inconclusive Trial (High Variance / Underpowered Sample)",
            "E": "Protocol Discrepancy Identified Prior to Unblinding"
        }

        actual = "A" if idx % 2 == 1 else "C"

        dockets = [
            DocketEntry(1, "2025-11-10", "ORIGINAL PUBLICATION", "Lead University Consortium", "Published high-impact paper reporting novelty effect in cognitive performance (N=120, p=0.012)."),
            DocketEntry(2, "2026-02-01", "PRE-REGISTRATION", "Reproducibility Project", "Pre-registered high-powered direct replication protocol (Target N=600, power=0.95)."),
            DocketEntry(3, "2026-08-30", "DATA COLLECTION COMPLETED", "Independent Lab Network", "Completed double-blind experimental trials across 4 independent testing sites.")
        ]

        posture = f"Scientific Open Science Replication Study #{idx}. Analysis pending unblinding at cutoff T0."
        facts = f"Original study reported Cohen's d = 0.54 (95% CI 0.18-0.90) for neural feedback intervention on working memory capacity. Independent replication protocol doubled sample size per arm (N=300 per arm) and matched equipment, stimuli calibration, and participant exclusion criteria exactly."
        precedents = [
            "Open Science Framework (OSF) Reproducibility Guidelines.",
            "Meta-analytic Base Rates: Psychology & Neuroscience replication success rate = 39.4%."
        ]
        exhibits = [
            {"id": "1", "title": "OSF Registered Protocol", "description": "Detailed pre-analysis plan and power calculation code."},
            {"id": "2", "title": "Multi-site Data Quality Audit", "description": "Blinded data completeness audit confirming < 1% missing values."}
        ]
        base_rate = {"A": 0.40, "B": 0.25, "C": 0.25, "D": 0.08, "E": 0.02}

        return CaseEvidencePacket(
            case_id=cid,
            domain="SCIENTIFIC_REPLICATION",
            title=f"Reproducibility Replication Docket #{idx}",
            cutoff_time=cutoff,
            outcome_categories=outcomes,
            actual_outcome=actual,
            docket_entries=dockets,
            background_facts=facts,
            procedural_posture=posture,
            legal_or_domain_precedents=precedents,
            supporting_exhibits=exhibits,
            base_rate_prior=base_rate
        )

    def build_synthetic_case(self, idx: int) -> CaseEvidencePacket:
        cid = f"SYNTH-{idx:03d}"
        cutoff = "2026-09-05T17:00:00-04:00"

        outcomes = {
            "A": "State Transition Alpha (Node S_0 -> S_1)",
            "B": "State Transition Beta (Node S_0 -> S_2)",
            "C": "State Transition Gamma (Node S_0 -> S_3)",
            "D": "State Transition Delta (Node S_0 -> S_4)",
            "E": "State Transition Epsilon (Terminal Sink S_5)"
        }

        actual = "C" if idx % 3 == 0 else "A"

        dockets = [
            DocketEntry(1, "2026-09-01", "GRAPH INITIALIZATION", "Deterministic System Simulator", "Initialized directed acyclic graph G=(V,E) with 6 nodes and weighted transition probabilities."),
            DocketEntry(2, "2026-09-03", "PERTURBATION VECTOR APPLIED", "Clifford Geometry Transport", "Applied rotor R_12(pi/4) phase perturbation to initial state multivector M_0."),
            DocketEntry(3, "2026-09-05", "STATE OBSERVATION T0", "State Measurement Node", "Recorded observable feature multivector M_T0 prior to final graph step.")
        ]

        posture = f"Structured Deterministic Graph Simulation #{idx}. Final transition step pending at cutoff T0."
        facts = f"Initial state M_0 encoded with scalar trust s = 0.82, risk vector e1 = 0.15, e2 = 0.08, deception e12 = 0.00. Transition matrix governed by Cl(7,0) geometric rotor evolution."
        precedents = [
            "Clifford Algebra Cl(7,0) 128-Blade Manifold Conservation Law.",
            "Invariant Reconstruction Residual Bound: |M_rec - M_orig| < 1.0e-12."
        ]
        exhibits = [
            {"id": "1", "title": "Multivector State Tensor", "description": "128-element floating point multivector representation."},
            {"id": "2", "title": "Graph Adjacency Matrix", "description": "Canonical weighted transition weights."}
        ]
        base_rate = {"A": 0.20, "B": 0.20, "C": 0.20, "D": 0.20, "E": 0.20}

        return CaseEvidencePacket(
            case_id=cid,
            domain="STRUCTURED_SYNTHETIC",
            title=f"Structured Geometric Synthetic Graph #{idx}",
            cutoff_time=cutoff,
            outcome_categories=outcomes,
            actual_outcome=actual,
            docket_entries=dockets,
            background_facts=facts,
            procedural_posture=posture,
            legal_or_domain_precedents=precedents,
            supporting_exhibits=exhibits,
            base_rate_prior=base_rate
        )

    def generate_all_200_packets(self) -> List[CaseEvidencePacket]:
        packets = []
        for i in range(1, 51):
            packets.append(self.build_legal_case(i))
        for i in range(1, 51):
            packets.append(self.build_sports_case(i))
        for i in range(1, 26):
            packets.append(self.build_regulatory_case(i))
        for i in range(1, 26):
            packets.append(self.build_corporate_case(i))
        for i in range(1, 26):
            packets.append(self.build_scientific_case(i))
        for i in range(1, 26):
            packets.append(self.build_synthetic_case(i))
        return packets


if __name__ == "__main__":
    gen = EvidenceCorpusGenerator()
    pkts = gen.generate_all_200_packets()
    print("=" * 80)
    print(f"DAX Evidence Packet Corpus Generator: Built {len(pkts)} complete packets.")
    print("=" * 80)
    sample = pkts[0]
    print(sample.get_full_text())
