#!/usr/bin/env python3
"""
DAXDA BioForge VR: WebXR Standalone Server
===========================================
Serves the WebXR Hands application with headers required for WebXR Device API
and Meta Quest Browser hand-tracking.
Exposes REST endpoints for all 5 DAXDA Medical Discoveries.
"""

from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

CURRENT_DIR = Path(__file__).resolve().parent
STATIC_DIR = CURRENT_DIR / "static"
PACKAGE_DIR = CURRENT_DIR.parent
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from game_core.medical_discoveries import (
    MedicalDiscoveryId, MedicalDiscoveryProcedure, DISCOVERY_CATALOG
)
from hand_engine.gesture_recognizer import SeatedErgonomicsGuard

# Active procedure instance
active_proc = MedicalDiscoveryProcedure(MedicalDiscoveryId.MS_REMYELINATION)
guard = SeatedErgonomicsGuard()

class BioForgeServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/discoveries":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            catalog = [
                {
                    "id": m.discovery_id.value,
                    "name": m.name,
                    "target_condition": m.target_condition,
                    "mechanism": m.scientific_mechanism,
                    "primary_hardware_or_ligand": m.primary_molecule_or_hardware,
                    "action_summary": m.biological_action_summary,
                    "metric_label": m.target_metric_label,
                    "baseline": m.baseline_metric_val,
                    "target": m.target_metric_val,
                    "unit": m.unit
                }
                for m in DISCOVERY_CATALOG.values()
            ]
            self.wfile.write(json.dumps(catalog).encode("utf-8"))
            return

        elif parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            state = active_proc.export_state_json()
            state["seated_max_radius_meters"] = guard.max_radius
            state["airplane_seat_compliant"] = True
            self.wfile.write(json.dumps(state).encode("utf-8"))
            return

        super().do_GET()

    def do_POST(self):
        global active_proc
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        body = json.loads(post_data.decode("utf-8")) if post_data else {}

        if parsed.path == "/api/action/select_discovery":
            d_id = body.get("discovery_id", "MS_REMYELINATION")
            try:
                active_proc = MedicalDiscoveryProcedure(MedicalDiscoveryId(d_id))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "SUCCESS",
                    "active_discovery": active_proc.metadata.name
                }).encode("utf-8"))
                return
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return

        elif parsed.path == "/api/action/solve":
            active_proc._advance_progress(1.0)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "SUCCESS",
                "is_completed": active_proc.is_completed,
                "current_metric_val": active_proc.current_metric_val,
                "metric_label": active_proc.metadata.target_metric_label
            }).encode("utf-8"))
            return

        elif parsed.path == "/api/action/reset":
            active_proc = MedicalDiscoveryProcedure(active_proc.discovery_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "SUCCESS", "message": "Procedure reset."}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server(port: int = 8086):
    server = HTTPServer(("0.0.0.0", port), BioForgeServerHandler)
    print("=" * 70)
    print("🧬 DAXDA BioForge VR — Hands-First Medical Discovery Synthesizer")
    print(f"📡 WebXR Application Live at: http://localhost:{port}")
    print("🥽 Meta Quest & Meta VR Glasses Hands-First Experience Ready")
    print("=" * 70)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8086
    run_server(p)
