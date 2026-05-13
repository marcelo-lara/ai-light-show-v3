import json
import importlib.util, sys, os
spec = importlib.util.spec_from_file_location("mapping", os.path.join(os.path.dirname(__file__), "engine", "mapping.py"))
mapping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapping)


def test_load_fixture_data():
    data = mapping.load_fixture_data("data/fixtures")
    assert "fixtures" in data and isinstance(data["fixtures"], list)
    assert "pois" in data and isinstance(data["pois"], list)


def test_pixel_order_linear_and_serpentine():
    w, h = 4, 3
    linear = mapping.pixel_order(w, h, serpentine=False)
    assert linear[0] == (0, 0)
    assert linear[1] == (1, 0)
    assert linear[-1] == (3, 2)

    serp = mapping.pixel_order(w, h, serpentine=True)
    # second row should be reversed
    assert serp[4] == (3, 1)
    assert serp[5] == (2, 1)


def test_generate_manifest_gamma_and_brightness():
    w, h = 2, 1
    colors = [(255, 128, 0), (0, 64, 255)]
    m = mapping.generate_manifest(w, h, colors, serpentine=False, gamma=1.0, brightness=0.5)
    assert m["pixel_count"] == 2
    # brightness 0.5 should halve values
    assert m["pixels"][0]["r"] in (127, 128)
    assert m["pixels"][0]["g"] in (63, 64)
    assert m["pixels"][0]["b"] == 0
