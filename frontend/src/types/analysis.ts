/**
 * Analysis type definitions for beat phase, bar phase, energy, and structure metadata.
 * Corresponds to Epic 02.F1 - Analysis type updates
 */

export interface BeatTimingSignal {
  beat_times: number[];
  beat_phase: number; // 0..1, position within current beat
  nearest_beat_distance: number; // frames to nearest beat
  beat_confidence: number; // 0..1
}

export interface BarTimingSignal {
  bar_times: number[];
  bar_phase: number; // 0..1, position within current bar
  bar_duration: number; // seconds
  bar_confidence: number; // 0..1
}

export interface SmoothedEnvelope {
  band: 'sub_bass' | 'bass' | 'low_mid' | 'high_mid' | 'treble' | 'global_energy';
  values: number[]; // normalized 0..1
  timestamps: number[];
}

export interface GlobalEnergy {
  curve: number[]; // normalized 0..1
  peak: number; // max value in curve
  rms: number; // root mean square
}

export interface MusicalStructure {
  downbeats: Array<{
    time: number;
    confidence: number;
  }>;
  phrases: Array<{
    start: number;
    end: number;
    confidence: number;
  }>;
  sections: Array<{
    start: number;
    end: number;
    section_type: string;
    confidence: number;
  }>;
}

export interface AnalysisDiagnostics {
  beat_confidence: number;
  beat_count: number;
  section_count: number;
  phrase_count: number;
  source_metadata: {
    analyzer: string;
    version: string;
    sample_rate: number;
    analysis_date: string;
  };
  basic_stats: {
    min_energy: number;
    max_energy: number;
    mean_energy: number;
    bpm_estimated: number;
  };
}

export interface AnalysisFeatures {
  times: number[];
  beat_times: number[];
  beat_signals: BeatTimingSignal;
  bar_signals: BarTimingSignal;
  global_energy: GlobalEnergy;
  smoothed_envelopes: SmoothedEnvelope[];
  onset_env?: number[];
  freq_data: {
    sub_bass: number[];
    bass: number[];
    low_mid: number[];
    high_mid: number[];
    treble: number[];
  };
  musical_structure: MusicalStructure;
  diagnostics: AnalysisDiagnostics;
}
