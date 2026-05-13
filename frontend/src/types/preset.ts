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
  type: 'lfo' | 'envelope' | string;
  params: Record<string, unknown>;
}

export interface TransitionSchema {
  type: string;
  duration: number;
  params?: Record<string, unknown>;
}

export interface SceneSchema {
  start: number;
  end: number;
  preset_id: string;
  params?: Record<string, unknown>;
  seed: number;
  intensity?: number;
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

// Modulator value shape exposed by the backend for UI inspection
export interface ModulatorValue {
  id: string;
  value: number;
}

// Mapping operation shape the frontend may display or construct
export interface MappingOp {
  op: 'scale' | 'clamp' | 'invert' | 'quantize' | 'curve' | 'smooth' | 'lag' | string;
  // optional parameters for ops
  factor?: number;
  offset?: number;
  min?: number;
  max?: number;
  step?: number;
  gamma?: number;
}

export interface ModulatorTraceEntry {
  timestamp: number;
  mod_values: Record<string, number>;
}

// Shape the UI can use to inspect live modulators and mappings
export interface ModulatorInspection {
  current_values: Record<string, number>;
  trace: ModulatorTraceEntry[];
  mappings?: Record<string, MappingOp[]>;
}
