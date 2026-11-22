/**
 * DAXDA BioForge VR: Hands-First Medical Discovery Synthesizer
 * ==============================================================
 * Meta VR Start Developer Competition 2026
 * 
 * Allows the player to pick through all of DAXDA's medical discoveries
 * and virtually performs the exact scientific and biological mechanism
 * of each discovery using bare hands (no controllers).
 */

(function () {
  'use strict';

  // --- Constants & Config ---
  const SEATED_MAX_RADIUS = 0.60; // 0.60m Airplane Seat Test Envelope
  const SNAP_DISTANCE = 0.065;    // Magnetic docking threshold

  // --- Audio Synthesizer ---
  class BioSpatialAudioSynth {
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

    playSnapDock() {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(880, t);
      osc.frequency.exponentialRampToValueAtTime(1760, t + 0.03);
      osc.frequency.exponentialRampToValueAtTime(440, t + 0.09);

      gain.gain.setValueAtTime(0.7, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.1);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.1);
    }

    playLaserHum() {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(670, t); // 670Hz tone matching 670nm NIR laser
      osc.frequency.linearRampToValueAtTime(810, t + 0.2);

      gain.gain.setValueAtTime(0.35, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.25);
    }

    playNeuralChime() {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      [528, 660, 792, 1056].forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, t);

        gain.gain.setValueAtTime(0.2, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 1.2 + idx * 0.2);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 1.5);
      });
    }

    playBioelectricScan() {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(55, t); // 55Hz sub-bass
      osc.frequency.linearRampToValueAtTime(110, t + 0.3);

      gain.gain.setValueAtTime(0.5, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.4);
    }
  }

  // --- Medical Discovery Catalog Definitions ---
  const DISCOVERY_PROFILES = {
    MS_REMYELINATION: {
      id: 'MS_REMYELINATION',
      name: 'MS Axon Remyelination',
      target: 'GPR17 / CN045 / EBV Nullification',
      metricLabel: 'Nerve Conduction Velocity',
      baselineVal: 12.4,
      targetVal: 118.5,
      unit: 'm/s',
      instruction: 'Pinch the golden CN045 ligand and dock it into the GPR17 receptor pocket on the demyelinated axon.',
      completionDetails: 'The Cl(16,4) geometric phase-shift bound CN045 to GPR17, nullifying EBV inflammation and triggering oligodendrocyte precursor cell differentiation. Conduction velocity restored to 118.5 m/s!'
    },
    CELLULAR_REGEN_BED: {
      id: 'CELLULAR_REGEN_BED',
      name: 'Cellular Regen Chamber',
      target: 'V_mem Reversal & 670nm ATP Boost',
      metricLabel: 'Intracellular ATP Output',
      baselineVal: 100.0,
      targetVal: 485.0,
      unit: 'pmol/cell',
      instruction: 'Hover open palm to scan bioelectric V_mem, twist wrist to trigger senescent apoptosis, and aim 670nm laser to energize mitochondria.',
      completionDetails: 'Bioelectric resting membrane potential restored. 670nm NIR laser stimulated Cytochrome C Oxidase, accelerating cellular ATP production by +400%!'
    },
    NEURO_FMRI_CONNECTOME: {
      id: 'NEURO_FMRI_CONNECTOME',
      name: 'Neuro-fMRI Connectome',
      target: '360-Parcel Glasser CKA Sync',
      metricLabel: 'Representational Similarity (CKA)',
      baselineVal: 0.42,
      targetVal: 0.98,
      unit: 'CKA Score',
      instruction: 'Align asynchronous cortical parcels across left and right hemispheres using wrist dial rotation to synchronize double-gamma HRF.',
      completionDetails: 'Double-gamma HRF deconvolution completed across 360 Glasser cortical parcels. Inter-hemispheric phase coupling synchronized at 0.98 CKA correlation!'
    },
    RIEMANNIAN_BCI_RECOVERY: {
      id: 'RIEMANNIAN_BCI_RECOVERY',
      name: 'Riemannian BCI Recovery',
      target: 'S_d++ Covariance & Mu-Rhythm',
      metricLabel: 'Mu-Rhythm Sensorimotor Coherence',
      baselineVal: 0.28,
      targetVal: 0.94,
      unit: 'Coherence Index',
      instruction: 'Grasp the deviant covariance matrix on the curved SPD manifold and guide it toward the Fréchet geometric mean.',
      completionDetails: 'Riemannian tangent space mapping aligned motor cortex covariance on S_d++. Sensorimotor mu-rhythm (10.2Hz) restored, inducing active neuroplastic motor recovery!'
    },
    QUANTUM_PSYCHOMETRICS: {
      id: 'QUANTUM_PSYCHOMETRICS',
      name: 'Quantum Psychometrics',
      target: 'Wang-Busemeyer QQ Invariant',
      metricLabel: 'Wang-Busemeyer QQ Delta',
      baselineVal: 0.384,
      targetVal: 0.000,
      unit: 'q_diff Error',
      instruction: 'Reorient non-commutative measurement projection axes on the quantum Bloch sphere to satisfy the QQ equality.',
      completionDetails: 'Lüders quantum state projection verified. Cognitive context order bias completely eliminated (q_diff < 1e-15), restoring emotional and mental equilibrium!'
    }
  };

  // --- Main Application Class ---
  class BioForgeApp {
    constructor() {
      this.container = document.getElementById('canvas-container');
      this.audio = new BioSpatialAudioSynth();

      this.activeDiscoveryId = 'MS_REMYELINATION';
      this.progress = 0.0;
      this.isCompleted = false;
      this.isSimMode = true;
      this.activeGesture = 'IDLE';

      // Three.js Core
      this.scene = null;
      this.camera = null;
      this.renderer = null;

      // 3D Bio Objects
      this.bioGroup = null;
      this.interactiveEntity = null;
      this.dockTarget = null;
      this.heldObject = null;
      this.myelinSheaths = [];
      this.cellMeshes = [];
      this.actionPotentialPulses = [];

      // Simulated Hand
      this.simulatedHand = {
        pos: new THREE.Vector3(0.0, 1.05, -0.32),
        isPinching: false,
        meshGroup: null
      };

      this.initThree();
      this.loadDiscovery(this.activeDiscoveryId);
      this.bindUI();
      this.bindControls();

      this.renderer.setAnimationLoop((time, frame) => this.onFrame(time, frame));
    }

    initThree() {
      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color(0x05070c);
      this.scene.fog = new THREE.FogExp2(0x05070c, 0.35);

      this.camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.05, 20);
      this.camera.position.set(0, 1.25, 0.18); // Seated view looking at 0.60m desk zone

      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      this.renderer.setSize(window.innerWidth, window.innerHeight);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.xr.enabled = true;
      this.container.appendChild(this.renderer.domElement);

      // Lights
      const ambient = new THREE.AmbientLight(0xffffff, 0.9);
      this.scene.add(ambient);

      const cyanKey = new THREE.DirectionalLight(0x00f0ff, 2.5);
      cyanKey.position.set(2, 4, 3);
      this.scene.add(cyanKey);

      const goldFill = new THREE.PointLight(0xffbe3b, 2.8, 5.0);
      goldFill.position.set(-1.5, 2, -0.5);
      this.scene.add(goldFill);

      // Seated Desk (0.60m Airplane Seat Radius Indicator)
      const deskGeo = new THREE.CylinderGeometry(0.55, 0.55, 0.02, 32);
      const deskMat = new THREE.MeshStandardMaterial({
        color: 0x0a101d,
        metalness: 0.8,
        roughness: 0.3,
        transparent: true,
        opacity: 0.8
      });
      const desk = new THREE.Mesh(deskGeo, deskMat);
      desk.position.set(0, 0.82, -0.38);
      this.scene.add(desk);

      // Glowing Safe Perimeter Ring
      const ringGeo = new THREE.RingGeometry(0.53, 0.55, 64);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, side: THREE.DoubleSide });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      ring.position.set(0, 0.835, -0.38);
      this.scene.add(ring);

      this.initVirtualHands();

      window.addEventListener('resize', () => {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
      });
    }

    initVirtualHands() {
      const group = new THREE.Group();
      const palmGeo = new THREE.BoxGeometry(0.06, 0.015, 0.07);
      const palmMat = new THREE.MeshStandardMaterial({ color: 0x00e676, roughness: 0.3, metalness: 0.5 });
      const palm = new THREE.Mesh(palmGeo, palmMat);
      group.add(palm);

      const tipGeo = new THREE.SphereGeometry(0.014, 16, 16);
      const tipMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x00f0ff, emissiveIntensity: 0.8 });
      const tip = new THREE.Mesh(tipGeo, tipMat);
      tip.position.set(0, 0.01, -0.05);
      group.add(tip);

      const thumbGeo = new THREE.SphereGeometry(0.012, 16, 16);
      const thumbMat = new THREE.MeshStandardMaterial({ color: 0xffbe3b, emissive: 0xffbe3b, emissiveIntensity: 0.8 });
      const thumb = new THREE.Mesh(thumbGeo, thumbMat);
      thumb.position.set(-0.03, 0.01, -0.02);
      group.add(thumb);

      group.position.copy(this.simulatedHand.pos);
      this.scene.add(group);
      this.simulatedHand.meshGroup = group;
    }

    loadDiscovery(id) {
      this.activeDiscoveryId = id;
      this.progress = 0.0;
      this.isCompleted = false;
      this.heldObject = null;
      this.myelinSheaths = [];
      this.cellMeshes = [];
      this.actionPotentialPulses = [];
      document.getElementById('completion-banner').style.display = 'none';

      if (this.bioGroup) {
        this.scene.remove(this.bioGroup);
      }
      this.bioGroup = new THREE.Group();
      this.bioGroup.position.set(0, 1.05, -0.38);

      const p = DISCOVERY_PROFILES[id];
      document.getElementById('active-discovery-name').innerText = p.name;
      document.getElementById('metric-label').innerText = p.metricLabel;
      document.getElementById('instruction-text').innerText = p.instruction;
      this.updateHUD();

      // Update Carousel Active Card
      document.querySelectorAll('.discovery-card').forEach(c => {
        c.classList.toggle('active', c.getAttribute('data-id') === id);
      });

      // Construct the 3D Discovery Representation
      if (id === 'MS_REMYELINATION') {
        this.buildMSAxonScene();
      } else if (id === 'CELLULAR_REGEN_BED') {
        this.buildCellularRegenScene();
      } else if (id === 'NEURO_FMRI_CONNECTOME') {
        this.buildNeuroFMRIScene();
      } else if (id === 'RIEMANNIAN_BCI_RECOVERY') {
        this.buildRiemannianBCIScene();
      } else if (id === 'QUANTUM_PSYCHOMETRICS') {
        this.buildQuantumPsychometricsScene();
      }

      this.scene.add(this.bioGroup);
    }

    // --- 1. MS Remyelination 3D Scene ---
    buildMSAxonScene() {
      // Axon Cylinder Core
      const axonGeo = new THREE.CylinderGeometry(0.018, 0.018, 0.36, 32);
      const axonMat = new THREE.MeshStandardMaterial({ color: 0x334466, roughness: 0.6 });
      const axon = new THREE.Mesh(axonGeo, axonMat);
      axon.rotation.z = Math.PI / 2;
      this.bioGroup.add(axon);

      // GPR17 Receptor Target Pocket (Glowing Blue Ring)
      const pocketGeo = new THREE.TorusGeometry(0.035, 0.005, 16, 32);
      const pocketMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, wireframe: true });
      const pocket = new THREE.Mesh(pocketGeo, pocketMat);
      pocket.position.set(0, 0, 0);
      this.bioGroup.add(pocket);
      this.dockTarget = pocket;

      // 4 Myelin Sheath Segments (Initial unmyelinated / faint)
      [-0.12, -0.04, 0.04, 0.12].forEach(x => {
        const sheathGeo = new THREE.CylinderGeometry(0.032, 0.032, 0.065, 32);
        const sheathMat = new THREE.MeshStandardMaterial({
          color: 0xffbe3b,
          transparent: true,
          opacity: 0.15,
          roughness: 0.2
        });
        const sheath = new THREE.Mesh(sheathGeo, sheathMat);
        sheath.rotation.z = Math.PI / 2;
        sheath.position.set(x, 0, 0);
        this.bioGroup.add(sheath);
        this.myelinSheaths.push(sheath);
      });

      // Floating CN045 Maturation Ligand Molecule
      const ligandGeo = new THREE.DodecahedronGeometry(0.028);
      const ligandMat = new THREE.MeshStandardMaterial({
        color: 0xffbe3b,
        emissive: 0xffaa00,
        emissiveIntensity: 0.6,
        metalness: 0.8,
        roughness: 0.2
      });
      const ligand = new THREE.Mesh(ligandGeo, ligandMat);
      ligand.position.set(-0.16, -0.06, 0.08);
      this.bioGroup.add(ligand);
      this.interactiveEntity = ligand;
    }

    // --- 2. Cellular Regeneration Bed 3D Scene ---
    buildCellularRegenScene() {
      // Scanning Chamber Ring Base
      const baseGeo = new THREE.TorusGeometry(0.18, 0.008, 16, 48);
      const baseMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, metalness: 0.9 });
      const base = new THREE.Mesh(baseGeo, baseMat);
      base.rotation.x = Math.PI / 2;
      this.bioGroup.add(base);

      // Cell Cluster: 1 high-entropy senescent cell (red) + 4 healthy cells (blue)
      const redGeo = new THREE.SphereGeometry(0.035, 24, 24);
      const redMat = new THREE.MeshStandardMaterial({ color: 0xff3366, emissive: 0xff0044, emissiveIntensity: 0.7 });
      const redCell = new THREE.Mesh(redGeo, redMat);
      redCell.position.set(0, 0, 0);
      this.bioGroup.add(redCell);
      this.cellMeshes.push(redCell);
      this.dockTarget = redCell;

      // 670nm NIR Laser Emitter
      const laserGeo = new THREE.ConeGeometry(0.02, 0.07, 16);
      const laserMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x00aaff, emissiveIntensity: 0.8 });
      const laser = new THREE.Mesh(laserGeo, laserMat);
      laser.rotation.z = Math.PI / 4;
      laser.position.set(0.16, -0.05, 0.06);
      this.bioGroup.add(laser);
      this.interactiveEntity = laser;
    }

    // --- 3. Neuro-fMRI Connectome 3D Scene ---
    buildNeuroFMRIScene() {
      // Holographic Brain Left & Right Hemispheres
      const brainMat = new THREE.MeshStandardMaterial({
        color: 0x0077ff,
        wireframe: true,
        transparent: true,
        opacity: 0.4
      });
      const leftHemi = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 16), brainMat);
      leftHemi.position.set(-0.06, 0, 0);
      this.bioGroup.add(leftHemi);

      const rightHemi = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 16), brainMat);
      rightHemi.position.set(0.06, 0, 0);
      this.bioGroup.add(rightHemi);

      // Active Parcel Node to Align
      const parcelGeo = new THREE.IcosahedronGeometry(0.03, 1);
      const parcelMat = new THREE.MeshStandardMaterial({ color: 0x00e676, emissive: 0x00e676, emissiveIntensity: 0.8 });
      const parcel = new THREE.Mesh(parcelGeo, parcelMat);
      parcel.position.set(-0.14, 0.06, 0.08);
      this.bioGroup.add(parcel);
      this.interactiveEntity = parcel;

      const targetSlot = new THREE.Mesh(new THREE.SphereGeometry(0.035, 12, 12), new THREE.MeshBasicMaterial({ color: 0xffbe3b, wireframe: true }));
      targetSlot.position.set(0, 0.04, 0);
      this.bioGroup.add(targetSlot);
      this.dockTarget = targetSlot;
    }

    // --- 4. Riemannian BCI Recovery 3D Scene ---
    buildRiemannianBCIScene() {
      // Curved SPD Manifold Ellipsoid
      const spdGeo = new THREE.SphereGeometry(0.16, 32, 16);
      const spdMat = new THREE.MeshStandardMaterial({
        color: 0x112244,
        wireframe: true,
        transparent: true,
        opacity: 0.6
      });
      const spdManifold = new THREE.Mesh(spdGeo, spdMat);
      this.bioGroup.add(spdManifold);

      // Geodesic Center Target (Fréchet Mean)
      const frechetGeo = new THREE.RingGeometry(0.03, 0.035, 32);
      const frechetMat = new THREE.MeshBasicMaterial({ color: 0x00e676, side: THREE.DoubleSide });
      const frechetRing = new THREE.Mesh(frechetGeo, frechetMat);
      this.bioGroup.add(frechetRing);
      this.dockTarget = frechetRing;

      // Deviant Covariance Matrix Vector
      const covGeo = new THREE.OctahedronGeometry(0.032);
      const covMat = new THREE.MeshStandardMaterial({ color: 0xff3366, emissive: 0xff3366, emissiveIntensity: 0.7 });
      const covNode = new THREE.Mesh(covGeo, covMat);
      covNode.position.set(0.14, -0.06, 0.08);
      this.bioGroup.add(covNode);
      this.interactiveEntity = covNode;
    }

    // --- 5. Quantum Psychometrics 3D Scene ---
    buildQuantumPsychometricsScene() {
      // Quantum Bloch Sphere
      const blochGeo = new THREE.SphereGeometry(0.15, 32, 32);
      const blochMat = new THREE.MeshStandardMaterial({
        color: 0x07152e,
        transparent: true,
        opacity: 0.5,
        roughness: 0.2
      });
      const bloch = new THREE.Mesh(blochGeo, blochMat);
      this.bioGroup.add(bloch);

      // Equator Ring
      const eqGeo = new THREE.RingGeometry(0.148, 0.152, 64);
      const eqRing = new THREE.Mesh(eqGeo, new THREE.MeshBasicMaterial({ color: 0x00f0ff, side: THREE.DoubleSide }));
      eqRing.rotation.x = Math.PI / 2;
      this.bioGroup.add(eqRing);

      // Target QQ Invariant Node
      const targetGeo = new THREE.SphereGeometry(0.02, 16, 16);
      const targetMat = new THREE.MeshBasicMaterial({ color: 0x00e676, wireframe: true });
      const target = new THREE.Mesh(targetGeo, targetMat);
      target.position.set(0, 0.15, 0);
      this.bioGroup.add(target);
      this.dockTarget = target;

      // Density Operator Vector
      const stateGeo = new THREE.ConeGeometry(0.015, 0.06, 16);
      const stateMat = new THREE.MeshStandardMaterial({ color: 0xffbe3b, emissive: 0xffaa00, emissiveIntensity: 0.8 });
      const state = new THREE.Mesh(stateGeo, stateMat);
      state.position.set(-0.12, 0.04, 0.08);
      this.bioGroup.add(state);
      this.interactiveEntity = state;
    }

    bindUI() {
      // Discovery Card Selection (Index Poke / Click)
      document.querySelectorAll('.discovery-card').forEach(btn => {
        btn.addEventListener('click', (e) => {
          this.audio.init();
          const dId = btn.getAttribute('data-id');
          this.loadDiscovery(dId);
        });
      });

      // WebXR Button
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
              document.getElementById('hand-status').innerText = 'QUEST HANDS LIVE';
              btnWebXR.style.display = 'none';
            } else {
              alert('Immersive VR mode not supported on current browser profile. Desktop Hand Simulator active.');
            }
          } catch (err) {
            alert('WebXR launching fallback: ' + err.message);
          }
        }
      });

      document.getElementById('btn-toggle-sim').addEventListener('click', () => {
        this.audio.init();
        this.isSimMode = !this.isSimMode;
        document.getElementById('hand-status').innerText = this.isSimMode ? 'SIMULATOR ACTIVE' : 'XR HARDWARE STANDBY';
      });

      // Dial Controls
      document.getElementById('btn-dial-left').addEventListener('click', () => {
        this.audio.init();
        this.applyWristDial(-0.1);
      });
      document.getElementById('btn-dial-right').addEventListener('click', () => {
        this.audio.init();
        this.applyWristDial(0.1);
      });

      // Auto-Dock
      document.getElementById('btn-auto-dock').addEventListener('click', () => {
        this.audio.init();
        if (this.interactiveEntity && this.dockTarget) {
          this.interactiveEntity.position.copy(this.dockTarget.position);
          this.onEntityDocked();
        }
      });

      document.getElementById('btn-reset-puzzle').addEventListener('click', () => {
        this.loadDiscovery(this.activeDiscoveryId);
      });

      document.getElementById('btn-next-discovery').addEventListener('click', () => {
        const ids = Object.keys(DISCOVERY_PROFILES);
        const nextIdx = (ids.indexOf(this.activeDiscoveryId) + 1) % ids.length;
        this.loadDiscovery(ids[nextIdx]);
      });
    }

    bindControls() {
      let isDragging = false;

      window.addEventListener('mousedown', (e) => {
        this.audio.init();
        if (e.target.closest('.hud-overlay')) return;
        isDragging = true;
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

        // Seated 0.60m spherical coordinate projection
        const targetX = THREE.MathUtils.clamp(dx * 0.35, -0.28, 0.28);
        const targetY = THREE.MathUtils.clamp(1.2 - dy * 0.35, 0.85, 1.35);
        const targetZ = -0.32 + (dy * 0.08);

        this.simulatedHand.pos.set(targetX, targetY, targetZ);
        if (this.simulatedHand.meshGroup) {
          this.simulatedHand.meshGroup.position.copy(this.simulatedHand.pos);
        }
      });

      window.addEventListener('keydown', (e) => {
        this.audio.init();
        if (e.code === 'Space') {
          this.setSimPinch(true);
        } else if (e.code === 'KeyR') {
          this.applyWristDial(0.08);
        } else if (e.code === 'KeyH') {
          this.audio.playBioelectricScan();
          this.advanceProgress(0.12);
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
        // Check if hand is near interactive entity
        if (this.interactiveEntity && !this.heldObject) {
          const worldPos = new THREE.Vector3();
          this.interactiveEntity.getWorldPosition(worldPos);
          if (this.simulatedHand.pos.distanceTo(worldPos) <= 0.085) {
            this.heldObject = this.interactiveEntity;
            this.audio.playSnapDock();
          }
        }
      } else {
        // Release held object
        if (this.heldObject && this.dockTarget) {
          const entPos = new THREE.Vector3();
          const targetPos = new THREE.Vector3();
          this.heldObject.getWorldPosition(entPos);
          this.dockTarget.getWorldPosition(targetPos);

          if (entPos.distanceTo(targetPos) <= SNAP_DISTANCE) {
            // SNAP INTO TARGET!
            this.heldObject.position.copy(this.dockTarget.position);
            this.onEntityDocked();
          }
        }
        this.heldObject = null;
      }
    }

    applyWristDial(delta) {
      this.audio.playLaserHum();
      this.advanceProgress(Math.abs(delta) * 0.6);
      if (this.bioGroup) {
        this.bioGroup.rotation.y += delta * 2;
      }
    }

    onEntityDocked() {
      this.audio.playSnapDock();
      this.advanceProgress(0.65);

      // Trigger Discovery-Specific Biological Reaction:
      if (this.activeDiscoveryId === 'MS_REMYELINATION') {
        // Animate Myelin Sheath wrapping around axon!
        this.myelinSheaths.forEach(s => {
          s.material.opacity = 0.95;
          s.scale.set(1.15, 1.0, 1.15);
        });
      } else if (this.activeDiscoveryId === 'CELLULAR_REGEN_BED') {
        // Senescent cell apoptosis (fade red cell to green/blue healthy state)
        if (this.cellMeshes[0]) {
          this.cellMeshes[0].material.color.setHex(0x00e676);
          this.cellMeshes[0].material.emissive.setHex(0x00aa44);
        }
      }
    }

    advanceProgress(amount) {
      this.progress = Math.min(1.0, this.progress + amount);
      this.updateHUD();

      if (this.progress >= 0.999 && !this.isCompleted) {
        this.isCompleted = true;
        this.audio.playNeuralChime();
        const p = DISCOVERY_PROFILES[this.activeDiscoveryId];
        document.getElementById('completion-details').innerText = p.completionDetails;
        document.getElementById('completion-banner').style.display = 'block';
      }
    }

    updateHUD() {
      const p = DISCOVERY_PROFILES[this.activeDiscoveryId];
      const curVal = p.baselineVal + (p.targetVal - p.baselineVal) * this.progress;

      document.getElementById('metric-value').innerText = curVal.toFixed(1) + ' ' + p.unit;
      const pct = Math.round(this.progress * 100);
      document.getElementById('meter-fill').style.width = pct + '%';
      document.getElementById('progress-display').innerText = pct + '%';
    }

    onFrame(time, frame) {
      // 1. Drag held entity with hand clamped to seated sphere
      if (this.heldObject) {
        const hp = this.simulatedHand.pos.clone();
        // Convert to bioGroup local space
        if (this.bioGroup) {
          hp.sub(this.bioGroup.position);
        }
        this.heldObject.position.copy(hp);
      }

      // 2. Gentle orbital motion
      if (this.bioGroup) {
        this.bioGroup.rotation.y = Math.sin(time * 0.0006) * 0.12;
      }

      // 3. Render WebGL
      this.renderer.render(this.scene, this.camera);
    }
  }

  window.addEventListener('DOMContentLoaded', () => {
    window.bioForge = new BioForgeApp();
  });
})();
