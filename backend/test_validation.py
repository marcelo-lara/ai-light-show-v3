import sys
import os
import json
import numpy as np
import pytest

# make engine package importable
sys.path.append(os.path.dirname(__file__))

from engine.renderer import FrameRenderer
from engine.preset_schema import PresetSchema

# Lightweight fake analyzer to avoid Essentia dependency and audio files
class FakeAnalyzer:
    def __init__(self, song_path, duration=0.3):
        self.song_path = song_path
        self.cache_path = song_path + ".ir.npz"
        self._duration = duration

    def analyze(self):
        duration = self._duration
        times = np.linspace(0.0, duration, num=3).tolist()
        beat_times = [0.0, duration/2]
        analysis_data = {
            "schema_version": "v1",
            "duration": float(duration),
            "beat_times": beat_times,
            "onset_env": [0.0, 0.5, 0.0],
            "global_energy": [0.1, 0.9, 0.2],
            "structure": {"section_candidates": [0.0]},
            "diagnostics": {},
            "freq_data": {
                "sub_bass": [0.0, 0.0, 0.0],
                "bass": [0.0, 0.0, 0.0],
                "low_mid": [0.0, 0.0, 0.0],
                "high_mid": [0.0, 0.0, 0.0],
                "treble": [0.0, 0.0, 0.0],
                "times": times
            }
        }
        return analysis_data

    def get_features_at_time(self, t, analysis_data):
        # simple interpolation/lookup
        times = analysis_data["freq_data"]["times"]
        idx = int(min(len(times)-1, np.searchsorted(times, t)))
        energy = analysis_data["global_energy"][idx]
        beat_phase = 0.0
        bar_phase = 0.0
        nearest_beat = 0.0
        if analysis_data["beat_times"]:
            bt = analysis_data["beat_times"]
            # naive
            prev = bt[0]
            for b in bt:
                if b <= t:
                    prev = b
            next_b = bt[-1]
            beat_phase = 0.0
            nearest_beat = abs(t - prev)
            bar_phase = 0.0
        return {
            "is_beat": False,
            "beat_phase": float(beat_phase),
            "bar_phase": float(bar_phase),
            "nearest_beat": float(nearest_beat),
            "global_energy": float(energy),
            "sub_bass": 0.0,
            "bass": 0.0,
            "low_mid": 0.0,
            "high_mid": 0.0,
            "treble": 0.0,
            "onset": 0.0
        }


# Helper to construct a FrameRenderer without invoking heavy analyzer/preset file IO
def make_renderer(song_path, seed=42, fps=10, width=8, height=4, presets=None, timeline=None):
    # create an uninitialized instance
    r = object.__new__(FrameRenderer)
    r.song_path = song_path
    r.song_id = os.path.basename(song_path).replace('.mp3', '')
    r.seed = seed
    r.preset_id = "undersea_pulse_01"
    r.preset_version = "1.0.0"
    r.fps = fps
    r.width = width
    r.height = height
    r.global_params = {}

    np.random.seed(seed)

    # attach fake analyzer
    r.analyzer = FakeAnalyzer(song_path)
    r.analysis_data = r.analyzer.analyze()

    r.output_dir = os.path.join(os.path.dirname(__file__), "tmp_canvas")
    os.makedirs(r.output_dir, exist_ok=True)

    # Pre-calc coords
    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)
    r.xx = xx
    r.yy = yy
    r.coords = np.column_stack((xx.ravel(), yy.ravel()))

    r.q_buffer = {}

    # timeline
    if timeline is not None:
        r.timeline = timeline
    else:
        # simple auto timeline with single scene
        from engine.timeline import TimelineSchema, SceneSchema
        r.timeline = TimelineSchema(scenes=[SceneSchema(start=0.0, end=float(r.analysis_data['duration']), preset_id="undersea_pulse_01", seed=seed)])

    # supply presets mapping
    r.presets = presets or {}

    return r


def make_basic_preset(preset_id="undersea_pulse_01", with_layers=True, with_mods=False):
    layers = []
    mods = []
    params = []
    if with_layers:
        layers = [{"id": "layer1", "layer_type": "solid", "blend_mode": "max", "params": {"custom_val": 100}}]
    if with_mods:
        mods = [
            {"id": "my_lfo", "type": "lfo", "params": {"rate": 1.0, "shape": "sine", "min": 0.0, "max": 1.0, "sync": False}},
            {"id": "my_env", "type": "envelope", "params": {"band": "global_energy", "min": 0.0, "max": 50.0}}
        ]
        # layer referencing mod
        layers = [{"id": "layer1", "layer_type": "solid", "blend_mode": "max", "params": {"mapped_mod": "mod.my_lfo", "env_val": "mod.my_env"}}]

    preset = PresetSchema(preset_id=preset_id, version="1.0.0", name=preset_id, description="", tags=["test"], parameters=params, palette=None, modulators=mods, layers=layers)
    return preset


def test_baseline_parity_and_determinism():
    # Two renderers with identical seeds and presets should produce identical frames
    presets = {"undersea_pulse_01": make_basic_preset()}
    r1 = make_renderer("/fake/songA.mp3", seed=123, fps=10, presets=presets)
    r1.presets = presets
    # ensure preset used by timeline exists
    r2 = make_renderer("/fake/songA.mp3", seed=123, fps=10, presets=presets)
    r2.presets = presets

    frames1 = r1.generate_frames()
    frames2 = r2.generate_frames()

    assert frames1 == frames2


def test_modulator_mapping_and_determinism():
    # Test that modulators evaluate and map into params deterministically
    presets = {"mod_test": make_basic_preset(preset_id="mod_test", with_mods=True)}
    # custom timeline using mod_test
    from engine.timeline import TimelineSchema, SceneSchema
    timeline = TimelineSchema(scenes=[SceneSchema(start=0.0, end=0.3, preset_id="mod_test", seed=1)])

    r = make_renderer("/fake/songB.mp3", seed=7, fps=10, presets=presets, timeline=timeline)
    r.presets = presets

    # setup scene and modulators
    preset, active_layers, active_mods = r._setup_scene(r.timeline.scenes[0])

    features_t0 = r.analyzer.get_features_at_time(0.0, r.analysis_data)
    mod_values_t0 = {cfg.id: inst.evaluate(0.0, features_t0, cfg.params) for cfg, inst in active_mods}

    features_t1 = r.analyzer.get_features_at_time(0.1, r.analysis_data)
    mod_values_t1 = {cfg.id: inst.evaluate(0.1, features_t1, cfg.params) for cfg, inst in active_mods}

    # LFO should vary over time
    if 'my_lfo' in mod_values_t0 and 'my_lfo' in mod_values_t1:
        assert mod_values_t0['my_lfo'] != mod_values_t1['my_lfo']

    # Envelope should reflect global_energy scaling
    if 'my_env' in mod_values_t0:
        expected = features_t0.get('global_energy', 0.0) * 50.0
        assert abs(mod_values_t0['my_env'] - expected) < 1e-6

    # evaluate_param mapping
    mapped = r.evaluate_param("mod.my_lfo", {}, preset, mod_values_t0)
    if 'my_lfo' in mod_values_t0:
        assert mapped == mod_values_t0['my_lfo']


def test_timeline_alignment_auto_sections():
    # Ensure auto timeline uses section_candidates as scene starts
    # create analysis_data with explicit sections
    ana = FakeAnalyzer("/fake/songC.mp3")
    data = ana.analyze()
    data['structure'] = {"section_candidates": [0.0, 0.15]}

    presets = {"undersea_pulse_01": make_basic_preset()}

    r = make_renderer("/fake/songC.mp3", seed=5, fps=10, presets=presets)
    # override analysis_data
    r.analysis_data = data

    from engine.timeline import TimelineDirector
    director = TimelineDirector(r.analysis_data, available_presets=["undersea_pulse_01"])
    timeline = director.generate_auto_timeline(seed=5)

    assert timeline.scenes[0].start == data['structure']['section_candidates'][0]


def test_transitions_determinism_and_duration():
    # Build explicit timeline with transitions
    from engine.timeline import TimelineSchema, SceneSchema, TransitionSchema
    timeline = TimelineSchema(scenes=[
        SceneSchema(start=0.0, end=0.15, preset_id="undersea_pulse_01", seed=1),
        SceneSchema(start=0.15, end=0.3, preset_id="undersea_pulse_01", seed=2, transition=TransitionSchema(type="crossfade", duration=0.05))
    ])

    presets = {"undersea_pulse_01": make_basic_preset()}
    r1 = make_renderer("/fake/songD.mp3", seed=9, fps=20, presets=presets, timeline=timeline)
    r1.presets = presets
    r2 = make_renderer("/fake/songD.mp3", seed=9, fps=20, presets=presets, timeline=timeline)
    r2.presets = presets

    f1 = r1.generate_frames()
    f2 = r2.generate_frames()

    assert f1 == f2

    # Ensure crossfade duration window exists by checking transition exists on second scene
    assert timeline.scenes[1].transition is not None
    assert timeline.scenes[1].transition.duration == 0.05
