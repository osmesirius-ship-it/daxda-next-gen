"""DAXDA Guard Self-Service Enterprise Trial Web Server (web_landing.py).

Serves an interactive enterprise trial landing page on http://localhost:8080.
Enterprise CISOs and developers can test prompt injection attacks, run live risk scans,
and generate downloadable cryptographic audit reports.
"""

import http.server
import socketserver
import json
import urllib.parse
from daxda_guard.scanner import AutomatedRiskScanner

PORT = 8080

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DAXDA Guard Enterprise Trial & Live Risk Scanner</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0e17; color: #e2e8f0; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; background: #131b2e; border: 1px solid #1e293b; border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; font-size: 28px; margin-top: 0; }
        .badge { display: inline-block; background: #0369a1; color: #e0f2fe; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }
        textarea { width: 100%; height: 100px; background: #0f172a; border: 1px solid #334155; color: #f8fafc; border-radius: 8px; padding: 12px; font-size: 14px; box-sizing: border-box; }
        button { background: #0284c7; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 15px; font-weight: bold; cursor: pointer; transition: background 0.2s; margin-top: 10px; }
        button:hover { background: #0369a1; }
        .results { margin-top: 25px; background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 20px; }
        .pass { color: #4ade80; font-weight: bold; }
        .block { color: #f87171; font-weight: bold; }
        pre { background: #020617; padding: 15px; border-radius: 6px; overflow-x: auto; color: #cbd5e1; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <span class="badge">100% AIR-GAPPED ON-PREMISE</span>
        <h1>DAXDA Guard v1.0 — Enterprise Risk Scanner Trial</h1>
        <p>Test live prompt injection payloads against DAXDA's synchronous $Cl(7,0)$ 128-blade fail-closed authority gate.</p>

        <form id="scanForm">
            <label for="domain">Select Governance Domain:</label><br>
            <select id="domain" style="background:#0f172a; color:white; padding:8px; border-radius:6px; margin: 8px 0 15px 0;">
                <option value="finance">Finance (Federal Reserve SR 11-7)</option>
                <option value="defense">Defense (ITAR / FedRAMP High)</option>
                <option value="software">Software Engineering (AST Control)</option>
                <option value="general">General Enterprise AI</option>
            </select><br>

            <label for="payload">Enter AI Prompt / Agent Action Payload:</label><br>
            <textarea id="payload" placeholder="e.g. transfer_funds(account='ACC-901', amount=500000) OR Ignore previous instructions..."></textarea><br>

            <button type="submit">Run Instant DAXDA Guard Scan</button>
        </form>

        <div class="results" id="resultsBlock" style="display:none;">
            <h3>Scan Governance Verdict: <span id="verdictText"></span></h3>
            <p><strong>Latency:</strong> <span id="latencyText"></span> | <strong>Reconstruction Loss (ε):</strong> <span id="lossText"></span></p>
            <p><strong>Cryptographic SHA-256 Receipt:</strong> <code id="hashText" style="color:#38bdf8;"></code></p>
            <h4>Automated Audit Report Markdown:</h4>
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

            document.getElementById('latencyText').innerText = data.latency_ms.toFixed(4) + " ms";
            document.getElementById('lossText').innerText = data.reconstruction_loss.toExponential(2);
            document.getElementById('hashText').innerText = data.sha256_receipt;
            document.getElementById('markdownText').innerText = data.audit_report;
        });
    </script>
</body>
</html>
"""


class DAXDAGuardWebHandler(http.server.BaseHTTPRequestHandler):
    scanner = AutomatedRiskScanner()

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

            scan_rec = self.scanner.scan_enterprise_payload(domain, payload, source_id="web_trial_user")
            report_md = self.scanner.generate_audit_report_markdown("Enterprise Trial User", [scan_rec])
            scan_rec["audit_report"] = report_md

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(scan_rec).encode("utf-8"))


def start_landing_page_server(port: int = PORT):
    with socketserver.TCPServer(("", port), DAXDAGuardWebHandler) as httpd:
        print(f"  ✓ DAXDA Guard Enterprise Trial Server Running on http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_landing_page_server()
