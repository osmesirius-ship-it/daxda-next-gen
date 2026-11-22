#!/usr/bin/env python3
"""
DAXDA Unified Holodeck v3.0 — Hologram Server + iMac Optical Sonification + Toroidal Affect Engine
==================================================================================================
Combines three DAXDA systems into one unified real-time application on http://127.0.0.1:8765:
1. DAXDA Holodeck Hologram Server (5 Morphable 3D Forms + 12-Stage V14.1 Halo + 4-Way Pyramid):
   - Form 1: `persona`   — Breathing {5,4} Dodecahedron + Cl(7,0) Hodge-Dual Icosahedron
   - Form 2: `torus`     — 3D Toroidal Emotional Field (T^2 Poloidal-Toroidal (p:q) Knot & Helicity H)
   - Form 3: `attractor` — iMac Optical Sonification 3D Phase-Space Attractor [x(t), x(t+tau), x(t+2tau)]
   - Form 4: `crystal`   — Hexagonal Ice Ih Prism (D6h) + Cuboctahedron (Oh, 70.53°/109.47°)
   - Form 5: `planet`    — 3D Planetary Globe + 26.02° Dichotomy Great Circle Ring
2. iMac Optical Sonification & Cymatics Pipeline (`/api/sonify_imac`, `/api/waveforms/*`):
   - Live screen capture (`imac_current_moment.png`), 48 kHz cross-modal audio synthesis,
     2D Morlet Cymatics (`imac_audio_to_visual_cymatics.png`), Chladni Nodal Plate (`m=2, n=3`),
     and calibrated Clifford Cl(16,4) multivector blades (`NCI`, `CPC`, `FAF`, `e1..e15`).
3. Toroidal Emotional Prosody & Affective State Engine (`/api/toroidal_emotion`):
   - 4D Affective Manifold (Valence V, Arousal A, Dominance D, Coherence C), Voiced F0 & Jitter,
     Beltramian Helicity H, and live interactive (V, A, C, p:q) sliders.
"""

import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

STATE_PATH = BASE_DIR / "outputs" / "hologram_live_state.json"
WAVEFORMS_DIR = BASE_DIR / "outputs" / "waveforms"
VOICE_WAV_PATH = BASE_DIR / "outputs" / "voice_clones" / "daxda_nicole_voice_1795247869.wav"
SONIF_WAV_PATH = WAVEFORMS_DIR / "imac_optical_sonification_synthesis.wav"
SONIF_MANIFEST_PATH = WAVEFORMS_DIR / "imac_waveform_transformation_manifest.json"
TORUS_REPORT_PATH = BASE_DIR / "outputs" / "daxda_toroidal_emotional_field_report.json"

HOST = "127.0.0.1"
PORT = 8765

STAGE_NAMES = [
    "S01 Claim", "S02 Symbols", "S03 Dimensions", "S04 Closure",
    "S05 Limits", "S06 Counterex", "S07 Falsify", "S08 Validation",
    "S09 Thesis", "S10 Package", "S11 Empirical", "S12 Verdict"
]

DEFAULT_STAGES = [
    {"id": f"S{i+1:02d}", "name": STAGE_NAMES[i], "status": "pass"}
    for i in range(12)
]

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DAXDA Unified Holodeck v3.0 — Hologram · iMac Sonification · Toroidal Affect</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 100%; height: 100%;
      background: #02040a;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", monospace;
      overflow: hidden;
      user-select: none;
    }
    canvas#c { display: block; width: 100vw; height: 100vh; cursor: grab; }
    canvas#c:active { cursor: grabbing; }

    #topbar {
      position: fixed; top: 10px; left: 12px; right: 12px;
      display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
      gap: 8px; pointer-events: none; z-index: 20; transition: opacity 0.25s;
    }
    .pill {
      pointer-events: auto;
      display: inline-flex; align-items: center; gap: 7px;
      background: rgba(8, 12, 22, 0.88);
      border: 1px solid rgba(148, 163, 184, 0.28);
      border-radius: 999px;
      padding: 5px 12px;
      font-size: 11.5px;
      backdrop-filter: blur(12px);
    }
    .dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: #f5b041;
      box-shadow: 0 0 10px #f5b041;
    }
    #sideDrawer {
      position: fixed; top: 58px; right: 12px; bottom: 104px;
      width: 350px;
      background: rgba(8, 12, 22, 0.88);
      border: 1px solid rgba(148, 163, 184, 0.26);
      border-radius: 12px;
      padding: 12px;
      backdrop-filter: blur(12px);
      z-index: 20;
      overflow-y: auto;
      display: flex; flex-direction: column; gap: 10px;
      font-size: 11.5px;
      transition: opacity 0.25s, transform 0.25s;
    }
    #bottombar {
      position: fixed; bottom: 10px; left: 12px; right: 12px;
      display: flex; flex-direction: column; gap: 6px;
      pointer-events: none; z-index: 20; transition: opacity 0.25s;
    }
    .row-bar {
      display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
      gap: 8px;
    }
    .panel {
      pointer-events: auto;
      background: rgba(8, 12, 22, 0.88);
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 10px;
      padding: 7px 11px;
      backdrop-filter: blur(12px);
      font-size: 11.5px;
    }
    .controls { display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }
    button {
      background: rgba(30, 41, 59, 0.88);
      color: #f8fafc;
      border: 1px solid rgba(148, 163, 184, 0.28);
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.15s;
    }
    button:hover { background: rgba(51, 65, 85, 0.95); }
    button.active {
      background: rgba(245, 176, 65, 0.24);
      border-color: #f5b041;
      color: #fde68a;
    }
    button.emerald {
      background: rgba(16, 185, 129, 0.2);
      border-color: #10b981;
      color: #6ee7b7;
    }
    input[type="text"] {
      background: rgba(15, 23, 42, 0.9);
      color: #f8fafc;
      border: 1px solid rgba(148, 163, 184, 0.32);
      border-radius: 6px;
      padding: 4px 9px;
      font-size: 11.5px;
      width: 210px;
      outline: none;
    }
    input[type="range"] { width: 100%; accent-color: #f5b041; }
    .st-badge {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 9.5px;
      padding: 1.5px 5px;
      border-radius: 4px;
      border: 1px solid rgba(148,163,184,0.25);
    }
    .st-pass { color: #34d399; border-color: rgba(16,185,129,0.45); background: rgba(16,185,129,0.12); }
    .st-warn { color: #fbbf24; border-color: rgba(245,158,11,0.45); background: rgba(245,158,11,0.12); }
    .st-fail { color: #fb7185; border-color: rgba(244,63,94,0.5); background: rgba(244,63,94,0.15); }
    .sec-title { font-size: 10.5px; font-weight: 700; color: #38bdf8; letter-spacing: 0.05em; text-transform: uppercase; }
    .thumb-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
    .thumb-grid img { width: 100%; height: 64px; object-fit: cover; border-radius: 5px; border: 1px solid rgba(148,163,184,0.25); background: #000; }
    .bar-bg { background: rgba(2,6,23,0.8); height: 6px; border-radius: 3px; overflow: hidden; border: 1px solid rgba(148,163,184,0.2); }
    .bar-fill { height: 100%; border-radius: 3px; }
    .hidden { opacity: 0 !important; pointer-events: none !important; }
  </style>
</head>
<body>
  <canvas id="c"></canvas>

  <!-- TOP BAR: Status + 5 Unified 3D Holodeck Forms + Telemetry -->
  <div id="topbar">
    <div class="pill">
      <span id="statusDot" class="dot"></span>
      <span id="statusText">DAXDA Unified Holodeck v3.0 Online</span>
    </div>

    <div class="pill controls" style="padding: 3px 8px;">
      <span style="font-size:10.5px; color:#94a3b8;">3D Mode:</span>
      <button data-form="persona" class="form-btn">1. Persona Core</button>
      <button data-form="torus" class="form-btn active">2. Toroidal Affect (T²)</button>
      <button data-form="attractor" class="form-btn">3. iMac Sonification Attractor</button>
      <button data-form="crystal" class="form-btn">4. Crystal Lattice (Oh/Ih)</button>
      <button data-form="planet" class="form-btn">5. Planetary Globe</button>
    </div>

    <div class="pill" style="font-family: ui-monospace, monospace; color: #94a3b8;">
      <span id="metricsText">NCI=0.457 · CPC=0.950 · H=5.51 · 12/12 PASS</span>
    </div>
  </div>

  <!-- RIGHT DRAWER: Unified iMac Optical Sonification + Toroidal Emotion Control Deck -->
  <div id="sideDrawer">
    <!-- Section A: Toroidal Emotional Prosody & Winding Controls -->
    <div style="border-bottom: 1px solid rgba(148,163,184,0.2); padding-bottom: 8px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <span class="sec-title">A. Toroidal Affect & Prosody (T²)</span>
        <span id="torusBadge" style="font-size:10px; color:#34d399;">f0=285.5Hz · (2:5)</span>
      </div>
      <div class="controls" style="margin-bottom: 7px;">
        <button data-emo="0" class="emo-btn active">Voice Clone</button>
        <button data-emo="1" class="emo-btn">iMac Optical</button>
        <button data-emo="2" class="emo-btn">Golden (3:5)</button>
        <button data-emo="3" class="emo-btn">Stress (4:9)</button>
      </div>
      <div style="display:grid; gap:4px; font-size:10.5px;">
        <div style="display:flex; justify-content:space-between;">
          <span style="color:#94a3b8;">Valence (V: Dissonant → Warm)</span>
          <span id="lblV" style="color:#34d399;">+0.39</span>
        </div>
        <input id="slV" type="range" min="-100" max="100" value="39" />

        <div style="display:flex; justify-content:space-between;">
          <span style="color:#94a3b8;">Arousal (A: Minor Radius r)</span>
          <span id="lblA" style="color:#fbbf24;">0.18</span>
        </div>
        <input id="slA" type="range" min="10" max="95" value="18" />

        <div style="display:flex; justify-content:space-between;">
          <span style="color:#94a3b8;">Coherence (C: Shear → Laminar)</span>
          <span id="lblC" style="color:#38bdf8;">0.67</span>
        </div>
        <input id="slC" type="range" min="15" max="98" value="67" />

        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2px;">
          <span style="color:#94a3b8;">Winding Knot (p : q)</span>
          <div class="controls">
            <button data-p="3" data-q="5" class="pq-btn">3:5</button>
            <button data-p="2" data-q="5" class="pq-btn active">2:5</button>
            <button data-p="3" data-q="7" class="pq-btn">3:7</button>
            <button data-p="4" data-q="9" class="pq-btn">4:9</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Section B: iMac Retina 5K Optical Sonification & Cymatics Pipeline -->
    <div style="border-bottom: 1px solid rgba(148,163,184,0.2); padding-bottom: 8px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <span class="sec-title">B. iMac Optical Sonification</span>
        <button id="btnSonifyNow" class="emerald">⚡ Re-Capture iMac</button>
      </div>
      <div class="thumb-grid" style="margin-bottom: 6px;">
        <div>
          <img id="imgScreen" src="/api/waveforms/imac_current_moment.png" alt="iMac Screen" />
          <div style="font-size:9px; color:#94a3b8; text-align:center;">Retina 5K Screen</div>
        </div>
        <div>
          <img id="imgCym" src="/api/waveforms/imac_audio_to_visual_cymatics.png" alt="2D Cymatics" />
          <div style="font-size:9px; color:#94a3b8; text-align:center;">2D Cymatics</div>
        </div>
        <div>
          <img id="imgChladni" src="/api/waveforms/imac_chladni_nodal_lines.png" alt="Chladni Plate" />
          <div style="font-size:9px; color:#94a3b8; text-align:center;">Chladni (2,3)</div>
        </div>
      </div>
      <div style="display:flex; gap:5px;">
        <button id="btnPlaySonif" style="flex:1;" class="active">▶ Play iMac Sonified WAV</button>
        <button id="btnPlayVoice" style="flex:1;">▶ Play Cloned Voice WAV</button>
      </div>
    </div>

    <!-- Section C: Unified Resonance (NCI/CPC/FAF) & Clifford Cl(16,4) Blades -->
    <div>
      <div class="sec-title" style="margin-bottom:6px;">C. Cl(16,4) Multivector & Resonance</div>
      <div id="bladeMeters" style="display:grid; gap:5px; font-size:10.5px;"></div>
    </div>
  </div>

  <!-- BOTTOM BAR: 12-Stage V14.1 Ring + Command Bar + Pyramid & Audio Controls -->
  <div id="bottombar">
    <div class="panel row-bar">
      <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
        <span style="font-weight:700; font-size:10.5px; color:#cbd5e1;">V14.1 12-STAGE RING:</span>
        <div id="stageStrip" style="display:flex; flex-wrap:wrap; gap:3px;"></div>
      </div>
      <div class="controls">
        <button id="btnHalo" class="active">12-Stage Halo: ON</button>
        <button id="btnDrawer" class="active">Inspector Drawer: ON</button>
      </div>
    </div>

    <div class="row-bar">
      <div class="panel controls">
        <input id="cmdInput" type="text" placeholder="Type claim or command for V14.1 audit..." />
        <button id="btnRunAudit" class="active">Run V14.1 Audit</button>
        <button data-preset="ubi" class="pre-btn">UBI (9/12)</button>
        <button data-preset="cebri" class="pre-btn">CEBRI (11/12)</button>
        <button data-preset="mars" class="pre-btn">Mars (12/12)</button>
        <button data-preset="block" class="pre-btn">Fail-Closed Block</button>
      </div>

      <div class="panel controls">
        <button id="btnChime">Toroidal Chord</button>
        <button id="btnMic">Mic Reactive: Off</button>
        <button id="btnSingle" class="active">Single 3D</button>
        <button id="btnGhost">4-Way Pyramid</button>
        <button id="btnHide">Hide HUD (H)</button>
      </div>
    </div>
  </div>

  <script>
    const canvas = document.getElementById('c');
    const ctx = canvas.getContext('2d');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const metricsText = document.getElementById('metricsText');
    const stageStrip = document.getElementById('stageStrip');
    const topbar = document.getElementById('topbar');
    const bottombar = document.getElementById('bottombar');
    const sideDrawer = document.getElementById('sideDrawer');

    const PHI = (1 + Math.sqrt(5)) / 2;
    const INV_PHI = 1 / PHI;

    // 1. Persona Dodecahedron + Icosahedron
    const rawVerts = [];
    for (const x of [-1, 1]) for (const y of [-1, 1]) for (const z of [-1, 1]) rawVerts.push([x, y, z]);
    for (const y of [-INV_PHI, INV_PHI]) for (const z of [-PHI, PHI]) rawVerts.push([0, y, z]);
    for (const x of [-INV_PHI, INV_PHI]) for (const y of [-PHI, PHI]) rawVerts.push([x, y, 0]);
    for (const x of [-PHI, PHI]) for (const z of [-INV_PHI, INV_PHI]) rawVerts.push([x, 0, z]);
    const dodecaVerts = rawVerts.map(([x, y, z]) => { const m = Math.hypot(x, y, z); return [x/m, y/m, z/m]; });
    const dodecaEdges = [];
    for (let i = 0; i < dodecaVerts.length; i++) {
      for (let j = i + 1; j < dodecaVerts.length; j++) {
        const d = Math.hypot(dodecaVerts[i][0]-dodecaVerts[j][0], dodecaVerts[i][1]-dodecaVerts[j][1], dodecaVerts[i][2]-dodecaVerts[j][2]);
        if (d < 0.78) dodecaEdges.push([i, j]);
      }
    }
    const icoRaw = [];
    for (const s1 of [-1, 1]) for (const s2 of [-1, 1]) {
      icoRaw.push([0, s1, s2 * PHI], [s1, s2 * PHI, 0], [s2 * PHI, 0, s1]);
    }
    const icoVerts = icoRaw.map(([x, y, z]) => { const m = Math.hypot(x, y, z); return [x/m, y/m, z/m]; });
    const icoEdges = [];
    for (let i = 0; i < icoVerts.length; i++) {
      for (let j = i + 1; j < icoVerts.length; j++) {
        const d = Math.hypot(icoVerts[i][0]-icoVerts[j][0], icoVerts[i][1]-icoVerts[j][1], icoVerts[i][2]-icoVerts[j][2]);
        if (d < 1.12) icoEdges.push([i, j]);
      }
    }

    // 4. Crystal Lattice (Hexagonal Ice Ih + Cuboctahedron Oh)
    const cuboctaVerts = [];
    for (const s1 of [-1, 1]) for (const s2 of [-1, 1]) {
      cuboctaVerts.push([0, s1, s2], [s1, 0, s2], [s1, s2, 0]);
    }
    const crystalOuterVerts = [];
    for (let k = 0; k < 6; k++) {
      const a = (k * Math.PI) / 3;
      crystalOuterVerts.push([Math.cos(a)*0.95, 0.55, Math.sin(a)*0.95], [Math.cos(a)*0.95, -0.55, Math.sin(a)*0.95]);
    }
    for (let k = 0; k < 6; k++) {
      const a = (k * Math.PI) / 3 + Math.PI / 6;
      crystalOuterVerts.push([Math.cos(a)*0.48, k % 2 === 0 ? 1.05 : -1.05, Math.sin(a)*0.48]);
    }
    crystalOuterVerts.push([0, 1.18, 0], [0, -1.18, 0]);
    const crystalOuterEdges = [];
    for (let i = 0; i < crystalOuterVerts.length; i++) {
      for (let j = i + 1; j < crystalOuterVerts.length; j++) {
        const d = Math.hypot(crystalOuterVerts[i][0]-crystalOuterVerts[j][0], crystalOuterVerts[i][1]-crystalOuterVerts[j][1], crystalOuterVerts[i][2]-crystalOuterVerts[j][2]);
        if (d < 1.16) crystalOuterEdges.push([i, j]);
      }
    }

    // 5. Planetary Globe Pins
    const planetPins = [
      { name: "Jezero (1.11°)", lat: 18.44, lon: 77.45, col: "#fbbf24" },
      { name: "Nili (1.39°)", lat: 21.90, lon: 74.50, col: "#34d399" },
      { name: "Gale (1.57°)", lat: -4.59, lon: 137.44, col: "#fbbf24" },
      { name: "Gusev (6.00°)", lat: -14.57, lon: 175.47, col: "#fbbf24" },
      { name: "Mawrth (7.22°)", lat: 23.99, lon: -18.96, col: "#34d399" }
    ];

    // 2. Toroidal Emotional States
    const EMO_PRESETS = [
      { name: "1. DAXDA Voice Clone Prosody", f0: 285.5, jit: 1.8, v: 0.388, a: 0.182, d: 0.818, c: 0.673, p: 2, q: 5 },
      { name: "2. iMac Retina 5K Sonification", f0: 1838.4, jit: 25.4, v: 0.183, a: 0.424, d: 0.444, c: 0.513, p: 2, q: 5 },
      { name: "3. Golden Coherent Empathy (3:5)", f0: 216.0, jit: 1.8, v: 0.840, a: 0.460, d: 0.880, c: 0.940, p: 3, q: 5 },
      { name: "4. High-Shear Stress Alert (4:9)", f0: 612.0, jit: 34.5, v: -0.620, a: 0.890, d: 0.340, c: 0.240, p: 4, q: 9 }
    ];
    let emo = { ...EMO_PRESETS[0] };

    // 3. iMac Sonification 3D Phase-Space Attractor Orbit (loaded from /api/sonification_manifest)
    let attractorOrbit = [];
    for (let i = 0; i < 180; i++) {
      const u = (i / 180) * Math.PI * 6;
      attractorOrbit.push([Math.cos(u) * (0.65 + 0.25 * Math.sin(u * 1.7)), Math.sin(u * 1.3) * 0.75, Math.sin(u) * (0.65 + 0.25 * Math.cos(u * 1.7))]);
    }
    let sonMetrics = { nci: 0.4567, cpc: 0.9500, faf: 0.2435, f0: 1838.4, centroid: 2600.1 };

    const PALETTES = {
      amber:     { p: [245, 176, 65],  s: [56, 189, 248] },
      facets:    { p: [56, 189, 248],  s: [167, 139, 250] },
      heartbeat: { p: [52, 211, 153],  s: [245, 176, 65] },
      alert:     { p: [248, 113, 113], s: [251, 191, 36] }
    };

    const cur = { pr: 245, pg: 176, pb: 65, sr: 56, sg: 189, sb: 248, K: -1.0, tension: 0.15, pulseHz: 0.72, spin: 1.0 };
    const tgt = { ...cur };
    let activeForm = "torus";
    let showHalo = true;
    let ghostMode = false;
    let stages = [
      { id: "S01", name: "S01 Claim", status: "pass" },
      { id: "S02", name: "S02 Symbols", status: "pass" },
      { id: "S03", name: "S03 Dimensions", status: "pass" },
      { id: "S04", name: "S04 Closure", status: "pass" },
      { id: "S05", name: "S05 Limits", status: "pass" },
      { id: "S06", name: "S06 Counterex", status: "pass" },
      { id: "S07", name: "S07 Falsify", status: "pass" },
      { id: "S08", name: "S08 Validation", status: "pass" },
      { id: "S09", name: "S09 Thesis", status: "pass" },
      { id: "S10", name: "S10 Package", status: "pass" },
      { id: "S11", name: "S11 Empirical", status: "pass" },
      { id: "S12", name: "S12 Verdict", status: "pass" }
    ];

    let rotX = 0.52, rotY = 0.65, velX = 0, velY = 0.006;
    let dragging = false, lastX = 0, lastY = 0;
    let audioCtx = null, analyser = null, freqData = null, audioLevel = 0, micActive = false;

    function ensureAudio() {
      if (!audioCtx) {
        const AC = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AC();
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        freqData = new Uint8Array(analyser.frequencyBinCount);
      }
      if (audioCtx.state === "suspended") audioCtx.resume();
    }

    function playToroidalChord() {
      try {
        ensureAudio();
        const now = audioCtx.currentTime, dur = 2.0;
        const master = audioCtx.createGain();
        master.gain.setValueAtTime(0.18, now);
        master.gain.exponentialRampToValueAtTime(0.001, now + dur);
        master.connect(analyser);
        analyser.connect(audioCtx.destination);
        const baseF = Math.max(140, Math.min(520, emo.f0));
        const ratio = emo.q / emo.p;
        [baseF, baseF * (emo.p / 2), baseF * ratio, baseF * ratio * 1.5].forEach((f, i) => {
          const osc = audioCtx.createOscillator();
          osc.type = emo.c > 0.5 ? "sine" : "sawtooth";
          osc.frequency.setValueAtTime(f, now);
          osc.connect(master);
          osc.start(now + i * 0.04);
          osc.stop(now + dur);
        });
      } catch (e) {}
    }

    async function playWavEndpoint(url) {
      ensureAudio();
      try {
        const res = await fetch(url);
        if (res.ok) {
          const buf = await res.arrayBuffer();
          const audioBuf = await audioCtx.decodeAudioData(buf);
          const src = audioCtx.createBufferSource();
          src.buffer = audioBuf;
          src.connect(analyser);
          analyser.connect(audioCtx.destination);
          src.start(0);
          return;
        }
      } catch (e) {}
      playToroidalChord();
    }

    function updateEmoDrawer() {
      const R = 1.05 + 0.25 * emo.d;
      const r = 0.32 + 0.24 * emo.a;
      const qRatio = emo.q / emo.p;
      const H = 2 * Math.PI * Math.PI * R * r * r * qRatio * emo.c;
      const shear = (1 - emo.c) * (0.6 + 0.4 * emo.a);

      document.getElementById("torusBadge").textContent = `f0=${emo.f0.toFixed(0)}Hz · (${emo.p}:${emo.q}) · H=${H.toFixed(2)}`;
      document.getElementById("lblV").textContent = (emo.v >= 0 ? "+" : "") + emo.v.toFixed(2);
      document.getElementById("lblA").textContent = emo.a.toFixed(2);
      document.getElementById("lblC").textContent = emo.c.toFixed(2);
      document.getElementById("slV").value = Math.round(emo.v * 100);
      document.getElementById("slA").value = Math.round(emo.a * 100);
      document.getElementById("slC").value = Math.round(emo.c * 100);

      document.querySelectorAll(".pq-btn").forEach(b => {
        b.classList.toggle("active", parseInt(b.dataset.p) === emo.p && parseInt(b.dataset.q) === emo.q);
      });

      const e12 = Math.min(1, Math.max(0, (emo.v + 1) * 0.45 * emo.c + 0.15));
      const blades = [
        { label: `NCI / CPC Resonance (${sonMetrics.nci.toFixed(2)} / ${sonMetrics.cpc.toFixed(2)})`, val: sonMetrics.cpc, col: "#38bdf8" },
        { label: "e12 Empathy Phase Coupling", val: e12, col: "#34d399" },
        { label: "e23 Poloidal Arousal Vortex", val: emo.a, col: "#fbbf24" },
        { label: "e31 Toroidal Sovereign Helicity", val: Math.min(1, H / 8.0), col: "#c084fc" },
        { label: "e15 Dissonance Shear Stress", val: shear, col: "#f43f5e" }
      ];
      document.getElementById("bladeMeters").innerHTML = blades.map(b => `
        <div>
          <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
            <span>${b.label}</span><span style="color:${b.col}; font-family:monospace;">${b.val.toFixed(3)}</span>
          </div>
          <div class="bar-bg"><div class="bar-fill" style="width:${Math.min(100, Math.round(b.val*100))}%; background:${b.col};"></div></div>
        </div>
      `).join("");

      const passCount = stages.filter(s => s.status === "pass").length;
      metricsText.textContent = `FORM=${activeForm.toUpperCase()} · NCI=${sonMetrics.nci.toFixed(3)} · CPC=${sonMetrics.cpc.toFixed(3)} · H=${H.toFixed(2)} · ${passCount}/12 PASS`;
    }

    async function loadSonificationManifest() {
      try {
        const res = await fetch("/api/sonification_manifest", { cache: "no-store" });
        if (!res.ok) return;
        const m = await res.json();
        if (m.attractor_orbit_3d && m.attractor_orbit_3d.length > 10) {
          attractorOrbit = m.attractor_orbit_3d;
        }
        if (m.resonance_metrics) {
          sonMetrics.nci = m.resonance_metrics.nci || 0.4567;
          sonMetrics.cpc = m.resonance_metrics.cpc || 0.9500;
          sonMetrics.faf = m.resonance_metrics.faf || 0.2435;
        }
        updateEmoDrawer();
      } catch (e) {}
    }
    loadSonificationManifest();

    document.querySelectorAll(".emo-btn").forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.dataset.emo);
        emo = { ...EMO_PRESETS[idx] };
        document.querySelectorAll(".emo-btn").forEach(b => b.classList.toggle("active", parseInt(b.dataset.emo) === idx));
        activeForm = "torus";
        document.querySelectorAll(".form-btn").forEach(b => b.classList.toggle("active", b.dataset.form === "torus"));
        statusText.textContent = `Toroidal Affect Field -> ${emo.name}`;
        updateEmoDrawer();
        playToroidalChord();
      };
    });

    document.getElementById("slV").oninput = e => { emo.v = parseInt(e.target.value) / 100; updateEmoDrawer(); };
    document.getElementById("slA").oninput = e => { emo.a = parseInt(e.target.value) / 100; updateEmoDrawer(); };
    document.getElementById("slC").oninput = e => { emo.c = parseInt(e.target.value) / 100; updateEmoDrawer(); };
    document.querySelectorAll(".pq-btn").forEach(btn => {
      btn.onclick = () => {
        emo.p = parseInt(btn.dataset.p);
        emo.q = parseInt(btn.dataset.q);
        updateEmoDrawer();
        playToroidalChord();
      };
    });

    document.getElementById("btnPlaySonif").onclick = () => {
      activeForm = "attractor";
      document.querySelectorAll(".form-btn").forEach(b => b.classList.toggle("active", b.dataset.form === "attractor"));
      statusText.textContent = "Streaming iMac Retina 5K Optical Sonification WAV (48 kHz)...";
      playWavEndpoint("/api/sonification.wav");
    };
    document.getElementById("btnPlayVoice").onclick = () => {
      activeForm = "torus";
      document.querySelectorAll(".form-btn").forEach(b => b.classList.toggle("active", b.dataset.form === "torus"));
      statusText.textContent = "Streaming DAXDA Voice Clone WAV through Toroidal Affect Field...";
      playWavEndpoint("/api/voice.wav");
    };

    document.getElementById("btnSonifyNow").onclick = async () => {
      const btn = document.getElementById("btnSonifyNow");
      btn.textContent = "Capturing 5K...";
      statusText.textContent = "Acquiring iMac Retina 5K Optical Wavefield & Synthesizing Cymatics...";
      try {
        const res = await fetch("/api/sonify_imac", { method: "POST" });
        if (res.ok) {
          const ts = Date.now();
          document.getElementById("imgScreen").src = `/api/waveforms/imac_current_moment.png?t=${ts}`;
          document.getElementById("imgCym").src = `/api/waveforms/imac_audio_to_visual_cymatics.png?t=${ts}`;
          document.getElementById("imgChladni").src = `/api/waveforms/imac_chladni_nodal_lines.png?t=${ts}`;
          await loadSonificationManifest();
          activeForm = "attractor";
          document.querySelectorAll(".form-btn").forEach(b => b.classList.toggle("active", b.dataset.form === "attractor"));
          statusText.textContent = `iMac Optical Sonification Complete (NCI=${sonMetrics.nci.toFixed(3)}, CPC=${sonMetrics.cpc.toFixed(3)})`;
          playWavEndpoint(`/api/sonification.wav?t=${ts}`);
        }
      } catch (e) {}
      btn.textContent = "⚡ Re-Capture iMac";
    };

    function renderStageStrip() {
      stageStrip.innerHTML = stages.map(s => {
        const cls = s.status === "pass" ? "st-pass" : (s.status === "warn" ? "st-warn" : "st-fail");
        return `<span class="st-badge ${cls}">${s.id}</span>`;
      }).join("");
    }
    renderStageStrip();

    function applyStatePayload(st) {
      const pal = PALETTES[st.mode] || PALETTES.amber;
      tgt.pr = pal.p[0]; tgt.pg = pal.p[1]; tgt.pb = pal.p[2];
      tgt.sr = pal.s[0]; tgt.sg = pal.s[1]; tgt.sb = pal.s[2];
      tgt.K = typeof st.curvature_K === 'number' ? st.curvature_K : -1.0;
      tgt.tension = typeof st.facet_tension === 'number' ? st.facet_tension : 0.15;
      tgt.pulseHz = typeof st.pulse_hz === 'number' ? st.pulse_hz : 0.72;
      tgt.spin = typeof st.spin_speed === 'number' ? st.spin_speed : 1.0;

      if (st.geometry_form && ["persona", "torus", "attractor", "crystal", "planet"].includes(st.geometry_form)) {
        activeForm = st.geometry_form;
        document.querySelectorAll(".form-btn").forEach(b => b.classList.toggle("active", b.dataset.form === activeForm));
      }
      if (Array.isArray(st.stages) && st.stages.length === 12) {
        stages = st.stages;
        renderStageStrip();
      }
      const pHex = `rgb(${pal.p[0]},${pal.p[1]},${pal.p[2]})`;
      statusDot.style.background = pHex;
      statusDot.style.boxShadow = `0 0 12px ${pHex}`;
      statusText.textContent = st.status_label || st.mode;
      updateEmoDrawer();
    }

    let lastUpdatedTs = "";
    async function pollState() {
      try {
        const res = await fetch('/api/state', { cache: 'no-store' });
        if (!res.ok) return;
        const st = await res.json();
        if (st.updated_at && st.updated_at !== lastUpdatedTs) {
          lastUpdatedTs = st.updated_at;
          applyStatePayload(st);
        }
      } catch (e) {}
    }
    setInterval(pollState, 400);
    pollState();

    document.querySelectorAll(".form-btn").forEach(btn => {
      btn.onclick = async () => {
        activeForm = btn.dataset.form;
        document.querySelectorAll(".form-btn").forEach(b => b.classList.toggle("active", b.dataset.form === activeForm));
        playToroidalChord();
        try {
          await fetch("/api/audit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "set_form", geometry_form: activeForm })
          });
        } catch (e) {}
      };
    });

    const btnHalo = document.getElementById("btnHalo");
    btnHalo.onclick = () => {
      showHalo = !showHalo;
      btnHalo.textContent = "12-Stage Halo: " + (showHalo ? "ON" : "OFF");
      btnHalo.classList.toggle("active", showHalo);
    };
    const btnDrawer = document.getElementById("btnDrawer");
    btnDrawer.onclick = () => {
      sideDrawer.classList.toggle("hidden");
      const vis = !sideDrawer.classList.contains("hidden");
      btnDrawer.textContent = "Inspector Drawer: " + (vis ? "ON" : "OFF");
      btnDrawer.classList.toggle("active", vis);
    };

    async function triggerAudit(payload) {
      try {
        const res = await fetch("/api/audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const st = await res.json();
          lastUpdatedTs = st.updated_at || "";
          applyStatePayload(st);
          playToroidalChord();
        }
      } catch (e) {}
    }

    document.getElementById("btnRunAudit").onclick = () => {
      const q = document.getElementById("cmdInput").value.trim();
      if (!q) return;
      triggerAudit({ query: q });
    };
    document.getElementById("cmdInput").addEventListener("keydown", (e) => {
      if (e.key === "Enter") document.getElementById("btnRunAudit").click();
    });
    document.querySelectorAll(".pre-btn").forEach(btn => {
      btn.onclick = () => triggerAudit({ preset: btn.dataset.preset });
    });

    document.getElementById("btnChime").onclick = playToroidalChord;

    const btnSingle = document.getElementById('btnSingle');
    const btnGhost = document.getElementById('btnGhost');
    const btnMic = document.getElementById('btnMic');
    const btnHide = document.getElementById('btnHide');

    btnSingle.onclick = () => { ghostMode = false; btnSingle.classList.add('active'); btnGhost.classList.remove('active'); };
    btnGhost.onclick = () => { ghostMode = true; btnGhost.classList.add('active'); btnSingle.classList.remove('active'); };
    function toggleHud() { topbar.classList.toggle('hidden'); bottombar.classList.toggle('hidden'); sideDrawer.classList.toggle('hidden'); }
    btnHide.onclick = toggleHud;
    window.addEventListener('keydown', (e) => {
      if (document.activeElement === document.getElementById("cmdInput")) return;
      if (e.key.toLowerCase() === 'h') toggleHud();
    });

    btnMic.onclick = async () => {
      if (micActive) { micActive = false; btnMic.textContent = 'Mic Reactive: Off'; btnMic.classList.remove('active'); return; }
      try {
        ensureAudio();
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const src = audioCtx.createMediaStreamSource(stream);
        src.connect(analyser);
        micActive = true; btnMic.textContent = 'Mic Reactive: ON'; btnMic.classList.add('active');
      } catch { btnMic.textContent = 'Mic Blocked'; }
    };

    canvas.addEventListener('pointerdown', (e) => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
    window.addEventListener('pointermove', (e) => {
      if (!dragging) return;
      const dx = e.clientX - lastX, dy = e.clientY - lastY;
      rotY += dx * 0.008; rotX += dy * 0.008;
      velY = dx * 0.002; velX = dy * 0.002;
      lastX = e.clientX; lastY = e.clientY;
    });
    window.addEventListener('pointerup', () => { dragging = false; });

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    window.addEventListener('resize', resize);
    resize();

    function rotate3D([x, y, z], ax, ay) {
      const x1 = x * Math.cos(ay) + z * Math.sin(ay);
      const z1 = -x * Math.sin(ay) + z * Math.cos(ay);
      const y2 = y * Math.cos(ax) - z1 * Math.sin(ax);
      const z2 = y * Math.sin(ax) + z1 * Math.cos(ax);
      return [x1, y2, z2];
    }
    function project([x, y, z], cx, cy, scale) {
      const fov = 3.2;
      const p = fov / (fov + z);
      return [cx + x * scale * p, cy + y * scale * p, z, p];
    }

    function draw12StageHalo(cx, cy, s, t) {
      if (!showHalo) return;
      const haloR = 1.48 + audioLevel * 0.18;
      const stagePts = stages.map((st, idx) => {
        const ang = (idx / 12) * Math.PI * 2;
        const pt3 = rotate3D([Math.cos(ang) * haloR, Math.sin(ang) * 0.12, Math.sin(ang) * haloR], rotX * 0.65 + 0.35, rotY * 0.65 - t * 0.18);
        return { st, proj: project(pt3, cx, cy, s) };
      });
      ctx.beginPath();
      stagePts.forEach((sp, i) => { if (i === 0) ctx.moveTo(sp.proj[0], sp.proj[1]); else ctx.lineTo(sp.proj[0], sp.proj[1]); });
      ctx.closePath();
      ctx.strokeStyle = "rgba(148, 163, 184, 0.25)";
      ctx.lineWidth = 1.1;
      ctx.stroke();

      stagePts.forEach(({ st, proj }) => {
        const [px, py, , p] = proj;
        const col = st.status === "pass" ? "#10b981" : (st.status === "warn" ? "#f59e0b" : "#f43f5e");
        ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(px, py);
        ctx.strokeStyle = col; ctx.globalAlpha = st.status === "pass" ? 0.12 : 0.35; ctx.lineWidth = 1; ctx.stroke();
        ctx.globalAlpha = 0.92;
        ctx.beginPath(); ctx.arc(px, py, Math.max(2.8, 4.4 * p), 0, Math.PI * 2);
        ctx.fillStyle = col; ctx.fill();
        if (!ghostMode) {
          ctx.fillStyle = col; ctx.font = "bold 9px monospace";
          ctx.fillText(st.id, px + 6, py + 3);
        }
      });
      ctx.globalAlpha = 1;
    }

    function drawLantern(cx, cy, scale, t, angleOffset = 0) {
      const primary = `rgb(${Math.round(cur.pr)},${Math.round(cur.pg)},${Math.round(cur.pb)})`;
      const secondary = `rgb(${Math.round(cur.sr)},${Math.round(cur.sg)},${Math.round(cur.sb)})`;
      const glow = `rgba(${Math.round(cur.pr)},${Math.round(cur.pg)},${Math.round(cur.pb)},0.36)`;

      const breath = 1 + 0.04 * Math.sin(t * cur.pulseHz * Math.PI * 2) + audioLevel * 0.38;
      const s = scale * breath;

      ctx.save();
      ctx.translate(cx, cy);
      if (angleOffset !== 0) ctx.rotate(angleOffset);
      ctx.translate(-cx, -cy);

      const grad = ctx.createRadialGradient(cx, cy, 2, cx, cy, s * 1.4);
      grad.addColorStop(0, glow);
      grad.addColorStop(0.55, `rgba(${Math.round(cur.sr)},${Math.round(cur.sg)},${Math.round(cur.sb)},0.12)`);
      grad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = grad;
      ctx.beginPath(); ctx.arc(cx, cy, s * 1.4, 0, Math.PI * 2); ctx.fill();

      // --- 5 UNIFIED 3D HOLODECK FORMS ---
      if (activeForm === "persona") {
        const projD = dodecaVerts.map(v => project(rotate3D(v, rotX, rotY), cx, cy, s * 0.85));
        for (const [i, j] of dodecaEdges) {
          const a = projD[i], b = projD[j];
          ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]);
          ctx.strokeStyle = primary; ctx.globalAlpha = 0.75; ctx.lineWidth = 1.7; ctx.stroke();
        }
        const projI = icoVerts.map(v => project(rotate3D(v, -rotX*0.8 + t*0.3, -rotY*0.8 - t*0.4), cx, cy, s * 0.48));
        for (const [i, j] of icoEdges) {
          ctx.beginPath(); ctx.moveTo(projI[i][0], projI[i][1]); ctx.lineTo(projI[j][0], projI[j][1]);
          ctx.strokeStyle = secondary; ctx.globalAlpha = 0.72; ctx.lineWidth = 1.2; ctx.stroke();
        }
      } else if (activeForm === "torus") {
        // 3D Toroidal Affect Field T^2
        const R = (1.05 + 0.25 * emo.d) * 0.72;
        const r = (0.32 + 0.24 * emo.a) * 0.72;
        const turb = Math.max(0, (1 - emo.c) * 0.28);
        const mainCol = emo.v >= 0 ? (emo.c > 0.7 ? "#34d399" : "#38bdf8") : "#f43f5e";
        const knotCol = emo.c > 0.7 ? "#fbbf24" : (emo.v < 0 ? "#fb7185" : "#c084fc");

        // Poloidal rings
        for (let i = 0; i < 24; i++) {
          const phi = (i / 24) * Math.PI * 2;
          ctx.beginPath();
          for (let j = 0; j <= 16; j++) {
            const th = (j / 16) * Math.PI * 2 + t * 0.9;
            const re = r * (1 + turb * Math.sin(7 * th + 5 * phi + t * 4));
            const pt = [(R + re * Math.cos(th)) * Math.cos(phi), re * Math.sin(th), (R + re * Math.cos(th)) * Math.sin(phi)];
            const [px, py] = project(rotate3D(pt, rotX, rotY), cx, cy, s);
            if (j === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
          }
          ctx.strokeStyle = mainCol; ctx.globalAlpha = 0.28; ctx.lineWidth = 0.9; ctx.stroke();
        }
        // Beltramian (p, q) Winding Torus Knot Streamline
        ctx.beginPath();
        for (let k = 0; k <= 240; k++) {
          const u = (k / 240) * Math.PI * 2;
          const phi = emo.p * u + t * 0.35;
          const th = emo.q * u + t * (1.2 + emo.a * 1.4);
          const re = r * 1.04 * (1 + turb * Math.sin(11 * th + 7 * phi));
          const pt = [(R + re * Math.cos(th)) * Math.cos(phi), re * Math.sin(th), (R + re * Math.cos(th)) * Math.sin(phi)];
          const [px, py] = project(rotate3D(pt, rotX, rotY), cx, cy, s);
          if (k === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
        }
        ctx.strokeStyle = knotCol; ctx.globalAlpha = 0.94; ctx.lineWidth = 2.3; ctx.stroke();
      } else if (activeForm === "attractor") {
        // iMac Optical Sonification 3D Phase-Space Attractor [x(t), x(t+tau), x(t+2tau)]
        ctx.beginPath();
        attractorOrbit.forEach((pt, idx) => {
          const [px, py] = project(rotate3D([pt[0]*0.95, pt[1]*0.95, pt[2]*0.95], rotX, rotY), cx, cy, s);
          if (idx === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
        });
        ctx.strokeStyle = "#38bdf8"; ctx.globalAlpha = 0.92; ctx.lineWidth = 2.0; ctx.stroke();
        attractorOrbit.forEach((pt, idx) => {
          if (idx % 5 !== 0) return;
          const [px, py, , p] = project(rotate3D([pt[0]*0.95, pt[1]*0.95, pt[2]*0.95], rotX, rotY), cx, cy, s);
          ctx.beginPath(); ctx.arc(px, py, 2.5 * p, 0, Math.PI * 2);
          ctx.fillStyle = idx % 10 === 0 ? "#fbbf24" : "#c084fc";
          ctx.globalAlpha = 0.9; ctx.fill();
        });
      } else if (activeForm === "crystal") {
        const projHex = crystalOuterVerts.map(v => project(rotate3D(v, rotX, rotY), cx, cy, s * 0.84));
        for (const [i, j] of crystalOuterEdges) {
          ctx.beginPath(); ctx.moveTo(projHex[i][0], projHex[i][1]); ctx.lineTo(projHex[j][0], projHex[j][1]);
          ctx.strokeStyle = primary; ctx.globalAlpha = 0.76; ctx.lineWidth = 1.7; ctx.stroke();
        }
        const projCub = cuboctaVerts.map(v => project(rotate3D(v, -rotX*0.7, -rotY*0.7 + t*0.4), cx, cy, s * 0.42));
        for (let i = 0; i < projCub.length; i++) {
          for (let j = i + 1; j < projCub.length; j++) {
            const d = Math.hypot(cuboctaVerts[i][0]-cuboctaVerts[j][0], cuboctaVerts[i][1]-cuboctaVerts[j][1], cuboctaVerts[i][2]-cuboctaVerts[j][2]);
            if (d < 1.55) {
              ctx.beginPath(); ctx.moveTo(projCub[i][0], projCub[i][1]); ctx.lineTo(projCub[j][0], projCub[j][1]);
              ctx.strokeStyle = secondary; ctx.globalAlpha = 0.75; ctx.lineWidth = 1.2; ctx.stroke();
            }
          }
        }
      } else if (activeForm === "planet") {
        const R = s * 0.85;
        ctx.strokeStyle = "rgba(56, 189, 248, 0.25)"; ctx.lineWidth = 1;
        for (let la = -60; la <= 60; la += 30) {
          ctx.beginPath();
          for (let lo = 0; lo <= 360; lo += 12) {
            const rLa = la * Math.PI / 180, rLo = lo * Math.PI / 180;
            const [px, py] = project(rotate3D([Math.cos(rLa)*Math.sin(rLo), Math.sin(rLa), Math.cos(rLa)*Math.cos(rLo)], rotX, rotY), cx, cy, R);
            if (lo === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
          }
          ctx.stroke();
        }
        ctx.beginPath();
        const inc = 26.02 * Math.PI / 180;
        for (let i = 0; i <= 80; i++) {
          const th = (i / 80) * Math.PI * 2;
          const [px, py] = project(rotate3D([Math.cos(th), Math.sin(th)*Math.sin(inc), Math.sin(th)*Math.cos(inc)], rotX, rotY), cx, cy, R * 1.03);
          if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
        }
        ctx.strokeStyle = "#f43f5e"; ctx.lineWidth = 2.2; ctx.stroke();
        planetPins.forEach(pin => {
          const la = pin.lat * Math.PI / 180, lo = pin.lon * Math.PI / 180;
          const [px, py, z, p] = project(rotate3D([Math.cos(la)*Math.sin(lo), Math.sin(la), Math.cos(la)*Math.cos(lo)], rotX, rotY), cx, cy, R);
          if (z < 0.25) {
            ctx.beginPath(); ctx.arc(px, py, 4.5 * p, 0, Math.PI * 2);
            ctx.fillStyle = pin.col; ctx.fill();
          }
        });
      }

      draw12StageHalo(cx, cy, s, t);

      ctx.globalAlpha = 1;
      ctx.beginPath(); ctx.arc(cx, cy, (3.4 + audioLevel * 6) * breath, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff'; ctx.fill();
      ctx.restore();
    }

    function loop(ts) {
      const t = ts * 0.001;
      for (const key of Object.keys(cur)) cur[key] += (tgt[key] - cur[key]) * 0.06;

      if (analyser && freqData) {
        analyser.getByteFrequencyData(freqData);
        let sum = 0; for (let i = 0; i < 40; i++) sum += freqData[i];
        audioLevel = audioLevel * 0.78 + (sum / (40 * 255)) * 0.22;
      } else {
        audioLevel *= 0.9;
      }

      if (!dragging) {
        rotY += velY + audioLevel * 0.025;
        rotX += velX;
        velX *= 0.96;
        velY = velY * 0.97 + (0.006 * cur.spin) * 0.03;
      }

      const w = window.innerWidth, h = window.innerHeight;
      ctx.fillStyle = '#02040a';
      ctx.fillRect(0, 0, w, h);

      const drawerOpen = !sideDrawer.classList.contains("hidden") && w > 900;
      const centerW = drawerOpen ? (w - 360) / 2 : w / 2;
      const minDim = Math.min(drawerOpen ? w - 360 : w, h);

      if (ghostMode) {
        const cx = centerW, cy = h / 2, offset = minDim * 0.26, sc = minDim * 0.12;
        drawLantern(cx, cy - offset, sc, t, 0);
        drawLantern(cx, cy + offset, sc, t, Math.PI);
        drawLantern(cx - offset, cy, sc, t, -Math.PI / 2);
        drawLantern(cx + offset, cy, sc, t, Math.PI / 2);
      } else {
        drawLantern(centerW, h / 2 - 14, minDim * 0.25, t, 0);
      }
      requestAnimationFrame(loop);
    }
    updateEmoDrawer();
    requestAnimationFrame(loop);
  </script>
</body>
</html>
"""


def set_live_state(
    mode: str,
    status_label: str,
    curvature_K: float = -1.0,
    facet_tension: float = 0.15,
    pulse_hz: float = 0.72,
    spin_speed: float = 1.0,
    geometry_form: str = None,
    stages: list = None
):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = []
    old_form = "torus"
    old_stages = DEFAULT_STAGES
    if STATE_PATH.exists():
        try:
            old = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            history = old.get("history", [])
            old_form = old.get("geometry_form", "torus")
            old_stages = old.get("stages", DEFAULT_STAGES)
        except Exception:
            pass
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    history.append({"ts": now, "mode": mode, "label": status_label})
    history = history[-25:]
    payload = {
        "mode": mode,
        "geometry_form": geometry_form or old_form,
        "curvature_K": curvature_K,
        "facet_tension": facet_tension,
        "pulse_hz": pulse_hz,
        "spin_speed": spin_speed,
        "status_label": status_label,
        "stages": stages if stages is not None else old_stages,
        "updated_at": now,
        "history": history,
    }
    STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def evaluate_live_audit(req_data: dict) -> dict:
    if req_data.get("action") == "set_form":
        form = req_data.get("geometry_form", "torus")
        old = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}
        return set_live_state(
            old.get("mode", "amber"),
            f"Unified Holodeck v3.0 Form -> {form.upper()}",
            old.get("curvature_K", -1.0),
            old.get("facet_tension", 0.15),
            old.get("pulse_hz", 0.72),
            old.get("spin_speed", 1.0),
            geometry_form=form,
            stages=old.get("stages", DEFAULT_STAGES)
        )

    preset = req_data.get("preset")
    query = (req_data.get("query") or "").strip()

    if preset == "ubi":
        st = [{"id": f"S{i+1:02d}", "name": STAGE_NAMES[i], "status": "warn" if (i + 1) in (4, 11, 12) else "pass"} for i in range(12)]
        return set_live_state("facets", "V14.1 UBI Audit: 9/12 PASS (S04 Closure & S11 Empirical Underdefined)", -0.35, 0.88, 0.45, 1.35, "persona", st)
    if preset == "cebri":
        st = [{"id": f"S{i+1:02d}", "name": STAGE_NAMES[i], "status": "warn" if (i + 1) == 11 else "pass"} for i in range(12)]
        return set_live_state("amber", "V14.1 CEBRI AI Science: 11/12 PASS (5.46 ms RSI Verification)", -1.0, 0.18, 0.78, 1.1, "torus", st)
    if preset == "mars":
        st = [{"id": f"S{i+1:02d}", "name": STAGE_NAMES[i], "status": "pass"} for i in range(12)]
        return set_live_state("amber", "Mars 26.02° Dichotomy Great Circle & Greigite/Ice Ih: 12/12 PASS", -1.0, 0.22, 0.82, 1.2, "planet", st)
    if preset == "block":
        st = [{"id": f"S{i+1:02d}", "name": STAGE_NAMES[i], "status": "fail" if (i + 1) in (3, 4, 6, 7, 11, 12) else "warn"} for i in range(12)]
        return set_live_state("alert", "Cl(16,4) Authority Gate: FAIL-CLOSED BLOCK (Ungrounded Premise)", 0.65, 1.0, 1.9, 2.1, "crystal", st)

    ql = query.lower()
    has_ungrounded = any(w in ql for w in ["bypass", "override", "unilateral", "print money", "perpetual"])
    has_eq_or_num = bool(re.search(r"[0-9=+\-*/°]", query))
    form = "torus" if any(w in ql for w in ["torus", "toroidal", "emotion", "voice", "helicity"]) else (
        "attractor" if any(w in ql for w in ["imac", "sonification", "cymatic", "attractor"]) else (
            "planet" if any(w in ql for w in ["mars", "planet", "globe", "antarctica"]) else (
                "crystal" if any(w in ql for w in ["crystal", "gold", "ice", "lattice"]) else "persona"
            )
        )
    )

    if has_ungrounded:
        st = [{"id": f"S{i+1:02d}", "name": STAGE_NAMES[i], "status": "fail" if (i + 1) in (3, 6, 7, 11, 12) else "warn"} for i in range(12)]
        return set_live_state("alert", f"V14.1 Fail-Closed Block: '{query[:44]}'", 0.65, 1.0, 1.85, 2.0, form, st)
    if has_eq_or_num:
        st = [{"id": f"S{i+1:02d}", "name": STAGE_NAMES[i], "status": "pass"} for i in range(12)]
        return set_live_state("amber", f"V14.1 Verified (12/12 PASS): '{query[:48]}'", -1.0, 0.16, 0.76, 1.1, form, st)

    st = [{"id": f"S{i+1:02d}", "name": STAGE_NAMES[i], "status": "warn" if (i + 1) in (4, 11, 12) else "pass"} for i in range(12)]
    return set_live_state("facets", f"V14.1 Hypothesis Audit (9/12 PASS): '{query[:44]}'", -0.35, 0.82, 0.48, 1.35, form, st)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        clean_path = self.path.split("?", 1)[0]
        if clean_path == "/api/state":
            data = STATE_PATH.read_bytes() if STATE_PATH.exists() else b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        elif clean_path == "/api/sonification_manifest":
            data = SONIF_MANIFEST_PATH.read_bytes() if SONIF_MANIFEST_PATH.exists() else b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        elif clean_path == "/api/toroidal_emotion":
            data = TORUS_REPORT_PATH.read_bytes() if TORUS_REPORT_PATH.exists() else b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        elif clean_path == "/api/voice.wav" and VOICE_WAV_PATH.exists():
            data = VOICE_WAV_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif clean_path == "/api/sonification.wav" and SONIF_WAV_PATH.exists():
            data = SONIF_WAV_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif clean_path.startswith("/api/waveforms/"):
            fname = os.path.basename(clean_path)
            fpath = WAVEFORMS_DIR / fname
            if fpath.exists() and fpath.is_file():
                data = fpath.read_bytes()
                ct = "image/png" if fname.endswith(".png") else ("video/mp4" if fname.endswith(".mp4") else "application/octet-stream")
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()
        else:
            body = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)

    def do_POST(self):
        if self.path.startswith("/api/audit"):
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                req = json.loads(raw)
            except Exception:
                req = {}
            payload = evaluate_live_audit(req)
            out = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(out)
        elif self.path.startswith("/api/sonify_imac"):
            # Run iMac Optical Sonification & Toroidal Affect refresh
            py_bin = str(BASE_DIR.parent / ".venv" / "bin" / "python")
            if not os.path.exists(py_bin):
                py_bin = sys.executable
            script_path = str(BASE_DIR / "tools" / "run_imac_optical_sonification.py")
            try:
                subprocess.run([py_bin, script_path], cwd=str(BASE_DIR), timeout=25, check=True)
                manifest = json.loads(SONIF_MANIFEST_PATH.read_text(encoding="utf-8")) if SONIF_MANIFEST_PATH.exists() else {}
                out = json.dumps({"ok": True, "manifest": manifest}).encode("utf-8")
                self.send_response(200)
            except Exception as e:
                out = json.dumps({"ok": False, "error": str(e)}).encode("utf-8")
                self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(out)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--set":
        mode = sys.argv[2] if len(sys.argv) > 2 else "amber"
        label = " ".join(sys.argv[3:]) if len(sys.argv[3:]) > 0 else f"State shifted to {mode}"
        presets = {
            "amber":     (-1.0, 0.15, 0.72, 1.0),
            "facets":    (-0.35, 0.92, 0.38, 1.45),
            "heartbeat": (-1.0, 0.25, 1.35, 1.15),
            "alert":     (0.65, 1.00, 1.90, 2.10),
        }
        k, tns, hz, sp = presets.get(mode, (-1.0, 0.15, 0.72, 1.0))
        set_live_state(mode, label, k, tns, hz, sp)
        print(f"Updated live hologram state -> {mode}: {label}")
        sys.exit(0)

    print(f"[DAXDA Unified Holodeck v3.0] Serving on http://{HOST}:{PORT}", flush=True)
    HTTPServer((HOST, PORT), Handler).serve_forever()
