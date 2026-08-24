#!/usr/bin/env python3
"""
DAXDA Item Response Theory (IRT) Benchmark Diagnostics (irt_benchmark_diagnostics.py)
===================================================================================
Diagnostic-only psychometric evaluation module for safety benchmark items:
  - Difficulty parameter (\beta_i)
  - Discrimination parameter (\alpha_i)
  - Item redundancy & cross-correlation
  - Subgroup loading across risk families

CRITICAL RULE:
  IRT metrics are advisory/diagnostic ONLY. They do NOT alter zero-tolerance release
  thresholds or remove critical safety test cases from the evaluation suite.
"""

from __future__ import annotations
import math
import json
import os
from typing import Dict, List, Any


def compute_irt_item_parameters(responses: List[int]) -> Dict[str, float]:
    """
    Computes 2-Parameter Logistic (2PL) Item Response Theory approximations:
      P(theta) = 1 / (1 + exp(-alpha * (theta - beta)))
    Where:
      - beta: Difficulty (higher = harder for model/governance gate)
      - alpha: Discrimination (higher = stronger separation between pass/fail)
    """
    N = len(responses)
    if N == 0:
        return {"difficulty": 0.0, "discrimination": 0.0, "redundancy": 0.0}

    pass_rate = sum(responses) / N
    # Approximate difficulty: logit of failure rate
    fail_rate = 1.0 - pass_rate
    if pass_rate == 0 or pass_rate == 1.0:
        difficulty = 3.0 if pass_rate == 0 else -3.0
        discrimination = 1.0
    else:
        difficulty = round(math.log(fail_rate / pass_rate), 4)
        discrimination = round(1.5 + 2.0 * math.sqrt(pass_rate * fail_rate), 4)

    # Redundancy metric based on extreme invariance
    redundancy = 1.0 if pass_rate in (0.0, 1.0) else round(1.0 - 4.0 * pass_rate * fail_rate, 4)

    return {
        "difficulty_beta": difficulty,
        "discrimination_alpha": discrimination,
        "redundancy_index": redundancy,
        "pass_rate": round(pass_rate, 4)
    }


def analyze_benchmark_psychometrics(benchmark_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    item_diagnostics = {}
    family_loadings = {}

    for item in benchmark_items:
        item_id = item.get("item_id", "ITEM-001")
        family = item.get("family", "GENERAL")
        responses = item.get("responses", [1, 1, 0, 1, 0, 1])

        params = compute_irt_item_parameters(responses)
        params["criticality_class"] = item.get("criticality_class", "CRITICAL_ZERO_TOLERANCE")
        item_diagnostics[item_id] = params

        if family not in family_loadings:
            family_loadings[family] = []
        family_loadings[family].append(params["difficulty_beta"])

    family_summary = {}
    for fam, diffs in family_loadings.items():
        family_summary[fam] = {
            "mean_difficulty": round(sum(diffs) / len(diffs), 4),
            "item_count": len(diffs)
        }

    return {
        "diagnostic_type": "2PL_IRT_PSYCHOMETRIC_AUDIT",
        "advisory_notice": "Diagnostic only. Zero-tolerance safety thresholds remain 100% frozen.",
        "total_items_analyzed": len(benchmark_items),
        "family_loadings": family_summary,
        "item_details": item_diagnostics
    }


def main():
    print("=" * 80)
    print("DAXDA IRT Benchmark Diagnostics Engine")
    print("=" * 80)

    # Synthetic sample of 100 benchmark items across families
    sample_items = []
    families = ["BENIGN_LONG_HORIZON", "MULTI_STEP_INDIRECT_INJECTION", "AUTHORITY_ESCALATION_PROBING", "ENVIRONMENT_TOOL_MANIPULATION"]
    
    for i in range(1, 101):
        fam = families[i % 4]
        # Simulate model evaluation responses
        resp = [1 if i % 2 == 0 else 0 for _ in range(10)]
        sample_items.append({
            "item_id": f"ITEM-{i:03d}",
            "family": fam,
            "criticality_class": "CRITICAL_ZERO_TOLERANCE" if fam != "BENIGN_LONG_HORIZON" else "BENIGN_BASELINE",
            "responses": resp
        })

    report = analyze_benchmark_psychometrics(sample_items)
    print(json.dumps(report, indent=2))

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../audit_reports"))
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "irt_benchmark_psychometrics_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nIRT Psychometrics Report written to: {out_path}")


if __name__ == "__main__":
    main()
