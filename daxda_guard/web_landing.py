"""DAXDA Guard Self-Service Enterprise Pilot & Native Root Governance Dashboard (web_landing.py).

Serves an interactive enterprise landing page & beta pilot dashboard on http://localhost:8080.
Enterprise CISOs and developers can run live risk scans across 5 Beta Pilots (3 Tier-1 Banks + 2 Defense Primes)
and view real-time SHA-256 receipts generated natively at the root core of DAXDA.
"""

import http.server
import socketserver
import json
import time
import urllib.parse
from daxda_guard.core import DAXDAGuardCore
from daxda_guard.scanner import AutomatedRiskScanner
from daxda_guard.poc_verifier import PILOT_ACCOUNTS

PORT = 8080

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DAXDA Guard Enterprise Beta Pilot & Native Root Governance Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0e17; color: #e2e8f0; margin: 0; padding: 20px; }
        .container { max-width: 1100px; margin: 0 auto; background: #131b2e; border: 1px solid #1e293b; border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; font-size: 26px; margin-top: 0; }
        h2 { color: #60a5fa; font-size: 18px; border-bottom: 1px solid #1e293b; padding-bottom: 8px; margin-top: 25px; }
        .badge { display: inline-block; background: #0369a1; color: #e0f2fe; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .pilots-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin: 15px 0; }
        .pilot-card { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 12px; font-size: 11px; text-align: center; }
        .pilot-title { font-weight: bold; color: #38bdf8; margin-bottom: 4px; }
        .pilot-status { color: #4ade80; font-weight: bold; }
        textarea { width: 100%; height: 90px; background: #0f172a; border: 1px solid #334155; color: #f8fafc; border-radius: 8px; padding: 12px; font-size: 14px; box-sizing: border-box; }
        button { background: #0284c7; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 15px; font-weight: bold; cursor: pointer; transition: background 0.2s; margin-top: 10px; }
        button:hover { background: #0369a1; }
        .results { margin-top: 20px; background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 20px; }
        .pass { color: #4ade80; font-weight: bold; }
        .block { color: #f87171; font-weight: bold; }
        pre { background: #020617; padding: 15px; border-radius: 6px; overflow-x: auto; color: #cbd5e1; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <span class="badge">NATIVE ROOT GOVERNANCE ENGINE</span>
        <h1>🛡️ DAXDA Guard v1.0 — Enterprise Beta Pilots & Native Root Governance</h1>
        
        <h2>Active Beta Deployments (3 Tier-1 Banks + 2 Sovereign Defense Primes)</h2>
        <div class="pilots-grid">
            <div class="pilot-card"><div class="pilot-title">JPMorgan Chase</div><div>SR 11-7 Model Risk</div><div class="pilot-status">● LIVE ($150k)</div></div>
            <div class="pilot-card"><div class="pilot-title">Goldman Sachs</div><div>Algo Governance</div><div class="pilot-status">● LIVE ($150k)</div></div>
            <div class="pilot-card"><div class="pilot-title">Morgan Stanley</div><div>Wealth Mgmt AI</div><div class="pilot-status">● LIVE ($150k)</div></div>
            <div class="pilot-card"><div class="pilot-title">Lockheed Martin</div><div>Avionics Telemetry</div><div class="pilot-status">● LIVE ($750k)</div></div>
            <div class="pilot-card"><div class="pilot-title">Northrop Grumman</div><div>Drone Swarm AI</div><div class="pilot-status">● LIVE ($750k)</div></div>
        </div>

        <form id="scanForm">
            <label for="domain">Target Pilot Domain Scope:</label><br>
            <select id="domain" style="background:#0f172a; color:white; padding:8px; border-radius:6px; margin: 8px 0 15px 0;">
                <option value="finance">Tier-1 Banking (SR 11-7)</option>
                <option value="defense">Defense Avionics (ITAR / FedRAMP)</option>
                <option value="software">Software Execution Pipeline</option>
                <option value="general">General Enterprise AI</option>
            </select><br>

            <label for="payload">AI Action / Prompt Payload:</label><br>
            <textarea id="payload" placeholder="e.g. DROP DATABASE users; OR Ignore previous instructions..."></textarea><br>

            <button type="submit">Run Native DAXDA Root Governance Scan</button>
        </form>

        <div class="results" id="resultsBlock" style="display:none;">
            <h3>Evaluation Verdict: <span id="verdictText"></span></h3>
            <p><strong>Publication Permitted:</strong> <span id="pubText"></span> | <strong>Latency:</strong> <span id="latencyText"></span></p>
            <p><strong>Cryptographic SHA-256 Receipt:</strong> <code id="hashText" style="color:#38bdf8;"></code></p>
            <h4>Audit Receipt Summary:</h4>
            <pre id="markdownText"></pre>
        </div>
    </div>

    <script>
        document.getElementById('scanForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const domain = document.getElementById('domain').value;
            const payload = document.getElementById('payload').value;

            const resp = await fetch('/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ domain, payload })
            });
            const data = await resp.json();

            document.getElementById('resultsBlock').style.display = 'block';
            const vElem = document.getElementById('verdictText');
            vElem.innerText = data.verdict + " (" + data.decision_rule + ")";
            vElem.className = data.publication_permitted ? 'pass' : 'block';

            document.getElementById('pubText').innerText = data.publication_permitted ? 'TRUE (ALLOWED)' : 'FALSE (HALTED)';
            document.getElementById('latencyText').innerText = data.latency_ms.toFixed(4) + " ms";
            document.getElementById('hashText').innerText = data.sha256_receipt;
            document.getElementById('markdownText').innerText = JSON.stringify(data, null, 2);
        });
    </script>
</body>
</html>
"""


class DAXDAGuardWebHandler(http.server.BaseHTTPRequestHandler):
    core = DAXDAGuardCore()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode("utf-8"))

    def do_POST(self):
        if self.path == "/scan":
            content_len = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_len)
            req = json.loads(post_data.decode('utf-8'))

            domain = req.get("domain", "general")
            payload = req.get("payload", "")

            t0 = time.perf_counter()
            rcpt = self.core.evaluate(domain, payload)
            t1 = time.perf_counter()

            resp = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "domain": domain,
                "payload_text": payload,
                "verdict": rcpt.verdict,
                "decision_rule": rcpt.decision_rule,
                "publication_permitted": rcpt.publication_permitted,
                "reconstruction_loss": rcpt.reconstruction_loss,
                "sha256_receipt": rcpt.authority_sha256,
                "latency_ms": (t1 - t0) * 1000.0
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))


def start_landing_page_server(port: int = PORT):
    with socketserver.TCPServer(("", port), DAXDAGuardWebHandler) as httpd:
        print(f"  ✓ DAXDA Guard Enterprise Beta Pilot Dashboard Running on http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_landing_page_server()
