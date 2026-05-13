import sys
import os
import numpy as cpu_np

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from engine import layers
from types import SimpleNamespace


def make_context(width=10, height=5):
    np = layers.np
    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)
    coords = np.column_stack((xx.ravel(), yy.ravel()))
    palette = SimpleNamespace(primary="#ff0000", secondary="#00ff00", accent="#0000ff", background="#000000")
    return layers.FrameContext(coords=coords, features={}, q_buffer={}, width=width, height=height, palette=palette)


def to_host(arr):
    if hasattr(layers.np, 'asnumpy'):
        return cpu_np.asarray(layers.np.asnumpy(arr))
    return cpu_np.asarray(arr)


def test_particle_field_layer_seeded_determinism():
    seed = 123
    # First run
    layers.np.random.seed(seed)
    ctx1 = make_context()
    p1 = layers.ParticleFieldLayer()
    out1 = p1.render(ctx1)

    # Second run - reset seed and recreate context
    layers.np.random.seed(seed)
    ctx2 = make_context()
    p2 = layers.ParticleFieldLayer()
    out2 = p2.render(ctx2)

    a1 = to_host(out1)
    a2 = to_host(out2)
    assert a1.shape == a2.shape
    assert cpu_np.array_equal(a1, a2), "ParticleFieldLayer is not deterministic for same seed"


def test_background_sweep_and_waveform_ring_determinism():
    seed = 42
    layers.np.random.seed(seed)
    ctx1 = make_context()
    b1 = layers.BackgroundSweepLayer()
    w1 = layers.WaveformRingLayer()
    out_b1 = b1.render(ctx1)
    out_w1 = w1.render(ctx1)

    layers.np.random.seed(seed)
    ctx2 = make_context()
    b2 = layers.BackgroundSweepLayer()
    w2 = layers.WaveformRingLayer()
    out_b2 = b2.render(ctx2)
    out_w2 = w2.render(ctx2)

    assert cpu_np.array_equal(to_host(out_b1), to_host(out_b2)), "BackgroundSweepLayer not deterministic"
    assert cpu_np.array_equal(to_host(out_w1), to_host(out_w2)), "WaveformRingLayer not deterministic"
