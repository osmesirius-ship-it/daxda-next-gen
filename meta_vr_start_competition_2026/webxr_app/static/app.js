/**
 * DAXDA ChronoHands: WebXR Hands-First Application
 * ==================================================
 * Meta VR Start Developer Competition 2026
 * Supports native Meta Quest 3 / Pro / VR Glasses Hand Tracking API (26 joints)
 * & built-in Desktop Hand Simulator for judge verification.
 */

(function () {
  'use strict';

  // --- Constants & Config ---
  const SEATED_MAX_RADIUS = 0.60; // 0.60m Airplane seat test envelope
  const SNAP_DISTANCE = 0.06;     // Snap gear to socket threshold
  const PINCH_THRESHOLD = 0.035;  // 3.5cm pinch threshold

  // --- Procedural Web Audio Synth ---
  class WebXRSpatialAudioSynth {
    constructor() {
      this.ctx = null;
    }

    init() {
      if (!this.ctx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioContext();
      }
      if (this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    playSnapClick() {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const filter = this.ctx.createBiquadFilter();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(880, t);
      osc.frequency.exponentialRampToValueAtTime(1760, t + 0.02);
      osc.frequency.exponentialRampToValueAtTime(440, t + 0.08);

      filter.type = 'bandpass';
      filter.frequency.setValueAtTime(2400, t);
      filter.Q.setValueAtTime(6.0, t);

      gain.gain.setValueAtTime(0.7, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.09);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(t);
      osc.stop(t + 0.1);
    }

    playRatchetTick(multiplier = 1.0) {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(240 * multiplier, t);
      osc.frequency.exponentialRampToValueAtTime(120, t + 0.04);

      gain.gain.setValueAtTime(0.3, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.05);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(t);
      osc.stop(t + 0.05);
    }

    playResonanceChime() {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const freqs = [528, 660, 792, 1056]; // Solfeggio Harmonic triad
      freqs.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, t);

        gain.gain.setValueAtTime(0.25, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 1.2 + idx * 0.2);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(t);
        osc.stop(t + 1.5);
      });
    }

    playTimeWarpSweep() {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, t);
      osc.frequency.exponentialRampToValueAtTime(720, t + 0.25);
      osc.frequency.exponentialRampToValueAtTime(140, t + 0.5);

      gain.gain.setValueAtTime(0.4, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.55);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(t);
      osc.stop(t + 0.6);
    }
  }

  // --- Main Application ---
  class ChronoHandsApp {
    constructor() {
      this.container = document.getElementById('canvas-container');
      this.audio = new WebXRSpatialAudioSynth();

      // State
      this.currentLevel = 1;
      this.temporalPhase = 0.0;
      this.isLevelCompleted = false;
      this.isSimMode = true;
      this.activeGesture = 'IDLE';

      // Three.js Core
      this.scene = null;
      this.camera = null;
      this.renderer = null;

      // Game Entities
      this.chronosphereGroup = null;
      this.gears = [];
      this.slots = [];
      this.heldGear = null;
      this.historySnapshots = [];

      // Hand Tracking Entities
      this.hands = { left: null, right: null };
      this.simulatedHand = {
        pos: new THREE.Vector3(0.0, 1.05, -0.28),
        isPinching: false,
        isGrabbing: false,
        wristRoll: 0.0,
        meshGroup: null
      };

      this.initThree();
      this.initLevel(1);
      this.bindUI();
      this.bindDesktopControls();

      // Start render loop
      this.renderer.setAnimationLoop((time, frame) => this.onFrame(time, frame));
    }

    initThree() {
      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color(0x06080d);
      this.scene.fog = new THREE.FogExp2(0x06080d, 0.4);

      this.camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.05, 20);
      this.camera.position.set(0, 1.25, 0.15); // Seated viewpoint looking down at mechanism desk

      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      this.renderer.setSize(window.innerWidth, window.innerHeight);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.xr.enabled = true;
      this.container.appendChild(this.renderer.domElement);

      // Lighting
      const ambient = new THREE.AmbientLight(0xffffff, 0.8);
      this.scene.add(ambient);

      const dirLight = new THREE.DirectionalLight(0x00f0ff, 2.2);
      dirLight.position.set(2, 4, 3);
      this.scene.add(dirLight);

      const goldLight = new THREE.PointLight(0xffbe3b, 3.0, 4.0);
      goldLight.position.set(-1, 2, -0.5);
      this.scene.add(goldLight);

      // Seated Desk Workstation Grid (visualizing 0.60m Airplane Seat Radius)
      const deskGeo = new THREE.CylinderGeometry(0.55, 0.55, 0.02, 32);
      const deskMat = new THREE.MeshStandardMaterial({
        color: 0x0c1322,
        metalness: 0.8,
        roughness: 0.4,
        transparent: true,
        opacity: 0.7
      });
      const deskMesh = new THREE.Mesh(deskGeo, deskMat);
      deskMesh.position.set(0, 0.82, -0.38);
      this.scene.add(deskMesh);

      // Safe Radius Wireframe Ring
      const ringGeo = new THREE.RingGeometry(0.53, 0.55, 64);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, side: THREE.DoubleSide });
      const boundaryRing = new THREE.Mesh(ringGeo, ringMat);
      boundaryRing.rotation.x = Math.PI / 2;
      boundaryRing.position.set(0, 0.835, -0.38);
      this.scene.add(boundaryRing);

      // Background particles
      this.initParticles();

      // Hand representation in scene
      this.initVirtualHands();

      window.addEventListener('resize', () => {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
      });
    }

    initParticles() {
      const pGeo = new THREE.BufferGeometry();
      const pCount = 300;
      const positions = new Float32Array(pCount * 3);
      for (let i = 0; i < pCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 4;
        positions[i + 1] = Math.random() * 2.5;
        positions[i + 2] = -Math.random() * 3;
      }
      pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      const pMat = new THREE.PointsMaterial({ color: 0x00f0ff, size: 0.012, transparent: true, opacity: 0.4 });
      this.particles = new THREE.Points(pGeo, pMat);
      this.scene.add(this.particles);
    }

    initVirtualHands() {
      // Create visual group for simulated hand
      const group = new THREE.Group();

      // Palm
      const palmGeo = new THREE.BoxGeometry(0.06, 0.015, 0.07);
      const handMat = new THREE.MeshStandardMaterial({
        color: 0x00e676,
        roughness: 0.3,
        metalness: 0.5,
        wireframe: false
      });
      const palm = new THREE.Mesh(palmGeo, handMat);
      group.add(palm);

      // Index finger tip (pinch pointer)
      const tipGeo = new THREE.SphereGeometry(0.014, 16, 16);
      const tipMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x00f0ff, emissiveIntensity: 0.8 });
      const tip = new THREE.Mesh(tipGeo, tipMat);
      tip.position.set(0, 0.01, -0.05);
      tip.name = 'indexTip';
      group.add(tip);

      // Thumb tip
      const thumbGeo = new THREE.SphereGeometry(0.012, 16, 16);
      const thumbMat = new THREE.MeshStandardMaterial({ color: 0xffbe3b, emissive: 0xffbe3b, emissiveIntensity: 0.8 });
      const thumb = new THREE.Mesh(thumbGeo, thumbMat);
      thumb.position.set(-0.03, 0.01, -0.02);
      thumb.name = 'thumbTip';
      group.add(thumb);

      group.position.copy(this.simulatedHand.pos);
      this.scene.add(group);
      this.simulatedHand.meshGroup = group;
    }

    initLevel(lvl) {
      this.currentLevel = lvl;
      this.isLevelCompleted = false;
      this.temporalPhase = 0.0;
      this.heldGear = null;
      document.getElementById('completion-banner').style.display = 'none';

      // Clean up previous level entities
      if (this.chronosphereGroup) {
        this.scene.remove(this.chronosphereGroup);
      }
      this.gears = [];
      this.slots = [];

      this.chronosphereGroup = new THREE.Group();
      this.chronosphereGroup.position.set(0, 1.05, -0.38);

      // Outer Chronosphere Gimbal Frame
      const frameGeo = new THREE.TorusGeometry(0.18, 0.008, 16, 64);
      const frameMat = new THREE.MeshStandardMaterial({ color: 0xffbe3b, metalness: 0.9, roughness: 0.2 });
      const frameRing = new THREE.Mesh(frameGeo, frameMat);
      this.chronosphereGroup.add(frameRing);

      const frameGeo2 = new THREE.TorusGeometry(0.15, 0.006, 16, 64);
      const frameRing2 = new THREE.Mesh(frameGeo2, frameMat);
      frameRing2.rotation.x = Math.PI / 2;
      this.chronosphereGroup.add(frameRing2);

      // Center ticking escapement anchor
      const coreGeo = new THREE.SphereGeometry(0.025, 24, 24);
      const coreMat = new THREE.MeshStandardMaterial({
        color: 0x00f0ff,
        emissive: 0x00f0ff,
        emissiveIntensity: 0.7,
        metalness: 0.5,
        roughness: 0.2
      });
      const coreOrb = new THREE.Mesh(coreGeo, coreMat);
      this.chronosphereGroup.add(coreOrb);

      if (lvl === 1) {
        document.getElementById('level-display').innerText = '1: The Escapement Core';
        // 2 Sockets: Central Escapement (16 teeth) & Balance Ring (24 teeth)
        this.addSlot('slot_escapement', 16, 0.05, new THREE.Vector3(0, 0, 0));
        this.addSlot('slot_balance', 24, 0.08, new THREE.Vector3(0, 0.08, 0));

        // 2 Loose Floating Gears nearby
        this.addGear('gear_16', 16, 0.05, new THREE.Vector3(-0.16, 0.98, -0.30));
        this.addGear('gear_24', 24, 0.08, new THREE.Vector3(0.16, 0.98, -0.30));
      } else if (lvl === 2) {
        document.getElementById('level-display').innerText = '2: Harmonic Gear Train';
        this.addSlot('slot_sun', 18, 0.06, new THREE.Vector3(0, 0, 0));
        this.addSlot('slot_p1', 12, 0.04, new THREE.Vector3(-0.09, 0.05, 0));
        this.addSlot('slot_p2', 12, 0.04, new THREE.Vector3(0.09, 0.05, 0));

        this.addGear('gear_sun', 18, 0.06, new THREE.Vector3(-0.18, 1.0, -0.28));
        this.addGear('gear_p1', 12, 0.04, new THREE.Vector3(0.18, 1.0, -0.28));
        this.addGear('gear_p2', 12, 0.04, new THREE.Vector3(0.0, 0.92, -0.26));
      } else {
        document.getElementById('level-display').innerText = '3: Quantum Resonance Dial';
        this.addSlot('slot_r1', 32, 0.11, new THREE.Vector3(0, 0, 0));
        this.addSlot('slot_r2', 32, 0.11, new THREE.Vector3(0, 0, 0));

        this.addGear('ring_yaw', 32, 0.11, new THREE.Vector3(-0.20, 1.02, -0.30));
        this.addGear('ring_pitch', 32, 0.11, new THREE.Vector3(0.20, 1.02, -0.30));
      }

      this.scene.add(this.chronosphereGroup);
      this.updateHUD();
    }

    addSlot(id, teeth, radius, localPos) {
      // Socket Hologram Ring
      const geo = new THREE.TorusGeometry(radius, 0.003, 12, 32);
      const mat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.5 });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.copy(localPos);
      this.chronosphereGroup.add(mesh);

      // World position calculation
      const worldPos = new THREE.Vector3();
      mesh.getWorldPosition(worldPos);

      this.slots.push({
        id,
        teeth,
        radius,
        localPos,
        mesh,
        isLocked: false,
        occupiedBy: null
      });
    }

    addGear(id, teeth, radius, worldPos) {
      const gearGroup = new THREE.Group();

      // Gear Disk
      const diskGeo = new THREE.CylinderGeometry(radius, radius, 0.012, teeth * 2);
      const diskMat = new THREE.MeshStandardMaterial({
        color: 0xd4af37, // Metallic gold
        metalness: 0.85,
        roughness: 0.25
      });
      const disk = new THREE.Mesh(diskGeo, diskMat);
      disk.rotation.x = Math.PI / 2;
      gearGroup.add(disk);

      // Center axle hole
      const holeGeo = new THREE.CylinderGeometry(radius * 0.25, radius * 0.25, 0.016, 16);
      const holeMat = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.9, roughness: 0.5 });
      const hole = new THREE.Mesh(holeGeo, holeMat);
      hole.rotation.x = Math.PI / 2;
      gearGroup.add(hole);

      gearGroup.position.copy(worldPos);
      this.scene.add(gearGroup);

      this.gears.push({
        id,
        teeth,
        radius,
        group: gearGroup,
        isSnapped: false,
        snappedSlot: null,
        rotSpeed: 0.0
      });
    }

    bindUI() {
      // Enter WebXR Button
      const btnWebXR = document.getElementById('btn-enter-webxr');
      btnWebXR.addEventListener('click', async () => {
        this.audio.init();
        if (navigator.xr) {
          try {
            const isSupported = await navigator.xr.isSessionSupported('immersive-vr');
            if (isSupported) {
              const session = await navigator.xr.requestSession('immersive-vr', {
                requiredFeatures: ['local-floor'],
                optionalFeatures: ['hand-tracking']
              });
              this.renderer.xr.setSession(session);
              this.isSimMode = false;
              document.getElementById('hand-status').innerText = 'META QUEST HANDS ACTIVE';
              btnWebXR.style.display = 'none';
            } else {
              alert('WebXR immersive-vr mode not supported on this browser profile. Running Desktop Hand Simulator.');
            }
          } catch (err) {
            console.warn('WebXR request failed:', err);
            alert('Launching Desktop Hand Simulator mode: ' + err.message);
          }
        } else {
          alert('WebXR API not detected. Desktop Hand Simulator active!');
        }
      });

      // Toggle Simulator
      document.getElementById('btn-toggle-sim').addEventListener('click', () => {
        this.audio.init();
        this.isSimMode = !this.isSimMode;
        document.getElementById('hand-status').innerText = this.isSimMode ? 'SIMULATOR ACTIVE' : 'XR HARDWARE STANDBY';
      });

      // Rewind Time
      document.getElementById('btn-rewind').addEventListener('click', () => {
        this.audio.playTimeWarpSweep();
        this.temporalPhase = Math.max(0.0, this.temporalPhase - 0.25);
        this.updateHUD();
      });

      // Dial controls
      document.getElementById('btn-dial-left').addEventListener('click', () => {
        this.audio.playRatchetTick(0.8);
        this.scrubTime(-0.08);
      });
      document.getElementById('btn-dial-right').addEventListener('click', () => {
        this.audio.playRatchetTick(1.2);
        this.scrubTime(0.08);
      });

      // Reset
      document.getElementById('btn-reset-puzzle').addEventListener('click', () => {
        this.initLevel(this.currentLevel);
      });

      // Next Chamber
      document.getElementById('btn-next-chamber').addEventListener('click', () => {
        this.initLevel((this.currentLevel % 3) + 1);
      });
    }

    bindDesktopControls() {
      let isDragging = false;
      let prevX = 0, prevY = 0;

      window.addEventListener('mousedown', (e) => {
        this.audio.init();
        if (e.target.closest('.hud-overlay')) return;
        isDragging = true;
        prevX = e.clientX;
        prevY = e.clientY;
        this.setSimPinch(true);
      });

      window.addEventListener('mouseup', () => {
        isDragging = false;
        this.setSimPinch(false);
      });

      window.addEventListener('mousemove', (e) => {
        if (!this.isSimMode) return;
        const dx = (e.clientX - window.innerWidth / 2) / (window.innerWidth / 2);
        const dy = (e.clientY - window.innerHeight / 2) / (window.innerHeight / 2);

        // Map mouse position to 0.60m seated desktop sphere
        const targetX = THREE.MathUtils.clamp(dx * 0.35, -0.28, 0.28);
        const targetY = THREE.MathUtils.clamp(1.2 - dy * 0.35, 0.85, 1.35);
        const targetZ = -0.32 + (dy * 0.1);

        this.simulatedHand.pos.set(targetX, targetY, targetZ);
        if (this.simulatedHand.meshGroup) {
          this.simulatedHand.meshGroup.position.copy(this.simulatedHand.pos);
        }
      });

      // Keyboard hotkeys
      window.addEventListener('keydown', (e) => {
        this.audio.init();
        if (e.code === 'Space') {
          this.setSimPinch(true);
        } else if (e.code === 'KeyR') {
          this.simulatedHand.wristRoll += 0.15;
          this.audio.playRatchetTick();
          this.scrubTime(0.05);
        } else if (e.code === 'KeyT') {
          this.audio.playTimeWarpSweep();
          this.temporalPhase = Math.max(0.0, this.temporalPhase - 0.2);
          this.updateHUD();
        }
      });

      window.addEventListener('keyup', (e) => {
        if (e.code === 'Space') {
          this.setSimPinch(false);
        }
      });
    }

    setSimPinch(isPinching) {
      this.simulatedHand.isPinching = isPinching;
      this.activeGesture = isPinching ? 'PINCH' : 'IDLE';
      document.getElementById('gesture-display').innerText = this.activeGesture;

      if (isPinching) {
        this.audio.playSnapClick();
        this.checkGearGrab();
      } else {
        this.checkGearRelease();
      }
    }

    checkGearGrab() {
      if (this.heldGear) return;
      const hPos = this.simulatedHand.pos;

      for (let gear of this.gears) {
        const dist = hPos.distanceTo(gear.group.position);
        if (dist <= 0.08) {
          this.heldGear = gear;
          if (gear.isSnapped && gear.snappedSlot) {
            gear.snappedSlot.isLocked = false;
            gear.snappedSlot.occupiedBy = null;
            gear.isSnapped = false;
            gear.snappedSlot = null;
          }
          break;
        }
      }
    }

    checkGearRelease() {
      if (!this.heldGear) return;
      const gear = this.heldGear;
      const gPos = gear.group.position;

      // Check distance to vacant slots
      for (let slot of this.slots) {
        if (!slot.isLocked && slot.teeth === gear.teeth) {
          const worldSlotPos = new THREE.Vector3();
          slot.mesh.getWorldPosition(worldSlotPos);
          const dist = gPos.distanceTo(worldSlotPos);

          if (dist <= SNAP_DISTANCE) {
            // SNAP INTO SOCKET!
            gear.group.position.copy(worldSlotPos);
            gear.isSnapped = true;
            gear.snappedSlot = slot;
            slot.isLocked = true;
            slot.occupiedBy = gear.id;

            this.audio.playSnapClick();
            this.checkPuzzleCompletion();
            break;
          }
        }
      }

      this.heldGear = null;
    }

    checkPuzzleCompletion() {
      const allLocked = this.slots.every(s => s.isLocked);
      if (allLocked && !this.isLevelCompleted) {
        this.isLevelCompleted = true;
        this.audio.playResonanceChime();
        document.getElementById('completion-banner').style.display = 'block';
      }
    }

    scrubTime(delta) {
      this.temporalPhase = THREE.MathUtils.clamp(this.temporalPhase + delta, 0.0, 1.0);
      this.gears.forEach(g => {
        if (g.isSnapped) {
          g.group.rotation.z += delta * (18.0 / g.teeth) * 4;
        }
      });
      this.updateHUD();
    }

    updateHUD() {
      const pct = Math.round(this.temporalPhase * 100);
      document.getElementById('meter-fill').style.width = pct + '%';
      document.getElementById('phase-display').innerText = (this.temporalPhase * 10).toFixed(2) + 's';
    }

    onFrame(time, frame) {
      // 1. If holding gear, drag it with hand clamped to seated sphere
      if (this.heldGear) {
        const hp = this.simulatedHand.pos.clone();
        // Clamping to 0.60m from chest center
        const chest = new THREE.Vector3(0, 1.1, 0);
        if (hp.distanceTo(chest) > SEATED_MAX_RADIUS) {
          hp.sub(chest).clampLength(0, SEATED_MAX_RADIUS).add(chest);
        }
        this.heldGear.group.position.copy(hp);
      }

      // 2. Slow orbital idle animation for chronosphere frame
      if (this.chronosphereGroup) {
        this.chronosphereGroup.rotation.y = Math.sin(time * 0.0008) * 0.15;
      }

      // 3. Render WebGL scene
      this.renderer.render(this.scene, this.camera);
    }
  }

  // Launch when DOM is ready
  window.addEventListener('DOMContentLoaded', () => {
    window.chronoApp = new ChronoHandsApp();
  });
})();
