import importlib.util, sys, os

# load helper functions from test_validation to reuse make_renderer and helpers
spec = importlib.util.spec_from_file_location("test_validation", os.path.join(os.path.dirname(__file__), "test_validation.py"))
_test_validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_test_validation)

from engine.renderer import FrameRenderer


def test_modulator_trace_determinism():
    presets = {"mod_test": _test_validation.make_basic_preset(preset_id="mod_test", with_mods=True)}
    from engine.timeline import TimelineSchema, SceneSchema
    timeline = TimelineSchema(scenes=[SceneSchema(start=0.0, end=0.3, preset_id="mod_test", seed=1)])

    r1 = _test_validation.make_renderer("/fake/songB.mp3", seed=7, fps=10, presets=presets, timeline=timeline)
    r1.presets = presets
    r2 = _test_validation.make_renderer("/fake/songB.mp3", seed=7, fps=10, presets=presets, timeline=timeline)
    r2.presets = presets

    frames1 = r1.generate_frames()
    frames2 = r2.generate_frames()

    # Ensure modulator_trace exists and is deterministic between runs with same inputs
    assert hasattr(r1, 'modulator_trace') and hasattr(r2, 'modulator_trace')
    assert r1.modulator_trace == r2.modulator_trace


def test_mapping_order_ops():
    # Use a simple renderer to access evaluate_param
    r = _test_validation.make_renderer("/fake/songX.mp3", seed=1, fps=10)
    preset = _test_validation.make_basic_preset()

    # base mod value
    mod_values = {"x": 0.6}

    mapping_scale_then_clamp = {"mod": "x", "mapping": [{"op": "scale", "factor": 2.0}, {"op": "clamp", "min": 0.0, "max": 1.0}]}
    mapping_clamp_then_scale = {"mod": "x", "mapping": [{"op": "clamp", "min": 0.0, "max": 1.0}, {"op": "scale", "factor": 2.0}]}

    out1 = r.evaluate_param(mapping_scale_then_clamp, {}, preset, mod_values)
    out2 = r.evaluate_param(mapping_clamp_then_scale, {}, preset, mod_values)

    # scale then clamp: 0.6*2 = 1.2 -> clamp -> 1.0
    assert abs(out1 - 1.0) < 1e-6
    # clamp then scale: clamp(0.6)=0.6 -> *2 = 1.2
    assert abs(out2 - 1.2) < 1e-6
    assert out1 != out2
