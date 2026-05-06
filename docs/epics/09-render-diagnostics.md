# Epic 09: Render Diagnostics

## Story

As a developer and show reviewer, I want render diagnostics so I can tell whether a show is healthy, synchronized, varied, and performant.

## Why This Matters

Low-resolution output can fail quietly: too dark, too static, too noisy, too repetitive, or too expensive to generate. Diagnostics make quality visible.

## Scope

- Frame brightness statistics.
- Color distribution.
- Motion/change between frames.
- Beat response score.
- Section variation score.
- Dropped or missing frame detection.
- Render duration and memory usage.
- Cache size.
- Visual contact sheets.
- Short preview GIF or image strip for each render.

## Acceptance Criteria

- Each render produces a diagnostics summary.
- Obviously blank or static renders are flagged.
- Diagnostics can be shown in the frontend.
- Golden output tests can catch accidental visual changes.

## Dependencies

- Render contract.
- Preview console.

## First Iteration

Generate brightness, average color, frame-delta, and blank-frame warnings for every render artifact.

