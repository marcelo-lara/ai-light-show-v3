try:
    import cupy as np
    print("Renderer: Using GPU via CuPy")
except Exception:
    import numpy as np
    print("Renderer: CuPy not found, falling back to NumPy")
import numpy as cpu_np
import json
import os
import uuid
import hashlib
import random
import time
from .analyzer import AudioAnalyzer
from .layers import FrameContext, get_layer
from .preset_schema import PresetSchema
from .modulators import get_modulator
from .timeline import TimelineDirector, TimelineSchema
from .diagnostics import Diagnostics

class Compositor:
    @staticmethod
    def blend_max(layer1, layer2):
        return np.maximum(layer1, layer2)
        
    @staticmethod
    def blend_add(layer1, layer2):
        # Add and clip to 255
        return np.clip(layer1.astype(np.uint16) + layer2.astype(np.uint16), 0, 255).astype(np.uint8)

class FrameRenderer:
    def __init__(self, song_path, seed: int, preset_id: str = "undersea_pulse_01", preset_version: str = "1.0.0", params=None, fps=50, width=100, height=50, timeline: TimelineSchema = None):
        self.song_path = song_path
        self.song_id = os.path.basename(song_path).replace('.mp3', '')
        self.seed = seed
        self.preset_id = preset_id
        self.preset_version = preset_version
        self.fps = fps
        self.width = width
        self.height = height
        self.global_params = params or {}
        
        np.random.seed(self.seed)
        
        self.analyzer = AudioAnalyzer(song_path)
        self.analysis_data = self.analyzer.analyze()
        
        # Output directory for cached JSON frames (repo-local to avoid requiring system /data)
        repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.output_dir = os.path.join(repo_root, 'data', 'canvas')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Pre-calculate coordinate grid
        x = np.arange(width)
        y = np.arange(height)
        self.xx, self.yy = np.meshgrid(x, y)
        self.coords = np.column_stack((self.xx.ravel(), self.yy.ravel()))
        
        self.q_buffer = {}
        
        # Initialize Timeline
        if timeline:
            self.timeline = timeline
        else:
            # Auto-generate a timeline based on sections, using the requested preset as a baseline
            director = TimelineDirector(self.analysis_data, available_presets=[preset_id])
            self.timeline = director.generate_auto_timeline(seed=self.seed)
            
        # Pre-load all presets needed by the timeline
        self.presets = {}
        for scene in self.timeline.scenes:
            if scene.preset_id not in self.presets:
                preset_path = f"/data/presets/{scene.preset_id}.json"
                if os.path.exists(preset_path):
                    with open(preset_path, 'r') as f:
                        p = PresetSchema(**json.load(f))
                else:
                    # try repo-level data/presets (repo may mount ./data -> /data in containers)
                    repo_alt = os.path.join(os.path.dirname(__file__), "..", "..", "data", "presets", f"{scene.preset_id}.json")
                    backend_alt = os.path.join(os.path.dirname(__file__), "..", "data", "presets", f"{scene.preset_id}.json")
                    backend_presets = os.path.join(os.path.dirname(__file__), "..", "presets", f"{scene.preset_id}.json")
                    if os.path.exists(repo_alt):
                        with open(repo_alt, 'r') as f:
                            p = PresetSchema(**json.load(f))
                    elif os.path.exists(backend_alt):
                        with open(backend_alt, 'r') as f:
                            p = PresetSchema(**json.load(f))
                    elif os.path.exists(backend_presets):
                        with open(backend_presets, 'r') as f:
                            p = PresetSchema(**json.load(f))
                    else:
                        raise FileNotFoundError(f"Preset file not found for {scene.preset_id}: tried {preset_path}, {repo_alt}, {backend_alt}, {backend_presets}")
                # Normalize nested dicts (for test environments where pydantic may be missing)
                from types import SimpleNamespace
                def _norm_list(lst):
                    new = []
                    for item in lst:
                        if isinstance(item, dict):
                            new.append(SimpleNamespace(**item))
                        else:
                            new.append(item)
                    return new
                try:
                    p.parameters = _norm_list(p.parameters)
                except Exception:
                    pass
                try:
                    p.layers = _norm_list(p.layers)
                except Exception:
                    pass
                try:
                    p.modulators = _norm_list(p.modulators)
                except Exception:
                    pass
                self.presets[scene.preset_id] = p

    def _to_host_array(self, array):
        if hasattr(np, "asnumpy"):
            return np.asnumpy(array)
        return cpu_np.asarray(array)

    def _setup_scene(self, scene):
        preset = self.presets[scene.preset_id]
        
        from types import SimpleNamespace
        def _to_obj(x):
            if isinstance(x, dict):
                return SimpleNamespace(**x)
            return x
        
        active_layers = []
        for layer_config in preset.layers:
            cfg = _to_obj(layer_config)
            layer_inst = get_layer(cfg.layer_type)
            active_layers.append((cfg, layer_inst))
            
        active_modulators = []
        for mod_config in preset.modulators:
            mcfg = _to_obj(mod_config)
            mod_inst = get_modulator(mcfg.type)
            active_modulators.append((mcfg, mod_inst))
            
        return preset, active_layers, active_modulators

    def evaluate_param(self, param_val, scene_params, preset, mod_values=None):
        if mod_values and isinstance(param_val, str) and param_val.startswith("mod."):
            mod_id = param_val.replace("mod.", "")
            if mod_id in mod_values:
                return mod_values[mod_id]
                
        if isinstance(param_val, str) and param_val.startswith("param."):
            param_name = param_val.replace("param.", "")
            # Scene params override global params
            if param_name in scene_params:
                return scene_params[param_name]
            if param_name in self.global_params:
                return self.global_params[param_name]
            # fallback to default
            for p in preset.parameters:
                if p.id == param_name:
                    return p.default
        return param_val

    def generate_frames(self, output_format: str = "legacy"):
        duration = self.analysis_data['duration']
        total_frames = int(duration * self.fps)
        
        # Ensure deterministic render sequence by re-seeding at start
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        frames = [] if output_format == "legacy" else bytearray()
        # diagnostics collector
        diagnostics = Diagnostics(self.coords.shape[0])
        start_time = time.time()
        print(f"Generating {total_frames} frames at {self.fps} FPS...")
        
        active_scene = None
        preset = None
        active_layers = []
        active_modulators = []
        
        prev_scene = None
        prev_preset = None
        prev_layers = []
        prev_modulators = []
        
        for frame_idx in range(total_frames):
            time_sec = frame_idx / self.fps
            
            # Find active scene
            current_scene = self.timeline.scenes[0]
            for scene in self.timeline.scenes:
                if scene.start <= time_sec <= scene.end:
                    current_scene = scene
                    break
                    
            if current_scene != active_scene:
                prev_scene = active_scene
                prev_preset = preset
                prev_layers = active_layers
                prev_modulators = active_modulators
                
                active_scene = current_scene
                # Swap out state
                preset, active_layers, active_modulators = self._setup_scene(current_scene)
            
            audio_features = self.analyzer.get_features_at_time(time_sec, self.analysis_data)
            
            # Ensure palette exists on the preset to avoid None in layers
            def _palette_or_default(p):
                pal = getattr(p, 'palette', None)
                if pal is None:
                    return type('P', (), { 'primary': '#000000', 'secondary': '#000000', 'accent': '#000000', 'background': '#000000' })()
                return pal

            context = FrameContext(
                coords=self.coords,
                features=audio_features,
                q_buffer=self.q_buffer,
                width=self.width,
                height=self.height,
                palette=_palette_or_default(preset)
            )
            
            # Helper to render a specific scene state
            def render_scene_state(scene, p_preset, p_layers, p_mods):
                mod_values = {}
                for mod_config, mod_inst in p_mods:
                    mod_values[mod_config.id] = mod_inst.evaluate(time_sec, audio_features, mod_config.params)
                
                ctx = FrameContext(
                    coords=self.coords,
                    features=audio_features,
                    q_buffer=self.q_buffer,
                    width=self.width,
                    height=self.height,
                    palette=_palette_or_default(p_preset)
                )
                
                pixels = np.zeros((self.coords.shape[0], 3), dtype=np.uint8)
                for config, layer in p_layers:
                    evaluated_params = {k: self.evaluate_param(v, scene.params, p_preset, mod_values) for k, v in config.params.items()}
                    layer_pixels = layer.render(ctx, **evaluated_params)
                    
                    if scene.intensity != 1.0:
                        layer_pixels = (layer_pixels * scene.intensity).astype(np.uint8)
                        
                    if config.blend_mode == "max":
                        pixels = Compositor.blend_max(pixels, layer_pixels)
                    elif config.blend_mode == "add":
                        pixels = Compositor.blend_add(pixels, layer_pixels)
                    else:
                        pixels = layer_pixels
                return pixels

            # Render current scene
            final_pixels = render_scene_state(active_scene, preset, active_layers, active_modulators)
            
            # Apply transition if active
            if active_scene.transition and prev_scene is not None:
                trans = active_scene.transition
                if time_sec < active_scene.start + trans.duration:
                    progress = (time_sec - active_scene.start) / trans.duration
                    progress = max(0.0, min(1.0, progress))
                    
                    if trans.type == "hard_cut":
                        pass # final_pixels is already current scene
                    elif trans.type == "crossfade":
                        prev_pixels = render_scene_state(prev_scene, prev_preset, prev_layers, prev_modulators)
                        # Blend based on progress (0.0 = all prev, 1.0 = all current)
                        final_pixels = (prev_pixels * (1.0 - progress) + final_pixels * progress).astype(np.uint8)
                    elif trans.type == "beat_flash":
                        # Flash white on beat, fade to current
                        flash_val = (1.0 - progress) * 255.0 * audio_features.get('global_energy', 1.0)
                        final_pixels = np.clip(final_pixels + flash_val, 0, 255).astype(np.uint8)

            host_pixels = self._to_host_array(final_pixels).astype(cpu_np.uint8, copy=False)
            diagnostics.update(host_pixels)

            if output_format == "legacy":
                r = host_pixels[:, 0].astype(cpu_np.uint32)
                g = host_pixels[:, 1].astype(cpu_np.uint32)
                b = host_pixels[:, 2].astype(cpu_np.uint32)
                packed_pixels = (r << 16) | (g << 8) | b

                frames.append({
                    "timestamp": time_sec,
                    "pixels": packed_pixels.tolist()
                })
            else:
                frames.extend(host_pixels.reshape(-1).tobytes())
            
            if frame_idx % 500 == 0 and frame_idx > 0:
                print(f"Processed {frame_idx}/{total_frames} frames...")
                
        end_time = time.time()
        # store diagnostics summary on the renderer for export
        self.render_diagnostics = diagnostics.summary(render_duration=end_time - start_time)
        return frames

    def export(self):
        hash_input = f"{self.song_id}_{self.seed}_{json.dumps(self.global_params, sort_keys=True)}_{self.fps}_timeline"
        render_id = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        base_name = f"{self.song_id}.{render_id}"
        output_path = os.path.join(self.output_dir, f"{base_name}.json")
        # Legacy single-file path (kept for backward compatibility)
        frame_path = os.path.join(self.output_dir, f"{base_name}.bin")

        frame_bytes = self.generate_frames(output_format="rgb24")

        print(f"Saving show metadata to {output_path}...")
        
        bytes_per_frame = self.width * self.height * 3
        # chunk by frames to limit memory pressure on clients/servers
        chunk_frames = 200
        chunk_size = bytes_per_frame * chunk_frames

        # Write chunked files
        chunk_files = []
        idx = 0
        for start in range(0, len(frame_bytes), chunk_size):
            chunk_name = f"{base_name}.bin.{idx:04d}"
            chunk_path = os.path.join(self.output_dir, chunk_name)
            with open(chunk_path, 'wb') as cf:
                cf.write(frame_bytes[start:start+chunk_size])
            chunk_files.append(os.path.basename(chunk_path))
            idx += 1

        # Also keep a monolithic file for backward compatibility (optional)
        try:
            with open(frame_path, 'wb') as f:
                f.write(frame_bytes)
        except Exception:
            # If disk is constrained, it's acceptable to omit the monolith.
            pass

        metadata = {
            "schema_version": "v2",
            "render_id": render_id,
            "preset_id": self.preset_id,
            "preset_version": self.preset_version,
            "seed": self.seed,
            "params": self.global_params,
            "song_id": self.song_id,
            "analysis_id": "v1",
            "analysis_diagnostics": self.analysis_data.get('diagnostics', {}),
            "analysis_structure": self.analysis_data.get('structure', {}),
            "fps": self.fps,
            "duration": self.analysis_data['duration'],
            "frame_count": int(self.analysis_data['duration'] * self.fps),
            "resolution": {"width": self.width, "height": self.height},
            "frame_encoding": "rgb24",
            # For compatibility, point frame_data_path at the first chunk (if present)
            "frame_data_path": chunk_files[0] if chunk_files else os.path.basename(frame_path),
            "frame_chunks": chunk_files,
            "chunk_frames": chunk_frames,
            "bytes_per_frame": bytes_per_frame,
            "timeline": self.timeline.dict(),
            "render_diagnostics": getattr(self, 'render_diagnostics', {})
        }

        with open(output_path, 'w') as f:
            json.dump({"metadata": metadata}, f)

        print("Export complete! (wrote {} chunks)".format(len(chunk_files)))
        return output_path
