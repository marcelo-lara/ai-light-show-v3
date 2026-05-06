# Epic 01: Render Contract

## Story

As a show author, I want every generated `100x50` show to follow a stable, versioned contract so playback, preview, diagnostics, and export all agree on what the frames mean.

## Why This Matters

The current frontend loads cached JSON frames directly. That is a good start, but the format needs to become an explicit product contract before we build richer engines on top of it.

## Scope

- Define `canvas.width = 100` and `canvas.height = 50` as canonical output.
- Add schema versioning to render artifacts.
- Store renderer version, preset id, preset version, seed, params, song id, analysis id, FPS, duration, and frame count.
- Decide whether frames stay packed RGB integers or move to a compact binary artifact with JSON sidecar.
- Add artifact compatibility checks in frontend and backend.
- Add deterministic render seed behavior.

## Acceptance Criteria

- Render artifacts include enough metadata to reproduce a show.
- The frontend rejects incompatible artifacts with a clear message.
- Regenerating with the same inputs produces identical output.
- A short fixture render can be used as a golden output in tests.

## Dependencies

- Existing frame renderer.
- Existing frontend frame loader.

## First Iteration

Keep the JSON format, add `schema_version`, `render_id`, `preset_id`, `params`, and `seed`, then update the frontend type definitions.

