try:
    import numpy as np
except Exception:
    import numpy as np


class Diagnostics:
    """Collect simple render diagnostics per frame.

    Tracks average brightness, average color, mean frame delta, blank frames, and render duration.
    """
    def __init__(self, num_pixels: int):
        self.num_pixels = num_pixels
        self.frame_count = 0
        self.total_brightness = 0.0
        self.total_color = np.zeros(3, dtype=np.float64)
        self.total_frame_delta = 0.0
        self.prev_frame = None
        self.blank_frame_count = 0
        self.blank_warnings = []

    def update(self, pixels):
        """Ingest a frame. `pixels` is an (N,3) uint8 array."""
        arr = np.asarray(pixels)
        if arr.size == 0:
            return

        # mean brightness across all channels and pixels
        frame_brightness = float(arr.mean())
        # mean color per channel
        frame_mean_color = arr.mean(axis=0).astype(np.float64)

        # accumulate
        self.total_brightness += frame_brightness
        self.total_color += frame_mean_color

        # frame delta against previous frame (mean absolute difference)
        if self.prev_frame is not None:
            delta = np.mean(np.abs(arr.astype(np.int32) - self.prev_frame.astype(np.int32)))
            self.total_frame_delta += float(delta)

        # blank-frame detection: very low brightness
        if frame_brightness < 5.0:
            self.blank_frame_count += 1
            # store a compact warning
            self.blank_warnings.append({"frame": self.frame_count, "brightness": frame_brightness})

        # update state
        self.prev_frame = arr.copy()
        self.frame_count += 1

    def summary(self, render_duration: float = 0.0):
        """Return a summary dict of diagnostics."""
        if self.frame_count == 0:
            return {
                "frame_count": 0,
                "average_brightness": 0.0,
                "average_color": {"r": 0.0, "g": 0.0, "b": 0.0},
                "average_frame_delta": 0.0,
                "blank_frame_count": 0,
                "blank_warnings": [],
                "render_duration": float(render_duration),
            }

        avg_brightness = self.total_brightness / float(self.frame_count)
        avg_color = (self.total_color / float(self.frame_count)).tolist()
        # average delta is defined over frame_count - 1 intervals
        avg_delta = (self.total_frame_delta / float(max(1, self.frame_count - 1))) if self.frame_count > 1 else 0.0

        return {
            "frame_count": int(self.frame_count),
            "average_brightness": float(avg_brightness),
            "average_color": {"r": float(avg_color[0]), "g": float(avg_color[1]), "b": float(avg_color[2])},
            "average_frame_delta": float(avg_delta),
            "blank_frame_count": int(self.blank_frame_count),
            "blank_warnings": list(self.blank_warnings),
            "render_duration": float(render_duration),
        }
