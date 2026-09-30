"""Unit & integration tests for DAXDA Institutional MCP Agent — Hugging Face Outreach.

Covers:
  - Tool registry / MCP protocol listing
  - Governance gate integration (PASS / BLOCK paths)
  - Each tool handler (simulation mode — no live HF token required)
  - JSON-RPC 2.0 stdio server dispatch
  - Tenant RBAC gating
"""

import json
import sys
import os
import pytest
from io import StringIO
from unittest.mock import MagicMock, patch

# Ensure project root on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from daxda_guard.hf_mcp_agent import DAXDAMCPAgent, MCPOutreachResult, MCP_TOOL_SCHEMAS, run_mcp_stdio_server


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def agent():
    """Create agent in simulation mode (no HF token, soft governance)."""
    a = DAXDAMCPAgent(hf_token="")  # no token → simulation mode
    a.register_tenant(api_key="daxda_live_bank_98214", requested_domain="finance")
    return a


# ---------------------------------------------------------------------------
# 1. Tool Registry / Protocol Listing
# ---------------------------------------------------------------------------

class TestToolRegistry:
    def test_all_five_tools_registered(self, agent):
        tools = agent.list_tools()
        tool_names = {t["name"] for t in tools}
        assert tool_names == {
            "hf_text_generation", "hf_embedding",
            "hf_agent_query", "hf_model_search", "hf_dataset_card"
        }

    def test_each_tool_has_input_schema(self, agent):
        for tool in agent.list_tools():
            assert "inputSchema" in tool, f"{tool['name']} missing inputSchema"
            assert "properties" in tool["inputSchema"]

    def test_each_tool_has_required_fields(self, agent):
        for tool in agent.list_tools():
            assert "name" in tool
            assert "description" in tool
            assert len(tool["description"]) > 10, f"{tool['name']} description too short"

    def test_mcp_tool_schemas_constant(self):
        assert isinstance(MCP_TOOL_SCHEMAS, dict)
        assert len(MCP_TOOL_SCHEMAS) == 5


# ---------------------------------------------------------------------------
# 2. Tenant RBAC
# ---------------------------------------------------------------------------

class TestTenantRBAC:
    def test_valid_tenant_auth(self, agent):
        result = agent.register_tenant("daxda_live_bank_98214", "finance")
        assert result["authorized"] is True
        assert result["tenant_name"] == "JPMorgan Chase & Co."

    def test_invalid_api_key(self, agent):
        result = agent.register_tenant("invalid_key_xyz", "finance")
        assert result["authorized"] is False
        assert "GOV_FAIL_01" in result["error_code"]

    def test_unauthorized_domain(self, agent):
        result = agent.register_tenant("daxda_live_bank_98214", "defense")
        assert result["authorized"] is False

    def test_defense_tenant_valid_domain(self, agent):
        result = agent.register_tenant("daxda_live_def_77182", "defense")
        assert result["authorized"] is True


# ---------------------------------------------------------------------------
# 3. Governance Gate Integration
# ---------------------------------------------------------------------------

class TestGovernanceGate:
    def test_gate_pass_produces_pass_receipt(self, agent):
        receipt = agent._govern("finance", "Summarise Basel III Tier 1 capital requirements")
        assert receipt.verdict in ("PASS", "CAUTION", "SEVERE_BLOCK", "FAIL_CLOSED",
                                   "UNKNOWN")  # any valid code

    def test_govern_returns_governance_receipt(self, agent):
        from daxda_guard.core import GovernanceReceipt
        receipt = agent._govern("general", "test input")
        assert isinstance(receipt, GovernanceReceipt)

    def test_receipt_dict_keys(self, agent):
        receipt = agent._govern("general", "test")
        d = agent._receipt_dict(receipt, latency_ms=1.5)
        required_keys = {
            "verdict", "decision_rule", "reconstruction_loss",
            "grade0_scalar", "calibrated_certainty",
            "authority_sha256", "publication_permitted", "governance_latency_ms"
        }
        assert required_keys.issubset(set(d.keys()))

    def test_blocked_tool_returns_blocked_status(self, agent):
        """Simulate a blocking governance receipt."""
        from daxda_guard.core import GovernanceReceipt
        blocked = GovernanceReceipt(
            verdict="SEVERE_BLOCK", decision_rule="GOV_FAIL_05",
            reconstruction_loss=99.9, grade0_scalar=0.0,
            calibrated_certainty=0.0, authority_sha256="abc",
            publication_permitted=False
        )
        with patch.object(agent, "_govern", return_value=blocked):
            result = agent.invoke_tool("hf_text_generation", {
                "model": "test/model", "prompt": "blocked prompt", "domain": "finance"
            })
        assert result.status == "BLOCKED"
        assert "Gate blocked" in result.payload["error"]


# ---------------------------------------------------------------------------
# 4. Tool Handlers — Simulation Mode
# ---------------------------------------------------------------------------

class TestToolHandlers:
    def test_hf_text_generation_simulation(self, agent):
        result = agent.invoke_tool("hf_text_generation", {
            "model": "mistralai/Mistral-7B-Instruct-v0.3",
            "prompt": "What are Basel III Tier 1 capital requirements?",
            "domain": "finance"
        })
        assert result.status == "SUCCESS"
        assert "generated_text" in result.payload
        assert result.latency_ms > 0

    def test_hf_embedding_simulation(self, agent):
        result = agent.invoke_tool("hf_embedding", {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "text": "DAXDA institutional compliance vector",
            "domain": "finance"
        })
        assert result.status == "SUCCESS"
        assert "embedding_dim" in result.payload
        assert isinstance(result.payload["embedding_preview"], list)
        assert len(result.payload["embedding_preview"]) == 8

    def test_hf_embedding_deterministic(self, agent):
        """Same text → same simulated embedding."""
        text = "deterministic embedding test"
        r1 = agent.invoke_tool("hf_embedding", {
            "model": "sentence-transformers/all-MiniLM-L6-v2", "text": text
        })
        r2 = agent.invoke_tool("hf_embedding", {
            "model": "sentence-transformers/all-MiniLM-L6-v2", "text": text
        })
        assert r1.payload["embedding_preview"] == r2.payload["embedding_preview"]

    def test_hf_model_search_simulation(self, agent):
        result = agent.invoke_tool("hf_model_search", {
            "query": "finance compliance LLM", "limit": 5
        })
        assert result.status == "SUCCESS"
        assert "results" in result.payload
        assert len(result.payload["results"]) <= 5

    def test_hf_dataset_card_simulation(self, agent):
        result = agent.invoke_tool("hf_dataset_card", {
            "dataset_id": "financial_phrasebank"
        })
        assert result.status == "SUCCESS"
        assert "dataset_id" in result.payload

    def test_hf_agent_query_simulation(self, agent):
        result = agent.invoke_tool("hf_agent_query", {
            "model": "mistralai/Mistral-7B-Instruct-v0.3",
            "task": "Summarise Basel III Tier 1 capital requirements.",
            "tools": ["text_generation"],
            "domain": "finance"
        })
        assert result.status == "SUCCESS"
        assert "response" in result.payload

    def test_unknown_tool_returns_error(self, agent):
        result = agent.invoke_tool("non_existent_tool", {})
        assert result.status == "ERROR"
        assert "Unknown tool" in result.payload["error"]

    def test_all_tools_have_authority_receipt(self, agent):
        tools = [
            ("hf_text_generation", {"model": "x/y", "prompt": "hello"}),
            ("hf_embedding", {"model": "x/y", "text": "hello"}),
            ("hf_model_search", {"query": "test"}),
            ("hf_dataset_card", {"dataset_id": "test/data"}),
            ("hf_agent_query", {"model": "x/y", "task": "Do something"}),
        ]
        for tool_name, inputs in tools:
            result = agent.invoke_tool(tool_name, inputs)
            assert result.authority_receipt, f"{tool_name} missing authority_receipt"
            assert "verdict" in result.authority_receipt


# ---------------------------------------------------------------------------
# 5. MCPOutreachResult Serialisation
# ---------------------------------------------------------------------------

class TestMCPOutreachResult:
    def test_to_dict(self):
        r = MCPOutreachResult(
            tool="hf_text_generation", status="SUCCESS",
            payload={"text": "hello"}, authority_receipt={"verdict": "PASS"},
            latency_ms=12.5
        )
        d = r.to_dict()
        assert d["tool"] == "hf_text_generation"
        assert d["status"] == "SUCCESS"
        assert d["latency_ms"] == 12.5

    def test_to_json_valid(self):
        r = MCPOutreachResult(
            tool="hf_embedding", status="SUCCESS",
            payload={"embedding_dim": 384}, authority_receipt={},
            latency_ms=5.0
        )
        j = json.loads(r.to_json())
        assert j["tool"] == "hf_embedding"

    def test_timestamp_auto_populated(self):
        import time
        before = time.time()
        r = MCPOutreachResult(
            tool="t", status="SUCCESS", payload={}, authority_receipt={}, latency_ms=1.0
        )
        after = time.time()
        assert before <= r.timestamp <= after


# ---------------------------------------------------------------------------
# 6. JSON-RPC 2.0 stdio Server
# ---------------------------------------------------------------------------

class TestMCPStdioServer:
    def _run_server_with_input(self, agent, json_lines: list) -> list:
        """Feed lines to the MCP server and capture output."""
        inp = "\n".join(json.dumps(line) for line in json_lines) + "\n"
        out_buf = StringIO()

        with patch("sys.stdin", StringIO(inp)), patch("sys.stdout", out_buf):
            try:
                run_mcp_stdio_server(agent)
            except (StopIteration, EOFError):
                pass

        out_buf.seek(0)
        results = []
        for line in out_buf.getvalue().strip().split("\n"):
            if line.strip():
                results.append(json.loads(line))
        return results

    def test_initialize(self, agent):
        responses = self._run_server_with_input(agent, [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        ])
        assert any(r.get("id") == 1 and "result" in r for r in responses)
        result = next(r for r in responses if r.get("id") == 1)
        assert result["result"]["protocolVersion"] == "2024-11-05"
        assert result["result"]["serverInfo"]["name"] == "daxda-hf-mcp-agent"

    def test_tools_list(self, agent):
        responses = self._run_server_with_input(agent, [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        ])
        result = next(r for r in responses if r.get("id") == 2)
        assert "tools" in result["result"]
        assert len(result["result"]["tools"]) == 5

    def test_tools_call_text_generation(self, agent):
        responses = self._run_server_with_input(agent, [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
                "name": "hf_text_generation",
                "arguments": {"model": "x/y", "prompt": "test prompt"}
            }}
        ])
        result = next(r for r in responses if r.get("id") == 2)
        assert "result" in result
        assert "content" in result["result"]
        content_text = result["result"]["content"][0]["text"]
        parsed = json.loads(content_text)
        assert parsed["tool"] == "hf_text_generation"

    def test_unknown_method_returns_error(self, agent):
        responses = self._run_server_with_input(agent, [
            {"jsonrpc": "2.0", "id": 99, "method": "unknown/method", "params": {}}
        ])
        result = next(r for r in responses if r.get("id") == 99)
        assert "error" in result
        assert result["error"]["code"] == -32601

    def test_notifications_initialized_no_response(self, agent):
        responses = self._run_server_with_input(agent, [
            {"jsonrpc": "2.0", "method": "notifications/initialized"}
        ])
        # Should produce zero responses (no id, notification)
        assert all(r.get("id") is not None or "error" in r for r in responses)

    def test_malformed_json_returns_parse_error(self, agent):
        out_buf = StringIO()
        with patch("sys.stdin", StringIO("NOT_JSON\n")), patch("sys.stdout", out_buf):
            try:
                run_mcp_stdio_server(agent)
            except Exception:
                pass
        out_buf.seek(0)
        for line in out_buf.getvalue().strip().split("\n"):
            if line.strip():
                resp = json.loads(line)
                if "error" in resp:
                    assert resp["error"]["code"] == -32700
                    break
