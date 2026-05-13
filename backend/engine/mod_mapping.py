from typing import List, Dict, Any
import math


def apply_mapping(value: float, ops: List[Dict[str, Any]]) -> float:
    """Apply mapping operations in order to a base value.
    Supported ops: scale (factor, offset), clamp (min, max), invert, quantize (step), curve (gamma), smooth/lag (no-op placeholder)
    """
    v = float(value)
    for op in ops:
        name = op.get('op')
        if name == 'scale':
            factor = op.get('factor', 1.0)
            offset = op.get('offset', 0.0)
            v = v * factor + offset
        elif name == 'clamp':
            lo = op.get('min', None)
            hi = op.get('max', None)
            if lo is not None:
                v = max(lo, v)
            if hi is not None:
                v = min(hi, v)
        elif name == 'invert':
            v = 1.0 - v
        elif name == 'quantize':
            step = op.get('step', 1.0)
            if step > 0:
                v = round(v / step) * step
        elif name == 'curve':
            # gamma curve
            g = op.get('gamma', 1.0)
            if v >= 0:
                v = math.pow(v, g)
        elif name in ('smooth', 'lag'):
            # placeholders for stateful ops; not implemented deterministically here
            v = v
        else:
            # unknown op, ignore
            v = v
    return v
