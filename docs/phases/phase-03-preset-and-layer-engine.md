# Phase 3: Preset And Layer Engine

## Goal

Move from hardcoded shader orchestration to a reusable low-res visual engine. Presets should compose layers, palettes, blend modes, masks, and modulators.

## Included Epics

- [Epic 03: Preset Schema](../epics/03-preset-schema.md)
- [Epic 04: Layer Library](../epics/04-layer-library.md)
- [Epic 05: Modulation System](../epics/05-modulation-system.md)

## Deliverables

- Preset files or structured preset definitions.
- Layer registry.
- Palette system.
- Blend modes.
- Stateful per-preset render context.
- Seeded randomness.

## Exit Criteria

- The current wave and pulse looks are represented as presets.
- Adding a new look does not require changing renderer control flow.
- Parameters can be introspected by the frontend.

