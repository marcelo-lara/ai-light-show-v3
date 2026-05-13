/**
 * Shader metadata types for Raindrops and Spectroid Chase shaders
 * Epic 11.F1 & 12.F1 - Shader metadata types
 */

import type { PresetParameter } from './preset';

export interface POI {
  id: string;
  name: string;
  location: { x: number; y: number }; // normalized 0..1
  description?: string;
  metadata?: Record<string, unknown>;
}

export interface Parcan extends POI {
  fixture_type: 'parcan';
  pan?: number; // degrees
  tilt?: number; // degrees
}

export interface RaindropsShaderMetadata {
  id: 'raindrops';
  displayName: 'Raindrops';
  description: string;
  parameters: PresetParameter[];
  poi_selection?: {
    single: boolean; // true: select one POI, false: select multiple
    allow_all: boolean;
  };
  behaviors: {
    pulse_start: 'poi_source' | 'canvas_center' | 'random';
    pulse_transit: 'poi_pass_through' | 'direct' | 'curved';
    collision: 'enabled' | 'disabled';
  };
}

export interface SpectroidChaseShaderMetadata {
  id: 'spectroid_chase';
  displayName: 'Spectroid Chase';
  description: string;
  parameters: PresetParameter[];
  trigger_source: 'spectroid' | 'note' | 'chord';
  anchor_type: 'parcan' | 'poi';
  line_behavior: {
    direction: 'outward' | 'bidirectional';
    motion_type: 'linear' | 'curved';
    follow_enabled: boolean;
  };
}

export interface ShaderControlGroup {
  group_id: string;
  label: string;
  parameters: PresetParameter[];
  order: number;
}

export interface ShaderMetadata {
  id: string;
  displayName: string;
  description: string;
  shader_type: 'wave' | 'pulse' | 'line' | 'particle' | 'other';
  parameters: PresetParameter[];
  requires_pois?: boolean;
  requires_fixtures?: boolean;
  control_groups?: ShaderControlGroup[];
}

export const RAINDROPS_METADATA: RaindropsShaderMetadata = {
  id: 'raindrops',
  displayName: 'Raindrops',
  description: 'POI-aware radial pulse layer with collision behavior',
  parameters: [
    {
      id: 'pulse_rate',
      label: 'Pulse Rate (Hz)',
      type: 'float',
      default: 2.0,
      min: 0.1,
      max: 10.0,
      step: 0.1,
      ui_group: 'Pulse Behavior',
    },
    {
      id: 'radius_growth',
      label: 'Radius Growth (px/s)',
      type: 'float',
      default: 50.0,
      min: 10.0,
      max: 200.0,
      step: 5.0,
      ui_group: 'Pulse Behavior',
    },
    {
      id: 'decay_rate',
      label: 'Decay Rate',
      type: 'float',
      default: 0.95,
      min: 0.5,
      max: 0.99,
      step: 0.01,
      ui_group: 'Pulse Behavior',
    },
    {
      id: 'collision_strength',
      label: 'Collision Strength',
      type: 'float',
      default: 0.8,
      min: 0.0,
      max: 1.0,
      step: 0.1,
      ui_group: 'Collision',
    },
    {
      id: 'poi_selection',
      label: 'Selected POIs',
      type: 'select',
      default: 'all',
      options: ['all', 'custom'],
      ui_group: 'POI Selection',
    },
  ],
  poi_selection: {
    single: false,
    allow_all: true,
  },
  behaviors: {
    pulse_start: 'poi_source',
    pulse_transit: 'poi_pass_through',
    collision: 'enabled',
  },
};

export const SPECTROID_CHASE_METADATA: SpectroidChaseShaderMetadata = {
  id: 'spectroid_chase',
  displayName: 'Spectroid Chase',
  description: 'Note/chord-reactive chase shader with parcan anchors',
  parameters: [
    {
      id: 'trigger_sensitivity',
      label: 'Trigger Sensitivity',
      type: 'float',
      default: 0.7,
      min: 0.0,
      max: 1.0,
      step: 0.05,
      ui_group: 'Trigger',
    },
    {
      id: 'line_length',
      label: 'Line Length (px)',
      type: 'float',
      default: 100.0,
      min: 20.0,
      max: 500.0,
      step: 10.0,
      ui_group: 'Line Behavior',
    },
    {
      id: 'spread_angle',
      label: 'Spread Angle (°)',
      type: 'float',
      default: 45.0,
      min: 0.0,
      max: 360.0,
      step: 5.0,
      ui_group: 'Line Behavior',
    },
    {
      id: 'fade_time',
      label: 'Fade Time (s)',
      type: 'float',
      default: 0.5,
      min: 0.1,
      max: 3.0,
      step: 0.1,
      ui_group: 'Fade',
    },
    {
      id: 'chase_speed',
      label: 'Chase Speed (px/s)',
      type: 'float',
      default: 200.0,
      min: 50.0,
      max: 500.0,
      step: 10.0,
      ui_group: 'Motion',
    },
  ],
  trigger_source: 'spectroid',
  anchor_type: 'parcan',
  line_behavior: {
    direction: 'outward',
    motion_type: 'linear',
    follow_enabled: true,
  },
};
