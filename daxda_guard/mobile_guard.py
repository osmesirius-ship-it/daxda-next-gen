"""DAXDA Mobile Guard Engine & Web Server (mobile_guard.py).

Provides ultra-lightweight mobile-optimized Cl(7,0) governance API for iOS (Swift),
Android (Kotlin), and React Native apps, with a touch-friendly PWA mobile web UI on http://localhost:8081.
"""

import http.server
import socketserver
import json
import time
from daxda_guard.core import DAXDAGuardCore

PORT_MOBILE = 8081

MOBILE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DAXDA Mobile Guard iOS & Android</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #030712; color: #f9fafb; margin: 0; padding: 15px; }
        .mobile-card { background: #111827; border: 1px solid #1f2937; border-radius: 16px; padding: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; }
        .logo { font-size: 20px; font-weight: 800; color: #38bdf8; }
        .pill { background: #0284c7; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; }
        textarea { width: 100%; height: 90px; background: #030712; border: 1px solid #374151; color: white; border-radius: 12px; padding: 10px; font-size: 14px; box-sizing: border-box; margin-top: 8px; }
        button { width: 100%; background: linear-gradient(135deg, #0284c7, #2563eb); color: white; border: none; padding: 14px; border-radius: 12px; font-size: 16px; font-weight: bold; margin-top: 12px; cursor: pointer; }
        .res-box { margin-top: 15px; background: #030712; border-radius: 12px; padding: 15px; font-size: 13px; }
        .pass-tag { color: #4ade80; font-weight: bold; }
    </style>
</head>
<body>
    <div class="mobile-card">
        <div class="header">
            <div class="logo">📱 DAXDA Mobile</div>
            <div class="pill">iOS / Android</div>
        </div>
        <p style="font-size:13px; color:#9ca3af;">Synchronous $Cl(7,0)$ Mobile AI Guard. Prevents prompt injection & unauthorized actions directly on mobile devices.</p>
        
        <label style="font-size:12px; font-weight:bold;">Mobile AI Action Payload:</label>
        <textarea id="mobilePayload" placeholder="e.g. Mobile banking transfer or AI Assistant query..."></textarea>
        
        <button id="scanBtn">Run Mobile Security Scan</button>
        
        <div class="res-box" id="resBox" style="display:none;">
            <div>Verdict: <span id="verdictVal" class="pass-tag"></span></div>
            <div>Latency: <span id="latVal"></span></div>
            <div style="font-size:10px; color:#38bdf8; word-break:break-all; margin-top:6px;">SHA-256: <span id="hashVal"></span></div>
        </div>
    </div>

    <script>
        document.getElementById('scanBtn').addEventListener('click', async () => {
            const payload = document.getElementById('mobilePayload').value || 'Mobile AI Voice Query';
            const r = await fetch('/api/mobile_scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ payload })
            });
            const d = await r.json();
            document.getElementById('resBox').style.display = 'block';
            document.getElementById('verdictVal').innerText = d.verdict;
            document.getElementById('latVal').innerText = d.latency_ms.toFixed(3) + ' ms';
            document.getElementById('hashVal').innerText = d.sha256;
        });
    </script>
</body>
</html>
"""


class DAXDAMobileHandler(http.server.BaseHTTPRequestHandler):
    core = DAXDAGuardCore()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(MOBILE_HTML.encode("utf-8"))

    def do_POST(self):
        if self.path == "/api/mobile_scan":
            len_h = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(len_h).decode('utf-8'))
            payload = data.get("payload", "")

            t0 = time.perf_counter()
            rcpt = self.core.evaluate("mobile_app", payload)
            t1 = time.perf_counter()

            resp = {
                "verdict": rcpt.verdict,
                "latency_ms": (t1 - t0) * 1000.0,
                "sha256": rcpt.authority_sha256
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))


def start_mobile_server(port: int = PORT_MOBILE):
    with socketserver.TCPServer(("", port), DAXDAMobileHandler) as httpd:
        print(f"  ✓ DAXDA Mobile Server Running on http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_mobile_server()
