#!/usr/bin/env python3
import os
import re
import glob
import warnings

# Suppress warnings from TTS if any
warnings.filterwarnings("ignore")

try:
    from TTS.api import TTS
except ImportError:
    print("ERROR: 'TTS' library not found. Please install it with 'pip install TTS'")
    exit(1)

import torch

def clean_markdown_for_speech(text):
    """
    Strips markdown formatting so the TTS engine reads it conversationally.
    Removes bolding, italics, headers, code blocks, URLs.
    """
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`[^`]*`', '', text)
    # Remove blockquotes and alerts like > [!CAUTION]
    text = re.sub(r'>\s?\[!.*?\]', '', text)
    text = re.sub(r'>\s?', '', text)
    # Remove markdown headers
    text = re.sub(r'#+\s*', '', text)
    # Remove asterisks and bold/italics
    text = text.replace('*', '').replace('_', '')
    # Remove URLs/Links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove multiple spaces/newlines
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    print("[DAXDA RADIO] Initializing Synthesizer Engine...")
    
    # Configuration
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    input_dir = os.path.join(base_dir, 'docs', 'grand_challenge_suites')
    output_dir = os.path.join(base_dir, 'outputs', 'radio_broadcasts')
    voice_sample = os.path.join(base_dir, 'my_voice_sample.wav')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Check if voice sample exists
    if not os.path.exists(voice_sample):
        print(f"ERROR: Voice reference sample not found at: {voice_sample}")
        print("Please record a 10-second clear WAV file of your voice and save it as 'my_voice_sample.wav' in the root repo directory.")
        exit(1)

    print("[DAXDA RADIO] Loading XTTSv2 Voice Cloning Model...")
    # Get device (Apple Silicon MPS, CUDA, or CPU)
    device = "cpu"
    if torch.backends.mps.is_available():
        device = "mps"
        print("[DAXDA RADIO] Apple Silicon (Metal) Acceleration Enabled.")
    elif torch.cuda.is_available():
        device = "cuda"
        
    try:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    except Exception as e:
        print(f"Failed to load TTS model: {e}")
        print("You may need to agree to Coqui terms on first run via CLI: 'tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --text \"test\" --out_path test.wav'")
        exit(1)

    # Find all markdown reports
    md_files = glob.glob(os.path.join(input_dir, "*.md"))
    if not md_files:
        print(f"[DAXDA RADIO] No markdown files found in {input_dir}")
        exit(0)

    for md_file in md_files:
        filename = os.path.basename(md_file)
        name_without_ext = os.path.splitext(filename)[0]
        output_audio = os.path.join(output_dir, f"{name_without_ext}.wav")
        
        if os.path.exists(output_audio):
            print(f"[{name_without_ext}] Already synthesized. Skipping.")
            continue
            
        print(f"\n[DAXDA RADIO] Synthesizing Broadcast: {name_without_ext}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        clean_text = clean_markdown_for_speech(raw_text)
        
        # XTTSv2 handles relatively short chunks best. For a massive document, you'd typically split by paragraphs.
        # We will split by sentences or paragraphs and merge, but for this MVP, we process a limited chunk to prove concept, 
        # or rely on the TTS API if it supports chunking internally (XTTSv2 via TTS api usually handles text splits).
        
        try:
            print(f" -> Cloning voice and rendering {len(clean_text)} characters...")
            tts.tts_to_file(
                text=clean_text[:4000], # Limiting to 4000 chars for the MVP test to prevent OOM
                speaker_wav=voice_sample, 
                language="en", 
                file_path=output_audio
            )
            print(f" -> Successfully saved to {output_audio}")
        except Exception as e:
            print(f" -> ERROR during synthesis: {e}")

    print("\n[DAXDA RADIO] All available broadcasts synthesized.")

if __name__ == "__main__":
    main()
