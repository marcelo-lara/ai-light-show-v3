try:
    import cupy as np
except Exception:
    import numpy as np

class SpectroidChaseShader:
    def render(self, coords, features, q_buffer, width, height, palette, anchors=None, trigger_sensitivity=0.5, line_length=20.0, spread=0.2, fade=0.1, chase_speed=5.0):
        if anchors is None or len(anchors) == 0:
            # Default parcan anchors: bottom edge distributed
            anchors = [
                (width * 0.2, height),
                (width * 0.5, height),
                (width * 0.8, height)
            ]
            
        if 'spectroid' not in q_buffer:
            q_buffer['spectroid'] = {
                'lines': [], # list of dicts: {'x': x, 'y': y, 'vx': vx, 'vy': vy, 'length': l, 'energy': e}
                'last_chord': 0.0
            }
            
        state = q_buffer['spectroid']
        
        # Determine trigger from chords or global energy
        chord_strength = features.get('chords_strength', 0.0)
        current_trigger = chord_strength > trigger_sensitivity and chord_strength > state['last_chord']
            
        if current_trigger:
            # Spawn lines from all anchors aiming generally upwards
            for ax, ay in anchors:
                # Random spread angle mostly pointing up
                angle = -np.pi/2 + (np.random.rand() - 0.5) * spread * np.pi
                vx = np.cos(angle) * chase_speed
                vy = np.sin(angle) * chase_speed
                
                state['lines'].append({
                    'x': ax, 'y': ay, 'vx': vx, 'vy': vy, 'length': line_length, 'energy': 1.0
                })
            
        state['last_chord'] = chord_strength
        
        N = coords.shape[0]
        intensity_map = np.zeros(N, dtype=np.float32)
        
        new_lines = []
        for line in state['lines']:
            # Update position
            line['x'] += line['vx']
            line['y'] += line['vy']
            line['energy'] -= fade * 0.1
            
            if line['energy'] <= 0:
                continue
                
            # If offscreen by margin, kill
            if line['y'] < -line['length'] or line['x'] < -line['length'] or line['x'] > width + line['length']:
                continue
                
            # Render line segment
            # Vector from tail to head
            hx = line['x']
            hy = line['y']
            tx = hx - line['vx'] * line['length'] / chase_speed
            ty = hy - line['vy'] * line['length'] / chase_speed
            
            # Distance from pixel to line segment
            px = coords[:, 0]
            py = coords[:, 1]
            
            line_len_sq = (hx - tx)**2 + (hy - ty)**2
            if line_len_sq > 0:
                # Projection
                t = ((px - tx) * (hx - tx) + (py - ty) * (hy - ty)) / line_len_sq
                t = np.clip(t, 0.0, 1.0)
                proj_x = tx + t * (hx - tx)
                proj_y = ty + t * (hy - ty)
                dist = np.sqrt((px - proj_x)**2 + (py - proj_y)**2)
            else:
                dist = np.sqrt((px - hx)**2 + (py - hy)**2)
                
            line_thickness = 1.0
            glow = np.clip(1.0 - (dist / line_thickness), 0.0, 1.0)
            intensity_map += glow * line['energy']
            
            new_lines.append(line)
            
        state['lines'] = new_lines
        
        intensity_map = np.clip(intensity_map, 0.0, 1.0)
        
        colors = np.zeros((N, 3), dtype=np.uint8)
        
        # Convert hex to RGB safely
        def hex_to_rgb(hex_str):
            hex_str = hex_str.lstrip('#')
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            
        primary_rgb = hex_to_rgb(palette.accent)
        for i in range(3):
            colors[:, i] = (primary_rgb[i] * intensity_map).astype(np.uint8)
            
        return colors
