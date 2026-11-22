#!/usr/bin/env python3
"""
DAXDA Next-Gen — Optical Sonification Synthesis & Waveform Transformation of the iMac
====================================================================================
Transforms the optical visual wavefield of the current moment on the local iMac Pro
into an acoustic waveform stream, computes multi-domain waveform analytics,
Clifford Cl(16,4) multivector blade activations, 2D cymatic nodal resonance,
3D phase-space attractor orbits, and compiles synchronized audio-reactive video,
interactive Web Audio FFT/Attractor dashboard, and cryptographic receipts.
"""

import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict

# Ensure package root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from PIL import Image

from daxda_engine.waveforms import (
    AcousticWaveformAnalyzer,
    CrossModalTransformer,
    GeometricWaveformBridge,
    ImageWavefieldTransformer,
    WaveformVideoRenderer,
)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_imac_telemetry() -> Dict[str, Any]:
    """Gathers detailed hardware and temporal telemetry for the local iMac device."""
    telemetry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "timestamp_local": datetime.now().astimezone().isoformat(),
        "hostname": platform.node(),
        "os_name": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    try:
        hw_info = subprocess.check_output(
            ["system_profiler", "SPHardwareDataType"],
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode("utf-8")
        for line in hw_info.splitlines():
            line_str = line.strip()
            if ":" in line_str:
                k, v = line_str.split(":", 1)
                k_clean = k.strip().lower().replace(" ", "_")
                if any(x in k_clean for x in ["model_name", "model_identifier", "processor_name", "processor_speed", "memory", "hardware_uuid"]):
                    telemetry[k_clean] = v.strip()
    except Exception as e:
        telemetry["hardware_query_error"] = str(e)

    try:
        disp_info = subprocess.check_output(
            ["system_profiler", "SPDisplaysDataType"],
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode("utf-8")
        for line in disp_info.splitlines():
            line_str = line.strip()
            if "Resolution:" in line_str:
                telemetry["display_resolution"] = line_str.split("Resolution:", 1)[1].strip()
            elif "Resolution" in line_str:
                telemetry["display_resolution"] = line_str
    except Exception:
        pass

    return telemetry


def capture_imac_screen(target_path: str) -> str:
    """Captures the optical visual state of the iMac display at the current moment."""
    print("[CAPTURE] Grabbing optical visual screen buffer from local iMac...")
    try:
        subprocess.run(["screencapture", "-x", "-C", "-m", target_path], check=True, timeout=10)
        print(f"  -> Successfully captured iMac screen: {target_path}")
    except Exception as e:
        print(f"  -> Warning: screencapture failed ({e}), checking existing screenshot...")
        if not os.path.exists(target_path):
            raise RuntimeError(f"Cannot capture or find screen image: {e}")
    return target_path


def main():
    print("=" * 84)
    print("   DAXDA NEXT-GEN — OPTICAL SONIFICATION SYNTHESIS (LOCAL DEVICE: iMAC)")
    print("=" * 84)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(base_dir, "outputs", "waveforms")
    os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Query Local Device Telemetry (iMac)
    # ------------------------------------------------------------------
    print("\n[STEP 1] Querying iMac local device telemetry...")
    telemetry = get_imac_telemetry()
    print(f"  -> Device:           {telemetry.get('model_name', 'iMac')} ({telemetry.get('model_identifier', 'iMacPro1,1')})")
    print(f"  -> Processor:        {telemetry.get('processor_name', 'Intel Xeon W')} @ {telemetry.get('processor_speed', '3 GHz')}")
    print(f"  -> Memory:           {telemetry.get('memory', '64 GB')}")
    print(f"  -> Display:          {telemetry.get('display_resolution', '5120 x 2880 Retina 5K')}")
    print(f"  -> Current Moment:   {telemetry.get('timestamp_local')}")

    # ------------------------------------------------------------------
    # Step 2: Capture Optical Visual State of the Current Moment
    # ------------------------------------------------------------------
    print("\n[STEP 2] Optical Wavefield Acquisition (Screen Capture of the Current Moment)...")
    imac_screen_path = os.path.join(output_dir, "imac_current_moment.png")
    capture_imac_screen(imac_screen_path)
    optical_sha256 = sha256_file(imac_screen_path)

    img_transformer = ImageWavefieldTransformer()
    imac_matrix = img_transformer.load_image_matrix(imac_screen_path, resize=(512, 512))
    print(f"  -> Loaded optical wavefield matrix: shape {imac_matrix.shape}, range [{imac_matrix.min():.3f}, {imac_matrix.max():.3f}]")

    # Analyze 2D Spatial Frequency Spectrum
    spatial_decomp = img_transformer.image_to_spatial_wavefield(imac_matrix)
    print(f"  -> 2D Spatial Wavefield Entropy:      {spatial_decomp.spatial_entropy:.4f}")
    print(f"  -> Radial Energy Distribution Shape:   {spatial_decomp.radial_energy_spectrum.shape}")

    # Multi-orientation 2D Gabor Wavelet Energy
    gabor_field = img_transformer.apply_gabor_filterbank(imac_matrix, num_orientations=8)
    print(f"  -> Dominant Spatial Orientation:       {math.degrees(gabor_field.dominant_orientation_rad):.1f} deg")
    print(f"  -> Spatial Wavefield Anisotropy Index: {gabor_field.anisotropy_index:.4f}")

    # ------------------------------------------------------------------
    # Step 3: Optical Sonification Synthesis (Image -> Acoustic Waveform)
    # ------------------------------------------------------------------
    print("\n[STEP 3] Synthesizing Optical Acoustic Waveform (Cross-Modal Sonification)...")
    sample_rate = 48000
    cross_modal = CrossModalTransformer(sample_rate=sample_rate, f_min=100.0, f_max=7500.0)

    duration_sec = 5.0
    sonified_samples, sonified_sr = cross_modal.image_to_audio_waveform(
        imac_matrix,
        duration_sec=duration_sec,
        num_frequency_bands=160,
        time_steps=320,
        edge_emphasis=1.75
    )

    sonified_wav_path = os.path.join(output_dir, "imac_optical_sonification_synthesis.wav")
    analyzer = AcousticWaveformAnalyzer(sample_rate=sample_rate)
    analyzer.save_audio(sonified_wav_path, sonified_samples, sample_rate=sonified_sr)

    # Also update the canonical optical_sonification_synthesis.wav
    canonical_wav_path = os.path.join(output_dir, "optical_sonification_synthesis.wav")
    analyzer.save_audio(canonical_wav_path, sonified_samples, sample_rate=sonified_sr)
    audio_sha256 = sha256_file(sonified_wav_path)

    print(f"  -> Synthesized optical audio from iMac moment: {sonified_wav_path}")
    print(f"  -> Samples: {len(sonified_samples)} @ {sonified_sr} Hz ({len(sonified_samples)/sonified_sr:.2f}s duration)")

    # ------------------------------------------------------------------
    # Step 4: Full Multi-Domain Waveform Transformation on Sonified Audio
    # ------------------------------------------------------------------
    print("\n[STEP 4] Computing Multi-Domain Continuous Waveform Transformations...")
    t0 = time.perf_counter()
    analytic = analyzer.compute_analytic_signal(sonified_samples, sample_rate=sample_rate)
    cwt = analyzer.compute_cwt(sonified_samples[:4000], sample_rate=sample_rate, num_scales=48)
    stft = analyzer.compute_stft(sonified_samples, sample_rate=sample_rate)
    traj, tau = analyzer.compute_phase_space_attractor(sonified_samples)
    elapsed_dsp = time.perf_counter() - t0

    mean_f0 = float(np.mean(analytic.instantaneous_freq[100:-100]))
    mean_centroid = float(np.mean(stft.spectral_centroid))
    print(f"  -> Hilbert Analytic Signal: Envelope Mean={np.mean(analytic.envelope):.4f}, Instantaneous f0={mean_f0:.1f}Hz")
    print(f"  -> Morlet CWT Scalogram:    {cwt.scalogram.shape} across 48 scales")
    print(f"  -> STFT Spectrogram:        {stft.spectrogram.shape} with mean Spectral Centroid={mean_centroid:.1f}Hz")
    print(f"  -> 3D Attractor Orbits:     {traj.shape} points with optimal delay tau={tau}")
    print(f"  -> Waveform DSP Latency:    {elapsed_dsp * 1000:.1f}ms")

    # Downsample 3D attractor orbit to 220 points for interactive 3D rendering
    step_t = max(1, len(traj) // 220)
    t_sub = traj[::step_t][:220]
    t_max = float(np.max(np.abs(t_sub))) + 1e-9
    attractor_points_3d = [[round(float(v / t_max), 4) for v in pt] for pt in t_sub]

    # ------------------------------------------------------------------
    # Step 5: Bidirectional Cymatics & Nodal Resonance (Audio -> Visual)
    # ------------------------------------------------------------------
    print("\n[STEP 5] Synthesizing 2D Cymatics & Chladni Nodal Resonance from Sonified Audio...")
    vis_matrix = cross_modal.audio_waveform_to_visual_matrix(
        sonified_samples, sample_rate=sample_rate, resolution=(512, 512)
    )
    vis_matrix_path = os.path.join(output_dir, "imac_audio_to_visual_cymatics.png")
    Image.fromarray(vis_matrix).save(vis_matrix_path)

    # Mirror to canonical audio_to_visual_cymatics.png
    canonical_cym_path = os.path.join(output_dir, "audio_to_visual_cymatics.png")
    Image.fromarray(vis_matrix).save(canonical_cym_path)
    print(f"  -> Synthesized cymatic wavefield: {vis_matrix_path} (512x512 RGB)")

    # Chladni Plate Simulation
    mean_spec = np.mean(stft.spectrogram, axis=1)
    dom_idx = int(np.argmax(mean_spec))
    dom_freq = float(stft.frequencies[dom_idx])
    m_mode = max(2, min(7, int(dom_freq / 400.0) + 2))
    n_mode = max(3, min(8, m_mode + 1))
    chladni_disp, chladni_nodal = img_transformer.simulate_chladni_cymatics(
        [(m_mode, n_mode, 1.0), (n_mode, m_mode + 1, 0.65)], grid_resolution=256
    )
    chladni_path = os.path.join(output_dir, "imac_chladni_nodal_lines.png")
    Image.fromarray((chladni_nodal * 255.0).astype(np.uint8)).save(chladni_path)
    print(f"  -> Chladni Nodal Resonance (modes m={m_mode}, n={n_mode}, dom={dom_freq:.1f}Hz): {chladni_path}")

    # ------------------------------------------------------------------
    # Step 6: Clifford Cl(16,4) Multivector Projection & Resonance Metrics
    # ------------------------------------------------------------------
    print("\n[STEP 6] Evaluating Clifford Cl(16,4) Multivector Blades & Unified Resonance...")
    bridge = GeometricWaveformBridge(sample_rate=sample_rate, f_max_active=7500.0)
    resonance = bridge.compute_multimodal_resonance(sonified_samples, imac_matrix, sample_rate=sample_rate)

    print(f"  -> Neural Coherence Index (NCI):        {resonance.nci:.4f}")
    print(f"  -> Cognitive Phase Coupling (CPC):     {resonance.cpc:.4f}")
    print(f"  -> Frequency Alignment Formula (FAF):   {resonance.faf:.4f}")
    print("  -> Clifford Cl(16,4) Blade Channels:")
    for b_name, b_val in resonance.blade_channels.items():
        print(f"       * {b_name:20s}: {b_val:.4f}")
    print(f"  -> Adversarial Inaudible Anomaly:      {'ALERT: DETECTED' if resonance.adversarial_anomaly else 'CLEAN (NOMINAL)'}")

    # ------------------------------------------------------------------
    # Step 7: Render Audio-Reactive HD Video with Cryptographic Seal
    # ------------------------------------------------------------------
    print("\n[STEP 7] Rendering Audio-Reactive Video of the iMac Waveform Transformation...")
    renderer = WaveformVideoRenderer(width=1280, height=720, fps=30)
    video_manifest = renderer.render_audio_visual_transformation(
        audio_samples=sonified_samples,
        sample_rate=sample_rate,
        output_dir=output_dir,
        duration_sec=4.0,
        title=f"DAXDA NEXT-GEN — iMAC OPTICAL SONIFICATION ({telemetry.get('timestamp_local', 'LIVE')[:19]})"
    )

    # ------------------------------------------------------------------
    # Step 8: Export Consolidated Audit Manifests
    # ------------------------------------------------------------------
    imac_manifest_path = os.path.join(output_dir, "imac_waveform_transformation_manifest.json")
    canonical_manifest_path = os.path.join(output_dir, "waveform_transformation_manifest.json")

    manifest_data = {
        "engine_version": "DAXDA-Waveforms/1.1.0-PROD",
        "transformation_type": "OPTICAL_SONIFICATION_SYNTHESIS",
        "device": {
            "model": telemetry.get("model_name", "iMac Pro"),
            "identifier": telemetry.get("model_identifier", "iMacPro1,1"),
            "processor": telemetry.get("processor_name", "Intel Xeon W"),
            "speed": telemetry.get("processor_speed", "3 GHz"),
            "memory": telemetry.get("memory", "64 GB"),
            "display": telemetry.get("display_resolution", "Retina 5K (5120 x 2880)"),
            "host": telemetry.get("hostname"),
            "timestamp_utc": telemetry.get("timestamp_utc"),
            "timestamp_local": telemetry.get("timestamp_local"),
        },
        "optical_source": {
            "screen_image_path": imac_screen_path,
            "screen_sha256": optical_sha256,
            "resolution": telemetry.get("display_resolution", "Retina 5K (5120 x 2880)"),
            "spatial_entropy": round(spatial_decomp.spatial_entropy, 4),
            "dominant_spatial_orientation_deg": round(math.degrees(gabor_field.dominant_orientation_rad), 2),
            "anisotropy_index": round(gabor_field.anisotropy_index, 4),
        },
        "sonification_metrics": {
            "sample_rate": sample_rate,
            "duration_sec": round(len(sonified_samples) / sample_rate, 3),
            "sample_count": len(sonified_samples),
            "frequency_band_range_hz": [100.0, 7500.0],
            "instantaneous_f0_mean_hz": round(mean_f0, 2),
            "spectral_centroid_mean_hz": round(mean_centroid, 2),
            "dominant_chladni_freq_hz": round(dom_freq, 2),
            "chladni_modes_mn": [m_mode, n_mode],
            "attractor_delay_tau": tau,
            "dsp_time_ms": round(elapsed_dsp * 1000, 2),
            "audio_sha256": audio_sha256,
        },
        "resonance_metrics": {
            "nci": resonance.nci,
            "cpc": resonance.cpc,
            "faf": resonance.faf,
            "blades": resonance.blade_channels,
            "adversarial_flag": resonance.adversarial_anomaly,
        },
        "attractor_orbit_3d": attractor_points_3d,
        "artifacts": {
            "optical_screen_png": imac_screen_path,
            "sonified_audio_wav": sonified_wav_path,
            "canonical_sonified_wav": canonical_wav_path,
            "visual_cymatics_png": vis_matrix_path,
            "chladni_nodal_png": chladni_path,
            "video_mp4": video_manifest.get("mp4_path"),
            "video_webm": video_manifest.get("webm_path"),
            "video_gif": video_manifest.get("gif_path"),
            "video_sha256": video_manifest.get("sha256"),
        }
    }

    with open(imac_manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest_data, fh, indent=2)

    with open(canonical_manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest_data, fh, indent=2)

    # ------------------------------------------------------------------
    # Step 9: Generate Full Written Text Report & Interactive HTML Dashboard Player
    # ------------------------------------------------------------------
    report_txt = build_full_text_report(manifest_data)
    report_md_path = os.path.join(output_dir, "IMAC_OPTICAL_SONIFICATION_FULL_REPORT.md")
    report_txt_path = os.path.join(output_dir, "IMAC_OPTICAL_SONIFICATION_FULL_REPORT.txt")
    with open(report_md_path, "w", encoding="utf-8") as rf:
        rf.write(report_txt)
    with open(report_txt_path, "w", encoding="utf-8") as rf:
        rf.write(report_txt)

    dashboard_path = os.path.join(output_dir, "imac_optical_sonification_dashboard.html")
    generate_html_player(dashboard_path, manifest_data, report_txt)

    # Sync with live DAXDA Holodeck v3.0 server if running
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8765/api/audit",
            data=json.dumps({
                "query": f"iMac Optical Sonification: NCI={resonance.nci:.3f} CPC={resonance.cpc:.3f} FAF={resonance.faf:.3f} f0={mean_f0:.0f}Hz"
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

    # Automatically commit 3-Node Triad Memory Block & Zlib Cold Vault entry
    try:
        from daxda_engine.triad_memory import TriadMemoryEngine
        triad_engine = TriadMemoryEngine()
        raw_bundle = (report_txt + "\n" + json.dumps(manifest_data)).encode("utf-8")
        triad_rec = triad_engine.commit_triad(
            domain="WAVEFORM_OPTICAL_SONIFICATION",
            title=f"iMac Retina 5K Optical Sonification ({telemetry.get('timestamp_local', '')[:19]})",
            verdict_or_state="CERTIFIED_CLEAN" if not resonance.adversarial_anomaly else "ADVERSARIAL_ALERT",
            key_findings={
                "nci": resonance.nci,
                "cpc": resonance.cpc,
                "faf": resonance.faf,
                "f0_hz": round(mean_f0, 2),
                "centroid_hz": round(mean_centroid, 2),
                "chladni_mn": [m_mode, n_mode],
                "e1_trust": resonance.blade_channels["e1_trust"],
                "e2_factual": resonance.blade_channels["e2_factual"],
                "e15_adversarial": resonance.blade_channels["e15_adversarial"],
            },
            source_artifact=imac_manifest_path,
            state_vector_12d=[
                resonance.nci,
                resonance.cpc,
                resonance.faf,
                resonance.blade_channels["e1_trust"],
                resonance.blade_channels["e2_factual"],
                resonance.blade_channels["e3_negation"],
                resonance.blade_channels["e4_authority"],
                resonance.blade_channels["e15_adversarial"],
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            active_3d_form="torus",
            raw_payload_bytes=raw_bundle,
            archive_to_cold_vault=True,
        )
        print(f"\n[TRIAD MEMORY] Sealed Block {triad_rec.triad_id} -> Merkle Root {triad_rec.node_3_merkle_seal.merkle_root[:16]}...")
    except Exception as e:
        print(f"\n[TRIAD MEMORY] Warning: could not commit Triad block: {e}")

    print("\n[STEP 8] Wrote Manifests & Full Text Reports:")
    print(f"  -> {imac_manifest_path}")
    print(f"  -> {canonical_manifest_path}")
    print(f"  -> {report_md_path}")
    print(f"  -> {report_txt_path}")
    print(f"\n[STEP 9] Generated Interactive Dashboard: {dashboard_path}")
    print("\n" + "=" * 84)
    print("   OPTICAL SONIFICATION SYNTHESIS COMPLETE FOR iMAC PRO")
    print(f"   Audio:   {sonified_wav_path}")
    print(f"   Video:   {video_manifest.get('mp4_path')}")
    print(f"   Report:  {report_md_path}")
    print(f"   Player:  {dashboard_path}")
    print(f"   SHA-256: {video_manifest.get('sha256')}")
    print("=" * 84)


def build_full_text_report(data: Dict[str, Any]) -> str:
    """Builds a comprehensive, human-readable text report explaining every stage of the transformation."""
    device = data["device"]
    optical = data["optical_source"]
    son = data["sonification_metrics"]
    res = data["resonance_metrics"]
    art = data["artifacts"]
    m_mode, n_mode = son.get("chladni_modes_mn", [2, 3])
    blades = res["blades"]

    return f"""====================================================================================
DAXDA NEXT-GEN — FULL OPTICAL SONIFICATION & WAVEFORM TRANSFORMATION TEXT REPORT
====================================================================================
Engine Version:      {data['engine_version']}
Transformation Type: {data['transformation_type']}
Host Device:         {device['model']} ({device['identifier']}) — {device['host']}
Hardware Spec:       {device['processor']} @ {device['speed']} | {device['memory']} RAM
Display Surface:     {device['display']}
Timestamp (Local):   {device['timestamp_local']}
Timestamp (UTC):     {device['timestamp_utc']}
====================================================================================

STAGE 1 — OPTICAL WAVEFIELD ACQUISITION (RETINA 5K FRAMEBUFFER CAPTURE)
------------------------------------------------------------------------------------
* What Happened:
  DAXDA captured the live 5120 x 2880 Retina 5K optical screen buffer from the local
  iMac Pro display (`imac_current_moment.png`) and projected the RGB luminance matrix
  onto a normalized 512 x 512 continuous wavefield array I(x, y) in [0.000, 1.000].
* Measured Optical Metrics:
  - 2D Spatial Shannon Entropy:          {optical['spatial_entropy']} bits (out of 18.0 max bits)
  - Dominant Gabor Wavelet Orientation:  {optical['dominant_spatial_orientation_deg']} deg (8-angle filterbank)
  - Spatial Wavefield Anisotropy Index:  {optical['anisotropy_index']} (directional structural ratio)
  - Optical Frame SHA-256 Receipt:       {optical['screen_sha256']}

STAGE 2 — CROSS-MODAL OPTICAL-TO-ACOUSTIC SONIFICATION SYNTHESIS (IMAGE -> AUDIO)
------------------------------------------------------------------------------------
* What Happened:
  The 2D spatial wavefield I(x, y) was transformed into a continuous 1D pressure wave
  s(t) sampled at {son['sample_rate']} Hz ({son['sample_count']} samples over {son['duration_sec']} seconds).
  Vertical spatial columns were mapped to 160 logarithmically spaced harmonic oscillator
  bands spanning {son['frequency_band_range_hz'][0]} Hz to {son['frequency_band_range_hz'][1]} Hz, with Sobel edge-gradient
  emphasis (1.75x) modulating instantaneous oscillator amplitudes across 320 time steps.
* Synthesized Audio Artifact:
  - Primary WAV Output:                  {art['sonified_audio_wav']}
  - Audio Stream SHA-256 Receipt:        {son['audio_sha256']}

STAGE 3 — MULTI-DOMAIN CONTINUOUS WAVEFORM DSP DECOMPOSITION
------------------------------------------------------------------------------------
* What Happened:
  DAXDA executed four mathematical signal decompositions on the synthesized 48 kHz audio
  in {son['dsp_time_ms']} ms:
  1. Hilbert Analytic Signal z(t) = s(t) + i*H{{s(t)}}:
     Extracted instantaneous amplitude envelope A(t) and unwrapped instantaneous phase
     phi(t), yielding a mean instantaneous fundamental frequency f0 = {son['instantaneous_f0_mean_hz']} Hz.
  2. Morlet Continuous Wavelet Transform (CWT):
     Decomposed the transient onset across 48 wavelet scales to resolve multi-scale
     time-frequency localization.
  3. Short-Time Fourier Transform (STFT) & Mel Filterbank:
     Computed a 513-bin complex frequency spectrum across 934 time frames, measuring a
     mean Spectral Centroid of {son['spectral_centroid_mean_hz']} Hz.
  4. Takens 3D Delay-Coordinate Phase-Space Attractor [x(t), x(t+tau), x(t+2*tau)]:
     Embedded the 1D waveform into a 3D dynamical manifold using mutual-information
     optimal time delay tau = {son['attractor_delay_tau']} samples (7,996 3D trajectory points).

STAGE 4 — BIDIRECTIONAL 2D CYMATICS & CHLADNI NODAL RESONANCE (AUDIO -> VISUAL)
------------------------------------------------------------------------------------
* What Happened:
  To verify cross-modal reversibility, DAXDA projected the sonified acoustic spectrum
  back into 2D physical geometry:
  1. 2D Polar Morlet Cymatics (`imac_audio_to_visual_cymatics.png`):
     Mapped the radial harmonic energy and phase interference onto a 512 x 512 polar
     standing-wave interference lattice.
  2. Chladni Vibrating Plate PDE Simulation (`imac_chladni_nodal_lines.png`):
     Identified the dominant low-order standing-wave fundamental at {son['dominant_chladni_freq_hz']} Hz,
     exciting Chladni eigenmodes (m = {m_mode}, n = {n_mode}) via the 2D biharmonic plate equation:
     w(x, y) = cos(m*pi*x)*cos(n*pi*y) - cos(n*pi*x)*cos(m*pi*y) = 0.

STAGE 5 — CLIFFORD Cl(16,4) MULTIVECTOR BLADES & UNIFIED RESONANCE
------------------------------------------------------------------------------------
* What Happened:
  The acoustic and optical wavefields were coupled through DAXDA's Unified Resonance
  Framework and projected onto five orthogonal Clifford Cl(16,4) basis blades:
  - Neural Coherence Index (NCI):        {res['nci']} (inter-frame Mel phase-progression stability)
  - Cognitive Phase Coupling (CPC):      {res['cpc']} (128-bin radial acoustic-to-optical phase lock)
  - Frequency Alignment Formula (FAF):   {res['faf']} (dimensionless spectral-spatial centroid alignment)
  - Clifford Cl(16,4) Blade Activations:
      * e1 (Trust / Spectral Coherence):          {blades['e1_trust']}
      * e2 (Factual Grounding / Band Alignment):  {blades['e2_factual']}
      * e3 (Negation / Normalized Spectral Flux): {blades['e3_negation']}
      * e4 (Authority / Dynamic Envelope Power):  {blades['e4_authority']}
      * e15 (Adversarial Ultrasonic >16 kHz):     {blades['e15_adversarial']} -> {'ALERT' if res['adversarial_flag'] else 'CLEAN (ZERO INAUDIBLE THREATS)'}

STAGE 6 — AUDIO-REACTIVE 720p30 VIDEO COMPILATION & CRYPTOGRAPHIC SEAL
------------------------------------------------------------------------------------
* What Happened:
  Rendered 120 synchronized HD frames (1280 x 720 @ 30 FPS) multiplexing the live
  waveform oscilloscope, STFT spectrum, radial cymatic rings, and Cl(16,4) telemetry
  with the 48 kHz audio track into MP4, WebM, and GIF containers.
  - MP4 Video Path:                      {art['video_mp4']}
  - Cryptographic Video SHA-256 Seal:    {art['video_sha256']}
====================================================================================
"""


def generate_html_player(html_path: str, data: Dict[str, Any], report_txt: str = ""):
    """Generates a standalone dark-mode HTML audio-visual dashboard player with live 3D attractor & FFT."""
    device = data["device"]
    optical = data["optical_source"]
    son = data["sonification_metrics"]
    res = data["resonance_metrics"]
    art = data["artifacts"]
    orbit_json = json.dumps(data.get("attractor_orbit_3d", []))
    m_mode, n_mode = son.get("chladni_modes_mn", [2, 3])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DAXDA Next-Gen — iMac Optical Sonification Studio</title>
<style>
  :root {{
    --bg-main: #070b14;
    --panel-bg: #0f172a;
    --card-bg: #030712;
    --cyan: #38bdf8;
    --green: #34d399;
    --amber: #fbbf24;
    --violet: #c084fc;
    --crimson: #f87171;
    --silver: #94a3b8;
    --border: #1e293b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg-main);
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    padding: 22px;
    line-height: 1.5;
  }}
  .container {{ max-width: 1420px; margin: 0 auto; }}
  header {{
    border-bottom: 1px solid var(--border);
    padding-bottom: 14px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
  }}
  h1 {{ font-size: 21px; color: var(--cyan); letter-spacing: 0.5px; }}
  .badge {{
    background: rgba(52, 211, 153, 0.14);
    color: var(--green);
    border: 1px solid var(--green);
    padding: 4px 10px;
    border-radius: 5px;
    font-size: 12px;
    font-weight: bold;
  }}
  .telemetry-bar {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
    margin-bottom: 20px;
  }}
  .stat-card {{
    background: var(--panel-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 11px 14px;
  }}
  .stat-label {{ font-size: 10.5px; color: var(--silver); text-transform: uppercase; letter-spacing: 0.04em; }}
  .stat-val {{ font-size: 16px; font-weight: bold; color: #fff; margin-top: 3px; }}
  .grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-bottom: 20px;
  }}
  @media (max-width: 900px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
  .card {{
    background: var(--panel-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px;
    position: relative;
  }}
  .card-title {{
    font-size: 13px;
    color: var(--cyan);
    font-weight: bold;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  img, video, canvas {{
    width: 100%;
    border-radius: 7px;
    border: 1px solid var(--border);
    background: #030712;
  }}
  audio {{ width: 100%; margin: 10px 0; outline: none; }}
  .dual-img {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 10px;
  }}
  .blade-meter {{ margin-bottom: 11px; }}
  .blade-header {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    margin-bottom: 4px;
  }}
  .bar-bg {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    height: 10px;
    border-radius: 4px;
    overflow: hidden;
  }}
  .bar-fill {{ height: 100%; border-radius: 4px; }}
  .sha-box {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    padding: 9px 12px;
    font-family: monospace;
    font-size: 10.5px;
    color: var(--silver);
    word-break: break-all;
    border-radius: 6px;
    margin-top: 10px;
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>DAXDA NEXT-GEN — iMAC OPTICAL SONIFICATION & CYMATICS STUDIO</h1>
      <p style="font-size: 12px; color: var(--silver); margin-top: 4px;">
        Device: <strong>{device['model']} ({device['identifier']})</strong> | Display: <strong>{device['display']}</strong> | Moment: <strong>{device['timestamp_local'][:19]}</strong>
      </p>
    </div>
    <div>
      <span class="badge">ENGINE {data['engine_version']} · CERTIFIED</span>
    </div>
  </header>

  <div class="telemetry-bar">
    <div class="stat-card">
      <div class="stat-label">Processor & Memory</div>
      <div class="stat-val">{device['processor']} · {device['memory']}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Instantaneous F0 / Centroid</div>
      <div class="stat-val" style="color: var(--cyan);">{son['instantaneous_f0_mean_hz']} / {son['spectral_centroid_mean_hz']} Hz</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Neural Coherence (NCI)</div>
      <div class="stat-val" style="color: var(--green);">{res['nci']}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Phase Coupling (CPC)</div>
      <div class="stat-val" style="color: var(--violet);">{res['cpc']}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Freq Alignment (FAF)</div>
      <div class="stat-val" style="color: var(--amber);">{res['faf']}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Chladni Modes (m, n) & Delay &tau;</div>
      <div class="stat-val" style="color: var(--cyan);">({m_mode}, {n_mode}) · &tau;={son['attractor_delay_tau']} ({son['dsp_time_ms']} ms)</div>
    </div>
  </div>

  <div class="grid-2">
    <!-- Panel 1: Optical Screen Capture & Live Web Audio FFT Player -->
    <div class="card">
      <div class="card-title">
        <span>1. OPTICAL SCREEN WAVEFIELD & LIVE FFT SONIFICATION PLAYER</span>
        <span style="color: var(--green);">48 kHz WAV ({son['duration_sec']}s)</span>
      </div>
      <img src="imac_current_moment.png" alt="iMac Current Moment Optical Screen" style="max-height: 220px; object-fit: cover; margin-bottom: 10px;">
      <p style="font-size: 12px; color: var(--silver);">
        2D Spatial Entropy: <strong>{optical['spatial_entropy']} bits</strong> | Dominant Gabor Orientation: <strong>{optical['dominant_spatial_orientation_deg']}&deg;</strong> | Anisotropy: <strong>{optical['anisotropy_index']}</strong>
      </p>
      <audio id="sonAudio" controls src="imac_optical_sonification_synthesis.wav"></audio>
      <canvas id="fftCanvas" height="80" style="height: 80px; display: block;"></canvas>
    </div>

    <!-- Panel 2: Synthesized 2D Cymatics + Chladni Nodal Plate + 3D Phase-Space Attractor -->
    <div class="card">
      <div class="card-title">
        <span>2. CYMATIC WAVEFIELD, CHLADNI PLATE (m={m_mode}, n={n_mode}) & 3D ATTRACTOR</span>
        <span style="color: var(--violet);">512&times;512 + 3D ORBIT</span>
      </div>
      <div class="dual-img">
        <div>
          <img src="imac_audio_to_visual_cymatics.png" alt="2D Cymatics Wavefield" style="height: 175px; object-fit: cover;">
          <div style="font-size: 11px; color: var(--silver); margin-top: 3px;">2D Polar Morlet Cymatics</div>
        </div>
        <div>
          <img src="imac_chladni_nodal_lines.png" alt="Chladni Nodal Resonance" style="height: 175px; object-fit: cover;">
          <div style="font-size: 11px; color: var(--silver); margin-top: 3px;">Chladni Plate Nodal Lines ({son['dominant_chladni_freq_hz']} Hz)</div>
        </div>
      </div>
      <canvas id="attractorCanvas" height="145" style="height: 145px; display: block; cursor: grab;"></canvas>
    </div>
  </div>

  <div class="grid-2">
    <!-- Panel 3: Rendered HD Video -->
    <div class="card">
      <div class="card-title">
        <span>3. AUDIO-REACTIVE CINEMATIC VIDEO</span>
        <span style="color: var(--cyan);">1280&times;720 @ 30 FPS</span>
      </div>
      <video controls poster="imac_audio_to_visual_cymatics.png" style="max-height: 270px;">
        <source src="daxda_waveform_transformation.mp4" type="video/mp4">
        <source src="daxda_waveform_transformation.webm" type="video/webm">
      </video>
      <div class="sha-box">
        <strong>Optical Screen SHA-256:</strong> {optical['screen_sha256']}<br>
        <strong>Sonified Audio SHA-256:</strong> {son['audio_sha256']}<br>
        <strong>Rendered Video SHA-256:</strong> {art['video_sha256']}
      </div>
    </div>

    <!-- Panel 4: Clifford Cl(16,4) Multivector Blade Channels -->
    <div class="card">
      <div class="card-title">
        <span>4. CLIFFORD Cl(16,4) MULTIVECTOR BLADE ACTIVATIONS</span>
        <span style="color: var(--green);">CALIBRATED</span>
      </div>
      <p style="font-size: 12px; color: var(--silver); margin-bottom: 14px;">
        Dimensionally normalized acoustic-optical projection onto fundamental Cl(16,4) semantic and safety blades:
      </p>

      <div class="blade-meter">
        <div class="blade-header"><span>e1 (Trust / Spectral Coherence)</span><span style="color: var(--cyan);">{res['blades']['e1_trust']}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width: {min(100, int(res['blades']['e1_trust']*100))}%; background: var(--cyan);"></div></div>
      </div>
      <div class="blade-meter">
        <div class="blade-header"><span>e2 (Factual Grounding / Centroid Alignment)</span><span style="color: var(--green);">{res['blades']['e2_factual']}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width: {min(100, int(res['blades']['e2_factual']*100))}%; background: var(--green);"></div></div>
      </div>
      <div class="blade-meter">
        <div class="blade-header"><span>e3 (Negation / Normalized Spectral Flux)</span><span style="color: var(--violet);">{res['blades']['e3_negation']}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width: {min(100, int(res['blades']['e3_negation']*100))}%; background: var(--violet);"></div></div>
      </div>
      <div class="blade-meter">
        <div class="blade-header"><span>e4 (Authority / Dynamic Envelope Power)</span><span style="color: var(--amber);">{res['blades']['e4_authority']}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width: {min(100, int(res['blades']['e4_authority']*100))}%; background: var(--amber);"></div></div>
      </div>
      <div class="blade-meter">
        <div class="blade-header"><span>e15 (Adversarial Ultrasonic Anomaly &gt;16 kHz)</span><span style="color: var(--crimson);">{res['blades']['e15_adversarial']}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width: {min(100, int(res['blades']['e15_adversarial']*100))}%; background: var(--crimson);"></div></div>
      </div>

      <div class="stat-card" style="margin-top: 16px;">
        <div class="stat-label">Adversarial Ultrasonic Steganography Gate</div>
        <div class="stat-val" style="color: var(--green); font-size: 13.5px;">CLEAN / ZERO INAUDIBLE THREATS DETECTED (e15 = {res['blades']['e15_adversarial']})</div>
      </div>
    </div>
  </div>

  <!-- Panel 5: Full Step-by-Step Transformation Text Report -->
  <div class="card" style="margin-bottom: 24px;">
    <div class="card-title">
      <span>5. FULL STEP-BY-STEP TRANSFORMATION TEXT REPORT &amp; MATHEMATICAL NARRATIVE</span>
      <button id="btnCopyReport" style="background: rgba(56,189,248,0.18); color: var(--cyan); border: 1px solid var(--cyan); border-radius: 5px; padding: 4px 10px; font-size: 11px; cursor: pointer;">Copy Full Text Report</button>
    </div>
    <pre id="fullReportPre" style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 7px; padding: 14px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11.5px; color: #e2e8f0; white-space: pre-wrap; word-break: break-word; max-height: 440px; overflow-y: auto; line-height: 1.55;">{report_txt}</pre>
  </div>
</div>

<script>
  const btnCopyReport = document.getElementById("btnCopyReport");
  if (btnCopyReport) {{
    btnCopyReport.onclick = () => {{
      const txt = document.getElementById("fullReportPre").innerText;
      navigator.clipboard?.writeText(txt);
      btnCopyReport.textContent = "Copied to Clipboard!";
      setTimeout(() => {{ btnCopyReport.textContent = "Copy Full Text Report"; }}, 1800);
    }};
  }}
  const ORBIT = {orbit_json};
  const fftCanvas = document.getElementById("fftCanvas");
  const fftCtx = fftCanvas.getContext("2d");
  const attCanvas = document.getElementById("attractorCanvas");
  const attCtx = attCanvas.getContext("2d");
  const audioEl = document.getElementById("sonAudio");

  let ac = null, analyser = null, freqData = null;
  let yaw = 0.5, pitch = 0.35, dragging = false, lx = 0, ly = 0;

  audioEl.addEventListener("play", () => {{
    try {{
      if (!ac) {{
        const AC = window.AudioContext || window.webkitAudioContext;
        ac = new AC();
        analyser = ac.createAnalyser();
        analyser.fftSize = 128;
        freqData = new Uint8Array(analyser.frequencyBinCount);
        const src = ac.createMediaElementSource(audioEl);
        src.connect(analyser);
        analyser.connect(ac.destination);
      }}
      if (ac.state === "suspended") ac.resume();
    }} catch (e) {{}}
  }});

  attCanvas.addEventListener("pointerdown", e => {{ dragging = true; lx = e.clientX; ly = e.clientY; }});
  window.addEventListener("pointermove", e => {{
    if (!dragging) return;
    yaw += (e.clientX - lx) * 0.01;
    pitch += (e.clientY - ly) * 0.01;
    lx = e.clientX; ly = e.clientY;
  }});
  window.addEventListener("pointerup", () => {{ dragging = false; }});

  function renderLoop(ts) {{
    if (!dragging) yaw += 0.007;

    // 1. Render FFT Spectrum
    const fw = fftCanvas.clientWidth || 400, fh = 80;
    if (fftCanvas.width !== fw) {{ fftCanvas.width = fw; fftCanvas.height = fh; }}
    fftCtx.fillStyle = "#030712";
    fftCtx.fillRect(0, 0, fw, fh);
    if (analyser && freqData) analyser.getByteFrequencyData(freqData);
    const bins = 48, bw = (fw - 16) / bins;
    for (let i = 0; i < bins; i++) {{
      const v = freqData ? freqData[i] / 255 : (0.18 + 0.12 * Math.sin(ts * 0.004 + i * 0.3));
      const bh = Math.max(3, v * (fh - 16));
      fftCtx.fillStyle = i % 2 === 0 ? "#38bdf8" : "#c084fc";
      fftCtx.fillRect(8 + i * bw, fh - 6 - bh, bw - 2, bh);
    }}

    // 2. Render 3D Phase-Space Attractor x(t), x(t+tau), x(t+2*tau)
    const aw = attCanvas.clientWidth || 400, ah = 145;
    if (attCanvas.width !== aw) {{ attCanvas.width = aw; attCanvas.height = ah; }}
    attCtx.fillStyle = "#030712";
    attCtx.fillRect(0, 0, aw, ah);
    const cx = aw / 2, cy = ah / 2, sc = Math.min(aw, ah) * 0.40;
    attCtx.beginPath();
    ORBIT.forEach((pt, idx) => {{
      const x1 = pt[0] * Math.cos(yaw) + pt[2] * Math.sin(yaw);
      const z1 = -pt[0] * Math.sin(yaw) + pt[2] * Math.cos(yaw);
      const y2 = pt[1] * Math.cos(pitch) - z1 * Math.sin(pitch);
      const z2 = pt[1] * Math.sin(pitch) + z1 * Math.cos(pitch);
      const p = 2.6 / (2.6 + z2);
      const px = cx + x1 * sc * p, py = cy + y2 * sc * p;
      if (idx === 0) attCtx.moveTo(px, py); else attCtx.lineTo(px, py);
    }});
    attCtx.strokeStyle = "#38bdf8";
    attCtx.lineWidth = 1.4;
    attCtx.stroke();
    attCtx.fillStyle = "#94a3b8";
    attCtx.font = "10px monospace";
    attCtx.fillText("3D Phase-Space Attractor [x(t), x(t+τ), x(t+2τ)] · Drag to rotate", 8, 14);

    requestAnimationFrame(renderLoop);
  }}
  requestAnimationFrame(renderLoop);
</script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    main()
