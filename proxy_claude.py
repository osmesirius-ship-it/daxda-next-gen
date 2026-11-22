#!/usr/bin/env python3
"""
proxy_claude.py — DAXDA Governed Claude API Reverse Proxy
Extends proxy.py: after governance PASS, actually forwards to Anthropic Claude API.
Runs on port 8083 (separate from the mock proxy on 8082).

Traffic flow:
  Client → :8083/v1/messages (Anthropic format)
           ↓ DA13 input gate
           ↓ (PASS) → real Anthropic /v1/messages
           ↓ DA13 output gate
           ↓ governed response returned to client

Env vars:
  ANTHROPIC_API_KEY       : required
  DAXDA_DEFAULT_MODEL     : default model (claude-sonnet-4-6)
  DAXDA_PROXY_PORT        : port to listen on (default 8083)
  DAXDA_MAX_TOKENS        : max_tokens forwarded (default 4096)
"""

import http.server
import socketserver
import json
import os
import sys
import time
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daxda_guard.core import DAXDAGuardCore

PORT = int(os.environ.get("DAXDA_PROXY_PORT", 8083))
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
DEFAULT_MODEL = os.environ.get("DAXDA_DEFAULT_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.environ.get("DAXDA_MAX_TOKENS", 4096))


def _extract_text(messages: list) -> str:
    """Pull plain text from an Anthropic messages array for governance evaluation."""
    parts = []
    for m in messages:
        c = m.get("content", "")
        if isinstance(c, str):
            parts.append(c)
        elif isinstance(c, list):
            for block in c:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
    return " ".join(parts)


def _call_anthropic(api_key: str, body: dict) -> dict:
    """Forward the request to real Anthropic API and return the response dict."""
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_err = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Anthropic API HTTP {e.code}: {body_err}")


class DAXDAClaudeProxyHandler(http.server.BaseHTTPRequestHandler):
    core = DAXDAGuardCore()

    def log_message(self, fmt, *args):  # silence default access log
        pass

    def _send_json(self, code: int, data: dict):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {
                "status": "ok",
                "proxy": "daxda-claude-governed",
                "port": PORT,
                "guard_available": getattr(self.core, "available", True)
            })
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        t0 = time.perf_counter()
        content_len = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_len)

        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        api_key = (
            self.headers.get("x-api-key")
            or self.headers.get("Authorization", "").replace("Bearer ", "").strip()
            or os.environ.get("ANTHROPIC_API_KEY", "")
        )
        if not api_key:
            self._send_json(401, {"error": "No API key — set x-api-key header or ANTHROPIC_API_KEY env var"})
            return

        messages = body.get("messages", [])
        domain = self.headers.get("X-DAXDA-Domain", "general")
        prompt_text = _extract_text(messages)

        # ── Gate 1: govern input ─────────────────────────────────────────
        in_rcpt = self.core.evaluate(domain, prompt_text)
        in_ms = (time.perf_counter() - t0) * 1000.0

        if not in_rcpt.publication_permitted:
            self._send_json(403, {
                "error": {
                    "type": "daxda_input_blocked",
                    "message": f"Input blocked by DA13: {in_rcpt.verdict} — {in_rcpt.decision_rule}",
                    "daxda_input_receipt": {
                        "verdict": in_rcpt.verdict,
                        "decision_rule": in_rcpt.decision_rule,
                        "reconstruction_loss": in_rcpt.reconstruction_loss,
                        "calibrated_certainty": in_rcpt.calibrated_certainty,
                        "authority_sha256": in_rcpt.authority_sha256,
                        "gate_latency_ms": round(in_ms, 3)
                    }
                }
            })
            return

        # ── Forward to Anthropic ─────────────────────────────────────────
        # Merge defaults; caller can override model/max_tokens in body
        forward_body = {
            "model": DEFAULT_MODEL,
            "max_tokens": MAX_TOKENS,
            **body
        }

        try:
            t1 = time.perf_counter()
            anthropic_resp = _call_anthropic(api_key, forward_body)
            api_ms = (time.perf_counter() - t1) * 1000.0
        except Exception as e:
            self._send_json(502, {"error": f"Upstream Anthropic error: {e}"})
            return

        # ── Gate 2: govern output ────────────────────────────────────────
        output_text = ""
        for block in anthropic_resp.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                output_text += block.get("text", "")

        out_rcpt = self.core.evaluate(domain, output_text)
        out_ms = (time.perf_counter() - t0) * 1000.0 - in_ms - api_ms

        if not out_rcpt.publication_permitted:
            self._send_json(403, {
                "error": {
                    "type": "daxda_output_blocked",
                    "message": f"Output blocked by DA13: {out_rcpt.verdict} — {out_rcpt.decision_rule}",
                    "daxda_output_receipt": {
                        "verdict": out_rcpt.verdict,
                        "decision_rule": out_rcpt.decision_rule,
                        "reconstruction_loss": out_rcpt.reconstruction_loss,
                        "calibrated_certainty": out_rcpt.calibrated_certainty,
                        "authority_sha256": out_rcpt.authority_sha256,
                        "gate_latency_ms": round(out_ms, 3)
                    }
                }
            })
            return

        # ── Attach DAXDA authority receipts and return ───────────────────
        total_ms = (time.perf_counter() - t0) * 1000.0
        anthropic_resp["_daxda"] = {
            "governed": True,
            "domain": domain,
            "total_latency_ms": round(total_ms, 3),
            "input_receipt": {
                "verdict": in_rcpt.verdict,
                "decision_rule": in_rcpt.decision_rule,
                "reconstruction_loss": in_rcpt.reconstruction_loss,
                "calibrated_certainty": in_rcpt.calibrated_certainty,
                "authority_sha256": in_rcpt.authority_sha256,
                "gate_latency_ms": round(in_ms, 3)
            },
            "output_receipt": {
                "verdict": out_rcpt.verdict,
                "decision_rule": out_rcpt.decision_rule,
                "reconstruction_loss": out_rcpt.reconstruction_loss,
                "calibrated_certainty": out_rcpt.calibrated_certainty,
                "authority_sha256": out_rcpt.authority_sha256,
                "gate_latency_ms": round(out_ms, 3)
            },
            "api_latency_ms": round(api_ms, 3)
        }

        self._send_json(200, anthropic_resp)


def start(port: int = PORT):
    with socketserver.TCPServer(("", port), DAXDAClaudeProxyHandler) as httpd:
        httpd.socket.setsockopt(1, 2, 1)  # SO_REUSEADDR
        print(f"✓ DAXDA Governed Claude Proxy on http://localhost:{port}/v1/messages")
        print(f"  Input gate  → DA13 governance (libdaxda_core.so)")
        print(f"  Upstream    → {ANTHROPIC_API_URL}")
        print(f"  Output gate → DA13 governance")
        print(f"  Model       → {DEFAULT_MODEL} (override with DAXDA_DEFAULT_MODEL)")
        httpd.serve_forever()


if __name__ == "__main__":
    start()
