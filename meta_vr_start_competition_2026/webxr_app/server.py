#!/usr/bin/env python3
"""
DAXDA ChronoHands: WebXR Standalone Server
===========================================
Serves the WebXR Hands application with headers required for WebXR Device API
and Meta Quest Browser hand-tracking.
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

from game_core.chronosphere import ChronosphereEngine, ChronosphereLevel
from hand_engine.gesture_recognizer import SeatedErgonomicsGuard, Vec3

# Server engine instance
engine = ChronosphereEngine(ChronosphereLevel.LEVEL_1_ESCAPEMENT)
guard = SeatedErgonomicsGuard()

class WebXRServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self):
        # Mandatory security & WebXR headers
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
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            state = engine.export_state_json()
            state["seated_guard_max_radius_meters"] = guard.max_radius
            state["airplane_seat_compliant"] = True
            self.wfile.write(json.dumps(state).encode("utf-8"))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        body = json.loads(post_data.decode("utf-8")) if post_data else {}

        if parsed.path == "/api/action/solve":
            # Simulate snapping all gears into vacant slots
            for g_id, gear in engine.gears.items():
                for s_id, slot in engine.slots.items():
                    if slot.occupied_by is None and slot.target_teeth == gear.teeth:
                        gear.current_pos = slot.position
                        gear.is_snapped = True
                        gear.snapped_slot_id = s_id
                        slot.occupied_by = g_id
                        slot.is_locked = True
                        break
            engine._check_puzzle_completion()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "SUCCESS",
                "is_completed": engine.is_completed,
                "message": "All gears snapped into chronosphere sockets."
            }).encode("utf-8"))
            return

        elif parsed.path == "/api/action/reset":
            engine._setup_level(engine.level)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "SUCCESS", "message": "Puzzle reset."}).encode("utf-8"))
            return

        elif parsed.path == "/api/action/scrub":
            delta = float(body.get("delta", 0.1))
            engine.scrub_temporal_dial(delta)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "SUCCESS",
                "temporal_phase": engine.temporal_phase
            }).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server(port: int = 8086):
    server = HTTPServer(("0.0.0.0", port), WebXRServerHandler)
    print("=" * 70)
    print("⏳ DAXDA ChronoHands — Meta VR Start Competition WebXR Server")
    print(f"📡 Serving WebXR Application at: http://localhost:{port}")
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
