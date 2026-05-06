# Epic 03: Preset Schema

## Story

As a show author, I want visual looks to be described as presets so new looks can be added, tuned, reused, and sequenced without changing renderer control flow.

## Why This Matters

The current renderer always calls a wave layer and a radial pulse layer. That blocks variety. A preset schema lets us turn visual design into data.

## Scope

- Define preset identity, version, display name, tags, and description.
- Define parameters with type, default, min, max, step, and UI grouping.
- Define layer stack.
- Define palette and color controls.
- Define blend modes.
- Define modulation bindings.
- Define preset-level seed behavior.
- Add preset validation.

## Acceptance Criteria

- Existing wave and pulse behavior can be represented as presets.
- The renderer can load a preset and render its declared layer stack.
- The frontend can inspect parameters from the preset schema.
- Invalid presets fail with actionable errors.

## Dependencies

- Render contract.
- Layer library.
- Modulation system.

## First Iteration

Create an in-repo JSON or YAML preset format and migrate the current wave/pulse stack into one preset named `undersea_pulse_01`.

