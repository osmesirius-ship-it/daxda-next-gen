#!/usr/bin/env python3
"""
DAXDA Acoustic Merkle Chime & Harmonic Sonification
====================================================
Synthesizes a tranquil harmonic bell chord (A=432 Hz pentatonic tuning)
sonifying sealed cryptographic Merkle roots for Nicole.
Provides gentle background acoustic feedback so the system and its creators
can reflect without constant cognitive overload.
"""

import sys
import os
import math
import wave
import struct
import subprocess
from typing import List, Optional

def generate_harmonic_chime(
    frequencies: Optional[List[float]] = None,
    duration: float = 2.5,
    sample_rate: int = 44100,
    output_path: str = "/tmp/daxda_merkle_chime.wav"
) -> str:
    """
    Generates a pure, multi-harmonic sine chord with organic exponential decay
    emulating a Tibetan singing bowl or acoustic bell chime.
    """
    if frequencies is None:
        # A=432 Hz harmonic pentatonic tuning
        frequencies = [432.0, 540.0, 648.0, 864.0]

    num_samples = int(sample_rate * duration)
    wav_file = wave.open(output_path, "w")
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)

    raw_data = bytearray()
    tau = 2.0 * math.pi

    for i in range(num_samples):
        t = float(i) / sample_rate
        # Organic exponential decay: fast attack (0.03s), peaceful fade out
        attack = min(1.0, t / 0.03)
        decay = math.exp(-2.2 * t)
        envelope = attack * decay

        sample_val = 0.0
        for idx, freq in enumerate(frequencies):
            weight = 1.0 / (idx + 1)
            sample_val += weight * math.sin(tau * freq * t)

        # Normalize and apply envelope
        sample_val = sample_val * envelope * 0.35 * 32767.0
        sample_int = int(max(-32768, min(32767, sample_val)))
        raw_data.extend(struct.pack("<h", sample_int))

    wav_file.writeframes(raw_data)
    wav_file.close()
    return output_path

def sonify_merkle_root(merkle_hash: str, output_path: str = "/tmp/daxda_merkle_chime.wav") -> str:
    """
    Maps the first bytes of a Merkle root to harmonic frequencies.
    """
    pentatonic = [288.0, 324.0, 360.0, 432.0, 486.0, 540.0, 648.0, 720.0, 864.0]
    byte_val = int(merkle_hash[:2], 16) if merkle_hash else 42
    f1 = pentatonic[byte_val % len(pentatonic)]
    f2 = pentatonic[(byte_val >> 2) % len(pentatonic)]
    f3 = pentatonic[(byte_val >> 4) % len(pentatonic)]
    return generate_harmonic_chime([f1, f2, f3], duration=2.2, output_path=output_path)

def play_chime(file_path: str = "/tmp/daxda_merkle_chime.wav", async_play: bool = True):
    """Plays the synthesized chime using macOS afplay."""
    if not os.path.exists(file_path):
        generate_harmonic_chime(output_path=file_path)

    cmd = ["afplay", file_path]
    if async_play:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    hash_arg = sys.argv[1] if len(sys.argv) > 1 else "432_harmonic_merkle"
    path = sonify_merkle_root(hash_arg)
    print(f"🔔 Synthesized Merkle Chime: {path}")
    play_chime(path, async_play=False)
