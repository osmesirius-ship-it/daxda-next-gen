# Hand Interactions & Spatial Biomechanics Specification

**Project**: DAXDA ChronoHands: Kinetic Chronosphere  
**Competition**: Meta VR Start Developer Competition 2026  
**Document**: Hands-First Interaction Model, Gesture Biomechanics, and Seated Ergonomics  

---

## 1. Core Design Philosophy: Hands-First Interaction

In traditional VR experiences, controllers introduce artificial cognitive friction: players must remember which trigger grabs an object, which grip holds it, and which thumbstick rotates it. 

**DAXDA ChronoHands** eliminates all controller abstractions. The human hand is treated as the primary biological input device, leveraging millions of years of evolutionary dexterity.

```
                      +-----------------------------------+
                      |   26-Joint WebXR Hand Skeleton    |
                      +-----------------------------------+
                                        │
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
             [Discrete Micro-Gestures]      [Continuous Analog Kinematics]
             • Precision Pinch (<2.8cm)     • Wrist Dial Roll (Temporal Scrub)
             • Power Grab (<4.5cm)          • Bi-Manual Spatial Stretch
             • Index Poke (1.6x Extension)  • Palm Magnetic Attraction
                        │                               │
                        └───────────────┬───────────────┘
                                        ▼
                      +-----------------------------------+
                      |   Seated Ergonomics Guard (0.60m) |
                      +-----------------------------------+
                                        ▼
                      +-----------------------------------+
                      |   Kinetic Clockwork Simulation    |
                      +-----------------------------------+
```

---

## 2. 26-Joint Hand Skeleton Architecture

DAXDA ChronoHands natively parses the full **WebXR Hand Input Specification** (`XRHand`), tracking 25 individual joints per hand plus the root anchor:

| Digit | Tracked Joint Nodes | Key Interaction Roles |
| :--- | :--- | :--- |
| **Wrist** | `wrist` | Base transform, spatial anchor, wrist roll angular dial |
| **Thumb** | `thumb-metacarpal`, `thumb-phalanx-proximal`, `thumb-phalanx-distal`, `thumb-tip` | Precision pinch counter-surface, radial grip opposition |
| **Index** | `index-metacarpal`, `index-proximal`, `index-intermediate`, `index-distal`, `index-tip` | Primary pinch tip, kinetic poke trigger, precision pointing |
| **Middle** | `middle-metacarpal`, `middle-proximal`, `middle-intermediate`, `middle-distal`, `middle-tip` | Palm center calculation, stability surface for power grab |
| **Ring** | `ring-metacarpal`, `ring-proximal`, `ring-intermediate`, `ring-distal`, `ring-tip` | Curl metric calculation for fist/grab discrimination |
| **Pinky** | `pinky-metacarpal`, `pinky-proximal`, `pinky-intermediate`, `pinky-distal`, `pinky-tip` | Hand plane normal calculation, hand roll orientation |

### Palm Center & Plane Normal Computation
To establish a stable reference frame independent of finger curling:
```python
# Palm Center
palm_center = (wrist + index_mcp + middle_mcp) / 3.0

# Palm Normal (Unit Vector)
vector_across = pinky_mcp - index_mcp
vector_along  = middle_mcp - wrist
palm_normal   = normalize(vector_across x vector_along)
```

---

## 3. Gestural Vocabulary & State Machine

### 3.1 Precision Pinch (Primary Manipulation)
- **Biomechanical Trigger**: Euclidean distance between `thumb-tip` and `index-finger-tip` is $\le 28\text{ mm}$.
- **Hysteresis Filtering**: To prevent contact flickering, pinch activates at $\le 28\text{ mm}$ and releases at $> 35\text{ mm}$.
- **Affordance**: Grasping floating brass gears, pulling lock pins, and placing components into orbital sockets.
- **Audio Feedback**: Instant 880Hz metallic triangle click with high Q-factor filter.

### 3.2 Snap-to-Socket (Magnetic Kinetic Latching)
- **Trigger**: When a held gear is released within $60\text{ mm}$ of a matching vacant socket with identical tooth count.
- **Motion Curve**: The gear interpolates smoothly along a cubic Hermite curve into the exact socket transform over $90\text{ ms}$.
- **Affordance**: Delivers the satisfying physical sensation of clockwork meshing without requiring pixel-perfect millimeter precision.

### 3.3 Wrist Chrono-Dial (Temporal Scrubber)
- **Biomechanical Trigger**: Rotation of the hand around the forearm longitudinal axis (wrist roll angle $\theta_{\text{roll}}$).
- **Affordance**: Twisting your wrist clockwise scrubs time forward, accelerating the gear train; twisting counter-clockwise scrubs backward in time to inspect gear friction or reverse jams.
- **Haptic/Audio Feedback**: Dynamic ratchet ticks whose repetition rate scales proportionally with angular velocity ($\Delta \theta / \Delta t$).

### 3.4 Bi-Manual Spatial Stretch (Exploded Schematic View)
- **Biomechanical Trigger**: Concurrent precision pinches in both left and right hands.
- **Affordance**: Moving your hands apart expands the 3D Chronosphere into an exploded concentric schematic view; bringing hands together collapses the mechanism back into compact operating form.

### 3.5 Palm Hover & Magnetic Containment
- **Biomechanical Trigger**: Palm normal vector aligns with the Chronosphere center ($\vec{n}_{\text{palm}} \cdot \vec{v}_{\text{target}} > 0.65$).
- **Affordance**: Emits a gentle gravitational stabilization field that floats loose gears into an orderly arc in front of the player.
- **Audio Feedback**: Deep 55Hz sub-bass resonant hum.

---

## 4. Seated Ergonomics & The "Airplane Seat Test"

The competition guidelines state:
> *"Design for seated, stationary use. Limit roomscale, no large physical movement. Apply the airplane seat test: does every interaction work in a two-foot radius?"*

DAXDA ChronoHands strictly enforces this requirement via our `SeatedErgonomicsGuard`:

```
          [Headset / Player Viewpoint] (y = 1.25m)
                     │
                     ▼
          [Torso Origin] (y = 1.05m)
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    [Neutral Desk]          [Safe Sphere Boundary]
    Reach: 0.35m            Radius: 0.60m (2.0 ft)
    Height: 0.82m           All interactive entities clamped
```

### 1. Zero Roomscale Requirement
- The entire game is playable while seated comfortably in an office chair, couch, or airplane seat.
- No physical steps, ducking, or 360-degree torso turns are ever required.

### 2. Elimination of "Gorilla Arm" Fatigue
- Traditional VR forces players to hold their arms outstretched horizontally for long periods, causing severe shoulder and trapezius fatigue ("gorilla arm").
- In DAXDA ChronoHands, the interactive desk floats at an optimal **elbow-neutral angle**: elbows rest comfortably on armrests or against the torso, with hands operating at a natural 30° to 45° angle.

### 3. 0.60m Hard Clamping Envelope
- Every gear, socket, and UI button is programmatically constrained within a $0.60\text{ meter}$ spherical radius centered at the user's sternum:
$$\sqrt{x^2 + (y - 1.05)^2 + z^2} \le 0.60\text{ m}$$
- If a physics impulse propels a gear toward the boundary, the engine gently clamps and damps its velocity, keeping it within arm's reach.

---

## 5. Cross-Modal Audio-Haptic Perception

Because bare hands lack the motorized eccentric rotating mass (ERM) motors of physical controllers, DAXDA ChronoHands employs **cross-modal audio-haptic synthesis**:

1. **Psychoacoustic Tactile Illusions**:
   - Scientific studies in multisensory perception demonstrate that sharp, band-limited transient clicks synchronized within $15\text{ ms}$ of visual finger contact trigger an involuntary haptic perception in the brain, convincing the player they "felt" the object snap.
2. **Quest Controller-Free Haptic Micro-Pulses**:
   - On Meta Quest headsets supporting hand tracking haptic pulses, subtle high-frequency tactile impulses are delivered directly when pinches initiate.
3. **Pure Procedural Audio**:
   - All sounds are generated in real-time via the Web Audio API without pre-recorded MP3/WAV files, ensuring zero latency ($<5\text{ ms}$) between finger collision and audio emission.

---

## 6. Accessibility & Inclusivity

- **One-Handed Playability**: Every puzzle can be completed 100% using either hand alone. The bi-manual stretch gesture has a single-handed dial alternative.
- **Left-Handed & Right-Handed Parity**: Hand tracking automatically mirrors all gesture recognition algorithms for left or right handedness.
- **Adjustable Snap Radius**: Players with tremors or limited fine motor control can activate "Assistive Snap Mode", expanding the magnetic socket capture distance from $60\text{ mm}$ to $120\text{ mm}$.
