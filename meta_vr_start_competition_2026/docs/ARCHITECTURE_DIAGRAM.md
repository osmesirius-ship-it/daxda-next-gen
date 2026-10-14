# Technical Architecture & System Specifications

**Project**: DAXDA BioForge VR: Hands-First Medical Discovery Synthesizer  
**Competition**: Meta VR Start Developer Competition 2026  
**Document**: Architecture Topology, Hand Tracking Pipeline, and Medical Discovery Engine Specifications  

---

## 1. High-Level System Architecture Topology

The following diagram illustrates the complete software architecture of DAXDA BioForge VR, showing the relationship between Meta VR hardware, the WebXR Hand Input API, the micro-gesture recognizer, the medical discovery simulation engine, and the procedural spatial audio synthesizer:

```mermaid
graph TB
    subgraph Hardware["Hardware & Platform Layer"]
        MQ["Meta Quest 3 / Pro / VR Glasses<br/>(Inside-Out Optical Tracking Cameras)"]
        BROWSER["Meta Quest Browser / WebXR Device Runtime<br/>(90fps Immersive-VR Session)"]
        SIM["Desktop XR Simulator<br/>(Virtual Hand Kinematics & Mouse Emulation)"]
    end

    subgraph HandTracking["WebXR Hand Tracking Pipeline"]
        XR_HAND["XRHand & XRJointPose Array<br/>(25 Joints per Hand at 90Hz)"]
        FILTER["Low-Pass Butterworth Velocity Filter<br/>(Jitter Reduction & Latency Compensation)"]
        GESTURE["Micro-Gesture Recognizer Engine<br/>• Precision Pinch (<28mm)<br/>• Palm Hover Field Scanner<br/>• Wrist Dial Rotor (<0.08 rad)<br/>• Bi-Manual Spatial Stretch"]
    end

    subgraph Governance["Seated Ergonomics Guard"]
        SEAT_GUARD["Airplane Seat Constraint Engine<br/>• Hard 0.60m Radius Perimeter Clamp<br/>• Elbow-Neutral Height Normalization (0.82m)<br/>• Zero Roomscale Enforcement"]
    end

    subgraph MedicalEngine["DAXDA Medical Discovery Simulation Engine"]
        DISCOVERY_MGR["Medical Discovery Protocol Manager<br/>(Interactive Catalog of 5 Breakthroughs)"]
        
        subgraph Protocols["Authentic DAXDA Biological Protocols"]
            P_MS["1. MS Remyelination<br/>GPR17 Pocket • CN045 Docking • Myelin Spiral"]
            P_REGEN["2. Cellular Regen Bed<br/>V_mem Scan • Senescent Apoptosis • 670nm ATP"]
            P_FMRI["3. Neuro-fMRI Connectome<br/>Double-Gamma HRF • 360-Parcel CKA Sync"]
            P_BCI["4. Riemannian BCI Recovery<br/>S_d++ Manifold • Karcher Flow • Mu-Rhythm"]
            P_QUANTUM["5. Quantum Psychometrics<br/>Bloch Sphere • Lüders State • Wang-Busemeyer QQ"]
        end
    end

    subgraph AudioEngine["3D Spatial Audio & Haptic Synth"]
        WEB_AUDIO["Procedural Web Audio API Synthesizer<br/>• 880Hz Metallic Docking Pulse<br/>• 670Hz Photobiomodulation Laser Hum<br/>• 528Hz Solfeggio Harmonic Chime<br/>• 55Hz Sub-Bass Magnetic Scan"]
        PANNER["WebXR HRTF Spatial Audio Panner<br/>(Inverse-Square Attenuation & Azimuth)"]
    end

    subgraph Presentation["Presentation & Render Loop"]
        THREE["Three.js WebGL / WebXR Render Pipeline<br/>(PBR Shaders, Axons, Cell Clusters, Brain Mesh)"]
        HUD["Bi-Focal Holographic HUD<br/>(Metric Gauge, Biological Progress, Comfort Rings)"]
    end

    %% Flow Connections
    MQ --> BROWSER
    SIM --> BROWSER
    BROWSER --> XR_HAND
    XR_HAND --> FILTER
    FILTER --> GESTURE

    GESTURE --> SEAT_GUARD
    SEAT_GUARD --> DISCOVERY_MGR

    DISCOVERY_MGR --> P_MS
    DISCOVERY_MGR --> P_REGEN
    DISCOVERY_MGR --> P_FMRI
    DISCOVERY_MGR --> P_BCI
    DISCOVERY_MGR --> P_QUANTUM

    DISCOVERY_MGR --> WEB_AUDIO
    WEB_AUDIO --> PANNER
    PANNER --> MQ

    DISCOVERY_MGR --> THREE
    GESTURE --> HUD
    THREE --> BROWSER
```

---

## 2. Real-Time Frame Execution Sequence (90Hz Loop)

The following sequence diagram details the frame-by-frame execution pipeline during a user pinch, molecular docking, and biological recovery:

```mermaid
sequenceDiagram
    autonumber
    actor Player as 👤 Player Hands
    participant Quest as 🥽 Meta Quest OS / XRHand
    participant Recognizer as ✋ Micro-Gesture Engine
    participant Guard as 🪑 Seated Guard (0.60m)
    participant Discovery as 🧬 Medical Engine
    participant Audio as 🔊 Spatial Audio Synth
    participant Renderer as 🖥️ Three.js WebXR Render Loop

    %% 90Hz Frame Tick
    Note over Player,Renderer: 90Hz WebXR RAF (RequestAnimationFrame) Tick
    Quest->>Recognizer: Stream 25 Joint Poses per hand (positions + orientations)
    Recognizer->>Recognizer: Compute Pinch Distance (Thumb Tip to Index Tip)
    
    alt Pinch Distance <= 0.028m (Precision Pinch)
        Recognizer->>Guard: Validate pinch world coordinates
        Guard-->>Recognizer: Clamped within 0.60m seated envelope
        Recognizer->>Discovery: interact_pinch_entity(hand_pos, radius=0.065m)
        Discovery-->>Renderer: Lock CN045 ligand to fingertip transform
    end

    alt Release Molecule near GPR17 Receptor (<= 0.065m)
        Player->>Recognizer: Open fingers (pinch distance > 0.035m)
        Recognizer->>Discovery: release_entity("cn045_ligand")
        Discovery->>Discovery: Snap ligand into receptor coordinates & lock
        Discovery->>Audio: trigger_event(SNAP_DOCK, world_pos)
        Audio-->>Player: Instant 880Hz metallic docking pulse (<15ms latency)
        Discovery->>Renderer: Animate golden myelin wrapping around axon
        Discovery->>Discovery: Update velocity metric (12.4 -> 118.5 m/s)
    end

    alt Wrist Dial Roll (Twist Hand)
        Player->>Recognizer: Rotate wrist forearm axis (Δroll)
        Recognizer->>Discovery: apply_wrist_dial_modulation(angle_delta)
        Discovery->>Audio: trigger_event(LASER_HUM, frequency)
        Audio-->>Player: Dynamic 670Hz tone with pitch glide
    end

    Discovery-->>Renderer: Update 3D bio-entities & active metric gauges
    Renderer-->>Player: Render stereo frame to Meta Quest displays
```

---

## 3. Mathematical & Biophysical Foundations

### 3.1 Seated Spherical Constraint Math
All biological interactions are constrained within a 0.60-meter radius of the player's seated sternum:
$$\mathcal{S}_{\text{seated}} = \{ \vec{p} \in \mathbb{R}^3 \mid \|\vec{p} - (0.0, 1.05, 0.0)\| \le 0.60\text{ m} \}$$

### 3.2 Biological State Transition Equations
1. **MS Remyelination ($Cl(16,4)$ Rotor Phase-Shift)**:
   $$V_{\text{conduction}} = V_{\text{baseline}} + (V_{\text{target}} - V_{\text{baseline}}) \cdot \Phi_{\text{myelin}}(t)$$
   where $V_{\text{baseline}} = 12.4\text{ m/s}$ and $V_{\text{target}} = 118.5\text{ m/s}$.
2. **Cellular Regeneration (670nm Photobiomodulation)**:
   $$\text{ATP}(t) = \text{ATP}_0 \cdot \left( 1 + 3.85 \cdot \int_0^t I_{670}(\tau) d\tau \right)$$
   accelerating baseline ATP ($100\text{ pmol}$) to $485\text{ pmol/cell}$ ($+400\%$).
3. **Riemannian BCI Covariance Manifold ($S_d^{++}$)**:
   Geodesic distance on the cone of symmetric positive-definite matrices under AIRM:
   $$\delta_{\text{AIRM}}(P_1, P_2) = \|\log(P_1^{-1/2} P_2 P_1^{-1/2})\|_F$$
   Fréchet geometric mean convergence restores $\mu$-rhythm sensorimotor coherence to $0.94$.

---

## 4. "Take It Away Test": 100% Offline Self-Containment

DAXDA BioForge VR operates **100% self-contained**:
- **Zero Cloud APIs**: No external LLMs, no remote databases.
- **Pure Procedural Audio**: Generates all sounds mathematically via Web Audio API.
- **Entrant-Built Biological Engine**: Every line of the medical discovery state machines, 26-joint hand recognizer, and WebXR render pipeline is original, entrant-built code.
