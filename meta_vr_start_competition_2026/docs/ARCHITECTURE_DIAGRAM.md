# Technical Architecture & System Specifications

**Project**: DAXDA ChronoHands: Kinetic Chronosphere  
**Competition**: Meta VR Start Developer Competition 2026  
**Document**: Architecture Topology, Hand Tracking Pipeline, and Kinetic Physics Specifications  

---

## 1. High-Level System Architecture Topology

The following diagram illustrates the complete software architecture of DAXDA ChronoHands, showing the relationship between Meta VR hardware, the WebXR Hand Input API, the micro-gesture recognizer, the kinetic physics simulation, and the procedural spatial audio engine:

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
        GESTURE["Micro-Gesture Recognizer Engine<br/>• Precision Pinch Evaluator<br/>• Power Grab Detector<br/>• Wrist Dial Roll Calculator<br/>• Bi-Manual Spatial Span Calculator"]
    end

    subgraph Governance["Seated Ergonomics Guard"]
        SEAT_GUARD["Airplane Seat Constraint Engine<br/>• Hard 0.60m Radius Perimeter Clamp<br/>• Elbow-Neutral Height Normalization (0.82m)<br/>• Zero Roomscale Enforcement"]
    end

    subgraph Simulation["Core Kinetic Simulation Engine"]
        CHRONO["Chronosphere Simulation Core<br/>• Orbital Gimbal Rings (Yaw, Pitch, Roll)<br/>• Planetary Gear Ratios & Teeth Meshing<br/>• Magnetic Snap-to-Socket Solver"]
        TIME_SCRUB["Temporal Scrubber & State Rewind Vault<br/>• 600-Frame Circular Ring Buffer<br/>• Reversible Mechanical Momentum Engine"]
    end

    subgraph AudioEngine["3D Spatial Audio & Haptic Synth"]
        WEB_AUDIO["Procedural Web Audio API Synthesizer<br/>• 880Hz Metallic Snap Oscillator<br/>• Dynamic Ratchet Tick Generator<br/>• 528Hz Solfeggio Harmonic Chime<br/>• 55Hz Sub-Bass Magnetic Hum"]
        PANNER["WebXR HRTF Spatial Audio Panner<br/>(Inverse-Square Attenuation & Azimuth)"]
    end

    subgraph Presentation["Presentation & Render Loop"]
        THREE["Three.js WebGL / WebXR Render Pipeline<br/>(PBR Metallic Shaders & Particle Dust)"]
        HUD["Bi-Focal Holographic HUD<br/>(Temporal Meter, Level Badge, Comfort Indicators)"]
    end

    %% Flow Connections
    MQ --> BROWSER
    SIM --> BROWSER
    BROWSER --> XR_HAND
    XR_HAND --> FILTER
    FILTER --> GESTURE

    GESTURE --> SEAT_GUARD
    SEAT_GUARD --> CHRONO
    CHRONO <--> TIME_SCRUB

    CHRONO --> WEB_AUDIO
    WEB_AUDIO --> PANNER
    PANNER --> MQ

    CHRONO --> THREE
    GESTURE --> HUD
    THREE --> BROWSER
```

---

## 2. Real-Time Frame Execution Sequence (90Hz Loop)

The following sequence diagram details the frame-by-frame execution pipeline during a user pinch, gear snap, and temporal scrub:

```mermaid
sequenceDiagram
    autonumber
    actor Player as 👤 Player Hands
    participant Quest as 🥽 Meta Quest OS / XRHand
    participant Recognizer as ✋ Micro-Gesture Engine
    participant Guard as 🪑 Seated Guard (0.60m)
    participant Physics as ⚙️ Chronosphere Engine
    participant Audio as 🔊 Spatial Audio Synth
    participant Renderer as 🖥️ Three.js WebXR Render Loop

    %% 90Hz Frame Tick
    Note over Player,Renderer: 90Hz WebXR RAF (RequestAnimationFrame) Tick
    Quest->>Recognizer: Stream 25 Joint Poses per hand (positions + orientations)
    Recognizer->>Recognizer: Compute Pinch Distance (Thumb Tip to Index Tip)
    
    alt Pinch Distance <= 0.028m (Pinch Active)
        Recognizer->>Guard: Validate pinch world coordinates
        Guard-->>Recognizer: Clamped within 0.60m seated envelope
        Recognizer->>Physics: try_grab_gear(hand_pos, grab_radius=0.05m)
        Physics-->>Renderer: Lock gear to hand transform
    end

    alt Release Gear near Socket (<= 0.06m)
        Player->>Recognizer: Open fingers (pinch distance > 0.035m)
        Recognizer->>Physics: release_held_gear(gear_id)
        Physics->>Physics: Snap gear to socket coordinates & lock
        Physics->>Audio: trigger_event(SNAP_CLICK, world_pos)
        Audio-->>Player: Instant 880Hz metallic mechanical click (<15ms latency)
        Physics->>Physics: check_puzzle_completion()
    end

    alt Wrist Dial Roll (Twist Hand)
        Player->>Recognizer: Rotate wrist forearm axis (Δroll)
        Recognizer->>Physics: scrub_temporal_dial(angle_delta)
        Physics->>Physics: Rotate all meshed gears proportionally (18/teeth)
        Physics->>Audio: trigger_event(GEAR_RATCHET, velocity)
        Audio-->>Player: Dynamic ticking ratchet sound
    end

    Physics->>Physics: record_snapshot() [Circular History Buffer]
    Physics-->>Renderer: Update 3D gear rotations & socket holograms
    Renderer-->>Player: Render stereo frame to Meta Quest displays
```

---

## 3. Coordinate Systems & Mathematical Foundations

### 3.1 Spatial Reference Frames
1. **WebXR User Space (`local-floor`)**:
   - Origin $(0, 0, 0)$ is established at the floor center beneath the user's chair.
   - Headset rests at nominal seated eye-level $y \approx 1.25\text{ m}$.
2. **Torso Reference Frame**:
   - Established at the sternum: $\vec{P}_{\text{torso}} = (0.0, 1.05, 0.0)$.
   - The **Airplane Seat Safe Sphere** is defined as:
     $$\mathcal{S}_{\text{seated}} = \{ \vec{p} \in \mathbb{R}^3 \mid \|\vec{p} - \vec{P}_{\text{torso}}\| \le 0.60\text{ m} \}$$
3. **Chronosphere Object Frame**:
   - The central mechanism floats at $\vec{P}_{\text{chrono}} = (0.0, 1.05, -0.38)$, sitting exactly in the player’s lap-to-chest manipulation zone.

### 3.2 Gear Kinematics & Gear Ratio Math
When the user scrubs the temporal dial by angle $\Delta \theta$, each meshed gear rotates according to its tooth count relative to the driving escapement ($T_{\text{drive}} = 18$ teeth):
$$\Delta \phi_{\text{gear}} = \Delta \theta \cdot \left( \frac{T_{\text{drive}}}{T_{\text{gear}}} \right) \cdot (-1)^{\text{parity}}$$

This guarantees physically accurate gear meshing: smaller 12-tooth planetary gears spin $1.5\times$ faster than the sun gear, while large 24-tooth balance rings rotate at $0.75\times$ speed.

---

## 4. "Take It Away Test": Offline Self-Containment

The competition design rules demand:
> *"Original, not a wrapper: Core experience is Entrant-built. Apply the take it away test: if you remove the third-party service, is there still a Project?"*

DAXDA ChronoHands passes the "Take It Away Test" with flying colors:
- **Zero Cloud APIs**: No external LLM, no server-side physics, and no third-party game engine subscription.
- **Self-Contained Procedural Synthesis**: All audio frequencies and sound effects are generated algebraically from sine, triangle, and sawtooth waves in the client's audio buffer.
- **Entrant-Built Physics & Hand Logic**: Every line of the 26-joint skeleton parser, gesture recognizer, and gear meshing engine was written from scratch by Dexter and the DAXDA team.
- **100% Offline Capability**: Runs seamlessly in standalone offline headsets without internet access.
