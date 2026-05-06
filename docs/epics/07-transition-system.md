# Epic 07: Transition System

## Story

As a show author, I want transitions between scenes to be intentional, musical, and previewable.

## Why This Matters

Hard cuts can be powerful, but accidental cuts feel cheap. BeatDrop-like systems feel rich partly because preset changes are treated as visual events.

## Scope

- Add transition types:
  - Hard cut.
  - Crossfade.
  - Beat flash cut.
  - Wipe.
  - Pixel dissolve.
  - Palette morph.
  - Intensity dip and rise.
- Allow transitions to align to beat, bar, phrase, or section boundaries.
- Add transition preview diagnostics.
- Add transition metadata to render artifacts.

## Acceptance Criteria

- Scene changes can use different transition types.
- Transition durations are expressed in beats or seconds.
- Transition output is deterministic and testable.

## Dependencies

- Timeline director.
- Layer library.
- Render contract.

## First Iteration

Implement hard cut, crossfade, and beat flash cut.

