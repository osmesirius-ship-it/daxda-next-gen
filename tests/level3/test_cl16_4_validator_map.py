"""
Unit Tests for DAXDA Cl(16,4) Validator Map & Unified Cross-Domain Bounty Solver
==============================================================================
"""

import pytest
import numpy as np
from daxda_engine.level3.orchestrator import (
    Cl16_4ValidatorMap,
    Cl16_4BountyMapNode,
    Cl16_4MapCertificationReport,
    get_all_20_bounty_definitions,
)


def test_20_bounty_definitions():
    defs = get_all_20_bounty_definitions()
    assert len(defs) == 20, "Must define exactly 20 bounties"

    # Verify domains
    domain_counts = {}
    for d in defs:
        assert len(d.vector_16d) == 16, f"{d.bounty_id} must have 16D vector"
        assert all(0.0 <= x <= 1.0 for x in d.vector_16d), f"{d.bounty_id} has out-of-range values"
        domain_counts[d.domain] = domain_counts.get(d.domain, 0) + 1

    assert len(domain_counts) == 5
    for dom, count in domain_counts.items():
        assert count == 4, f"{dom} must have exactly 4 sub-bounties"


def test_total_payout_pool():
    defs = get_all_20_bounty_definitions()
    total_payout = sum(d.payout_usd for d in defs)
    assert total_payout == 280000.0, f"Expected $280,000 USD, got {total_payout}"


def test_end_to_end_cl16_4_validator_map():
    vmap = Cl16_4ValidatorMap(cluster_workers=4)
    report: Cl16_4MapCertificationReport = vmap.solve_and_map_all()

    assert report.total_bounties == 20
    assert report.certified_bounties == 20
    assert report.certification_rate_pct == 100.0
    assert report.total_payout_usd == 280000.0
    assert report.is_topologically_closed is True
    assert report.graph_algebraic_connectivity_lambda2 > 0.0
    assert len(report.merkle_state_root) == 64

    for node in report.nodes:
        assert isinstance(node, Cl16_4BountyMapNode)
        assert node.certified is True
        assert node.dax_decision == "ACCEPT"
        assert node.dax_stability_score >= 0.75
        assert len(node.cl_indices) == 4
        assert node.temporal_coord["t"] > 0.0
        assert node.validation_latency_ms < 1000.0
        assert len(node.receipt_hash) > 0
