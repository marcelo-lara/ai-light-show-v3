try:
    import cupy as np
except Exception:
    import numpy as np

class RaindropsShader:
    def render(self, coords, features, q_buffer, width, height, palette, pois=None, trigger="beat", growth_rate=20.0, decay_rate=0.5, collision_strength=1.5):
        if pois is None or len(pois) == 0:
            # Default POIs if none provided: center and 4 quadrants
            pois = [
                (width/2, height/2),
                (width/4, height/4),
                (width*3/4, height/4),
                (width/4, height*3/4),
                (width*3/4, height*3/4)
            ]
            
        if 'raindrops' not in q_buffer:
            q_buffer['raindrops'] = {
                'pulses': [], # list of dicts: {'x': x, 'y': y, 'radius': r, 'energy': e, 'origin_idx': i}
                'last_trigger': False
            }
            
        state = q_buffer['raindrops']
        
        # Determine trigger
        current_trigger = False
        if trigger == "beat":
            current_trigger = features.get('beat', 0.0) > 0.5
        elif trigger == "onset":
            current_trigger = features.get('onset', 0.0) > 0.5
            
        # Spawn new pulse on trigger leading edge
        if current_trigger and not state['last_trigger']:
            # Pick a random POI
            idx = np.random.randint(0, len(pois))
            px, py = pois[idx]
            state['pulses'].append({
                'x': px, 'y': py, 'radius': 0.0, 'energy': 1.0, 'origin_idx': idx, 'hit_pois': {idx}
            })
            
        state['last_trigger'] = current_trigger
        
        N = coords.shape[0]
        intensity_map = np.zeros(N, dtype=np.float32)
        
        new_pulses = []
        for p in state['pulses']:
            # Update radius and energy
            p['radius'] += growth_rate * 0.1 # scaled by fps roughly
            p['energy'] -= decay_rate * 0.1
            
            if p['energy'] <= 0:
                continue
                
            # Check collisions with other POIs
            for i, (poi_x, poi_y) in enumerate(pois):
                if i in p['hit_pois']:
                    continue
                # distance from pulse origin to POI
                dist_to_poi = np.sqrt((p['x'] - poi_x)**2 + (p['y'] - poi_y)**2)
                # If pulse radius reaches POI
                if p['radius'] >= dist_to_poi:
                    p['hit_pois'].add(i)
                    # Spawn secondary collision pulse
                    new_pulses.append({
                        'x': poi_x, 'y': poi_y, 'radius': 0.0, 'energy': p['energy'] * collision_strength, 'origin_idx': i, 'hit_pois': {i}
                    })
            
            # Render ring
            x = coords[:, 0] - p['x']
            y = coords[:, 1] - p['y']
            r = np.sqrt(x**2 + y**2)
            
            dist = np.abs(r - p['radius'])
            # Ring thickness
            ring = np.clip(1.0 - (dist / 2.0), 0.0, 1.0)
            intensity_map += ring * p['energy']
            
            new_pulses.append(p)
            
        state['pulses'] = new_pulses
        
        intensity_map = np.clip(intensity_map, 0.0, 1.0)
        
        colors = np.zeros((N, 3), dtype=np.uint8)
        
        # Convert hex to RGB safely
        def hex_to_rgb(hex_str):
            hex_str = hex_str.lstrip('#')
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            
        primary_rgb = hex_to_rgb(palette.primary)
        for i in range(3):
            colors[:, i] = (primary_rgb[i] * intensity_map).astype(np.uint8)
            
        return colors
