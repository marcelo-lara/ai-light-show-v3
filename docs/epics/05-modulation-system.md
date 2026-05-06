# Epic 05: Modulation System

## Story

As a preset author, I want parameters to be driven by musical and procedural modulators so effects feel alive without hardcoding behavior inside each layer.

## Why This Matters

Production visuals need consistent modulation language. Without it, every layer invents its own smoothing, beat response, random motion, and intensity handling.

## Scope

- Define modulation sources:
  - Band envelopes.
  - Onset.
  - Beat pulse.
  - Beat phase.
  - Bar phase.
  - Phrase progress.
  - Section intensity.
  - LFO.
  - Random walk.
  - Seeded sample-and-hold.
- Define mapping operations: scale, clamp, invert, curve, smooth, lag, quantize.
- Allow parameter bindings in presets.
- Add debug output for modulated values.

## Acceptance Criteria

- A preset can bind a layer parameter to a modulator without custom code.
- Modulator values are deterministic.
- The frontend can show current modulator values during playback.

## Dependencies

- Analysis IR.
- Preset schema.

## First Iteration

Implement bindings for `bass`, `treble`, `global_energy`, `beat_pulse`, and `beat_phase`, with scale/clamp/curve mapping.

