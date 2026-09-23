#!/usr/bin/env python3
"""
DAXDA Cl(16,4) Self-Improvement CLI Tool
=========================================

Runs the Clifford Geometric Algebra Cl(16,4) recursive self-improvement pipeline.
"""

import sys
import os

# Ensure package root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from daxda_engine.cl16_4.recursive_self_improvement import run_recursive_self_improvement

if __name__ == "__main__":
    report = run_recursive_self_improvement()
    print("=" * 60)
    print(" DAXDA Cl(16,4) RECURSIVE SELF-IMPROVEMENT EXECUTION REPORT")
    print("=" * 60)
    print(f"Timestamp:        {report['cycle_timestamp']}")
    print(f"Engine:           {report['engine']}")
    print(f"Blade Dimensions: {report['blade_dimensions']:,}")
    print(f"Git Commit:       {report['git_commit']} (Branch: {report['git_branch']})")
    print(f"Status:           {report['status']}")
    print(f"Proposals:        Total: {report['total_proposals_evaluated']} | Passed: {report['passed_proposals']} | Blocked: {report['blocked_proposals']}")
    print(f"Execution Time:   {report['cycle_duration_ms']} ms")
    print("-" * 60)
    for idx, r in enumerate(report['results'], 1):
        status_icon = "✅" if r['success'] else "❌"
        print(f" [{idx}] {status_icon} {r['proposal_name']} ({r['type']}) -> Actual: {r['actual_outcome']} (Expected: {r['expected']}) | Score: {r['score']:.4f}")
    print("=" * 60)
