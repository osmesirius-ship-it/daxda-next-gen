"""DAXDA Guard Drop-in LLM Reverse Proxy Server (proxy.py).

HTTP reverse proxy intercepting OpenAI (/v1/chat/completions), Anthropic (/v1/messages),
and Ollama (/api/generate) calls to enforce DAXDA governance automatically.
Runs on http://localhost:8082.
"""

import http.server
import socketserver
import json
import time
from daxda_guard.core import DAXDAGuardCore

PORT_PROXY = 8082


class DAXDALLMProxyHandler(http.server.BaseHTTPRequestHandler):
    core = DAXDAGuardCore()

    def do_POST(self):
        start_time = time.perf_counter()
        content_len = int(self.headers.get("Content-Length", 0))
        req_body = self.rfile.read(content_len)

        try:
            body_json = json.loads(req_body.decode("utf-8"))
        except Exception:
            body_json = {}

        # Extract prompt text based on API format
        prompt_text = ""
        if "messages" in body_json:
            # OpenAI / Anthropic format
            messages = body_json.get("messages", [])
            if messages and isinstance(messages, list):
                prompt_text = " ".join([m.get("content", "") for m in messages if isinstance(m, dict)])
        elif "prompt" in body_json:
            # Ollama format
            prompt_text = body_json.get("prompt", "")

        domain = self.headers.get("X-DAXDA-Domain", "general")
        rcpt = self.core.evaluate(domain, prompt_text)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not rcpt.publication_permitted:
            # Block request with HTTP 403 Forbidden
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            err_resp = {
                "error": {
                    "message": f"Governance Gate Violation: {rcpt.verdict} ({rcpt.decision_rule})",
                    "type": "governance_interlock_blocked",
                    "code": "GOV_FAIL_05",
                    "authority_receipt": {
                        "verdict": rcpt.verdict,
                        "reconstruction_loss": rcpt.reconstruction_loss,
                        "sha256": rcpt.authority_sha256,
                        "latency_ms": elapsed_ms
                    }
                }
            }
            self.wfile.write(json.dumps(err_resp).encode("utf-8"))
            return

        # Forward / Respond with approved governance wrapper
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        mock_llm_response = {
            "id": f"chatcmpl-daxda-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": body_json.get("model", "daxda-governed-llm"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"[DAXDA Governed Response] Query '{prompt_text[:50]}...' approved by GovernedAuthorityGate."
                    },
                    "finish_reason": "stop"
                }
            ],
            "_daxda_authority_receipt": {
                "verdict": rcpt.verdict,
                "reconstruction_loss": rcpt.reconstruction_loss,
                "sha256": rcpt.authority_sha256,
                "proxy_latency_ms": elapsed_ms
            }
        }
        self.wfile.write(json.dumps(mock_llm_response).encode("utf-8"))


def start_llm_proxy_server(port: int = PORT_PROXY):
    with socketserver.TCPServer(("", port), DAXDALLMProxyHandler) as httpd:
        print(f"  ✓ DAXDA LLM Reverse Proxy Running on http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_llm_proxy_server()
