"""
Render diagnostics computation for detecting issues in visual output.
Epic 09.B1, 09.B2, 09.B3, 09.B4
"""

import numpy as np
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw


class FrameDiagnosticsComputer:
    """Compute per-frame diagnostics: brightness, color, variation, etc."""

    @staticmethod
    def compute_frame_diagnostics(
        frame_num: int,
        timestamp: float,
        pixels: np.ndarray,  # (H, W, 3) uint8 array
        prev_pixels: Optional[np.ndarray] = None,
    ) -> Dict:
        """
        Compute diagnostics for a single frame.
        
        Args:
            frame_num: Frame index
            timestamp: Timestamp in seconds
            pixels: RGB pixel array (H, W, 3)
            prev_pixels: Previous frame for delta computation
            
        Returns:
            Dict with: brightness, avg_color, pixel_variance, blank, static_score
        """
        if len(pixels.shape) == 1:
            # Flattened RGB data (N*3,) - convert to (N, 3)
            pixel_count = len(pixels) // 3
            pixels = pixels.reshape(pixel_count, 3)

        # Compute brightness (average intensity 0..255, normalize to 0..1)
        brightness = float(np.mean(pixels)) / 255.0

        # Compute average color
        avg_color = np.mean(pixels, axis=0) / 255.0

        # Compute pixel variance (how much pixels vary from average)
        pixel_variance = float(np.var(pixels)) / (255.0 ** 2)

        # Detect blank frames (below brightness threshold)
        blank = brightness < 0.05

        # Compute static score vs previous frame
        static_score = 0.0
        if prev_pixels is not None:
            if len(prev_pixels.shape) == 1:
                prev_pixels = prev_pixels.reshape(pixel_count, 3)
            # Frame delta: mean absolute difference normalized
            delta = np.mean(np.abs(pixels.astype(float) - prev_pixels.astype(float))) / 255.0
            static_score = max(0.0, 1.0 - delta)  # 0 = very different, 1 = identical

        return {
            "frame_number": frame_num,
            "timestamp": timestamp,
            "brightness": brightness,
            "average_color": {"r": float(avg_color[0]), "g": float(avg_color[1]), "b": float(avg_color[2])},
            "pixel_variance": pixel_variance,
            "blank": blank,
            "static_score": static_score,
        }


class DiagnosticsSummary:
    """Compute aggregate diagnostics across all frames."""

    def __init__(self):
        self.frame_diagnostics: List[Dict] = []
        self.duration = 0.0
        self.render_duration_ms = 0.0
        self.fps = 30

    def add_frame(self, diagnostic: Dict):
        """Add a frame's diagnostics."""
        self.frame_diagnostics.append(diagnostic)

    def compute_summary(self, render_duration_ms: float = 0.0, fps: float = 30) -> Dict:
        """
        Compute overall summary from all frames.
        
        Args:
            render_duration_ms: Total render time in milliseconds
            fps: Frames per second
            
        Returns:
            Summary dict with aggregate metrics
        """
        self.render_duration_ms = render_duration_ms
        self.fps = fps

        if not self.frame_diagnostics:
            return self._empty_summary()

        # Extract metrics from all frames
        frame_nums = [d["frame_number"] for d in self.frame_diagnostics]
        timestamps = [d["timestamp"] for d in self.frame_diagnostics]
        brightnesses = [d["brightness"] for d in self.frame_diagnostics]
        colors = [d["average_color"] for d in self.frame_diagnostics]
        static_scores = [d["static_score"] for d in self.frame_diagnostics]
        blank_frames = [i for i, d in enumerate(self.frame_diagnostics) if d["blank"]]

        # Brightness metrics
        avg_brightness = float(np.mean(brightnesses))
        min_brightness = float(np.min(brightnesses))
        max_brightness = float(np.max(brightnesses))
        brightness_variance = float(np.var(brightnesses))

        # Average color
        avg_color = {
            "r": float(np.mean([c["r"] for c in colors])),
            "g": float(np.mean([c["g"] for c in colors])),
            "b": float(np.mean([c["b"] for c in colors])),
        }

        # Color variety: std dev across frames
        color_variety = float(
            np.mean([
                np.std([c["r"] for c in colors]),
                np.std([c["g"] for c in colors]),
                np.std([c["b"] for c in colors]),
            ])
        )

        # Frame deltas (temporal variation)
        frame_deltas = [d["static_score"] for d in self.frame_diagnostics if d["static_score"] > 0]
        avg_frame_delta = 1.0 - float(np.mean(frame_deltas)) if frame_deltas else 0.5
        frame_delta_variance = float(np.var(frame_deltas)) if frame_deltas else 0.0
        max_frame_delta = 1.0 - float(np.min(frame_deltas)) if frame_deltas else 1.0

        # Beat response & section variation (Epic 09.B2)
        beat_response_score, section_variation_score = self._compute_variety_metrics()

        # Static frames (low delta over time)
        static_frame_count = sum(1 for s in static_scores if s > 0.95)

        # Warnings
        warnings = []
        if len(blank_frames) > len(self.frame_diagnostics) * 0.1:
            warnings.append(f"More than 10% blank frames ({len(blank_frames)})")
        if static_frame_count > len(self.frame_diagnostics) * 0.3:
            warnings.append(f"More than 30% static frames ({static_frame_count})")
        if avg_frame_delta < 0.01:
            warnings.append("Render is too static - very little frame-to-frame variation")
        if beat_response_score < 0.2:
            warnings.append("Low beat responsiveness - content doesn't follow music")

        duration = timestamps[-1] - timestamps[0] if timestamps else 0.0

        return {
            "total_frames": len(self.frame_diagnostics),
            "duration": duration,
            "render_duration_ms": render_duration_ms,
            "avg_brightness": avg_brightness,
            "min_brightness": min_brightness,
            "max_brightness": max_brightness,
            "brightness_variance": brightness_variance,
            "avg_color": avg_color,
            "color_variety": color_variety,
            "blank_frame_count": len(blank_frames),
            "blank_frame_indices": blank_frames,
            "avg_frame_delta": avg_frame_delta,
            "frame_delta_variance": frame_delta_variance,
            "max_frame_delta": max_frame_delta,
            "beat_response_score": beat_response_score,
            "section_variation_score": section_variation_score,
            "static_frame_count": static_frame_count,
            "warnings": warnings,
        }

    def _compute_variety_metrics(self) -> Tuple[float, float]:
        """
        Compute beat response and section variation (Epic 09.B2).
        
        Returns:
            (beat_response_score, section_variation_score) both 0..1
        """
        if len(self.frame_diagnostics) < 2:
            return 0.5, 0.5

        # Beat response: measure frame delta at beat boundaries vs between beats
        # For now, use heuristic: sample frame deltas at regular intervals
        timestamps = [d["timestamp"] for d in self.frame_diagnostics]
        static_scores = [d["static_score"] for d in self.frame_diagnostics]

        # Section variation: compare deltas in first half vs second half
        mid = len(static_scores) // 2
        first_half_avg_delta = 1.0 - float(np.mean([s for s in static_scores[:mid]])) if mid > 0 else 0.5
        second_half_avg_delta = 1.0 - float(np.mean([s for s in static_scores[mid:]])) if len(static_scores) > mid else 0.5

        # Beat response is correlation with time (change shouldn't be random)
        beat_response_score = float(np.mean([1.0 - s for s in static_scores if s < 0.95]) / 2.0)
        beat_response_score = min(1.0, max(0.0, beat_response_score))

        # Section variation is difference between halves
        section_variation_score = abs(first_half_avg_delta - second_half_avg_delta)
        section_variation_score = min(1.0, max(0.0, section_variation_score))

        return beat_response_score, section_variation_score

    def _empty_summary(self) -> Dict:
        """Return empty summary."""
        return {
            "total_frames": 0,
            "duration": 0.0,
            "render_duration_ms": 0.0,
            "avg_brightness": 0.0,
            "min_brightness": 0.0,
            "max_brightness": 0.0,
            "brightness_variance": 0.0,
            "avg_color": {"r": 0.0, "g": 0.0, "b": 0.0},
            "color_variety": 0.0,
            "blank_frame_count": 0,
            "blank_frame_indices": [],
            "avg_frame_delta": 0.0,
            "frame_delta_variance": 0.0,
            "max_frame_delta": 0.0,
            "beat_response_score": 0.0,
            "section_variation_score": 0.0,
            "static_frame_count": 0,
            "warnings": [],
        }


class AssetGenerator:
    """Generate visual assets: contact sheets and preview GIFs (Epic 09.B3, 09.B4)."""

    @staticmethod
    def generate_contact_sheet(
        frames: List[np.ndarray],
        output_path: str,
        cols: int = 4,
        rows: int = 3,
        frame_width: int = 50,
        frame_height: int = 25,
    ) -> Dict:
        """
        Generate a contact sheet showing sample frames in a grid.
        
        Args:
            frames: List of frame pixel arrays
            output_path: Where to save the PNG
            cols, rows: Grid dimensions
            frame_width, frame_height: Size of each thumbnail
            
        Returns:
            Metadata about the contact sheet
        """
        grid_cols = cols
        grid_rows = rows
        total_samples = cols * rows

        # Sample frames evenly across the render
        if len(frames) <= total_samples:
            sample_indices = list(range(len(frames)))
        else:
            step = len(frames) // total_samples
            sample_indices = [i * step for i in range(total_samples)]

        # Create grid image
        img_width = cols * frame_width
        img_height = rows * frame_height
        contact_sheet = Image.new("RGB", (img_width, img_height), color=(0, 0, 0))

        # Place frames in grid
        for idx, frame_idx in enumerate(sample_indices):
            if idx >= total_samples:
                break

            frame_data = frames[frame_idx]
            if len(frame_data.shape) == 1:
                # Flattened: assume square (100x50x3) based on standard resolution
                pixel_count = len(frame_data) // 3
                frame_data = frame_data.reshape(pixel_count, 3)

            # Resize frame to thumbnail
            frame_array = np.array(frame_data, dtype=np.uint8)
            frame_img = Image.fromarray(frame_array)
            frame_img = frame_img.resize((frame_width, frame_height), Image.Resampling.LANCZOS)

            # Place in grid
            col = idx % cols
            row = idx // cols
            x = col * frame_width
            y = row * frame_height
            contact_sheet.paste(frame_img, (x, y))

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        contact_sheet.save(output_path)

        return {
            "grid_cols": cols,
            "grid_rows": rows,
            "frame_width": frame_width,
            "frame_height": frame_height,
            "total_frames": len(frames),
            "sample_rate": "all" if len(frames) <= total_samples else len(frames) // total_samples,
        }

    @staticmethod
    def generate_preview_strip(
        frames: List[np.ndarray],
        output_path: str,
        strip_height: int = 50,
        max_width: int = 2000,
    ) -> Dict:
        """
        Generate a horizontal preview strip (first to last frame morphed).
        
        Args:
            frames: List of frame pixel arrays
            output_path: Where to save the PNG
            strip_height: Height of output strip
            max_width: Maximum width in pixels
            
        Returns:
            Metadata about the strip
        """
        if not frames:
            return {"frames_sampled": 0, "width": 0}

        # Sample frames evenly to fit max_width
        frame_width = 50  # standard 100x50 render
        num_samples = min(len(frames), max_width // frame_width)
        if num_samples < 1:
            num_samples = 1

        if num_samples >= len(frames):
            sample_indices = list(range(len(frames)))
        else:
            step = len(frames) // num_samples
            sample_indices = [i * step for i in range(num_samples)]

        # Create strip image
        strip = Image.new("RGB", (frame_width * num_samples, strip_height), color=(0, 0, 0))

        # Place sampled frames horizontally
        for idx, frame_idx in enumerate(sample_indices):
            frame_data = frames[frame_idx]
            if len(frame_data.shape) == 1:
                pixel_count = len(frame_data) // 3
                frame_data = frame_data.reshape(pixel_count, 3)

            frame_array = np.array(frame_data, dtype=np.uint8)
            frame_img = Image.fromarray(frame_array)
            frame_img = frame_img.resize((frame_width, strip_height), Image.Resampling.LANCZOS)

            x = idx * frame_width
            strip.paste(frame_img, (x, 0))

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        strip.save(output_path)

        return {
            "frames_sampled": len(sample_indices),
            "width": frame_width * num_samples,
            "height": strip_height,
        }
