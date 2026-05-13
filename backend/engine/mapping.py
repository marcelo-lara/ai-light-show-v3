import json
from typing import List, Tuple, Dict

# Canonical coordinate system: origin at top-left (0,0), row-major order

def load_fixture_data(fixtures_dir: str) -> Dict[str, List[Dict]]:
    """Load fixtures.json and pois.json from fixtures_dir."""
    with open(f"{fixtures_dir}/fixtures.json", "r") as f:
        fixtures = json.load(f)
    with open(f"{fixtures_dir}/pois.json", "r") as f:
        pois = json.load(f)
    return {"fixtures": fixtures, "pois": pois}


def pixel_order(width: int, height: int, serpentine: bool = False) -> List[Tuple[int, int]]:
    """Return list of (x,y) pixel coordinates in canonical row-major order.
    If serpentine is True, every other row is reversed (common LED strip layout).
    """
    coords: List[Tuple[int, int]] = []
    for y in range(height):
        row = [(x, y) for x in range(width)]
        if serpentine and (y % 2 == 1):
            row.reverse()
        coords.extend(row)
    return coords


def colors_to_sequence(colors: List[Tuple[int, int, int]], width: int, height: int, serpentine: bool = False) -> List[Tuple[int, int, int]]:
    """Map a flat or 2D color list into output sequence using pixel_order.
    Accepts colors as flat list length width*height or as list of rows.
    Returns list of (r,g,b) in mapped order.
    """
    # normalize input to 2D rows
    if len(colors) == width * height and isinstance(colors[0], tuple):
        # assume row-major flat
        rows = [colors[i * width:(i + 1) * width] for i in range(height)]
    else:
        rows = colors
    seq = []
    for x, y in pixel_order(width, height, serpentine):
        seq.append(rows[y][x])
    return seq


def apply_gamma_and_brightness(pixels: List[Tuple[int, int, int]], gamma: float = None, brightness: float = 1.0) -> List[Tuple[int, int, int]]:
    """Apply gamma correction and brightness limiting. Pixels are 0-255 ints.
    gamma=None means no correction. brightness in (0,1] scales values.
    """
    out = []
    for r, g, b in pixels:
        def fix(v: int) -> int:
            v_n = max(0, min(255, v)) / 255.0
            if gamma and gamma > 0:
                v_n = v_n ** gamma
            v_n = v_n * brightness
            return int(max(0, min(255, round(v_n * 255))))
        out.append((fix(r), fix(g), fix(b)))
    return out


def generate_manifest(width: int, height: int, colors: List[Tuple[int, int, int]], serpentine: bool = False, gamma: float = None, brightness: float = 1.0) -> Dict:
    """Generate an export manifest mapping pixels to ordered output array and metadata.
    Manifest contains pixel_count, ordering coordinates, and rgb values (post-processed).
    """
    seq = colors_to_sequence(colors, width, height, serpentine)
    processed = apply_gamma_and_brightness(seq, gamma=gamma, brightness=brightness)
    manifest = {
        "pixel_count": width * height,
        "width": width,
        "height": height,
        "serpentine": bool(serpentine),
        "pixels": [{"r": r, "g": g, "b": b} for (r, g, b) in processed],
    }
    return manifest
