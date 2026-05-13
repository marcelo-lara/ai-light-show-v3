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
        from .renderer_utils import setup_scene
        return setup_scene(self, scene)

    def evaluate_param(self, param_val, scene_params, preset, mod_values=None):
        from .renderer_utils import evaluate_param as _evaluate_param
        return _evaluate_param(self, param_val, scene_params, preset, mod_values)

    def generate_frames(self, output_format: str = "legacy", progress_callback=None):
        from .renderer_parts import generate_frames as _generate_frames
        return _generate_frames(self, output_format=output_format, progress_callback=progress_callback)

    def export(self, progress_callback=None, canvas_name: str = "default"):
        from .renderer_parts import export as _export
        return _export(self, progress_callback=progress_callback, canvas_name=canvas_name)
