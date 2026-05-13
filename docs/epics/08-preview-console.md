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
- Fixture and POI reference overlay on the preview canvas.
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

Add artifact metadata display, generation progress, schema error states, a fixture and POI reference overlay, and a fullscreen preview toggle.

## Next Steps

- Wire the generation-status API to report analysis and render as distinct phases with numeric progress so the console can show a real phase-aware progress bar instead of a generic generating state.
- Keep preview compatibility when render artifacts move from one monolithic binary payload to chunked binary frame files.

