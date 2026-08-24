#!/usr/bin/env python3
import os
import re
import glob
import warnings

# Suppress warnings from TTS if any
warnings.filterwarnings("ignore")

USE_TTS = True
try:
    from TTS.api import TTS
except ImportError:
    print("WARNING: 'TTS' library not found. Falling back to native macOS 'say' command.")
    USE_TTS = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

def clean_markdown_for_speech(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'>\s?\[!.*?\]', '', text)
    text = re.sub(r'>\s?', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = text.replace('*', '').replace('_', '')
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    global USE_TTS
    print("[DAXDA RADIO] Initializing Synthesizer Engine...")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    input_dir = os.path.join(base_dir, 'docs', 'grand_challenge_suites')
    output_dir = os.path.join(base_dir, 'outputs', 'radio_broadcasts')
    voice_sample = os.path.join(base_dir, 'my_voice_sample.wav')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tts = None
    if USE_TTS:
        print("[DAXDA RADIO] Loading XTTSv2 Voice Cloning Model...")
        device = "cpu"
        if HAS_TORCH and torch.cuda.is_available():
            device = "cuda"
        else:
            print("[DAXDA RADIO] Warning: Apple Silicon GPU lacks ComplexFloat support. Forcing CPU rendering. This will take some time...")
            
        try:
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        except Exception as e:
            print(f"Failed to load TTS model: {e}")
            USE_TTS = False

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
        
        try:
            if USE_TTS:
                print(f" -> Cloning voice and rendering {len(clean_text[:4000])} characters...")
                tts.tts_to_file(
                    text=clean_text[:4000],
                    speaker_wav=voice_sample, 
                    language="en", 
                    file_path=output_audio
                )
            else:
                print(f" -> Rendering {len(clean_text[:4000])} characters using Apple 'Samantha'...")
                safe_text = clean_text[:4000].replace("'", "").replace('"', "")
                os.system(f"say -v Samantha -o '{output_audio}' --data-format=LEI16@22050 '{safe_text}'")

            print(f" -> Successfully saved to {output_audio}")
        except Exception as e:
            print(f" -> ERROR during synthesis: {e}")

    print("\n[DAXDA RADIO] All available broadcasts synthesized.")

if __name__ == "__main__":
    main()
