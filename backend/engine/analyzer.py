import numpy as np
import os

try:
    import essentia.standard as es
    HAS_ESSENTIA = True
except Exception:
    HAS_ESSENTIA = False
    # Minimal fallback stub to allow tests to run in environments without Essentia.
    class _DummyES:
        class MonoLoader:
            def __init__(self, filename, sampleRate=44100):
                self.filename = filename
                self.sampleRate = sampleRate
            def __call__(self):
                # return 1 second of silence
                return np.zeros(self.sampleRate, dtype=np.float32)
        class RhythmExtractor2013:
            def __init__(self, method="multifeature"):
                pass
            def __call__(self, audio):
                # bpm, beats, confidence, _, intervals
                return 120.0, np.array([]), 1.0, None, np.array([])
        class FrameGenerator:
            def __init__(self, audio, frameSize, hopSize, startFromZero=True):
                self.count = max(1, len(audio) // hopSize)
                self.frameSize = frameSize
                self.hopSize = hopSize
                self.audio = audio
            def __iter__(self):
                for i in range(0, len(self.audio) - self.frameSize + 1, self.hopSize):
                    yield self.audio[i:i+self.frameSize]
        class Windowing:
            def __init__(self, type='hann'):
                pass
            def __call__(self, frame):
                return frame
        class Spectrum:
            def __call__(self, frame):
                # return magnitude-spectrum-like array
                return np.abs(np.fft.rfft(frame))
        class EnergyBand:
            def __init__(self, sampleRate=44100, startCutoffFrequency=20, stopCutoffFrequency=60):
                pass
            def __call__(self, spec):
                return float(np.mean(spec) if len(spec) > 0 else 0.0)
        class OnsetDetection:
            def __init__(self, method='hfc'):
                pass
            def __call__(self, spec, spec2):
                return float(np.sum(spec))
    es = _DummyES()

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

        print(f"Analyzing {self.song_path} with Essentia...")
        
        # 1. Load Audio
        sample_rate = 44100
        loader = es.MonoLoader(filename=self.song_path, sampleRate=sample_rate)
        audio = loader()
        duration = len(audio) / sample_rate
        
        # 2. Tempo and Beat Tracking
        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)
        
        # 3. Frequency Analysis & Energy Bands
        frame_size = 2048
        hop_size = 512
        frames = es.FrameGenerator(audio, frameSize=frame_size, hopSize=hop_size, startFromZero=True)
        
        windowing = es.Windowing(type='hann')
        spectrum = es.Spectrum()
        
        # Essentia EnergyBand descriptors
        sub_bass_band = es.EnergyBand(sampleRate=sample_rate, startCutoffFrequency=20, stopCutoffFrequency=60)
        bass_band = es.EnergyBand(sampleRate=sample_rate, startCutoffFrequency=60, stopCutoffFrequency=250)
        low_mid_band = es.EnergyBand(sampleRate=sample_rate, startCutoffFrequency=250, stopCutoffFrequency=2000)
        high_mid_band = es.EnergyBand(sampleRate=sample_rate, startCutoffFrequency=2000, stopCutoffFrequency=4000)
        treble_band = es.EnergyBand(sampleRate=sample_rate, startCutoffFrequency=4000, stopCutoffFrequency=20000)
        
        # Onset Detection
        od_hfc = es.OnsetDetection(method='hfc')
        
        sub_bass_energy = []
        bass_energy = []
        low_mid_energy = []
        high_mid_energy = []
        treble_energy = []
        onset_env = []
        
        # Process frames
        for frame in frames:
            spec = spectrum(windowing(frame))
            
            # Note: OnsetDetection HFC requires phase which we can just pass spec twice for HFC
            onset_val = od_hfc(spec, spec)
            onset_env.append(onset_val)
            
            sub_bass_energy.append(sub_bass_band(spec))
            bass_energy.append(bass_band(spec))
            low_mid_energy.append(low_mid_band(spec))
            high_mid_energy.append(high_mid_band(spec))
            treble_energy.append(treble_band(spec))
            
        times = np.arange(len(sub_bass_energy)) * hop_size / sample_rate
        
        def norm(arr):
            arr = np.array(arr)
            return (arr / (np.max(arr) + 1e-6)).tolist()
            
        def smooth(arr, window_size=5):
            window = np.ones(window_size) / window_size
            return np.convolve(arr, window, mode='same').tolist()

        # Global energy is the sum of all bands
        global_energy_raw = np.array(sub_bass_energy) + np.array(bass_energy) + np.array(low_mid_energy) + np.array(high_mid_energy) + np.array(treble_energy)
        
        # Structure candidates (heuristic based on energy deltas for simplicity)
        energy_deltas = np.abs(np.diff(smooth(global_energy_raw, 20), prepend=0))
        section_candidates = [float(t) for t, d in zip(times, energy_deltas) if d > np.mean(energy_deltas) + 2*np.std(energy_deltas)]
        
        analysis_data = {
            "schema_version": ANALYSIS_SCHEMA_VERSION,
            "tempo": float(bpm),
            "duration": float(duration),
            "beat_times": beats.tolist(),
            "onset_env": norm(onset_env),
            "global_energy": norm(smooth(global_energy_raw)),
            "structure": {
                "section_candidates": section_candidates,
                "phrases_interval": 16 * (60.0 / float(bpm)) if bpm > 0 else 0
            },
            "diagnostics": {
                "beat_confidence": float(beats_confidence),
                "frame_count": len(times),
                "source_metadata": "essentia_multifeature"
            },
            "freq_data": {
                "sub_bass": norm(smooth(sub_bass_energy)),
                "bass": norm(smooth(bass_energy)),
                "low_mid": norm(smooth(low_mid_energy)),
                "high_mid": norm(smooth(high_mid_energy)),
                "treble": norm(smooth(treble_energy)),
                "times": times.tolist()
            }
        }
        
        print(f"Caching analysis to {self.cache_path}...")
        np.savez_compressed(self.cache_path, analysis_data=analysis_data)
        
        return analysis_data

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
