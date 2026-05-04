import numpy as np
import os
import essentia.standard as es

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
            data = np.load(self.cache_path, allow_pickle=True)
            return data['analysis_data'].item()

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
        
        analysis_data = {
            "tempo": float(bpm),
            "duration": float(duration),
            "beat_times": beats.tolist(),
            "onset_env": norm(onset_env),
            "freq_data": {
                "sub_bass": norm(sub_bass_energy),
                "bass": norm(bass_energy),
                "low_mid": norm(low_mid_energy),
                "high_mid": norm(high_mid_energy),
                "treble": norm(treble_energy),
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
        is_beat = any(abs(bt - time_sec) < 0.02 for bt in analysis_data["beat_times"])
        
        times = analysis_data["freq_data"]["times"]
        sub_bass = np.interp(time_sec, times, analysis_data["freq_data"]["sub_bass"])
        bass = np.interp(time_sec, times, analysis_data["freq_data"]["bass"])
        low_mid = np.interp(time_sec, times, analysis_data["freq_data"]["low_mid"])
        high_mid = np.interp(time_sec, times, analysis_data["freq_data"]["high_mid"])
        treble = np.interp(time_sec, times, analysis_data["freq_data"]["treble"])
        
        onset = np.interp(time_sec, times, analysis_data["onset_env"])
        
        return {
            "is_beat": is_beat,
            "sub_bass": float(sub_bass),
            "bass": float(bass),
            "low_mid": float(low_mid),
            "high_mid": float(high_mid),
            "treble": float(treble),
            "onset": float(onset)
        }
