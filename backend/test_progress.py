import os
from backend.test_validation import make_renderer, make_basic_preset


def test_progress_callback_called():
    presets = {"undersea_pulse_01": make_basic_preset()}
    r = make_renderer("/fake/song_progress.mp3", seed=2, fps=10, width=8, height=4, presets=presets)
    r.presets = presets
    total_frames = int(r.analysis_data['duration'] * r.fps)

    calls = []
    def cb(phase, current, total):
        calls.append((phase, current, total))

    # call generate_frames with progress callback
    r.generate_frames(output_format="legacy", progress_callback=cb)

    assert len(calls) > 0, "Progress callback was not called"
    # final call should report completion with current==total
    last = calls[-1]
    assert last[1] == last[2]
    assert last[2] == total_frames
