# Development Handoff Stories

Use these as small implementation handoff units. Each story should fit one focused PR or one focused LLM task.

## Handoff Spec

- Frontend dev port: `3400`.
- Backend API port: `3401`.
- Split work into backend, frontend, and validation tracks.
- Story ids stay stable even if list order changes.
- Prefer smaller stories over broad multi-surface stories.
- The server owns `current_song` and `current_canvas` state.
- The frontend should request song changes from the backend instead of loading songs directly.
- When a new song is loaded, the backend should return or push the updated current song and current canvas state to the frontend.
- If the current song has no canvas or show yet, the song should still load successfully; canvas creation happens only when the user triggers `Render`.
- The left control column uses tabs: one `Main` tab with `show name` and `Render`, then one tab per shader or layer property group.

## Implementation Order

1. Epic 01: Render Contract
2. Epic 02: Analysis IR
3. Epic 03: Preset Schema
4. Epic 04: Layer Library
5. Epic 05: Modulation System
6. Epic 11: Raindrops Shader
7. Epic 12: Spectroid Chase Shader
8. Epic 06: Timeline Director
9. Epic 07: Transition System
10. Epic 08: Preview Console
11. Epic 09: Render Diagnostics
12. Epic 10: Fixture Mapping And Export

## Epic 01: Render Contract

### Backend Track

- [ ] 01.B1 Artifact schema v1: add `schema_version`, `render_id`, `preset_id`, `preset_version`, `seed`, `params`, `song_id`, `analysis_id`, `fps`, `duration`, and `frame_count` to the render artifact.
- [ ] 01.B2 Render id rules: generate a stable `render_id` from reproducible inputs instead of a random export id.
- [ ] 01.B3 Seed rules: make seed handling explicit and required in the render contract.
- [ ] 01.B4 Backend compatibility checks: reject missing required fields and unsupported schema versions.
- [ ] 01.B5 Current song state: add backend-owned `current_song` and `current_canvas` state to the playback contract.
- [ ] 01.B6 Empty canvas state: define the contract for a loaded song with no current canvas yet.

### Frontend Track

- [ ] 01.F1 Shared artifact type: define frontend types that match the backend render artifact contract.
- [ ] 01.F2 Frontend compatibility state: reject incompatible artifacts with a clear UI error state.
- [ ] 01.F3 Metadata display readiness: surface schema version, render id, preset id, and seed in a way the UI can consume.
- [ ] 01.F4 Current state types: add frontend types for backend-owned `current_song`, `current_canvas`, and empty-canvas states.

### Validation Track

- [ ] 01.V1 Deterministic render test: prove the same song, preset, params, and seed produce identical frames.
- [ ] 01.V2 Stable render id test: prove the same inputs produce the same `render_id`.
- [ ] 01.V3 Golden sample fixture: add one short canonical render artifact for regression checks.
- [ ] 01.V4 Empty canvas contract test: prove a song can load without an existing canvas or show.

## Epic 02: Analysis IR

### Backend Track

- [ ] 02.B1 Analysis schema v1: version the analysis cache and invalidate it when analyzer logic changes.
- [ ] 02.B2 Beat timing signals: add `beat_phase` and nearest-beat distance to timestamp queries.
- [ ] 02.B3 Bar timing signal: add `bar_phase` to timestamp queries.
- [ ] 02.B4 Smoothed envelopes: add smoothed per-band envelopes.
- [ ] 02.B5 Global energy: add a normalized global energy curve.
- [ ] 02.B6 Musical structure: add downbeat, phrase, and section candidates with confidence values.
- [ ] 02.B7 Analysis diagnostics: expose confidence, source metadata, and basic debug stats in the analysis artifact.

### Frontend Track

- [ ] 02.F1 Analysis type updates: add types for beat phase, bar phase, energy, and structure metadata.
- [ ] 02.F2 Analysis debug readiness: expose analysis metadata in a shape the UI can inspect later.

### Validation Track

- [ ] 02.V1 Cache invalidation test: prove analyzer schema changes invalidate cached analysis.
- [ ] 02.V2 Timestamp query test: prove beat phase, bar phase, and nearest-beat fields are available at render time.
- [ ] 02.V3 Signal sanity test: verify smoothed envelopes and energy values stay normalized and bounded.

## Epic 03: Preset Schema

### Backend Track

- [ ] 03.B1 Preset format v1: define preset identity, version, display fields, tags, and description.
- [ ] 03.B2 Parameter schema: define typed parameters with defaults, bounds, step size, and UI grouping.
- [ ] 03.B3 Layer stack schema: let a preset declare ordered layers and per-layer params.
- [ ] 03.B4 Palette schema: let a preset declare palette and color controls.
- [ ] 03.B5 Blend schema: let a preset declare blend modes at preset or layer level.
- [ ] 03.B6 Preset validation: fail invalid presets with actionable errors before render time.
- [ ] 03.B7 Baseline preset migration: represent the current wave plus pulse look as preset `undersea_pulse_01`.

### Frontend Track

- [ ] 03.F1 Preset summary type: add frontend types for preset identity, labels, and tags.
- [ ] 03.F2 Parameter schema type: add frontend types for typed preset parameters and UI groups.
- [ ] 03.F3 Preset loading readiness: make the UI able to consume schema-defined presets later without hardcoded assumptions.

### Validation Track

- [ ] 03.V1 Valid preset test: prove a valid preset loads and passes schema validation.
- [ ] 03.V2 Invalid preset test: prove invalid presets fail with actionable errors.
- [ ] 03.V3 Baseline parity test: prove `undersea_pulse_01` reproduces the current baseline look closely enough.

## Epic 04: Layer Library

### Backend Track

- [ ] 04.B1 Layer interface: define a registry-based layer API with deterministic seeded execution.
- [ ] 04.B2 Wave layer migration: convert wave into a reusable registry-backed layer.
- [ ] 04.B3 Radial pulse migration: convert radial pulse into a reusable registry-backed layer.
- [ ] 04.B4 Solid field layer: add a solid fill layer.
- [ ] 04.B5 Gradient field layer: add a gradient layer.
- [ ] 04.B6 Bars layer: add horizontal or vertical bars.
- [ ] 04.B7 Rings layer: add ring or expanding pulse output.
- [ ] 04.B8 Beat flash layer: add a beat flash layer.
- [ ] 04.B9 Scanner layer: add a scanner or sweep layer.
- [ ] 04.B10 Mirror transform: add mirror or symmetry transforms.
- [ ] 04.B11 Blend ops: add `max`, `add`, `alpha`, `multiply`, `screen`, `difference`, and `mask`.
- [ ] 04.B12 Scroll and zoom transforms: add scroll and zoom transforms.

### Frontend Track

- [ ] 04.F1 Layer metadata type: add frontend-readable layer ids, labels, and parameter schemas.
- [ ] 04.F2 Layer fixture browsing readiness: define a simple UI-facing shape for inspecting available layers later.

### Validation Track

- [ ] 04.V1 Registry test: prove layers are registered and loadable by id.
- [ ] 04.V2 Determinism test: prove seeded layers render reproducibly.
- [ ] 04.V3 Visual fixture coverage: add at least one fixture or snapshot test per layer.

## Epic 05: Modulation System

### Backend Track

- [ ] 05.B1 Audio modulator sources: support band envelopes, onset, beat pulse, beat phase, bar phase, and phrase progress.
- [ ] 05.B2 Procedural modulator sources: support LFO and seeded random sources.
- [ ] 05.B3 Mapping ops part 1: support scale, clamp, and invert.
- [ ] 05.B4 Mapping ops part 2: support curve, smooth, lag, and quantize.
- [ ] 05.B5 Preset bindings: allow presets to bind modulators to layer parameters without custom Python code.
- [ ] 05.B6 Deterministic execution: make modulator outputs stable for the same analysis, seed, and time.
- [ ] 05.B7 Debug output shape: expose resolved modulator values in a structured format.

### Frontend Track

- [ ] 05.F1 Modulator value types: add frontend types for current modulator values and mappings.
- [ ] 05.F2 Modulator inspection readiness: define a UI-facing shape for viewing live modulator values later.

### Validation Track

- [ ] 05.V1 Binding test: prove presets can bind modulators to layer parameters without layer-specific code.
- [ ] 05.V2 Determinism test: prove modulator outputs stay stable for the same inputs.
- [ ] 05.V3 Mapping test: prove mapping operations apply in the declared order.

## Epic 11: Raindrops Shader

### Backend Track

- [ ] 11.B1 Raindrops layer spec: define a POI-aware radial pulse layer named `raindrops`.
- [ ] 11.B2 POI source selection: allow pulses to start from one or more configured POIs.
- [ ] 11.B3 POI transit behavior: allow pulses to pass through configured POIs on the canvas.
- [ ] 11.B4 POI collision behavior: allow pulses to collide at configured POIs and create a visible interaction.
- [ ] 11.B5 Parameter schema: define controls for pulse rate, radius growth, decay, collision strength, and POI selection.
- [ ] 11.B6 Preset integration: make the raindrops shader usable from the preset and layer system.

### Frontend Track

- [ ] 11.F1 Shader metadata types: add frontend-readable types for the `raindrops` shader and its parameter schema.
- [ ] 11.F2 POI selection readiness: make the UI able to consume POI-backed shader controls later.
- [ ] 11.F3 Overlay compatibility: ensure the fixture and POI reference overlay remains useful while previewing raindrops output.

### Validation Track

- [ ] 11.V1 POI start test: prove pulses can originate from configured POIs.
- [ ] 11.V2 POI transit test: prove pulses can pass through intermediate POIs.
- [ ] 11.V3 POI collision test: prove two or more pulses can collide at a POI and produce deterministic output.
- [ ] 11.V4 Snapshot test: add at least one visual fixture or snapshot test for the raindrops shader.

## Epic 12: Spectroid Chase Shader

### Backend Track

- [ ] 12.B2 Central spectroid signal: define the analysis input for central spectroid, note, or chord-reactive triggering.
- [ ] 12.B1 Chase layer spec: define a note or chord-reactive shader named `spectroid_chase`.
- [ ] 12.B3 Parcan anchor selection: use parcan fixture positions as chase origin anchors on the canvas.
- [ ] 12.B4 Chase path generation: generate outward line motion from parcan anchors toward the canvas.
- [ ] 12.B5 Moving head follow lines: define line-follow behavior that moving heads can track visually later.
- [ ] 12.B6 Parameter schema: define controls for trigger sensitivity, line length, spread, fade, and chase speed.
- [ ] 12.B7 Preset integration: make the shader usable from the preset and layer system.

### Frontend Track

- [ ] 12.F1 Shader metadata types: add frontend-readable types for the `spectroid_chase` shader and its parameter schema.
- [ ] 12.F2 Fixture-anchor readiness: make the UI able to consume parcan-anchor and moving-head-line controls later.
- [ ] 12.F3 Overlay compatibility: ensure fixture and POI overlays remain useful while previewing the chase shader.

### Validation Track

- [ ] 12.V1 Trigger response test: prove the shader reacts deterministically to the central spectroid or note/chord signal.
- [ ] 12.V2 Parcan anchor test: prove chase lines start from parcan positions.
- [ ] 12.V3 Line-follow test: prove outward line motion is stable and visually trackable for moving-head follow behavior.
- [ ] 12.V4 Snapshot test: add at least one visual fixture or snapshot test for the spectroid chase shader.

## Epic 06: Timeline Director

### Backend Track

- [ ] 06.B1 Scene model: define scene fields for `start`, `end`, `preset_id`, `params`, `seed`, and `intensity`.
- [ ] 06.B2 Auto timeline from sections: generate a first-pass timeline from detected sections.
- [ ] 06.B3 Auto timeline from phrases or beats: support fallback scene generation from phrase or beat grouping.
- [ ] 06.B4 Scene overrides: support manual scene edits without breaking auto-generated defaults.
- [ ] 06.B5 Scene automation: support scene-level intensity automation.
- [ ] 06.B6 Param automation: support scene-level parameter automation.
- [ ] 06.B7 Artifact integration: include timeline metadata in render artifacts.

### Frontend Track

- [ ] 06.F1 Timeline types: add frontend types for scenes, ranges, and automation metadata.
- [ ] 06.F2 Timeline display readiness: make the UI able to consume timeline metadata later.

### Validation Track

- [ ] 06.V1 Multi-scene render test: prove one song can render with multiple scenes.
- [ ] 06.V2 Alignment test: prove scene boundaries align to beats or phrases by default.
- [ ] 06.V3 Override test: prove manual scene overrides persist over auto-generated defaults.

## Epic 07: Transition System

### Backend Track

- [ ] 07.B1 Transition model: define transition type, alignment target, duration, and params.
- [ ] 07.B2 Hard cut: implement hard cut transitions.
- [ ] 07.B3 Crossfade: implement crossfade transitions.
- [ ] 07.B4 Beat flash cut: implement beat flash cut transitions.
- [ ] 07.B5 Beat-aware alignment: allow transitions to snap to beat, bar, phrase, or section boundaries.
- [ ] 07.B6 Transition metadata: expose transition metadata in render artifacts.
- [ ] 07.B7 Transition debug info: expose preview or debug information in artifacts.

### Frontend Track

- [ ] 07.F1 Transition types: add frontend types for transition metadata.
- [ ] 07.F2 Transition preview readiness: make the UI able to consume transition metadata later.

### Validation Track

- [ ] 07.V1 Deterministic transition test: prove transition output is reproducible.
- [ ] 07.V2 Duration test: prove transition durations can be expressed and applied consistently.
- [ ] 07.V3 Alignment test: prove transitions honor beat, bar, phrase, or section alignment rules.

## Epic 08: Preview Console

### Backend Track

- [ ] 08.B3 Song load endpoint: add one backend action that sets the current song and returns the updated current song plus current canvas state.
- [ ] 08.B4 Missing canvas on load: make song-load succeed even when no show exists for that song.
- [ ] 08.B5 Render action contract: make `Render` create or replace the current canvas for the already loaded song.
- [ ] 08.B2 Metadata payload support: expose artifact metadata needed by the console without UI-only assumptions.
- [ ] 08.B1 Generation status payload: expose render job status, progress, and failure details through the API.

### Frontend Track

- [ ] 08.F1 Console network spec: update the frontend to target port `3400` and the backend API on port `3401`.
- [ ] 08.F4 Server-owned song flow: request song changes from the backend instead of loading song files directly in the frontend.
- [ ] 08.F5 Song-loaded UI update: update the frontend when the backend reports a new current song and current canvas.
- [ ] 08.F6 Empty canvas state UI: allow a song to be loaded and preview-ready even when no show exists yet.
- [ ] 08.F7 Main tab: add a `Main` tab in the left column with only `show name` input and a `Render` button.
- [ ] 08.F8 Shader tabs: add one left-column tab per shader or layer property group.
- [ ] 08.F10 Fixture overlay load: load fixture references from `data/fixtures/fixtures.json`.
- [ ] 08.F11 POI overlay load: load POI references from `data/fixtures/pois.json`.
- [ ] 08.F12 Canvas reference overlay: draw fixtures and POIs as a visual overlay on the canvas.
- [ ] 08.F13 Overlay marker styling: make fixture markers visually distinct from POI markers.
- [ ] 08.F2 Artifact metadata panel: show render metadata, schema version, preset id, seed, and compatibility state.
- [ ] 08.F3 Generation workflow UI: show render job status, progress, and failure details.
- [ ] 08.F9 Preset-driven controls: build shader or layer controls from schema-defined groups instead of hardcoded controls.
- [ ] 08.F14 Timeline view: add timeline display for scene and transition metadata.
- [ ] 08.F15 Frame inspector: add pixel inspection with coordinates and RGB values.
- [ ] 08.F16 Fullscreen preview: add fullscreen preview while preserving `100x50` pixel character.
- [ ] 08.F17 A/B compare: add compare mode between two renders.
- [ ] 08.F18 Approval workflow: add render approval status in the UI.

### Validation Track

- [ ] 08.V1 Port configuration check: prove the frontend and backend run on the documented ports `3400` and `3401`.
- [ ] 08.V2 Schema error state test: prove incompatible artifacts show a clear UI state.
- [ ] 08.V3 Song load flow test: prove the frontend asks the backend to load a song and updates when the backend confirms the new current song.
- [ ] 08.V4 Missing canvas flow test: prove a song with no canvas still loads and only creates a show on `Render`.
- [ ] 08.V5 Left-tab layout test: prove the left column shows one `Main` tab and one tab per shader or layer group.
- [ ] 08.V6 Overlay load test: prove fixtures and POIs load from their JSON files and render as overlay references.
- [ ] 08.V7 Overlay alignment test: prove fixture and POI markers stay aligned to canvas coordinates.
- [ ] 08.V8 Review workflow test: prove a user can load a song, render a show, inspect it, and approve it from the UI.

## Epic 09: Render Diagnostics

### Backend Track

- [ ] 09.B1 Diagnostics summary: compute brightness, average color, frame delta, blank-frame warnings, and render duration.
- [ ] 09.B2 Variety metrics: add beat-response and section-variation style signals that flag static or repetitive renders.
- [ ] 09.B3 Contact sheets: generate contact sheets for each render.
- [ ] 09.B4 Preview strip or GIF: generate a short preview strip or GIF for each render.

### Frontend Track

- [ ] 09.F1 Diagnostics types: add frontend types for diagnostics summaries and warnings.
- [ ] 09.F2 Diagnostics view: surface diagnostics summaries and warnings in the console UI.
- [ ] 09.F3 Diagnostics asset view: surface contact sheets and preview assets in the UI.

### Validation Track

- [ ] 09.V1 Blank render test: catch obviously blank renders.
- [ ] 09.V2 Static render test: catch accidentally static renders.
- [ ] 09.V3 Regression change test: catch accidental visual output changes.

## Epic 10: Fixture Mapping And Export

### Backend Track

- [ ] 10.B1 Canonical pixel order: document and encode the canonical origin and row-major pixel order.
- [ ] 10.B2a Fixture reference schema: treat `fixtures.json` as real fixture instances with fixture-type id and normalized canvas location.
- [ ] 10.B2b POI reference schema: treat `pois.json` as normalized points of interest with optional per-fixture pan and tilt calibration.
- [ ] 10.B2 Mapping config: define fixture or layout mapping inputs.
- [ ] 10.B3 Linear mapping: support linear pixel order.
- [ ] 10.B4 Serpentine mapping: support serpentine pixel order.
- [ ] 10.B5 Export manifest v1: export mapped frame metadata without changing the canonical render artifact.
- [ ] 10.B6 Gamma correction: add gamma correction to export.
- [ ] 10.B7 Brightness limiting: add brightness limiting to export.

### Frontend Track

- [ ] 10.F1 Export metadata types: add frontend types for export and mapping metadata.
- [ ] 10.F2 Export review readiness: make the UI able to inspect export metadata and mapping results later.
- [ ] 10.F3 Fixture and POI reference types: add frontend-readable types for fixture instances and POIs.

### Validation Track

- [ ] 10.V1 Orientation test pattern: add a test pattern that makes orientation obvious.
- [ ] 10.V2 Ordering test pattern: add a test pattern that makes pixel ordering obvious.
- [ ] 10.V3 Mapping validation: add validation checks for orientation, ordering, and layout mapping.
