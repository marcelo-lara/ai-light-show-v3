/**
 * Render diagnostics types for detecting issues in visual output.
 * Epic 09.F1 - Diagnostics types
 */

export interface FrameDiagnostics {
  frame_number: number;
  timestamp: number;
  brightness: number; // 0..1 average brightness
  average_color: { r: number; g: number; b: number }; // 0..1
  pixel_variance: number; // 0..1, how much pixels vary from average
  blank: boolean; // true if pixel count below threshold
  static_score: number; // 0..1, how static/similar to previous frame
}

export interface DiagnosticsSummary {
  total_frames: number;
  duration: number;
  render_duration_ms: number;
  
  // Brightness metrics
  avg_brightness: number; // 0..1
  min_brightness: number;
  max_brightness: number;
  brightness_variance: number;
  
  // Color metrics
  avg_color: { r: number; g: number; b: number };
  color_variety: number; // 0..1
  
  // Frame quality metrics
  blank_frame_count: number;
  blank_frame_indices: number[];
  
  // Temporal variation
  avg_frame_delta: number; // average pixel difference between consecutive frames
  frame_delta_variance: number;
  max_frame_delta: number;
  
  // Variety / responsiveness metrics
  beat_response_score: number; // 0..1, how much content changes on beats
  section_variation_score: number; // 0..1, how much varies between sections
  static_frame_count: number; // frames too similar to previous
  
  // Warnings
  warnings: string[];
}

export interface ContactSheetMetadata {
  grid_cols: number;
  grid_rows: number;
  frame_width: number;
  frame_height: number;
  total_frames: number;
  sample_rate: 'all' | number; // sample every N frames
}

export interface PreviewAsset {
  type: 'gif' | 'png' | 'jpg' | 'mp4';
  url: string;
  duration?: number;
  size_bytes: number;
  description?: string;
}

export interface RenderDiagnosticsOutput {
  summary: DiagnosticsSummary;
  frame_diagnostics?: FrameDiagnostics[]; // detailed per-frame data (optional, can be large)
  contact_sheet?: ContactSheetMetadata;
  preview_assets: PreviewAsset[];
  generated_at: string;
}
