export interface FrameData {
  timestamp: number;
  pixels: number[];
}

export interface PresetParameter {
  id: string;
  label: string;
  type: 'int' | 'float' | 'boolean' | 'color' | 'select';
  default: boolean | number | string;
  min?: number;
  max?: number;
  step?: number;
  options?: string[];
  ui_group: string;
}

export interface ModulatorConfig {
  id: string;
  type: 'lfo' | 'envelope';
  params: Record<string, unknown>;
}

export interface AnalysisFeatures {
  times: number[];
  beat_times: number[];
  global_energy: number[];
  onset_env?: number[];
  freq_data: {
    sub_bass: number[];
    bass: number[];
    low_mid: number[];
    high_mid: number[];
    treble: number[];
  };
}

export interface TransitionSchema {
  type: string;
  duration: number;
  params: Record<string, unknown>;
}

export interface SceneSchema {
  start: number;
  end: number;
  preset_id: string;
  params: Record<string, unknown>;
  seed: number;
  intensity: number;
  transition?: TransitionSchema;
}

export interface TimelineSchema {
  scenes: SceneSchema[];
}

export interface PresetSummary {
  preset_id: string;
  version: string;
  name: string;
  description: string;
  tags: string[];
  parameters: PresetParameter[];
  modulators?: ModulatorConfig[];
}

export interface ShowMetadata {
  schema_version: string;
  render_id: string;
  preset_id: string;
  preset_version: string;
  seed: number;
  params: Record<string, unknown>;
  song_id: string;
  analysis_id: string;
  palette?: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
  };
  analysis_features?: AnalysisFeatures;
  analysis_diagnostics?: {
    beat_confidence: number;
    frame_count: number;
    sources: string[];
  };
  analysis_structure?: {
    sections: number;
    phrases_interval: number;
    section_candidates: number[];
  };
  timeline?: TimelineSchema;
  fps: number;
  duration: number;
  frame_count: number;
  resolution: { width: number; height: number };
  frame_encoding?: string;
  frame_chunks?: string[];
  chunk_frames?: number;
  bytes_per_frame?: number;
}

export interface ShowData {
  metadata: ShowMetadata;
  frames?: FrameData[];
}

export interface ServerStatePayload {
  current_song: string | null;
  current_canvas: string | null;
}
