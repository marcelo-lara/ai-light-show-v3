import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.engine.renderer import FrameRenderer

if __name__ == "__main__":
    song_path = "data/songs/Cinderella - Ella Lee.mp3"
    print(f"Testing renderer with {song_path}...")
    renderer = FrameRenderer(song_path)
    output_file = renderer.export()
    print(f"Test successful! Output saved to: {output_file}")
