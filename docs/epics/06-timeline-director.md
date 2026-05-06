# Epic 06: Timeline Director

## Story

As a show author, I want a song-level timeline so a show evolves through scenes instead of running one visual recipe from beginning to end.

## Why This Matters

Production quality is often about timing and progression. Even strong effects get stale if they do not change with the song.

## Scope

- Define scene format: start, end, preset id, params, seed, intensity.
- Generate first-pass scenes from sections, phrase boundaries, or beat counts.
- Support manual scene overrides.
- Support scene-level parameter automation.
- Add timeline metadata to render artifacts.
- Add diagnostics for scene duration and transition alignment.

## Acceptance Criteria

- A song can render with multiple presets in one artifact.
- Scene boundaries align to beats or phrases by default.
- Timeline data is visible to the frontend.

## Dependencies

- Analysis IR.
- Preset schema.
- Transition system.

## First Iteration

Create a timeline with one scene per detected or configured section, using a small preset pool and beat-aligned boundaries.

