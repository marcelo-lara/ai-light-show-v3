import math

class BaseModulator:
    def evaluate(self, time_sec: float, features: dict, params: dict) -> float:
        raise NotImplementedError

class LfoModulator(BaseModulator):
    def evaluate(self, time_sec: float, features: dict, params: dict) -> float:
        # params: rate, shape (sine, tri, saw), min, max, sync (bool)
        rate = params.get('rate', 1.0)
        shape = params.get('shape', 'sine')
        min_val = params.get('min', 0.0)
        max_val = params.get('max', 1.0)
        sync = params.get('sync', False)
        
        # If sync is true, we drive the LFO by beat_phase instead of time
        # rate becomes a multiplier of the beat (e.g., rate=0.5 means half-note)
        if sync:
            phase = (features.get('beat_phase', 0.0) * rate) % 1.0
        else:
            phase = (time_sec * rate) % 1.0
            
        val = 0.0
        if shape == 'sine':
            val = (math.sin(phase * 2 * math.pi) + 1.0) / 2.0
        elif shape == 'tri':
            val = 2.0 * abs(phase - 0.5)
        elif shape == 'saw':
            val = phase
            
        return min_val + val * (max_val - min_val)

class EnvelopeFollowerModulator(BaseModulator):
    def evaluate(self, time_sec: float, features: dict, params: dict) -> float:
        # params: band (global_energy, sub_bass, etc), min, max
        band = params.get('band', 'global_energy')
        min_val = params.get('min', 0.0)
        max_val = params.get('max', 1.0)
        
        energy = features.get(band, 0.0)
        
        return min_val + energy * (max_val - min_val)

MODULATOR_REGISTRY = {
    "lfo": LfoModulator,
    "envelope": EnvelopeFollowerModulator
}

def get_modulator(mod_type: str):
    if mod_type not in MODULATOR_REGISTRY:
        raise ValueError(f"Unknown modulator type: {mod_type}")
    return MODULATOR_REGISTRY[mod_type]()
