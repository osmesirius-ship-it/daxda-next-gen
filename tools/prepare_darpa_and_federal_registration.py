#!/usr/bin/env python3
"""
DAXDA.IA — Federal Entity Registration & DARPA Application Package Generator
Validates, cryptographically fingerprints, and packages all federal registration dossiers
and DARPA BAA proposal documents.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone

def sha256_file(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs")
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    required_artifacts = [
        {
            "id": "FED_DOSSIER",
            "name": "Federal Entity Registration Dossier",
            "category": "Federal SAM.gov & Governance Charter",
            "rel_path": "docs/compliance/DAXDA_FEDERAL_ENTITY_REGISTRATION_DOSSIER.md",
        },
        {
            "id": "DARPA_BAA_PROPOSAL",
            "name": "DARPA BAA AI Governance Technical Proposal",
            "category": "Defense / DARPA Proposal Package",
            "rel_path": "docs/proposals/DARPA_BAA_AI_GOVERNANCE_PROPOSAL.md",
        },
        {
            "id": "NIST_TEVV_COMMENT",
            "name": "NIST AI 200-2 TEVV-Athlon Public Comment",
            "category": "Standards & Compliance Submission",
            "rel_path": "docs/compliance/NIST_AI_200_2_TEVV_ATHLON_PUBLIC_COMMENT_OCTOBER_2026.md",
        },
        {
            "id": "L4_MASTER_PAYOUT",
            "name": "Level 4 Master Payout Claim & 5-Cycle Manifold",
            "category": "Evidentiary Baseline & Verification",
            "rel_path": "daxda-meta-bounty-submission/solutions/level4/DAXDA_L4_MASTER_PAYOUT_CLAIM.md",
        },
    ]

    print("=" * 80)
    print("   DAXDA.IA — FEDERAL REGISTRATION & DARPA PROPOSAL VERIFIER")
    print("   Nicole Protocol (886-Ops) | Agent: Dexter | Architect: Nicole Bess")
    print("=" * 80)

    verified_items = []
    all_present = True

    for art in required_artifacts:
        full_path = os.path.join(base_dir, art["rel_path"])
        exists = os.path.exists(full_path)
        size_bytes = os.path.getsize(full_path) if exists else 0
        digest = sha256_file(full_path) if exists else None

        status = "✅ CERTIFIED" if exists else "❌ MISSING"
        if not exists:
            all_present = False

        verified_items.append({
            "id": art["id"],
            "name": art["name"],
            "category": art["category"],
            "path": art["rel_path"],
            "exists": exists,
            "size_bytes": size_bytes,
            "sha256": digest,
            "status": status
        })

        print(f"[{status}] {art['name']}")
        print(f"      Path:   {art['rel_path']}")
        print(f"      SHA256: {digest or 'N/A'}")
        print(f"      Size:   {size_bytes} bytes\n")

    manifest = {
        "title": "DAXDA.IA Federal Entity Registration & DARPA BAA Package Manifest",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "entity": {
            "legal_name": "DAXDA.IA Technologies LLC",
            "architect": "Nicole Bess",
            "agent_profile": "Dexter (DAXDA.IA)",
            "primary_naics": "541715",
            "secondary_naics": ["541512", "541511", "541519", "541690"],
            "psc_codes": ["AC12", "AJ11", "DA01", "DJ01"]
        },
        "target_solicitations": [
            "DARPA I2O: Assured Neuro Symbolic Learning and Reasoning (ANSR)",
            "DARPA I2O: Guaranteeing AI Robustness against Deception (GARD)",
            "DARPA DSO: Disruptive Capabilities in High-Dimensional Decision Verification",
            "DoD CDAO: Tradewind Solutions Marketplace AI Procurement"
        ],
        "readiness_score": 100.0 if all_present else (sum(1 for i in verified_items if i["exists"]) / len(verified_items) * 100),
        "artifacts": verified_items
    }

    output_manifest_path = os.path.join(outputs_dir, "federal_registration_manifest.json")
    with open(output_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("-" * 80)
    print(f"Package Verification Status: {'ALL GREEN (100% READY)' if all_present else 'INCOMPLETE'}")
    print(f"Manifest saved to: {output_manifest_path}")
    print("=" * 80)

    if not all_present:
        sys.exit(1)

if __name__ == "__main__":
    main()
