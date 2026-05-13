/**
 * Fixture mapping and export types for DMX/lighting control.
 * Epic 10.F1, 10.F2, 10.F3 - Export and fixture reference types
 */

export interface FixtureInstance {
  id: string;
  fixture_type_id: string; // references a fixture type (parcan, moving_head, etc)
  name: string;
  canvas_location: { x: number; y: number }; // normalized 0..1 coordinates
  dmx_address: number; // DMX starting address
  dmx_footprint: number; // number of channels used
  pan_min?: number; // degrees
  pan_max?: number;
  tilt_min?: number;
  tilt_max?: number;
  metadata?: Record<string, unknown>;
}

export interface PointOfInterest {
  id: string;
  name: string;
  canvas_location: { x: number; y: number }; // normalized 0..1 coordinates
  description?: string;
  associated_fixtures?: string[]; // fixture IDs this POI relates to
  per_fixture_calibration?: Record<
    string,
    {
      pan: number;
      tilt: number;
      intensity_scale: number;
    }
  >;
}

export type PixelOrderingType = 'linear' | 'serpentine' | 'custom';

export interface CanvasPixelMapping {
  width: number; // pixels
  height: number;
  origin: 'top_left' | 'bottom_left' | 'top_right' | 'bottom_right';
  row_major: boolean;
  ordering: PixelOrderingType;
  description?: string;
}

export interface MappingConfig {
  canvas_mapping: CanvasPixelMapping;
  fixtures: FixtureInstance[];
  mapping_type: 'linear' | 'serpentine' | 'custom';
  fixture_order: string[]; // fixture IDs in mapped order
}

export interface ExportManifest {
  render_id: string;
  export_id: string;
  canvas_name: string;
  mapping: MappingConfig;
  gamma_value: number; // typically 2.2
  brightness_limit: number; // 0..1, max output brightness
  export_format: 'dmx_sequence' | 'artnet' | 'e131' | 'qlc_plus' | 'other';
  frame_count: number;
  fps: number;
  notes?: string;
  generated_at: string;
}

export interface MappingValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
  coverage: {
    fixtures_used: number;
    total_fixtures: number;
    pixels_mapped: number;
    total_pixels: number;
    coverage_percent: number;
  };
}

/**
 * Test patterns for validating orientation and ordering.
 */
export interface TestPattern {
  name: string;
  description: string;
  generate(): Uint8Array; // generate pattern frame data
}

export const ORIENTATION_TEST_PATTERN: TestPattern = {
  name: 'orientation_test',
  description:
    'Bright corner markers to verify origin and orientation (top-left, top-right, bottom-left, bottom-right corners)',
  generate: () => new Uint8Array(), // implementation in backend
};

export const ORDERING_TEST_PATTERN: TestPattern = {
  name: 'ordering_test',
  description:
    'Gradient from left to right and top to bottom to verify row-major vs column-major ordering',
  generate: () => new Uint8Array(), // implementation in backend
};
