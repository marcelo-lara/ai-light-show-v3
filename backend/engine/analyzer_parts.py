import numpy as np
import essentia.standard as es

from .analysis_utils import norm, smooth

ANALYSIS_SCHEMA_VERSION = "v1"


def analyze_impl(self):
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
        onset_val = od_hfc(spec, spec)
        onset_env.append(onset_val)
        sub_bass_energy.append(sub_bass_band(spec))
        bass_energy.append(bass_band(spec))
        low_mid_energy.append(low_mid_band(spec))
        high_mid_energy.append(high_mid_band(spec))
        treble_energy.append(treble_band(spec))

    times = np.arange(len(sub_bass_energy)) * hop_size / sample_rate

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
