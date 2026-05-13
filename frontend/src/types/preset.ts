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
