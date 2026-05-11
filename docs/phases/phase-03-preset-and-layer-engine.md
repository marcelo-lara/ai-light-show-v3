# Phase 3: Preset And Layer Engine

## Goal

Move from hardcoded shader orchestration to a reusable low-res visual engine. Presets should compose layers, palettes, blend modes, masks, and modulators.

## Included Epics

- [Epic 03: Preset Schema](../epics/03-preset-schema.md)
- [Epic 04: Layer Library](../epics/04-layer-library.md)
- [Epic 05: Modulation System](../epics/05-modulation-system.md)
- [Epic 11: Raindrops Shader](../epics/11-raindrops-shader.md)
- [Epic 12: Spectroid Chase Shader](../epics/12-spectroid-chase-shader.md)

## Deliverables

- Preset files or structured preset definitions.
- Layer registry.
- Palette system.
- Blend modes.
- POI-aware shader behaviors.
- Fixture-aware chase behaviors.
- Stateful per-preset render context.
- Seeded randomness.

## Exit Criteria

- The current wave and pulse looks are represented as presets.
- A POI-driven raindrop look can be rendered without hardcoding a song-specific path.
- A note or chord-reactive chase look can start from parcan anchors and expand outward as moving-head-following lines.
- Adding a new look does not require changing renderer control flow.
- Parameters can be introspected by the frontend.

