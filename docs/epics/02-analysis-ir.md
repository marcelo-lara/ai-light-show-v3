# Epic 02: Analysis IR

## Story

As a preset author, I want a rich musical analysis IR so visual behavior can follow musical structure instead of only reacting to raw frequency values.

## Why This Matters

Beat-driven visuals become repetitive if every frame only knows five normalized bands and whether a beat is nearby. Production shows need musical context.

## Scope

- Version the analysis cache.
- Keep existing bands: `sub_bass`, `bass`, `low_mid`, `high_mid`, `treble`.
- Add beat phase, bar phase, and nearest beat distance.
- Add smoothed envelopes and transient curves per band.
- Add energy curve and intensity curve.
- Add downbeat and phrase candidates.
- Add section candidates such as intro, build, drop, breakdown, outro when confidence allows.
- Store confidence values and diagnostics.

## Acceptance Criteria

- Presets can query beat phase and phrase progress at any timestamp.
- Modulators can use smoothed values without each layer reimplementing smoothing.
- Analysis artifacts are cacheable and invalidated when the analyzer version changes.

## Dependencies

- Existing Essentia analyzer.
- Render contract metadata.

## First Iteration

Add beat phase, nearest beat distance, smoothed band envelopes, and a normalized global energy curve.

