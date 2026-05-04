try:
    import cupy as np
    print("RadialPulseShader: Using GPU via CuPy")
except Exception:
    import numpy as np
    print("RadialPulseShader: CuPy not found, falling back to NumPy")

from .base_shader import BaseShader

class RadialPulseShader(BaseShader):
    def render(self, coords, audio_features, q_buffer, **kwargs):
        """
        Generates a radial pulse centered on the canvas that expands on bass hits.
        Uses `sub_bass` and `bass` to drive intensity and decay.
        """
        N = coords.shape[0]
        colors = np.zeros((N, 3), dtype=np.uint8)
        
        # Center of the 100x50 canvas is (50, 25)
        center_x, center_y = kwargs.get('center', (50, 25))
        
        # Calculate distance of each coordinate to the center
        dx = coords[:, 0] - center_x
        dy = coords[:, 1] - center_y
        dist = np.sqrt(dx**2 + dy**2)
        
        # We use q_buffer to decay the pulse smoothly
        # q_buffer['pulse_radius'] tracks the expanding wave
        if 'pulse_radius' not in q_buffer:
            q_buffer['pulse_radius'] = 0.0
            
        bass_energy = audio_features.get('bass', 0.0)
        sub_bass_energy = audio_features.get('sub_bass', 0.0)
        is_beat = audio_features.get('is_beat', False)
        
        # If there's a strong beat or bass transient, expand pulse rapidly
        if is_beat and (bass_energy > 0.5 or sub_bass_energy > 0.5):
            q_buffer['pulse_radius'] = 10.0 + (bass_energy * 20.0)
        else:
            # Decay the pulse
            q_buffer['pulse_radius'] *= 0.95 
            
        radius = q_buffer['pulse_radius']
        
        # Create a ring effect
        # Intensity based on distance to the current pulse radius
        thickness = 5.0
        intensity = np.clip(1.0 - np.abs(dist - radius) / thickness, 0.0, 1.0)
        
        # Add some base brightness based on raw bass
        base_brightness = np.clip(bass_energy * 0.3, 0.0, 1.0)
        total_intensity = np.clip(intensity + base_brightness, 0.0, 1.0)
        
        # Color: Orange/Red for bass
        colors[:, 0] = (total_intensity * 255).astype(np.uint8) # R
        colors[:, 1] = (total_intensity * 100).astype(np.uint8) # G
        colors[:, 2] = (total_intensity * 0).astype(np.uint8)   # B
        
        return colors
