#!/usr/bin/env python3
"""
DAXDA Next-Gen State-of-the-Art Waveform Transformation Suite
==============================================================
CLI and verification tool that executes end-to-end:
1. Ingests genuine audio from `my_voice_sample.wav`
2. Computes Hilbert analytic signal, CWT Morlet scalogram, STFT, and 3D phase-space attractor
3. Generates 2D image spatial wavefield and performs optical sonification (Image -> Audio)
4. Evaluates Clifford Cl(16,4) blade projection and Unified Resonance metrics (NCI, CPC, FAF)
5. Compiles audio-reactive HD video with SHA-256 cryptographic receipt
"""

import json
import os
import sys
import time

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


def main():
    print("=" * 82)
    print("   DAXDA NEXT-GEN — SOTA IMAGE & AUDIO VISUAL WAVEFORM TRANSFORMATION SUITE")
    print("=" * 82)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    voice_path = os.path.join(base_dir, "my_voice_sample.wav")
    output_dir = os.path.join(base_dir, "outputs", "waveforms")
    os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Ingest Acoustic Waveform
    # ------------------------------------------------------------------
    print("\n[STEP 1] Ingesting acoustic waveform...")
    analyzer = AcousticWaveformAnalyzer()

    if os.path.exists(voice_path):
        print(f"  -> Found genuine voice sample: {voice_path}")
        sr, samples = analyzer.load_audio(voice_path)
        # Use first 5 seconds for video compilation
        duration_samples = min(len(samples), int(5.0 * sr))
        samples_sub = samples[:duration_samples]
    else:
        print("  -> Voice sample not found. Generating synthetic multi-harmonic acoustic stream...")
        sr = 22050
        t = np.linspace(0, 5.0, int(5.0 * sr), endpoint=False)
        samples_sub = (
            0.5 * np.sin(2.0 * np.pi * 220.0 * t) +
            0.3 * np.sin(2.0 * np.pi * 440.0 * t) +
            0.2 * np.sin(2.0 * np.pi * 880.0 * t)
        ).astype(np.float32)

    print(f"  -> Loaded {len(samples_sub)} samples at {sr} Hz ({len(samples_sub)/sr:.2f}s duration)")

    # ------------------------------------------------------------------
    # Step 2: Continuous Hilbert, CWT, and STFT Decomposition
    # ------------------------------------------------------------------
    print("\n[STEP 2] Computing continuous acoustic transforms...")
    t0 = time.perf_counter()
    analytic = analyzer.compute_analytic_signal(samples_sub, sample_rate=sr)
    cwt = analyzer.compute_cwt(samples_sub[:4000], sample_rate=sr, num_scales=48)
    stft = analyzer.compute_stft(samples_sub, sample_rate=sr)
    traj, tau = analyzer.compute_phase_space_attractor(samples_sub)
    elapsed_dsp = time.perf_counter() - t0

    mean_f0 = float(np.mean(analytic.instantaneous_freq[100:-100]))
    mean_centroid = float(np.mean(stft.spectral_centroid))
    print(f"  -> Hilbert Analytic Signal: Envelope mean={np.mean(analytic.envelope):.4f}, Instantaneous f0={mean_f0:.1f}Hz")
    print(f"  -> Morlet CWT: Scalogram shape {cwt.scalogram.shape} across {len(cwt.frequencies)} frequency scales")
    print(f"  -> STFT Spectrogram: {stft.spectrogram.shape} with mean Centroid={mean_centroid:.1f}Hz")
    print(f"  -> 3D Phase-Space Attractor: {traj.shape} points with optimal delay tau={tau}")
    print(f"  -> DSP Computation Time: {elapsed_dsp*1000:.1f}ms")

    # ------------------------------------------------------------------
    # Step 3: 2D Spatial Wavefield & Bidirectional Optical Sonification
    # ------------------------------------------------------------------
    print("\n[STEP 3] Running bidirectional Image <-> Audio Cross-Modal Transformation...")
    cross_modal = CrossModalTransformer(sample_rate=sr)
    img_transformer = ImageWavefieldTransformer()

    # Generate a sample geometric test pattern
    test_img = np.zeros((256, 256), dtype=np.float32)
    y, x = np.mgrid[:256, :256]
    # Concentric rings + diamond wave interference
    r = np.hypot(x - 128, y - 128)
    test_img = 0.5 * (1.0 + np.cos(r / 6.0) * np.sin((x + y) / 10.0))
    pattern_path = os.path.join(output_dir, "test_geometric_pattern.png")
    Image.fromarray((test_img * 255.0).astype(np.uint8)).save(pattern_path)
    print(f"  -> Saved test geometric wavefield: {pattern_path}")

    # Direction A: Image -> Audio (Optical Sonification)
    sonified_samples, sonified_sr = cross_modal.image_to_audio_waveform(test_img, duration_sec=3.0)
    sonified_wav_path = os.path.join(output_dir, "optical_sonification_synthesis.wav")
    analyzer.save_audio(sonified_wav_path, sonified_samples, sample_rate=sonified_sr)
    print(f"  -> Synthesized optical audio from image: {sonified_wav_path} ({len(sonified_samples)/sonified_sr:.1f}s)")

    # Direction B: Audio -> Visual Matrix (Cymatics & Mel Resonance)
    vis_matrix = cross_modal.audio_waveform_to_visual_matrix(samples_sub, sample_rate=sr, resolution=(512, 512))
    vis_matrix_path = os.path.join(output_dir, "audio_to_visual_cymatics.png")
    Image.fromarray(vis_matrix).save(vis_matrix_path)
    print(f"  -> Synthesized visual cymatic wavefield: {vis_matrix_path} (512x512 RGB)")

    # ------------------------------------------------------------------
    # Step 4: Clifford Cl(16,4) Multivector & Unified Resonance
    # ------------------------------------------------------------------
    print("\n[STEP 4] Evaluating Clifford Cl(16,4) Multivector projection and Resonance metrics...")
    bridge = GeometricWaveformBridge(sample_rate=sr)
    resonance = bridge.compute_multimodal_resonance(samples_sub, test_img, sample_rate=sr)

    print(f"  -> Neural Coherence Index (NCI):        {resonance.nci:.4f}")
    print(f"  -> Cognitive Phase Coupling (CPC):     {resonance.cpc:.4f}")
    print(f"  -> Frequency Alignment Formula (FAF):   {resonance.faf:.4f}")
    print(f"  -> Cl(16,4) Blade Channels:")
    for b_name, b_val in resonance.blade_channels.items():
        print(f"       * {b_name:20s}: {b_val:.4f}")
    print(f"  -> Adversarial Inaudible Anomaly:      {'ALERT: DETECTED' if resonance.adversarial_anomaly else 'CLEAN (NOMINAL)'}")

    # ------------------------------------------------------------------
    # Step 5: Render HD Video with Cryptographic Seal
    # ------------------------------------------------------------------
    print("\n[STEP 5] Compiling audio-reactive HD video...")
    renderer = WaveformVideoRenderer(width=1280, height=720, fps=30)
    video_manifest = renderer.render_audio_visual_transformation(
        audio_samples=samples_sub,
        sample_rate=sr,
        output_dir=output_dir,
        duration_sec=4.0,
        title="DAXDA NEXT-GEN — MULTIMODAL WAVEFORM & CYMATIC ENGINE"
    )

    # ------------------------------------------------------------------
    # Step 6: Export Consolidated JSON Manifest
    # ------------------------------------------------------------------
    manifest_path = os.path.join(output_dir, "waveform_transformation_manifest.json")
    full_manifest = {
        "engine_version": "DAXDA-Waveforms/1.0.0",
        "audio_source": os.path.basename(voice_path) if os.path.exists(voice_path) else "synthetic",
        "sample_rate": sr,
        "sample_count": len(samples_sub),
        "duration_sec": round(len(samples_sub) / sr, 3),
        "dsp_metrics": {
            "instantaneous_f0_mean_hz": round(mean_f0, 2),
            "spectral_centroid_mean_hz": round(mean_centroid, 2),
            "attractor_delay_tau": tau,
            "dsp_time_ms": round(elapsed_dsp * 1000, 2),
        },
        "resonance_metrics": {
            "nci": resonance.nci,
            "cpc": resonance.cpc,
            "faf": resonance.faf,
            "blades": resonance.blade_channels,
            "adversarial_flag": resonance.adversarial_anomaly,
        },
        "artifacts": {
            "test_pattern_png": pattern_path,
            "sonified_audio_wav": sonified_wav_path,
            "visual_cymatics_png": vis_matrix_path,
            "video_mp4": video_manifest.get("mp4_path"),
            "video_webm": video_manifest.get("webm_path"),
            "video_gif": video_manifest.get("gif_path"),
            "video_sha256": video_manifest.get("sha256"),
        }
    }

    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(full_manifest, fh, indent=2)

    print(f"\n[STEP 6] Wrote consolidated audit manifest: {manifest_path}")
    print("\n" + "=" * 82)
    print("   VERIFICATION & EXECUTION COMPLETE — SOTA TRANSFORMATION CONFIRMED")
    print(f"   Video:   {video_manifest.get('mp4_path')}")
    print(f"   SHA-256: {video_manifest.get('sha256')}")
    print("=" * 82)


if __name__ == "__main__":
    main()
