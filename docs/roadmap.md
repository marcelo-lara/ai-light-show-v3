# Roadmap

This roadmap is intentionally iterative. Each phase should leave the app more usable than before, even if later phases deepen the system.

## Phase Summary

1. **Phase 1: Baseline And Contracts**
   Stabilize the current `100x50` render contract, cache format, parameter behavior, and preview expectations.

2. **Phase 2: Musical Analysis IR**
   Expand audio analysis from raw features into show-ready musical signals.

3. **Phase 3: Preset And Layer Engine**
   Replace one-off shader wiring with composable presets, layers, modulators, palettes, and deterministic state.

4. **Phase 4: Timeline And Direction**
   Arrange visuals across song sections with transitions, cue points, intensity curves, and reviewable show structure.

5. **Phase 5: Production Console**
   Upgrade the frontend into a generation, tuning, inspection, and approval console.

6. **Phase 6: Quality, Performance, And Packaging**
   Add validation, visual regression checks, render diagnostics, cache management, and deployment-ready workflows.

## Epic Index

- [Epic 01: Render Contract](./epics/01-render-contract.md)
- [Epic 02: Analysis IR](./epics/02-analysis-ir.md)
- [Epic 03: Preset Schema](./epics/03-preset-schema.md)
- [Epic 04: Layer Library](./epics/04-layer-library.md)
- [Epic 05: Modulation System](./epics/05-modulation-system.md)
- [Epic 06: Timeline Director](./epics/06-timeline-director.md)
- [Epic 07: Transition System](./epics/07-transition-system.md)
- [Epic 08: Preview Console](./epics/08-preview-console.md)
- [Epic 09: Render Diagnostics](./epics/09-render-diagnostics.md)
- [Epic 10: Fixture Mapping And Export](./epics/10-fixture-mapping-and-export.md)

## Recommended Iteration Order

1. Lock the render contract and metadata.
2. Make the current two effects configurable through a preset schema.
3. Add analysis IR fields that immediately improve those effects.
4. Add 3-5 new low-res-native layers.
5. Add timeline scenes and beat-synced transitions.
6. Add frontend preview tools for comparison and approval.
7. Add diagnostics and regression tests.
8. Add physical fixture/export mapping.

