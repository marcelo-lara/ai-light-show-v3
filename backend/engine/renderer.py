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
from .mod_mapping import apply_mapping
from .diagnostics_compute import (
    FrameDiagnosticsComputer,
    DiagnosticsSummary,
    AssetGenerator,
)

from .compositor import Compositor

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
        # Support mapping dicts, e.g. {"mod":"my_lfo","mapping":[{"op":"scale","factor":2},{"op":"clamp","min":0,"max":1}]}
        if isinstance(param_val, dict):
            # resolve mod-based value
            if 'mod' in param_val:
                mod_id = param_val['mod']
                base = None
                if mod_values and mod_id in mod_values:
                    base = float(mod_values[mod_id])
                else:
                    base = float(param_val.get('value', 0.0))
                if 'mapping' in param_val:
                    return apply_mapping(base, param_val['mapping'])
                return base
            if 'param' in param_val:
                return self.evaluate_param(f"param.{param_val['param']}", scene_params, preset, mod_values)
            if 'value' in param_val:
                return param_val['value']

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

    def generate_frames(self, output_format: str = "legacy", progress_callback=None):
        from .renderer_parts import generate_frames as _generate_frames
        return _generate_frames(self, output_format=output_format, progress_callback=progress_callback)

    def export(self, progress_callback=None, canvas_name: str = "default"):
        from .renderer_parts import export as _export
        return _export(self, progress_callback=progress_callback, canvas_name=canvas_name)
