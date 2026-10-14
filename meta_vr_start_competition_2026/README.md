# DAXDA BioForge VR: Hands-First Medical Discovery Synthesizer

[![Meta VR Start](https://img.shields.io/badge/Meta%20VR%20Start-Developer%20Competition%202026-blue)](https://start-developer-competition-26.devpost.com/)
[![Track](https://img.shields.io/badge/Track-Gaming%20(Hands--First)-purple)](https://start-developer-competition-26.devpost.com/)
[![WebXR](https://img.shields.io/badge/WebXR-Immersive%20Hands%20(26--Joint)-brightgreen)](https://immersiveweb.dev/)
[![Tests](https://img.shields.io/badge/Tests-20%2F20%20Passing-success)](#automated-testing)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange)](LICENSE)

> **A hands-first spatial medical discovery game for Meta Quest & Meta VR Glasses.**  
> *Pick authentic DAXDA medical discoveries, manipulate bioelectric fields, and heal neural tissue—seated, with bare hands, zero controllers required.*

---

## 🌟 Executive Summary

**DAXDA BioForge VR** is conceived and built from a blank slate for the **Meta VR Start Developer Competition 2026 ($1M Prize Pool)**.

Placed inside a cutting-edge holographic clinical laboratory, players use their bare hands to interact with a floating catalog of **authentic DAXDA medical discoveries**, directly performing the exact biological, bioelectric, and molecular mechanism of each breakthrough:

1. **Multiple Sclerosis (MS) Axon Remyelination**: Pinch the `CN045` maturation ligand, dock it into the `GPR17` receptor pocket, and watch the myelin sheath wrap around the axon, restoring nerve velocity from $12.4\text{ m/s}$ to $118.5\text{ m/s}$.
2. **Cellular Regeneration Chamber**: Hover an open palm to scan resting membrane potential ($V_{\text{mem}}$), dial destructive RF frequencies to clear senescent cells, and aim a 670nm laser to accelerate ATP production by $+400\%$.
3. **Neuro-fMRI 360-Cortical Connectome**: Deconvolve double-gamma Hemodynamic Response Functions (HRF) and synchronize Centered Kernel Alignment (CKA) to $0.98$ across 360 Glasser cortical parcels.
4. **Riemannian BCI Motor Recovery**: Navigate an $S_d^{++}$ covariance manifold, guiding motor cortex covariance toward the Fréchet geometric mean to lock $10.2\text{ Hz}$ sensorimotor $\mu$-rhythm.
5. **Quantum Psychometrics**: Reorient projection measurement axes on a quantum Bloch sphere to eliminate cognitive order bias ($q_{\text{diff}} < 10^{-15}$), satisfying the Wang-Busemeyer QQ-equality invariant.

---

## 🎮 Hands-First Gestural Vocabulary

- ✋ **Index Poke**: Select medical protocols from the floating holographic discovery carousel.
- 🤏 **Precision Pinch**: Grasp molecular ligands (`CN045`), laser emitters, and projection vectors with millimeter fidelity.
- 🔄 **Wrist Dial Roll**: Continuously modulates $Cl(16,4)$ phase-shifts, RF frequencies, and temporal wave deconvolution.
- 🖐️ **Palm Hover**: Generates a 55Hz bioelectric diagnostic field scanning resting membrane potentials ($V_{\text{mem}}$).
- 🪑 **Airplane Seat Test Compliant**: All interactive holograms float strictly within a **0.60-meter (2-foot) radius** right in front of the player's chest. Zero roomscale steps or swatting.
- 🚌 **One Bus Stop Test Compliant**: Sub-2-second cold start, instant state checkpointing, and satisfying 2-to-3 minute discovery procedures.
- ⚙️ **Take It Away Test Compliant**: 100% entrant-built biological simulation, 26-joint hand tracking pipeline, and procedural Web Audio synthesis with zero third-party cloud API wrappers.

---

## 📁 Repository Structure

```
meta_vr_start_competition_2026/
├── LICENSE                                # Apache License 2.0 (Open Source)
├── README.md                              # This document
├── hand_engine/                           # 26-Joint Hand Tracking & Gesture Recognition
│   └── gesture_recognizer.py              # Precision pinch, power grab, wrist dial, seated guard
├── game_core/                             # Medical Discoveries & Kinetic Simulation
│   ├── medical_discoveries.py             # 5 Authentic DAXDA medical discovery state machines
│   └── chronosphere.py                    # Planetary gear ratios, sockets, and temporal scrubber
├── audio/                                 # Procedural Spatial Audio Engine
│   └── spatial_audio.py                   # Synthesis patches (clicks, chimes, ratchets, sweeps)
├── webxr_app/                             # WebXR Application & Desktop Simulator
│   ├── server.py                          # Zero-dependency Python server (port 8086)
│   └── static/
│       ├── index.html                     # WebXR HUD, medical carousel, and dual-mode controls
│       ├── style.css                      # Glassmorphism & Meta Quest dark aesthetic
│       └── app.js                         # Three.js WebXR render loop & hand simulator
├── tests/                                 # Automated Verification Suite
│   └── test_meta_vr_hands.py              # 20/20 automated unit & integration tests
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
*Expected: 20/20 tests passing in 0.06s.*

### 2. Launch Local WebXR & Desktop Simulator
```bash
python3 meta_vr_start_competition_2026/webxr_app/server.py 8086
```
Open **`http://localhost:8086`** in:
- **Meta Quest Browser**: Click **`🥽 Enter Meta Quest / VR WebXR`** to play with real bare hands.
- **Desktop Chrome / Safari / Edge**: Use the **Desktop Hand Simulator** with mouse drag, Spacebar pinch, and `R` key dial rotation.
