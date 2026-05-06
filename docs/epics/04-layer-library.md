# Epic 04: Layer Library

## Story

As a preset author, I want a library of low-resolution-native visual layers so I can build varied looks that read clearly on a `100x50` canvas.

## Why This Matters

At this resolution, not every effect works. The layer library should favor bold forms, clean rhythm, and strong silhouettes.

## Scope

- Convert current wave and radial pulse into reusable layers.
- Add low-res-native layers:
  - Solid and gradient fields.
  - Horizontal and vertical bars.
  - Rings and expanding pulses.
  - Beat flashes.
  - Scanners and sweeps.
  - Symmetric waveforms.
  - Particle sparks with bounded counts.
  - Pixel masks and stencils.
  - Noise fields.
  - Kaleidoscope or mirror transforms.
- Add blend modes: max, add, alpha, multiply, screen, difference, mask.
- Add coordinate transforms: mirror, rotate, scroll, zoom, warp.

## Acceptance Criteria

- Layers are registered by id.
- Layers expose parameter schemas.
- Layers are deterministic when seeded.
- Each layer has at least one visual fixture or snapshot test.

## Dependencies

- Preset schema.
- Modulation system.

## First Iteration

Create layer interfaces and migrate `WaveShader` and `RadialPulseShader` into the registry without changing their visible output.

