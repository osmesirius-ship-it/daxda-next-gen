# DAXDA ChronoHands: Kinetic Chronosphere

[![Meta VR Start](https://img.shields.io/badge/Meta%20VR%20Start-Developer%20Competition%202026-blue)](https://start-developer-competition-26.devpost.com/)
[![Track](https://img.shields.io/badge/Track-Gaming%20(Hands--First)-purple)](https://start-developer-competition-26.devpost.com/)
[![WebXR](https://img.shields.io/badge/WebXR-Immersive%20Hands%20(26--Joint)-brightgreen)](https://immersiveweb.dev/)
[![Tests](https://img.shields.io/badge/Tests-14%2F14%20Passing-success)](#automated-testing)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange)](LICENSE)

> **A hands-first spatial kinetic puzzle game for Meta Quest & Meta VR Glasses.**  
> *Manipulate time, snap gear mechanisms, and solve 3D chronospheres—seated, with bare hands, zero controllers required.*

---

## 🌟 Executive Summary

**DAXDA ChronoHands** is conceived and built from a blank slate for the **Meta VR Start Developer Competition 2026**.

In the tranquil heart of the Chrono-Archives, players use their bare hands to calibrate and assemble shattered **Chronospheres**—intricate 3D clockwork orbs that regulate the flow of time. Every single interaction is designed for **hands-first spatial interaction**, evaluated against the competition's strict seated design guidelines:

- ✋ **Hands-First**: Fully usable with bare hands end-to-end. Can be completed without ever pairing a controller.
- 🪑 **Airplane Seat Test Compliant**: All interactive gears, dials, and sockets float within a comfortable **0.60-meter (2-foot) radius** right in front of the player's chest. Zero roomscale steps or swatting.
- 🚌 **One Bus Stop Test Compliant**: Sub-2-second cold start, instant state checkpointing, and satisfying 3-to-5 minute chronological chambers.
- ⚙️ **Take It Away Test Compliant**: 100% entrant-built kinetic physics, 26-joint hand tracking pipeline, and procedural Web Audio synthesis with zero third-party cloud API wrappers.

---

## 🎮 Hands-First Gestural Vocabulary

| Gesture | Biomechanical Action | Game Function | Audio-Haptic Feedback |
| :--- | :--- | :--- | :--- |
| **Precision Pinch** | Thumb tip + Index tip contact ($\le 28\text{ mm}$) | Grasp floating brass gears & lock pins | 880Hz metallic mechanical click |
| **Magnetic Snap** | Release gear near vacant socket ($\le 60\text{ mm}$) | Snaps gear into socket alignment | Latching kinetic impulse |
| **Wrist Chrono-Dial** | Rotate forearm axis ($\Delta\theta_{\text{roll}}$) | Temporal scrubber (spins gear train in forward/reverse) | Dynamic mechanical ratchet ticks |
| **Bi-Manual Stretch** | Two-handed pinch pulled apart | Expands into exploded 3D schematic view | Harmonic resonance sweep |
| **Palm Hover** | Open palm facing Chronosphere | Emits gravitational containment field | 55Hz sub-bass magnetic hum |

---

## 📁 Repository Structure

```
meta_vr_start_competition_2026/
├── LICENSE                                # Apache License 2.0 (Open Source)
├── README.md                              # This document
├── hand_engine/                           # 26-Joint Hand Tracking & Gesture Recognition
│   └── gesture_recognizer.py              # Euclidean pinch, palm normals, and seated guard
├── game_core/                             # Kinetic Chronosphere Simulation Core
│   └── chronosphere.py                    # Planetary gear ratios, sockets, and temporal scrubber
├── audio/                                 # Procedural Spatial Audio Engine
│   └── spatial_audio.py                   # Synthesis patches (clicks, chimes, ratchets, sweeps)
├── webxr_app/                             # WebXR Application & Desktop Simulator
│   ├── server.py                          # Zero-dependency Python server (port 8086)
│   └── static/
│       ├── index.html                     # WebXR HUD, canvas, and dual-mode controls
│       ├── style.css                      # Glassmorphism & Meta Quest dark aesthetic
│       └── app.js                         # Three.js WebXR render loop & hand simulator
├── tests/                                 # Automated Verification Suite
│   └── test_meta_vr_hands.py              # 14/14 automated unit & integration tests
└── docs/                                  # Complete Submission Dossier
    ├── SUBMISSION_DETAILS.md              # Official Devpost submission form responses
    ├── HAND_INTERACTIONS_DESIGN.md        # Biomechanics, ergonomics, and accessibility
    ├── ARCHITECTURE_DIAGRAM.md            # System topology, sequence flows, and math
    ├── DEMO_VIDEO_SCRIPT.md               # 3-minute video voiceover script & visual cues
    └── BUILD_AND_DEPLOYMENT_GUIDE.md      # Quest Browser, Simulator, & Dashboard guide
```

---

## 🚀 Quickstart & Verification

### 1. Run Automated Test Suite
```bash
pytest meta_vr_start_competition_2026/tests/test_meta_vr_hands.py -v
```
*Expected: 14/14 tests passing in 0.05s.*

### 2. Launch Local WebXR & Desktop Simulator
```bash
python3 meta_vr_start_competition_2026/webxr_app/server.py 8086
```
Open **`http://localhost:8086`** in:
- **Meta Quest Browser**: Click **`🥽 Enter Meta Quest / VR WebXR`** to play with real bare hands.
- **Desktop Chrome / Safari / Edge**: Use the **Desktop Hand Simulator** with mouse drag, Spacebar pinch, and `R` key dial rotation.

---

## 📜 Devpost Submission Dossier

All formal competition documents are complete and ready for entry:
- **[Submission Form Text (`docs/SUBMISSION_DETAILS.md`)](docs/SUBMISSION_DETAILS.md)**
- **[Hand Interaction Design (`docs/HAND_INTERACTIONS_DESIGN.md`)](docs/HAND_INTERACTIONS_DESIGN.md)**
- **[System Architecture (`docs/ARCHITECTURE_DIAGRAM.md`)](docs/ARCHITECTURE_DIAGRAM.md)**
- **[3-Minute Demo Video Script (`docs/DEMO_VIDEO_SCRIPT.md`)](docs/DEMO_VIDEO_SCRIPT.md)**
- **[Build & Deployment Guide (`docs/BUILD_AND_DEPLOYMENT_GUIDE.md`)](docs/BUILD_AND_DEPLOYMENT_GUIDE.md)**
