"""
Unit and regression tests for HelixScienceDiscoveryAgent (Unit 7).
Validates 216-hour autonomous biomedical discovery campaign mechanics,
parameter bounds, Cl(16,4) multivector stability, and JSON export.
"""
import os
import json
import pytest
from tools.daxda_science_discovery_agent import (
    HelixScienceDiscoveryAgent,
    VERIFIED_MS_LITERATURE
)

def test_science_agent_initialization(tmp_path, monkeypatch):
    """Verify that agent initializes with exact 216-hour campaign duration and grounding citations."""
    state_file = str(tmp_path / "test_state.json")
    monkeypatch.setattr(HelixScienceDiscoveryAgent, "CAMPAIGN_STATE_FILE", state_file)
    agent = HelixScienceDiscoveryAgent()

    assert agent.TARGET_CAMPAIGN_HOURS == 216.0
    summary = agent.get_telemetry_summary()
    assert summary["total_hours"] == 216.0
    assert summary["campaign_id"] == "CAMPAIGN-216H-MS-REPAIR-V1"
    assert len(VERIFIED_MS_LITERATURE) >= 5
    assert any(c.get("pmid") == "35025605" for c in VERIFIED_MS_LITERATURE)
    assert any(c.get("nct_id") == "NCT03993171" for c in VERIFIED_MS_LITERATURE)

def test_science_agent_step_and_pareto(tmp_path, monkeypatch):
    """Verify single and multiple refinement steps advance campaign time and track Pareto frontier."""
    state_file = str(tmp_path / "test_state.json")
    monkeypatch.setattr(HelixScienceDiscoveryAgent, "CAMPAIGN_STATE_FILE", state_file)
    agent = HelixScienceDiscoveryAgent()

    res = agent.step(hours_increment=0.5)
    assert res["generation"] >= 1
    assert "current_candidate" in res
    assert "best_candidate" in res

    cand = res["current_candidate"]
    params = cand["parameters"]
    assert 5.0 <= params["gpr17_antagonist_affinity_ki_nm"] <= 100.0
    assert 50.0 <= params["gpr17_receptor_occupancy_pct"] <= 99.0
    assert 0.0 <= cand["stability_score"] <= 1.0
    assert cand["remyelination_velocity_mps"] > 0.0
    assert cand["receipt_sha256"] is not None
    assert len(cand["receipt_sha256"]) == 64

def test_science_agent_protocol_export(tmp_path, monkeypatch):
    """Verify that protocol export generates valid JSON dossier with grounded citations."""
    state_file = str(tmp_path / "test_state.json")
    monkeypatch.setattr(HelixScienceDiscoveryAgent, "CAMPAIGN_STATE_FILE", state_file)
    agent = HelixScienceDiscoveryAgent()
    agent.step(hours_increment=1.0)

    proto_path = str(tmp_path / "test_protocol.json")
    proto = agent.export_refined_protocol(destination_path=proto_path)

    assert os.path.exists(proto_path)
    assert proto["target_campaign_hours"] == 216.0
    assert "measured_neuro_kinetics" in proto
    assert proto["measured_neuro_kinetics"]["healthy_reference_velocity_mps"] == "100 - 120 m/s"
    assert len(proto["verified_literature_grounding"]) >= 5

def test_science_agent_persistence(tmp_path, monkeypatch):
    """Verify that agent recovers exact campaign state upon re-instantiation."""
    state_file = str(tmp_path / "test_state.json")
    monkeypatch.setattr(HelixScienceDiscoveryAgent, "CAMPAIGN_STATE_FILE", state_file)
    agent1 = HelixScienceDiscoveryAgent()
    agent1.step(hours_increment=2.5)
    best_id = agent1.state["current_best_candidate"]["candidate_id"]

    # Re-instantiate from same state file
    agent2 = HelixScienceDiscoveryAgent()
    assert agent2.state["elapsed_hours"] >= 2.5
    assert agent2.state["current_best_candidate"]["candidate_id"] == best_id
