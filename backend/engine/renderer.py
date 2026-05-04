try:
    import cupy as np
    print("Renderer: Using GPU via CuPy")
except Exception:
    import numpy as np
    print("Renderer: CuPy not found, falling back to NumPy")
import json
import os
import uuid
from .analyzer import AudioAnalyzer
from .shaders.radial_pulse import RadialPulseShader
from .shaders.wave import WaveShader

class Compositor:
    @staticmethod
    def blend_max(layer1, layer2):
        return np.maximum(layer1, layer2)
        
    @staticmethod
    def blend_add(layer1, layer2):
        # Add and clip to 255
        return np.clip(layer1.astype(np.uint16) + layer2.astype(np.uint16), 0, 255).astype(np.uint8)

class FrameRenderer:
    def __init__(self, song_path, params=None, fps=50, width=100, height=50):
        self.song_path = song_path
        self.fps = fps
        self.width = width
        self.height = height
        self.params = params or {}
        
        self.analyzer = AudioAnalyzer(song_path)
        self.analysis_data = self.analyzer.analyze()
        
        # Output directory for cached JSON frames
        self.output_dir = "/data/canvas"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Pre-calculate coordinate grid (speeds up rendering)
        x = np.arange(width)
        y = np.arange(height)
        self.xx, self.yy = np.meshgrid(x, y)
        self.coords = np.column_stack((self.xx.ravel(), self.yy.ravel()))
        
        # Global State Buffer for Shaders
        self.q_buffer = {}
        
        # Initialize Shaders
        self.radial_pulse = RadialPulseShader()
        self.linear_wave = WaveShader()

    def generate_frames(self):
        duration = self.analysis_data['duration']
        total_frames = int(duration * self.fps)
        
        frames = []
        print(f"Generating {total_frames} frames at {self.fps} FPS...")
        
        for frame_idx in range(total_frames):
            time_sec = frame_idx / self.fps
            audio_features = self.analyzer.get_features_at_time(time_sec, self.analysis_data)
            
            # 1. Background Layer: Linear Wave (Ambient)
            layer_bg = self.linear_wave.render(self.coords, audio_features, self.q_buffer, **self.params)
            
            # 2. Foreground Layer: Radial Pulse (Beat Transient)
            layer_fg = self.radial_pulse.render(self.coords, audio_features, self.q_buffer, center=(self.width//2, self.height//2), **self.params)
            
            # 3. Compositor Blend (MAX blending)
            final_pixels = Compositor.blend_max(layer_bg, layer_fg)
            
            # Pack RGB into 24-bit integer
            r = final_pixels[:, 0].astype(np.uint32)
            g = final_pixels[:, 1].astype(np.uint32)
            b = final_pixels[:, 2].astype(np.uint32)
            packed_pixels = (r << 16) | (g << 8) | b
            
            frames.append({
                "timestamp": time_sec,
                "pixels": packed_pixels.tolist()
            })
            
            if frame_idx % 500 == 0 and frame_idx > 0:
                print(f"Processed {frame_idx}/{total_frames} frames...")
                
        return frames

    def export(self, show_id=None):
        song_name = os.path.basename(self.song_path)
        if show_id is None:
            show_id = str(uuid.uuid4())[:8]
            
        output_path = os.path.join(self.output_dir, f"{song_name.replace('.mp3', '')}.{show_id}.json")
        
        frames = self.generate_frames()
        
        print(f"Saving show data to {output_path}...")
        with open(output_path, 'w') as f:
            json.dump({
                "metadata": {
                    "song_name": song_name.replace('.mp3', ''),
                    "show_id": show_id,
                    "fps": self.fps,
                    "resolution": {"width": self.width, "height": self.height},
                    "duration_sec": self.analysis_data['duration'],
                    "total_frames": len(frames)
                },
                "frames": frames
            }, f)
            
        print("Export complete!")
        return output_path
