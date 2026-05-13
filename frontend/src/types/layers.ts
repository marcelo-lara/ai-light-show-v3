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

export interface LayerMetadata {
  id: string;
  displayName: string;
  layer_type: string;
  params?: PresetParameter[];
  blend_modes?: string[];
  description?: string;
}

export type FixtureShape = 'point' | 'circle' | 'rect';

export interface Fixture {
  id: string;
  name: string;
  location: { x: number; y: number }; // normalized 0..1 coordinates
  shape: FixtureShape;
  width?: number; // normalized
  height?: number; // normalized
  color?: string;
  meta?: Record<string, unknown>;
}
