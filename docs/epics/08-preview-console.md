# Epic 08: Preview Console

## Story

As a user, I want the frontend to act like a production console so I can generate, inspect, compare, tune, and approve shows.

## Why This Matters

The current frontend proves playback sync, but production work needs review ergonomics. The UI should help users make decisions about shows.

## Scope

- Preset browser.
- Parameter editor generated from preset schema.
- Render job progress and logs.
- Timeline view.
- Section and beat markers on waveform.
- Frame inspector with pixel coordinates and RGB values.
- A/B compare between two renders.
- Fullscreen preview mode.
- Missing artifact and incompatible schema states.
- Render approval status.

## Acceptance Criteria

- A user can generate and review a show from the UI.
- Parameter changes are clearly tied to regenerated output.
- The UI exposes timeline and analysis context.
- Fullscreen preview preserves the `100x50` aspect ratio and pixel character.

## Dependencies

- Render contract.
- Preset schema.
- Timeline director.
- Render diagnostics.

## First Iteration

Add artifact metadata display, generation progress, schema error states, and a fullscreen preview toggle.

