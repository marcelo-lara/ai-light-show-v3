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
  layer_type:
    | 'wave'
    | 'pulse'
    | 'radial_pulse'
    | 'raindrops'
    | 'spectroid_chase'
    | 'solid'
    | 'gradient'
    | 'bars'
    | 'rings'
    | 'beat_flash'
    | 'scanner'
    | 'other';
  description?: string;
  params?: PresetParameter[];
  blend_modes?: string[];
  tags?: string[];
  requires_analysis?: boolean;
  requires_modulators?: boolean;
  supports_transforms?: boolean;
  example_params?: Record<string, unknown>;
  performance_tier?: 'low' | 'medium' | 'high'; // GPU load estimate
}

export interface LayerRegistry {
  layers: LayerMetadata[];
  by_type: Record<string, LayerMetadata>;
  by_tag: Record<string, LayerMetadata[]>;
}

/**
 * Layer fixture browsing interface for UI layer inspector.
 * Allows viewing available layers, their parameters, and previews.
 */
export interface LayerFixtureBrowser {
  all_layers: LayerMetadata[];
  featured_layers: LayerMetadata[]; // recommended / commonly used
  get_layer(layer_id: string): LayerMetadata | undefined;
  get_layers_by_tag(tag: string): LayerMetadata[];
  get_layers_by_type(layer_type: string): LayerMetadata[];
  search(query: string): LayerMetadata[];
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

/**
 * All available layers in the system with their complete metadata.
 * Populated by the backend during initialization.
 */
export const AVAILABLE_LAYERS: LayerRegistry = {
  layers: [],
  by_type: {},
  by_tag: {},
};
