# Epic 10: Fixture Mapping And Export

## Story

As a show operator, I want rendered frames to map cleanly to the final playback or lighting system.

## Why This Matters

The canonical canvas is `100x50`, but real hardware or downstream systems may need different ordering, segmentation, gamma, brightness limits, or transport formats.

## Scope

- Define canonical coordinate origin and pixel order.
- Add fixture/layout mapping config.
- Load fixture instances from `fixtures.json` and points of interest from `pois.json`.
- Treat fixture and POI locations as normalized canvas reference coordinates.
- Support serpentine and linear pixel order.
- Add brightness limiting and gamma correction.
- Add export formats required by playback targets.
- Add export validation.
- Add test patterns for fixture setup.

## Acceptance Criteria

- A rendered show can be transformed into a target fixture layout without modifying the render artifact.
- Export includes metadata needed by the playback system.
- Test patterns make orientation and pixel ordering obvious.

## Dependencies

- Render contract.
- Preview console.
- Render diagnostics.

## First Iteration

Document canonical pixel order, load fixture and POI reference data, and add a simple export manifest for row-major RGB frames.

