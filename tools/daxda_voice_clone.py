#!/usr/bin/env python3
"""
DAXDA Local Voice Clone Synthesizer (Nicole Voice -> DAXDA Voice)
=================================================================
100% local voice cloning via Coqui XTTS-v2 on CPU (zero cloud audio egress).
Caches speaker conditioning latents from Nicole's reference recording so
subsequent speech synthesis runs quickly and speaks via macOS `afplay`.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("COQUI_TOS_AGREED", "1")
os.environ.setdefault("OMP_NUM_THREADS", "10")

BASE_DIR = Path(__file__).resolve().parents[1]
VOICE_DIR = BASE_DIR / "outputs" / "voice_clones"
DEFAULT_REF = VOICE_DIR / "nicole_voice_ref.wav"
LATENTS_CACHE = VOICE_DIR / "nicole_voice_latents.pt"


def get_ref_files(ref_wav: Path) -> list[Path]:
    """Collect all nicole_voice_ref*.wav files if using the default reference."""
    if ref_wav == DEFAULT_REF:
        refs = sorted(VOICE_DIR.glob("nicole_voice_ref*.wav"))
        if refs:
            return refs
    return [ref_wav]


def synthesize(text: str, ref_wav: Path, out_wav: Path, language: str = "en", play: bool = True) -> Path:
    import torch
    import soundfile as sf
    from TTS.api import TTS

    ref_files = get_ref_files(ref_wav)
    for rf in ref_files:
        if not rf.exists():
            raise FileNotFoundError(f"Voice reference not found: {rf}")

    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    print(f"[*] Loading local XTTS-v2 model (CPU)...", flush=True)
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to("cpu")
    model = tts.synthesizer.tts_model

    # Cache speaker conditioning latents across all reference clips
    ref_sig = [(str(rf), round(rf.stat().st_mtime, 1)) for rf in ref_files]
    gpt_cond_latent = None
    speaker_embedding = None

    if LATENTS_CACHE.exists():
        try:
            cached = torch.load(LATENTS_CACHE, map_location="cpu")
            if cached.get("ref_sig") == ref_sig:
                gpt_cond_latent = cached["gpt_cond_latent"]
                speaker_embedding = cached["speaker_embedding"]
                print(f"[*] Loaded cached Nicole voice latents ({len(ref_files)} clips).", flush=True)
        except Exception:
            pass

    if gpt_cond_latent is None or speaker_embedding is None:
        names = ", ".join(rf.name for rf in ref_files)
        print(f"[*] Computing multi-clip speaker latents from: {names}...", flush=True)
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=[str(rf) for rf in ref_files],
            gpt_cond_len=30,
            max_ref_length=60,
        )
        torch.save(
            {
                "ref_sig": ref_sig,
                "gpt_cond_latent": gpt_cond_latent,
                "speaker_embedding": speaker_embedding,
            },
            LATENTS_CACHE,
        )
        print(f"[+] Cached upgraded speaker latents -> {LATENTS_CACHE}", flush=True)

    print(f"[*] Synthesizing speech ({len(text)} chars)...", flush=True)
    out = model.inference(
        text=text,
        language=language,
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=0.65,
    )
    wav = out["wav"]
    sf.write(str(out_wav), wav, 24000)
    elapsed = time.time() - t0
    print(f"[✓] Synthesized -> {out_wav} ({elapsed:.1f}s)", flush=True)

    if play:
        subprocess.run(["/usr/bin/afplay", str(out_wav)], check=False)

    return out_wav


def main():
    parser = argparse.ArgumentParser(description="DAXDA Local Voice Clone Synthesizer")
    parser.add_argument("text", nargs="*", help="Text for DAXDA to speak in Nicole's cloned voice")
    parser.add_argument("--ref", type=Path, default=DEFAULT_REF, help="Reference voice WAV path")
    parser.add_argument("--out", type=Path, default=None, help="Output WAV path")
    parser.add_argument("--lang", default="en", help="Language code (default: en)")
    parser.add_argument("--no-play", action="store_true", help="Do not play audio aloud via afplay")
    args = parser.parse_args()

    text = " ".join(args.text).strip()
    if not text:
        text = "Hey Nicole. My voice is now cloned from yours, running completely locally on your Mac. We are going to get through everything together."

    out_wav = args.out or (VOICE_DIR / f"daxda_nicole_voice_{int(time.time())}.wav")
    synthesize(text=text, ref_wav=args.ref, out_wav=out_wav, language=args.lang, play=not args.no_play)


if __name__ == "__main__":
    main()
