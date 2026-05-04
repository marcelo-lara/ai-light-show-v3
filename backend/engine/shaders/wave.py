try:
    import cupy as np
    print("WaveShader: Using GPU via CuPy")
except Exception:
    import numpy as np
    print("WaveShader: CuPy not found, falling back to NumPy")

from .base_shader import BaseShader

class WaveShader(BaseShader):
    def render(self, coords, audio_features, q_buffer, **kwargs):
        """
        Generates a smooth linear wave that undulates based on mid-range frequencies.
        Warping is applied to coordinates based on audio.
        """
        N = coords.shape[0]
        colors = np.zeros((N, 3), dtype=np.uint8)
        
        low_mid = audio_features.get('low_mid', 0.0)
        high_mid = audio_features.get('high_mid', 0.0)
        
        # Track time internally using q_buffer to keep the wave moving
        if 'wave_time' not in q_buffer:
            q_buffer['wave_time'] = 0.0
            
        # Time advances based on mid-frequency energy
        q_buffer['wave_time'] += 0.05 + (low_mid * 0.1)
        t = q_buffer['wave_time']

        x = coords[:, 0]
        y = coords[:, 1]
        
        # Primary Wave (slow, broad undulation)
        wave1 = np.sin(x * 0.05 + t * 0.8) * 4.0
        
        # Secondary Wave (faster, tighter ripples, driven by high_mid)
        wave2 = np.sin(x * 0.15 - t * 1.2) * (2.0 + high_mid * 5.0)
        
        # Tertiary Wave (diagonal flow for interlacing effect)
        wave3 = np.cos((x + y) * 0.08 + t * 1.5) * 3.0

        # Combine waves for complex displacement
        displacement = wave1 + wave2 + wave3
        
        # The water surface is at the top (y=0)
        # Intensity increases as y approaches 0 (surface) and decreases with depth
        depth_factor = np.clip(1.0 - (y / 50.0), 0.0, 1.0) # 1 at top, 0 at bottom
        
        # Caustic ripple intensity (interlacing bright spots)
        # We use a sine of the displaced coordinates to create sharp "lines" of light
        caustic_value = np.sin(displacement + (y * 0.2))
        # Sharpen the caustics by raising to a power, creating bright crests
        caustic_intensity = np.power(np.clip(caustic_value, 0.0, 1.0), 3.0)
        
        # Base water gradient (Deep Navy at bottom -> Bright Teal at top)
        # Navy: R=0, G=10, B=40
        # Teal: R=0, G=150, B=255
        base_r = 0.0
        base_g = 10.0 + (depth_factor * 140.0)
        base_b = 40.0 + (depth_factor * 215.0)
        
        # Add caustics (driven by audio energy and depth)
        caustic_boost = caustic_intensity * depth_factor * (1.0 + high_mid * 2.0)
        
        # Final colors
        r = np.clip(base_r + (caustic_boost * 50.0), 0, 255)
        g = np.clip(base_g + (caustic_boost * 200.0), 0, 255)
        b = np.clip(base_b + (caustic_boost * 255.0), 0, 255)
        
        colors[:, 0] = r.astype(np.uint8)
        colors[:, 1] = g.astype(np.uint8)
        colors[:, 2] = b.astype(np.uint8)
        
        return colors
