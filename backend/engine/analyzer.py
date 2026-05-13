import numpy as np
import os
import essentia.standard as es

ANALYSIS_SCHEMA_VERSION = "v1"

class AudioAnalyzer:
    def __init__(self, song_path):
        if not os.path.exists(song_path):
            raise FileNotFoundError(f"Audio file not found: {song_path}")
        
        self.song_path = song_path
        self.cache_path = self.song_path + ".ir.npz"
        
    def analyze(self):
        """
        Performs full track analysis using Essentia or loads from cache.
        Returns tempo, beat frames, onset envelope, and 5-band frequency data.
        """
        if os.path.exists(self.cache_path):
            print(f"Loading cached analysis from {self.cache_path}...")
            try:
                data = np.load(self.cache_path, allow_pickle=True)
                cached_data = data['analysis_data'].item()
                if cached_data.get('schema_version') == ANALYSIS_SCHEMA_VERSION:
                    return cached_data
                else:
                    print("Cache schema version mismatch, re-analyzing...")
            except Exception as e:
                print(f"Error loading cache: {e}, re-analyzing...")

        from .analyzer_parts import analyze_impl
        return analyze_impl(self)

    def get_features_at_time(self, time_sec, analysis_data):
        """
        Helper to interpolate features for a specific timestamp.
        """
        beat_times = analysis_data["beat_times"]
        is_beat = any(abs(bt - time_sec) < 0.02 for bt in beat_times)
        
        # Calculate beat_phase, nearest_beat, and bar_phase
        beat_phase = 0.0
        bar_phase = 0.0
        nearest_beat = 0.0
        
        if beat_times:
            # Find the last beat before current time
            idx = np.searchsorted(beat_times, time_sec) - 1
            if idx >= 0 and idx < len(beat_times) - 1:
                prev_beat = beat_times[idx]
                next_beat = beat_times[idx + 1]
                beat_duration = next_beat - prev_beat
                if beat_duration > 0:
                    beat_phase = (time_sec - prev_beat) / beat_duration
                nearest_beat = min(abs(time_sec - prev_beat), abs(next_beat - time_sec))
                bar_phase = ((idx % 4) + beat_phase) / 4.0
            elif idx >= len(beat_times) - 1:
                # After the last beat
                prev_beat = beat_times[-1]
                nearest_beat = abs(time_sec - prev_beat)
            else:
                # Before the first beat
                next_beat = beat_times[0]
                nearest_beat = abs(next_beat - time_sec)
        
        times = analysis_data["freq_data"]["times"]
        sub_bass = np.interp(time_sec, times, analysis_data["freq_data"]["sub_bass"])
        bass = np.interp(time_sec, times, analysis_data["freq_data"]["bass"])
        low_mid = np.interp(time_sec, times, analysis_data["freq_data"]["low_mid"])
        high_mid = np.interp(time_sec, times, analysis_data["freq_data"]["high_mid"])
        treble = np.interp(time_sec, times, analysis_data["freq_data"]["treble"])
        
        onset = np.interp(time_sec, times, analysis_data["onset_env"])
        energy = np.interp(time_sec, times, analysis_data["global_energy"])
        
        return {
            "is_beat": is_beat,
            "beat_phase": float(beat_phase),
            "bar_phase": float(bar_phase),
            "nearest_beat": float(nearest_beat),
            "global_energy": float(energy),
            "sub_bass": float(sub_bass),
            "bass": float(bass),
            "low_mid": float(low_mid),
            "high_mid": float(high_mid),
            "treble": float(treble),
            "onset": float(onset)
        }
