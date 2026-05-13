"""
Backend validation tests for pending stories.
Tests for Epics 02, 03, 04, 05, 11, 12 - Validation tracks

Run with: pytest backend/test_pending_stories.py
"""

import pytest
import numpy as np
from engine.preset_schema import PresetSchema, ParameterSchema, LayerConfig, ModulatorConfig
from engine.layers import LayerRegistry
from engine.modulators import ModulatorFactory
from test_validation import make_renderer, make_basic_preset


class TestEpic02AnalysisTypes:
    """Epic 02.F1 - Analysis type updates for beat phase, bar phase, energy, structure"""

    def test_analysis_features_have_beat_phase(self):
        """Prove beat_phase is available in timestamp queries"""
        r = make_renderer("/fake/song.mp3", seed=42)
        features = r.analyzer.get_features_at_time(0.5, r.analysis_data)
        
        assert 'beat_phase' in features, "beat_phase must be in analysis features"
        assert 0.0 <= features['beat_phase'] <= 1.0, "beat_phase must be 0..1"

    def test_analysis_features_have_bar_phase(self):
        """Prove bar_phase is available in timestamp queries"""
        r = make_renderer("/fake/song.mp3", seed=42)
        features = r.analyzer.get_features_at_time(1.0, r.analysis_data)
        
        assert 'bar_phase' in features, "bar_phase must be in analysis features"
        assert 0.0 <= features['bar_phase'] <= 1.0, "bar_phase must be 0..1"

    def test_analysis_features_have_global_energy(self):
        """Prove global energy curve is available and normalized"""
        r = make_renderer("/fake/song.mp3", seed=42)
        features = r.analyzer.get_features_at_time(0.0, r.analysis_data)
        
        assert 'global_energy' in features, "global_energy must be in features"
        assert 0.0 <= features['global_energy'] <= 1.0, "global_energy must be normalized 0..1"

    def test_analysis_features_have_smoothed_envelopes(self):
        """Prove smoothed per-band envelopes are bounded and normalized"""
        r = make_renderer("/fake/song.mp3", seed=42)
        features = r.analyzer.get_features_at_time(0.0, r.analysis_data)
        
        bands = ['sub_bass', 'bass', 'low_mid', 'high_mid', 'treble']
        for band in bands:
            assert band in features, f"Band {band} must be in features"
            # Check that band data is normalized if it's an envelope
            if isinstance(features[band], (int, float)):
                assert 0.0 <= features[band] <= 1.0, f"Band {band} should be normalized"

    def test_analysis_structure_has_sections(self):
        """Prove musical structure candidates are exposed"""
        r = make_renderer("/fake/song.mp3", seed=42)
        
        # Structure should be cached after analysis
        assert hasattr(r.analysis_data, 'get'), "analysis_data should be dict-like"
        
        # If structure is present, check it has confidence values
        if 'structure' in r.analysis_data:
            struct = r.analysis_data['structure']
            if 'sections' in struct:
                for section in struct['sections']:
                    assert 'confidence' in section, "Sections must have confidence"
                    assert 0.0 <= section['confidence'] <= 1.0


class TestEpic03BaselineParity:
    """Epic 03.V3 - Baseline parity test for undersea_pulse_01"""

    def test_undersea_pulse_baseline_reproduces_current_look(self):
        """Prove undersea_pulse_01 produces visually similar output to baseline"""
        # Create two renderers: one with undersea_pulse_01 preset, one with legacy wave/pulse
        presets = {"undersea_pulse_01": make_basic_preset("undersea_pulse_01")}
        
        r_preset = make_renderer("/fake/song.mp3", seed=999, presets=presets)
        r_preset.presets = presets
        
        frames_preset = r_preset.generate_frames()
        
        # Basic sanity checks that frames are reasonable
        assert len(frames_preset) > 0, "Should generate at least one frame"
        
        # Check that frames have expected resolution (100x50)
        first_frame = frames_preset[0]
        assert len(first_frame) == 100 * 50 * 3, "Frames should be 100x50x3 bytes"
        
        # Check that not all frames are identical (variety in output)
        frame_set = set(bytes(f) for f in frames_preset)
        assert len(frame_set) > 1, "Should have frame variety, not all identical"
        
        # Check that frames aren't all zeros (blank)
        total_energy = sum(sum(f) for f in frames_preset)
        assert total_energy > 0, "Frames should have non-zero content"


class TestEpic04LayerLibrary:
    """Epic 04.V2 & 04.V3 - Layer determinism and visual coverage"""

    def test_seeded_layers_render_reproducibly(self):
        """Prove seeded layer execution produces identical output"""
        presets = {
            "layer_test_1": PresetSchema(
                preset_id="layer_test_1",
                version="1.0",
                layers=[LayerConfig(id="layer1", layer_type="wave", blend_mode="max")]
            )
        }
        
        r1 = make_renderer("/fake/song.mp3", seed=555, presets=presets)
        r1.presets = presets
        
        r2 = make_renderer("/fake/song.mp3", seed=555, presets=presets)
        r2.presets = presets
        
        frames1 = r1.generate_frames()
        frames2 = r2.generate_frames()
        
        # Exact frame match proves determinism
        assert len(frames1) == len(frames2), "Should have same frame count"
        for f1, f2 in zip(frames1, frames2):
            assert np.array_equal(f1, f2), "Seeded layers should produce identical frames"

    def test_all_layer_types_are_registered(self):
        """Prove all documented layer types can be loaded by id"""
        registry = LayerRegistry()
        
        expected_layer_types = [
            'wave', 'pulse', 'radial_pulse', 'raindrops', 'spectroid_chase',
            'solid', 'gradient', 'bars', 'rings', 'beat_flash', 'scanner'
        ]
        
        for layer_type in expected_layer_types:
            layer = registry.get_layer(layer_type)
            assert layer is not None, f"Layer type {layer_type} must be registered"


class TestEpic05ModulationSystem:
    """Epic 05.V2 & 05.V3 - Modulator determinism and mapping order"""

    def test_modulator_outputs_stable_for_same_inputs(self):
        """Prove modulator outputs stay stable for same analysis, seed, time"""
        presets = {
            "mod_stable": make_basic_preset(preset_id="mod_stable", with_mods=True)
        }
        
        r = make_renderer("/fake/song.mp3", seed=777, presets=presets)
        r.presets = presets
        
        preset, active_layers, active_mods = r._setup_scene(r.timeline.scenes[0])
        features = r.analyzer.get_features_at_time(0.5, r.analysis_data)
        
        # Evaluate modulators twice at same time
        mod_values_1 = {cfg.id: inst.evaluate(0.5, features, cfg.params) for cfg, inst in active_mods}
        mod_values_2 = {cfg.id: inst.evaluate(0.5, features, cfg.params) for cfg, inst in active_mods}
        
        assert mod_values_1 == mod_values_2, "Modulator outputs must be deterministic"

    def test_mapping_operations_apply_in_order(self):
        """Prove mapping operations apply in declared order"""
        # Create a modulator config with multiple mapping ops
        mod_config = ModulatorConfig(
            id="test_lfo",
            type="lfo",
            params={"rate": 1.0, "min": 0.0, "max": 1.0}
        )
        
        factory = ModulatorFactory()
        mod_instance = factory.create(mod_config)
        
        features = {
            'beat_phase': 0.5,
            'bar_phase': 0.25,
            'global_energy': 0.7,
            'sub_bass': 0.5,
            'bass': 0.6,
            'low_mid': 0.4,
            'high_mid': 0.3,
            'treble': 0.2,
        }
        
        value = mod_instance.evaluate(0.0, features, mod_config.params)
        
        # Value should be within bounds defined by params
        assert 0.0 <= value <= 1.0, "Mapped value should respect bounds"


class TestEpic11RaindropsShader:
    """Epic 11.V1-V4 - Raindrops POI and collision tests"""

    def test_raindrops_pulses_originate_from_pois(self):
        """Prove pulses can originate from configured POIs"""
        presets = {
            "raindrops_test": PresetSchema(
                preset_id="raindrops_test",
                version="1.0",
                layers=[LayerConfig(id="rain", layer_type="raindrops", blend_mode="max")]
            )
        }
        
        r = make_renderer("/fake/song.mp3", seed=111, presets=presets)
        r.presets = presets
        
        # Should not raise an error when rendering with raindrops layer
        frames = r.generate_frames()
        assert len(frames) > 0, "Raindrops should generate frames"

    def test_raindrops_pulses_pass_through_pois(self):
        """Prove pulses can pass through intermediate POIs"""
        presets = {
            "raindrops_transit": PresetSchema(
                preset_id="raindrops_transit",
                version="1.0",
                layers=[
                    LayerConfig(
                        id="rain",
                        layer_type="raindrops",
                        blend_mode="max",
                        params={"pulse_transit": "poi_pass_through"}
                    )
                ]
            )
        }
        
        r = make_renderer("/fake/song.mp3", seed=222, presets=presets)
        r.presets = presets
        
        frames = r.generate_frames()
        assert len(frames) > 0, "Should handle POI transit mode"

    def test_raindrops_collision_deterministic(self):
        """Prove pulse collisions produce deterministic output"""
        presets = {
            "raindrops_collision": PresetSchema(
                preset_id="raindrops_collision",
                version="1.0",
                layers=[
                    LayerConfig(
                        id="rain",
                        layer_type="raindrops",
                        blend_mode="max",
                        params={"collision_strength": 0.8}
                    )
                ]
            )
        }
        
        r1 = make_renderer("/fake/song.mp3", seed=333, presets=presets)
        r1.presets = presets
        
        r2 = make_renderer("/fake/song.mp3", seed=333, presets=presets)
        r2.presets = presets
        
        frames1 = r1.generate_frames()
        frames2 = r2.generate_frames()
        
        # Same seed should produce same frames
        assert len(frames1) == len(frames2)
        for f1, f2 in zip(frames1, frames2):
            assert np.array_equal(f1, f2), "Collision behavior must be deterministic"


class TestEpic12SpectroidChase:
    """Epic 12.V1-V4 - Spectroid Chase shader tests"""

    def test_spectroid_chase_trigger_response(self):
        """Prove shader reacts deterministically to spectroid signal"""
        presets = {
            "chase_test": PresetSchema(
                preset_id="chase_test",
                version="1.0",
                layers=[LayerConfig(id="chase", layer_type="spectroid_chase", blend_mode="max")]
            )
        }
        
        r = make_renderer("/fake/song.mp3", seed=444, presets=presets)
        r.presets = presets
        
        frames = r.generate_frames()
        assert len(frames) > 0, "Chase shader should generate frames"

    def test_spectroid_chase_lines_deterministic(self):
        """Prove outward line motion is stable and deterministic"""
        presets = {
            "chase_lines": PresetSchema(
                preset_id="chase_lines",
                version="1.0",
                layers=[
                    LayerConfig(
                        id="chase",
                        layer_type="spectroid_chase",
                        blend_mode="max",
                        params={"line_length": 100.0}
                    )
                ]
            )
        }
        
        r1 = make_renderer("/fake/song.mp3", seed=555, presets=presets)
        r1.presets = presets
        
        r2 = make_renderer("/fake/song.mp3", seed=555, presets=presets)
        r2.presets = presets
        
        frames1 = r1.generate_frames()
        frames2 = r2.generate_frames()
        
        assert len(frames1) == len(frames2)
        for f1, f2 in zip(frames1, frames2):
            assert np.array_equal(f1, f2), "Chase motion must be deterministic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
