#!/usr/bin/env python3
"""
DAXDA MCP Server
Exposes DA13 governance tools so Claude can call them directly.

Tools exposed:
  - daxda_guard_check   : run DA13 governance gate on any text
  - daxda_run_cycle     : execute the Cl(16,4) RSI cycle (FastAPI /run-cycle)
  - daxda_full_query    : govern input → call Claude API → govern output

Usage:
  python mcp_server.py                # stdio transport (Claude Desktop / claude CLI)
  python mcp_server.py --port 3010    # SSE transport (web / remote)

Env vars required for daxda_full_query:
  ANTHROPIC_API_KEY   : your Anthropic key
  DAXDA_DEFAULT_MODEL : default claude model (optional, default claude-sonnet-4-6)
  DAXDA_API_BASE_URL  : DAXDA FastAPI base URL (optional, default http://localhost:8000)
"""

import argparse
import json
import os
import sys
import asyncio
from typing import Any

try:
    import anthropic
except ImportError:
    anthropic = None  # only needed for daxda_full_query

try:
    import httpx
except ImportError:
    httpx = None

# ---------------------------------------------------------------------------
# DAXDA Guard — inline import (repo must be on PYTHONPATH or run from repo root)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from daxda_guard.core import DAXDAGuardCore
    _guard = DAXDAGuardCore()
    _guard_available = getattr(_guard, "available", True)
except Exception as _e:
    _guard = None
    _guard_available = False
    _guard_error = str(_e)

# ---------------------------------------------------------------------------
# MCP primitives (pure-Python, no dependency required)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "daxda_guard_check",
        "description": (
            "Run the DAXDA DA13 governance gate on a piece of text. "
            "Returns verdict (PASS / CAUTION / SEVERE_BLOCK / FAIL_CLOSED), "
            "reconstruction_loss, calibrated_certainty, decision_rule, and "
            "publication_permitted. Use this before passing any text to an LLM "
            "or publishing output."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to evaluate."},
                "domain": {
                    "type": "string",
                    "description": "Governance domain tag (e.g. 'medical', 'finance', 'general').",
                    "default": "general"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "daxda_run_cycle",
        "description": (
            "Execute one Cl(16,4) Recursive Self-Improvement cycle on the DAXDA engine "
            "(POST /run-cycle on the FastAPI server). Returns passed_proposals, "
            "blocked_proposals, cycle_duration_ms."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "base_url": {
                    "type": "string",
                    "description": "DAXDA FastAPI base URL.",
                    "default": "http://localhost:8000"
                }
            },
            "required": []
        }
    },
    {
        "name": "daxda_full_query",
        "description": (
            "Governed end-to-end query: (1) DA13 gate checks the prompt, "
            "(2) if approved, calls Claude API, (3) DA13 gate checks the response. "
            "Returns the governed Claude response plus both authority receipts. "
            "Requires ANTHROPIC_API_KEY env var."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "User message to send through the governed pipeline."},
                "domain": {
                    "type": "string",
                    "description": "Governance domain tag.",
                    "default": "general"
                },
                "model": {
                    "type": "string",
                    "description": "Claude model to use.",
                    "default": "claude-sonnet-4-6"
                },
                "system": {
                    "type": "string",
                    "description": "Optional system prompt.",
                    "default": ""
                }
            },
            "required": ["prompt"]
        }
    }
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _guard_check(text: str, domain: str = "general") -> dict:
    if not _guard_available:
        return {
            "error": f"DAXDAGuardCore unavailable: {_guard_error if '_guard_error' in dir() else 'unknown'}",
            "publication_permitted": False
        }
    rcpt = _guard.evaluate(domain, text)
    return {
        "verdict": rcpt.verdict,
        "decision_rule": rcpt.decision_rule,
        "reconstruction_loss": rcpt.reconstruction_loss,
        "grade0_scalar": rcpt.grade0_scalar,
        "calibrated_certainty": rcpt.calibrated_certainty,
        "authority_sha256": rcpt.authority_sha256,
        "publication_permitted": rcpt.publication_permitted
    }


def _run_cycle(base_url: str = "http://localhost:8000") -> dict:
    if httpx is None:
        return {"error": "httpx not installed — run: pip install httpx"}
    try:
        import httpx as _httpx
        r = _httpx.post(f"{base_url.rstrip('/')}/run-cycle", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _full_query(
    prompt: str,
    domain: str = "general",
    model: str = None,
    system: str = ""
) -> dict:
    if anthropic is None:
        return {"error": "anthropic SDK not installed — run: pip install anthropic"}
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY env var not set"}

    model = model or os.environ.get("DAXDA_DEFAULT_MODEL", "claude-sonnet-4-6")

    # --- Gate 1: govern the input prompt ---
    input_receipt = _guard_check(prompt, domain)
    if not input_receipt.get("publication_permitted", False):
        return {
            "stage": "INPUT_BLOCKED",
            "input_receipt": input_receipt,
            "output": None,
            "output_receipt": None
        }

    # --- Call Claude API ---
    try:
        client = anthropic.Anthropic(api_key=api_key)
        messages = [{"role": "user", "content": prompt}]
        kwargs = {"model": model, "max_tokens": 4096, "messages": messages}
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        raw_text = response.content[0].text if response.content else ""
    except Exception as e:
        return {"error": f"Claude API call failed: {e}"}

    # --- Gate 2: govern the output ---
    output_receipt = _guard_check(raw_text, domain)
    if not output_receipt.get("publication_permitted", False):
        return {
            "stage": "OUTPUT_BLOCKED",
            "input_receipt": input_receipt,
            "output": None,
            "output_receipt": output_receipt
        }

    return {
        "stage": "PASS",
        "input_receipt": input_receipt,
        "output": raw_text,
        "output_receipt": output_receipt,
        "model": model,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }


def call_tool(name: str, args: dict) -> Any:
    if name == "daxda_guard_check":
        return _guard_check(args["text"], args.get("domain", "general"))
    elif name == "daxda_run_cycle":
        return _run_cycle(args.get("base_url", "http://localhost:8000"))
    elif name == "daxda_full_query":
        return _full_query(
            args["prompt"],
            args.get("domain", "general"),
            args.get("model"),
            args.get("system", "")
        )
    else:
        return {"error": f"Unknown tool: {name}"}


# ---------------------------------------------------------------------------
# MCP stdio transport (JSON-RPC 2.0)
# ---------------------------------------------------------------------------

def handle_request(req: dict) -> dict:
    method = req.get("method", "")
    req_id = req.get("id")

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, msg):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": msg}}

    if method == "initialize":
        return ok({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "daxda-mcp", "version": "1.0.0"}
        })

    if method == "tools/list":
        return ok({"tools": TOOLS})

    if method == "tools/call":
        params = req.get("params", {})
        name = params.get("name", "")
        args = params.get("arguments", {})
        try:
            result = call_tool(name, args)
            return ok({
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            })
        except Exception as e:
            return err(-32603, str(e))

    if method == "notifications/initialized":
        return None  # no response for notifications

    return err(-32601, f"Method not found: {method}")


def run_stdio():
    """Run MCP server on stdin/stdout (Claude Desktop / claude CLI mode)."""
    import io
    stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

    while True:
        line = stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_request(req)
        if resp is not None:
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()


def run_sse(port: int):
    """Run MCP server with SSE transport (FastAPI-based)."""
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import StreamingResponse, JSONResponse
        import uvicorn
    except ImportError:
        print("FastAPI/uvicorn required for SSE mode: pip install fastapi uvicorn", file=sys.stderr)
        sys.exit(1)

    app_sse = FastAPI(title="DAXDA MCP Server")

    @app_sse.post("/mcp")
    async def mcp_endpoint(request: Request):
        body = await request.json()
        resp = handle_request(body)
        return JSONResponse(resp or {})

    @app_sse.get("/health")
    def health():
        return {"status": "ok", "guard_available": _guard_available, "tools": [t["name"] for t in TOOLS]}

    uvicorn.run(app_sse, host="0.0.0.0", port=port)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAXDA MCP Server")
    parser.add_argument("--port", type=int, default=None, help="SSE port (omit for stdio)")
    args = parser.parse_args()

    if args.port:
        print(f"Starting DAXDA MCP Server (SSE) on port {args.port}", file=sys.stderr)
        run_sse(args.port)
    else:
        run_stdio()
