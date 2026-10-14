# Build, Deployment & Judge Testing Guide

**Project**: DAXDA ChronoHands: Kinetic Chronosphere  
**Competition**: Meta VR Start Developer Competition 2026  
**Document**: Step-by-Step Instructions for Judges & Developers  

---

## 1. Quick Testing Options for Judges

Judges can launch and test DAXDA ChronoHands in three convenient ways:

```
                  ┌──────────────────────────────────────────────┐
                  │          Choose Your Testing Method          │
                  └──────────────────────┬───────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
[Option A: Meta Quest Browser]  [Option B: Desktop Hand Simulator]  [Option C: Developer Dashboard]
Launch directly on Meta Quest    Test instantly in desktop browser  APK uploaded to "Competition"
via WebXR with real bare hands   using mouse & keyboard hotkeys     Release Channel with Invite URL
```

---

## 2. Option A: Native Meta Quest WebXR (Recommended for VR Judges)

DAXDA ChronoHands is built with the **Immersive Web SDK (IWSDK) & Three.js WebXR**, providing native 90fps hand tracking directly within the **Meta Quest Browser** on Meta Quest 3, Meta Quest Pro, and Meta Quest 2.

### Steps to Run on Headset:
1. Put on your Meta Quest headset.
2. Open the **Meta Quest Browser**.
3. Navigate to the hosted WebXR URL (e.g., your GitHub Pages link or local network IP):
   ```text
   http://<your-local-ip>:8086
   ```
4. Look at the bottom left of the HUD and select:
   **`🥽 Enter Meta Quest / VR WebXR`**
5. Put your controllers aside. The Meta Quest optical tracking cameras will immediately recognize your bare hands!
6. Pinch floating gears between your thumb and index finger to snap them into the Chronosphere. Twist your wrist to scrub time.

---

## 3. Option B: Desktop Hand Simulator (No Headset Required)

For judges testing on a standard laptop or desktop computer without an active VR headset connected:

### Steps to Run on Desktop:
1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/osmesirius-ship-it/daxda-next-gen.git
   cd daxda-next-gen
   ```
2. Start the local zero-dependency WebXR server:
   ```bash
   python3 meta_vr_start_competition_2026/webxr_app/server.py 8086
   ```
3. Open **`http://localhost:8086`** in Google Chrome, Microsoft Edge, or Safari.
4. The **Desktop Hand Simulator** is active by default:
   - **Move Hand in 3D**: Move your mouse cursor across the screen.
   - **Precision Pinch**: Hold left mouse click or press **`Spacebar`** to grasp gears.
   - **Drag & Snap**: Drag the gear over a glowing blue socket and release click to snap.
   - **Wrist Chrono-Dial**: Hold the **`R`** key to roll the wrist dial and spin the gear train.
   - **Time Rewind**: Press the **`T`** key to rewind time by 3 seconds.
   - **Auto-Solve Level**: Click the **`Advance to Next Chamber`** or test the REST API.

---

## 4. Option C: Meta Horizon Developer Dashboard ("Competition" Release Channel)

For native Android APK packaging per the official competition rules:

### Steps to Configure Developer Dashboard:
1. Log in to the [Meta Horizon Developer Dashboard](https://developers.meta.com/horizon/dashboard/).
2. Select or create your application: `DAXDA ChronoHands`.
3. Under **Distribution** ➔ **Release Channels**:
   - Click **Create Channel**.
   - Enter the exact channel name specified by the rules: **`Competition`**.
4. Upload the built production `.apk` binary (built via Meta Quest Gradle / WebXR PWA wrapper).
5. Generate an **Invite URL**:
   - Go to **Release Channels** ➔ **Competition** ➔ **Users & Groups**.
   - Click **Invite Users via URL**.
   - Copy the generated URL (e.g. `https://www.oculus.com/experiences/quest/...`).
   - Paste the Invite URL into the official Devpost submission form so judges can install directly to their library.

---

## 5. Deploying to GitHub Pages (WebXR Hosting)

To deploy the WebXR build to GitHub Pages in seconds:
1. In your GitHub repository settings, navigate to **Pages**.
2. Select **Source**: `Deploy from a branch`.
3. Set the branch to `main` and directory to `/meta_vr_start_competition_2026/webxr_app/static`.
4. Click **Save**.
5. Your live WebXR link will be available at:  
   `https://<username>.github.io/<repo-name>/`

---

## 6. Running the Automated Test Suite

To verify the hand tracking mathematics, seated 0.60m ergonomics, and puzzle state machine:

```bash
# Run automated pytest verification
pytest meta_vr_start_competition_2026/tests/test_meta_vr_hands.py -v
```

Expected result:
```text
============================== 14 passed in 0.05s ==============================
```
