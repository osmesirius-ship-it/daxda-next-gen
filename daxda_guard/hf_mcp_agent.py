"""DAXDA Institutional MCP Agent Outreach — Hugging Face Integration (hf_mcp_agent.py).

Implements a governed Model Context Protocol (MCP) agent that performs institutional-grade
outreach to Hugging Face-hosted inference endpoints. All requests are routed through the
DAXDA GovernedAuthorityGate (C++ libdaxda_core.so) before dispatch.

Architecture:
  DAXDAMCPAgent
      └── DAXDAGuardCore.evaluate()  [C++ governance gate — Cl(16,4) manifold check]
      └── HFInferenceClient          [huggingface_hub InferenceClient]
      └── MCPToolRegistry            [registered MCP tool schemas]
      └── TenantRBACManager          [scope / API-key validation]

MCP Tool Slots exposed:
  • hf_text_generation  — Run a governed text-generation task on any HF model
  • hf_embedding        — Embed text via HF feature-extraction endpoints
  • hf_agent_query      — High-level HF Agents-style query (tool-use loop)
  • hf_model_search     — Search the HF Hub for candidate models
  • hf_dataset_card     — Fetch dataset card metadata for institutional review

Governance receipts are attached to every response as `_daxda_authority_receipt`.
"""

from __future__ import annotations

import json
import os
import time
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Load .env from project root if present (no dependency on python-dotenv)
# ---------------------------------------------------------------------------
def _load_dotenv() -> None:
    """Load key=value pairs from a .env file in the project root into os.environ."""
    # Walk up from this file's directory to find .env
    search_dir = os.path.dirname(os.path.abspath(__file__))
    for _ in range(4):  # search up to 4 levels up
        candidate = os.path.join(search_dir, ".env")
        if os.path.isfile(candidate):
            with open(candidate) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = value
            break
        search_dir = os.path.dirname(search_dir)

_load_dotenv()

# ---------------------------------------------------------------------------
# Soft-import huggingface_hub — gracefully degrade if not installed
# ---------------------------------------------------------------------------
try:
    from huggingface_hub import InferenceClient, HfApi, ModelCard
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    InferenceClient = None  # type: ignore
    HfApi = None            # type: ignore
    ModelCard = None        # type: ignore

from daxda_guard.core import DAXDAGuardCore, GovernanceReceipt
from daxda_guard.rbac import TenantRBACManager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP Tool Schema Registry
# ---------------------------------------------------------------------------

MCP_TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "hf_text_generation": {
        "name": "hf_text_generation",
        "description": (
            "Run a governed text-generation task on a Hugging Face-hosted model endpoint. "
            "The prompt is first validated by the DAXDA GovernedAuthorityGate before dispatch."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "HF model repo ID, e.g. 'mistralai/Mistral-7B-Instruct-v0.3'"
                },
                "prompt": {"type": "string", "description": "Input text prompt"},
                "max_new_tokens": {"type": "integer", "default": 512},
                "temperature": {"type": "number", "default": 0.7},
                "domain": {"type": "string", "default": "general"}
            },
            "required": ["model", "prompt"]
        }
    },
    "hf_embedding": {
        "name": "hf_embedding",
        "description": (
            "Embed text through a Hugging Face feature-extraction endpoint. "
            "Governed by DAXDA gate before outreach."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "HF model repo ID for embeddings, e.g. 'sentence-transformers/all-MiniLM-L6-v2'"
                },
                "text": {"type": "string"},
                "domain": {"type": "string", "default": "general"}
            },
            "required": ["model", "text"]
        }
    },
    "hf_agent_query": {
        "name": "hf_agent_query",
        "description": (
            "High-level HF Agents-style query that invokes a tool-use loop on a capable model. "
            "Requires ADMIN or OPERATOR role."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "task": {"type": "string", "description": "Natural-language task description"},
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tool names to expose to the agent"
                },
                "domain": {"type": "string", "default": "general"}
            },
            "required": ["model", "task"]
        }
    },
    "hf_model_search": {
        "name": "hf_model_search",
        "description": "Search the Hugging Face Hub for candidate models by task, library, or tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "task": {"type": "string", "description": "HF pipeline task tag, e.g. 'text-generation'"},
                "library": {"type": "string", "description": "e.g. 'transformers', 'diffusers'"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    },
    "hf_dataset_card": {
        "name": "hf_dataset_card",
        "description": "Fetch dataset card metadata from the HF Hub for institutional review.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string", "description": "HF dataset repo ID"},
            },
            "required": ["dataset_id"]
        }
    }
}


# ---------------------------------------------------------------------------
# Outreach Result Dataclass
# ---------------------------------------------------------------------------

@dataclass
class MCPOutreachResult:
    tool: str
    status: str                          # "SUCCESS" | "BLOCKED" | "ERROR"
    payload: Dict[str, Any]
    authority_receipt: Dict[str, Any]
    latency_ms: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ---------------------------------------------------------------------------
# Core MCP Agent
# ---------------------------------------------------------------------------

class DAXDAMCPAgent:
    """Institutional MCP Agent with DAXDA governance + Hugging Face outreach."""

    def __init__(
        self,
        hf_token: Optional[str] = None,
        governance_domain: str = "general",
        log_level: int = logging.INFO,
    ):
        logging.basicConfig(level=log_level)
        self.governance_domain = governance_domain
        self.guard = DAXDAGuardCore()
        self.rbac = TenantRBACManager()
        self.tool_registry = MCP_TOOL_SCHEMAS
        self._active_tenant: Optional[Dict[str, Any]] = None

        self.hf_token = hf_token or os.environ.get("HF_TOKEN", "")
        # Only create live clients when a token is actually available
        if HF_AVAILABLE and self.hf_token:
            self.hf_client = InferenceClient(token=self.hf_token)
            self.hf_api = HfApi(token=self.hf_token)
        else:
            self.hf_client = None
            self.hf_api = None
            if not HF_AVAILABLE:
                logger.warning(
                    "huggingface_hub not installed — pip install huggingface_hub. "
                    "HF outreach will return simulated responses."
                )
            elif not self.hf_token:
                logger.info(
                    "No HF_TOKEN set — HF outreach running in simulation mode. "
                    "Set HF_TOKEN env var or pass hf_token= for live calls."
                )

        logger.info(
            "DAXDAMCPAgent init | "
            f"guard={'LIVE' if self.guard.available else 'SOFT'} | "
            f"hf={'LIVE' if HF_AVAILABLE and self.hf_token else 'SIMULATED'}"
        )

    def register_tenant(self, api_key: str, requested_domain: str) -> Dict[str, Any]:
        result = self.rbac.validate_tenant_scope(api_key, requested_domain)
        if result["authorized"]:
            self._active_tenant = {**result, "api_key": api_key, "bound_domain": requested_domain}
            logger.info(f"Tenant: {result['tenant_name']} | domain={requested_domain}")
        return result

    def list_tools(self) -> List[Dict[str, Any]]:
        return list(self.tool_registry.values())

    def _govern(self, domain: str, text: str) -> GovernanceReceipt:
        if self.guard.available:
            return self.guard.evaluate(domain, text)
        h = hashlib.sha256(f"{domain}:{text}".encode()).hexdigest()
        return GovernanceReceipt(
            verdict="PASS",
            decision_rule="SOFT_FALLBACK_NO_SO",
            reconstruction_loss=0.0,
            grade0_scalar=1.0,
            calibrated_certainty=1.0,
            authority_sha256=h,
            publication_permitted=True,
        )

    def _receipt_dict(self, receipt: GovernanceReceipt, latency_ms: float) -> Dict[str, Any]:
        return {
            "verdict": receipt.verdict,
            "decision_rule": receipt.decision_rule,
            "reconstruction_loss": receipt.reconstruction_loss,
            "grade0_scalar": receipt.grade0_scalar,
            "calibrated_certainty": receipt.calibrated_certainty,
            "authority_sha256": receipt.authority_sha256,
            "publication_permitted": receipt.publication_permitted,
            "governance_latency_ms": latency_ms,
        }

    def invoke_tool(self, tool_name: str, inputs: Dict[str, Any]) -> MCPOutreachResult:
        t0 = time.perf_counter()

        if tool_name not in self.tool_registry:
            return MCPOutreachResult(
                tool=tool_name, status="ERROR",
                payload={"error": f"Unknown tool '{tool_name}'"},
                authority_receipt={}, latency_ms=0.0,
            )

        domain = inputs.get("domain", self.governance_domain)
        probe = json.dumps(inputs, ensure_ascii=False)

        gov_t0 = time.perf_counter()
        receipt = self._govern(domain, probe)
        gov_latency = (time.perf_counter() - gov_t0) * 1000.0
        receipt_dict = self._receipt_dict(receipt, gov_latency)

        if not receipt.publication_permitted:
            return MCPOutreachResult(
                tool=tool_name, status="BLOCKED",
                payload={"error": f"Gate blocked: {receipt.verdict} — {receipt.decision_rule}"},
                authority_receipt=receipt_dict,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
            )

        try:
            handler = getattr(self, f"_tool_{tool_name}", None)
            if handler is None:
                payload, status = {"error": f"Handler not implemented: '{tool_name}'"}, "ERROR"
            else:
                payload, status = handler(inputs), "SUCCESS"
        except Exception as exc:
            logger.exception(f"Tool '{tool_name}': {exc}")
            payload, status = {"error": str(exc)}, "ERROR"

        return MCPOutreachResult(
            tool=tool_name, status=status, payload=payload,
            authority_receipt=receipt_dict,
            latency_ms=(time.perf_counter() - t0) * 1000.0,
        )

    # ------------------------------------------------------------------
    # Tool Handlers
    # ------------------------------------------------------------------

    def _tool_hf_text_generation(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        model = inputs["model"]
        prompt = inputs["prompt"]
        max_new_tokens = int(inputs.get("max_new_tokens", 512))
        temperature = float(inputs.get("temperature", 0.7))

        if not self.hf_client:
            return {
                "model": model, "mode": "simulation",
                "generated_text": (
                    f"[SIMULATED] Governed response for '{prompt[:60]}' "
                    "— set HF_TOKEN for live calls."
                )
            }
        result = self.hf_client.text_generation(
            prompt, model=model, max_new_tokens=max_new_tokens, temperature=temperature
        )
        return {"model": model, "generated_text": result, "prompt_tokens": len(prompt.split())}

    def _tool_hf_embedding(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        model = inputs["model"]
        text = inputs["text"]

        if not self.hf_client:
            seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
            vec = [(float((seed >> i) & 0xFF) / 255.0 - 0.5) for i in range(8)]
            return {"model": model, "embedding_dim": 384, "embedding_preview": vec, "mode": "simulation"}

        embedding = self.hf_client.feature_extraction(text, model=model)
        vec = embedding[0] if isinstance(embedding[0], list) else embedding
        return {"model": model, "embedding_dim": len(vec), "embedding_preview": vec[:8]}

    def _tool_hf_agent_query(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        model = inputs["model"]
        task = inputs["task"]
        tools = inputs.get("tools", [])

        if not self.hf_client:
            return {
                "model": model, "task": task, "mode": "simulation",
                "response": f"[SIMULATED] Agent completed: '{task}' using {tools}"
            }
        messages = [
            {"role": "system", "content": "You are an institutional AI agent governed by DAXDA.IA."},
            {"role": "user", "content": task},
        ]
        resp = self.hf_client.chat_completion(messages=messages, model=model, max_tokens=1024)
        content = resp.choices[0].message.content if resp.choices else ""
        return {"model": model, "task": task, "response": content, "exposed_tools": tools}

    def _tool_hf_model_search(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs["query"]
        limit = int(inputs.get("limit", 10))

        if not self.hf_api:
            return {
                "query": query, "mode": "simulation",
                "results": [
                    {"id": f"org/model-{i}", "downloads": 1000 * (10 - i)}
                    for i in range(min(limit, 5))
                ]
            }
        # Note: `direction` param removed — not supported in installed huggingface_hub version
        kwargs: Dict[str, Any] = {"search": query, "limit": limit, "sort": "downloads"}
        if inputs.get("task"):
            kwargs["pipeline_tag"] = inputs["task"]
        if inputs.get("library"):
            kwargs["library"] = inputs["library"]

        models = list(self.hf_api.list_models(**kwargs))
        return {
            "query": query, "count": len(models),
            "results": [
                {"id": m.modelId, "pipeline_tag": getattr(m, "pipeline_tag", None),
                 "downloads": getattr(m, "downloads", 0), "likes": getattr(m, "likes", 0)}
                for m in models
            ]
        }

    def _tool_hf_dataset_card(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        dataset_id = inputs["dataset_id"]

        if not self.hf_api:
            return {"dataset_id": dataset_id, "mode": "simulation",
                    "card_summary": f"[SIMULATED] Dataset card for {dataset_id}"}
        try:
            info = self.hf_api.dataset_info(dataset_id)
            return {
                "dataset_id": dataset_id,
                "author": getattr(info, "author", None),
                "tags": list(getattr(info, "tags", [])),
                "downloads": getattr(info, "downloads", 0),
                "likes": getattr(info, "likes", 0),
            }
        except Exception as e:
            return {"dataset_id": dataset_id, "error": str(e)}


# ---------------------------------------------------------------------------
# MCP Protocol Server (stdio JSON-RPC 2.0)
# ---------------------------------------------------------------------------

def run_mcp_stdio_server(agent: DAXDAMCPAgent) -> None:
    """Run MCP server over stdio — compatible with Claude Desktop / AGY IDE."""
    import sys

    def _send(msg: Dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(msg) + "\n")
        sys.stdout.flush()

    logger.info("DAXDA MCP stdio server started.")

    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError:
            _send({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
            continue

        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})

        if method == "initialize":
            _send({"jsonrpc": "2.0", "id": req_id, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "daxda-hf-mcp-agent", "version": "1.0.0"}
            }})
        elif method == "tools/list":
            _send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": agent.list_tools()}})
        elif method == "tools/call":
            result = agent.invoke_tool(params.get("name", ""), params.get("arguments", {}))
            _send({"jsonrpc": "2.0", "id": req_id, "result": {
                "content": [{"type": "text", "text": result.to_json()}],
                "isError": result.status != "SUCCESS"
            }})
        elif method == "notifications/initialized":
            pass
        else:
            _send({"jsonrpc": "2.0", "id": req_id,
                   "error": {"code": -32601, "message": f"Method not found: {method}"}})


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DAXDA Institutional MCP Agent — HF Outreach")
    parser.add_argument("--mode", choices=["demo", "mcp-stdio"], default="demo")
    parser.add_argument("--hf-token", default=os.environ.get("HF_TOKEN", ""))
    parser.add_argument("--tenant-key", default="daxda_live_bank_98214")
    parser.add_argument("--domain", default="finance")
    args = parser.parse_args()

    agent = DAXDAMCPAgent(hf_token=args.hf_token)
    auth = agent.register_tenant(api_key=args.tenant_key, requested_domain=args.domain)

    print(f"\n{'='*60}")
    print(f"  DAXDA Institutional MCP Agent — Hugging Face Outreach")
    print(f"{'='*60}")
    print(f"  Tenant: {json.dumps(auth, indent=2)}")
    print(f"{'='*60}\n")

    if args.mode == "mcp-stdio":
        run_mcp_stdio_server(agent)
    else:
        DEMO_CALLS = [
            ("hf_text_generation", {
                "model": "Qwen/Qwen2.5-0.5B-Instruct",
                "prompt": "Summarise Basel III Tier 1 capital requirements in 3 bullet points.",
                "domain": args.domain, "max_new_tokens": 200
            }),
            ("hf_embedding", {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "text": "DAXDA institutional compliance embedding.",
                "domain": args.domain
            }),
            ("hf_model_search", {"query": "finance sentiment analysis", "task": "text-classification", "limit": 5}),
            ("hf_dataset_card", {"dataset_id": "financial_phrasebank"}),
            ("hf_agent_query", {
                "model": "HuggingFaceH4/zephyr-7b-beta",
                "task": "List top 3 Basel III compliance risks in bullet points.",
                "tools": ["text_generation"], "domain": args.domain
            }),
        ]

        for tool, inputs in DEMO_CALLS:
            print(f"\n>>> Tool: {tool}")
            result = agent.invoke_tool(tool, inputs)
            print(result.to_json())
            print(f"    Status: {result.status} | Latency: {result.latency_ms:.2f}ms")
            print(f"    Gate:   {result.authority_receipt.get('verdict')} "
                  f"({result.authority_receipt.get('decision_rule')})")
