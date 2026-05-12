try:
    import cupy as np
    print("Layers: Using GPU via CuPy")
except Exception:
    import numpy as np
    print("Layers: CuPy not found, falling back to NumPy")

import colorsys

class FrameContext:
    def __init__(self, coords, features, q_buffer, width, height, palette):
        self.coords = coords
        self.features = features
        self.q_buffer = q_buffer
        self.width = width
        self.height = height
        self.palette = palette

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

class BaseLayer:
    def render(self, context: FrameContext, **kwargs):
        raise NotImplementedError

class BackgroundSweepLayer(BaseLayer):
    def render(self, context: FrameContext, **kwargs):
        N = context.coords.shape[0]
        colors = np.zeros((N, 3), dtype=np.uint8)
        
        # Access IR
        bar_phase = context.features.get('bar_phase', 0.0)
        
        # We sweep horizontally based on bar_phase
        x = context.coords[:, 0]
        normalized_x = x / context.width
        
        # Distance to the sweep line
        dist = np.abs(normalized_x - bar_phase)
        intensity = np.clip(1.0 - (dist * 5.0), 0.0, 1.0)
        
        # Color from palette
        primary_rgb = hex_to_rgb(context.palette.primary)
        bg_rgb = hex_to_rgb(context.palette.background)
        
        for i in range(3):
            base_col = bg_rgb[i]
            sweep_col = primary_rgb[i]
            colors[:, i] = (base_col + (sweep_col - base_col) * intensity).astype(np.uint8)
            
        return colors

class ParticleFieldLayer(BaseLayer):
    def render(self, context: FrameContext, **kwargs):
        N = context.coords.shape[0]
        colors = np.zeros((N, 3), dtype=np.uint8)
        
        energy = context.features.get('global_energy', 0.0)
        
        if 'particles' not in context.q_buffer:
            # simple particle state: positions (x,y) and velocities (vx,vy)
            num_particles = 100
            context.q_buffer['particles'] = {
                'x': np.random.rand(num_particles) * context.width,
                'y': np.random.rand(num_particles) * context.height,
                'vx': (np.random.rand(num_particles) - 0.5) * 2.0,
                'vy': (np.random.rand(num_particles) - 0.5) * 2.0
            }
            
        p = context.q_buffer['particles']
        
        # Update particles with energy burst
        burst = energy * 5.0
        p['x'] += p['vx'] * (1.0 + burst)
        p['y'] += p['vy'] * (1.0 + burst)
        
        # Wrap around
        p['x'] = p['x'] % context.width
        p['y'] = p['y'] % context.height
        
        # Render particles onto grid (simple point splat)
        # For simplicity and speed on GPU, we compute distance from all coords to all particles
        # To avoid OOM, we just draw small dots
        px = p['x'].astype(int)
        py = p['y'].astype(int)
        
        # Find indices in flat coordinate array (width*y + x)
        # assuming coords are generated with meshgrid where y varies slowly, x varies fast
        indices = py * context.width + px
        
        # ensure within bounds
        valid = (indices >= 0) & (indices < N)
        indices = indices[valid]
        
        accent_rgb = hex_to_rgb(context.palette.accent)
        for i in range(3):
            # Using basic indexing, we might overwrite if multiple particles hit the same pixel, which is fine
            colors[indices, i] = accent_rgb[i]
            
        return colors

class WaveformRingLayer(BaseLayer):
    def render(self, context: FrameContext, **kwargs):
        N = context.coords.shape[0]
        colors = np.zeros((N, 3), dtype=np.uint8)
        
        cx = context.width / 2.0
        cy = context.height / 2.0
        x = context.coords[:, 0] - cx
        y = context.coords[:, 1] - cy
        
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x) # -pi to pi
        
        # Normalize theta to 0..1
        norm_theta = (theta + np.pi) / (2 * np.pi)
        
        # Simple ring driven by bands
        bands = [
            context.features.get('sub_bass', 0.0),
            context.features.get('bass', 0.0),
            context.features.get('low_mid', 0.0),
            context.features.get('high_mid', 0.0),
            context.features.get('treble', 0.0)
        ]
        
        # create a smooth continuous waveform around the ring
        # For 5 bands, we interpolate
        # To make it fast, we just do a sum of sines
        wave = 0
        for i, val in enumerate(bands):
            wave += np.sin(norm_theta * np.pi * 2 * (i + 1)) * val * 5.0
            
        base_radius = min(context.width, context.height) * 0.3
        target_radius = base_radius + wave
        
        # Draw ring
        dist = np.abs(r - target_radius)
        intensity = np.clip(1.0 - dist, 0.0, 1.0)
        
        sec_rgb = hex_to_rgb(context.palette.secondary)
        for i in range(3):
            colors[:, i] = (sec_rgb[i] * intensity).astype(np.uint8)
            
        return colors

# Registry
LAYER_REGISTRY = {
    "bg_sweep": BackgroundSweepLayer,
    "particle_field": ParticleFieldLayer,
    "waveform_ring": WaveformRingLayer
}

# We also need to map the old ones:
from .shaders.wave import WaveShader
from .shaders.radial_pulse import RadialPulseShader
from .shaders.raindrops import RaindropsShader

# Wrap old shaders to new API for backward compatibility
class LegacyWaveLayer(BaseLayer):
    def __init__(self):
        self.shader = WaveShader()
    def render(self, context: FrameContext, **kwargs):
        return self.shader.render(context.coords, context.features, context.q_buffer, **kwargs)

class LegacyRadialPulseLayer(BaseLayer):
    def __init__(self):
        self.shader = RadialPulseShader()
    def render(self, context: FrameContext, **kwargs):
        return self.shader.render(context.coords, context.features, context.q_buffer, center=(context.width//2, context.height//2), **kwargs)

class RaindropsLayer(BaseLayer):
    def __init__(self):
        self.shader = RaindropsShader()
    def render(self, context: FrameContext, **kwargs):
        return self.shader.render(context.coords, context.features, context.q_buffer, context.width, context.height, context.palette, **kwargs)

class SpectroidChaseLayer(BaseLayer):
    def __init__(self):
        from .shaders.spectroid_chase import SpectroidChaseShader
        self.shader = SpectroidChaseShader()
    def render(self, context: FrameContext, **kwargs):
        return self.shader.render(context.coords, context.features, context.q_buffer, context.width, context.height, context.palette, **kwargs)

LAYER_REGISTRY["linear_wave"] = LegacyWaveLayer
LAYER_REGISTRY["radial_pulse"] = LegacyRadialPulseLayer
LAYER_REGISTRY["raindrops"] = RaindropsLayer
LAYER_REGISTRY["spectroid_chase"] = SpectroidChaseLayer

def get_layer(layer_type: str):
    if layer_type not in LAYER_REGISTRY:
        raise ValueError(f"Unknown layer type: {layer_type}")
    return LAYER_REGISTRY[layer_type]()
