#!/usr/bin/env python3
import os
import glob
from datetime import datetime
import pytz

try:
    from feedgen.feed import FeedGenerator
except ImportError:
    print("ERROR: 'feedgen' library not found. Please install it with 'pip install feedgen'")
    exit(1)

def generate_rss_feed(output_dir, audio_files):
    print("[DAXDA BROADCASTER] Generating Podcast RSS Feed...")
    fg = FeedGenerator()
    fg.load_extension('podcast')
    
    fg.title('DAXDA NextGen Radio')
    fg.description('Automated broadcasts of the DAXDA engine derivations and Grand Challenge Suites.')
    fg.link(href='https://github.com/DAXDA-NextGen', rel='alternate')
    fg.language('en')
    fg.podcast.itunes_category('Technology', 'Artificial Intelligence')
    
    for idx, audio in enumerate(audio_files):
        filename = os.path.basename(audio)
        title = filename.replace('.wav', '').replace('_', ' ').title()
        
        fe = fg.add_entry()
        fe.id(f"daxda-broadcast-{idx}")
        fe.title(title)
        fe.description(f"DAXDA Engine automated synthesis of: {title}")
        # In a real deployment, the URL would point to the hosted audio file
        fe.enclosure(f"https://your-server.com/audio/{filename}", 0, 'audio/x-wav') 
        
    rss_path = os.path.join(output_dir, "daxda_podcast_feed.xml")
    fg.rss_file(rss_path)
    print(f" -> RSS feed successfully saved to {rss_path}")
    print(" -> You can upload this XML to Spotify for Podcasters or Apple Podcasts.")

def generate_ffmpeg_loop_script(output_dir, audio_files):
    print("\n[DAXDA BROADCASTER] Generating FFmpeg 24/7 Radio Script...")
    
    list_file_path = os.path.join(output_dir, "playlist.txt")
    with open(list_file_path, 'w') as f:
        for audio in audio_files:
            f.write(f"file '{audio}'\n")
            
    print(f" -> Playlist saved to {list_file_path}")
    
    print("\n=======================================================")
    print("HOW TO BROADCAST TO YOUTUBE LIVE OR ICECAST:")
    print("=======================================================\n")
    print("To stream continuously (24/7 looping), run this terminal command:")
    print(f"\nffmpeg -f concat -safe 0 -stream_loop -1 -i {list_file_path} -c:a aac -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/<YOUR_STREAM_KEY>\n")
    print("Note: You can replace the YouTube RTMP URL with an Icecast endpoint if you prefer traditional internet radio.")
    print("=======================================================\n")

def main():
    print("Initializing DAXDA Broadcasting Station...")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    radio_dir = os.path.join(base_dir, 'outputs', 'radio_broadcasts')
    
    if not os.path.exists(radio_dir):
        print(f"ERROR: Broadcast directory not found at {radio_dir}")
        print("Run the 'daxda_radio_synthesizer.py' first to generate audio.")
        exit(1)
        
    audio_files = glob.glob(os.path.join(radio_dir, "*.wav"))
    if not audio_files:
        print(f"ERROR: No .wav files found in {radio_dir}. Generate them first.")
        exit(1)
        
    print(f"Found {len(audio_files)} broadcast tracks.")
    
    generate_rss_feed(radio_dir, audio_files)
    generate_ffmpeg_loop_script(radio_dir, audio_files)

if __name__ == "__main__":
    main()
