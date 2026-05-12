import sys
import os
import json
import hashlib

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from engine.renderer import FrameRenderer


def test_v1_v2_parity():
    song_dir = "/data/songs"
    songs = [f for f in os.listdir(song_dir) if f.endswith('.mp3')] if os.path.exists(song_dir) else []
    if not songs:
        print(f"Skipping parity test, no songs found in {song_dir}.")
        return

    song_path = os.path.join(song_dir, songs[0])
    renderer = FrameRenderer(song_path, seed=42, fps=5)

    # Legacy frames (list of dicts)
    legacy_frames = renderer.generate_frames()

    # v2 bytes
    v2_bytes = renderer.generate_frames(output_format="rgb24")

    bytes_per_frame = renderer.width * renderer.height * 3
    total_frames = int(renderer.analysis_data['duration'] * renderer.fps)

    # Build frames from v2 bytes
    frames_from_v2 = []
    for i in range(total_frames):
        start = i * bytes_per_frame
        end = start + bytes_per_frame
        if end > len(v2_bytes):
            break
        frame_bytes = v2_bytes[start:end]
        # convert to packed ints like legacy
        pixels = []
        for p in range(0, len(frame_bytes), 3):
            r = frame_bytes[p]
            g = frame_bytes[p+1]
            b = frame_bytes[p+2]
            packed = (r << 16) | (g << 8) | b
            pixels.append(packed)
        frames_from_v2.append({"timestamp": i / renderer.fps, "pixels": pixels})

    # Compare first N frames
    n = min(len(legacy_frames), len(frames_from_v2))
    if n == 0:
        print("No frames to compare; skipping parity check.")
        return

    for i in range(n):
        lf = legacy_frames[i]["pixels"]
        vf = frames_from_v2[i]["pixels"]
        assert lf == vf, f"Mismatch at frame {i}: legacy vs v2"

    print(f"v1/v2 parity test passed for {n} frames.")


if __name__ == '__main__':
    test_v1_v2_parity()
