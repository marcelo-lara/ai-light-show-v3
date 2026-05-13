import numpy as np
import math
from engine.diagnostics import Diagnostics


def test_diagnostics_basic():
    num_pixels = 4
    d = Diagnostics(num_pixels)

    # frame 1: all zeros (blank)
    f1 = np.zeros((num_pixels, 3), dtype=np.uint8)
    d.update(f1)

    # frame 2: all 255
    f2 = np.full((num_pixels, 3), 255, dtype=np.uint8)
    d.update(f2)

    # frame 3: all 128
    f3 = np.full((num_pixels, 3), 128, dtype=np.uint8)
    d.update(f3)

    summary = d.summary(render_duration=1.23)

    # frame brightnesses: 0,255,128 -> average ~127.666
    assert summary["frame_count"] == 3
    assert summary["blank_frame_count"] == 1
    assert math.isclose(summary["average_brightness"], (0 + 255 + 128) / 3.0, rel_tol=1e-6)

    # average color per channel should match brightness in these uniform frames
    avg_color = summary["average_color"]
    assert math.isclose(avg_color["r"], (0 + 255 + 128) / 3.0, rel_tol=1e-6)
    assert math.isclose(avg_color["g"], (0 + 255 + 128) / 3.0, rel_tol=1e-6)
    assert math.isclose(avg_color["b"], (0 + 255 + 128) / 3.0, rel_tol=1e-6)

    # average frame delta: between f1->f2 =255, f2->f3 =127 => avg = (255+127)/2 = 191
    assert math.isclose(summary["average_frame_delta"], (255 + 127) / 2.0, rel_tol=1e-6)

    assert math.isclose(summary["render_duration"], 1.23, rel_tol=1e-6)


if __name__ == '__main__':
    test_diagnostics_basic()
    print("test_diagnostics_basic passed")
