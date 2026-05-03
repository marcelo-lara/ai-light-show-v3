import json
import math
import os

# Configuration
SONG_NAME = "ayuni"
SHOW_ID = "wave_01"
FPS = 50
WIDTH = 100
HEIGHT = 50
DURATION_SEC = 10 # 10 seconds of mock data for testing
TOTAL_FRAMES = DURATION_SEC * FPS

OUTPUT_DIR = "../data/canvas"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Generate a mock wave effect
def generate_frame(frame_idx, time_sec):
    pixels = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Calculate an arbitrary wave pattern
            # Using simple sin waves to create an underwater feel
            wave_val = math.sin((x / 10.0) + (time_sec * 2)) + math.cos((y / 5.0) + time_sec)
            
            # Normalize to 0-1
            intensity = (wave_val + 2) / 4.0
            
            # Map intensity to a bluish color
            r = 0
            g = int(50 * intensity)
            b = int(255 * intensity)
            
            # Pack into 24-bit integer
            color_int = (r << 16) | (g << 8) | b
            pixels.append(color_int)
    
    return {
        "timestamp": round(time_sec, 3),
        "pixels": pixels
    }

def main():
    print(f"Generating mock data for {SONG_NAME}.{SHOW_ID} at {FPS} FPS...")
    
    data = {
        "metadata": {
            "song_name": SONG_NAME,
            "show_id": SHOW_ID,
            "fps": FPS,
            "resolution": {
                "width": WIDTH,
                "height": HEIGHT
            },
            "duration_sec": DURATION_SEC,
            "total_frames": TOTAL_FRAMES
        },
        "frames": []
    }
    
    for i in range(TOTAL_FRAMES):
        time_sec = i / float(FPS)
        frame_data = generate_frame(i, time_sec)
        data["frames"].append(frame_data)
        
    output_path = os.path.join(OUTPUT_DIR, f"{SONG_NAME}.{SHOW_ID}.json")
    with open(output_path, "w") as f:
        json.dump(data, f)
        
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()
