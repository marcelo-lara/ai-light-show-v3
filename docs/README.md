# AI Light Show V3 Documentation

This folder is the working plan for turning the current prototype into a production-grade `100x50` pixel light-show visualizer.

The goal is not to clone BeatDrop as a full-screen MilkDrop renderer. BeatDrop is the reference for expressive visual systems: presets, audio response, shapes, waves, transitions, shader-like math, caching, and performance controls. Our product is different: it renders intentional low-resolution pixel output for a fixed light canvas.

## North Star

Create a precomputed visual engine that makes `100x50` pixels feel authored, musical, varied, and stage-ready.

That means:

- Every pixel has purpose.
- The low resolution is a creative constraint, not a limitation to hide.
- Shows are synchronized to song structure, not only raw beat hits.
- Looks are generated from reusable presets and layers, not one-off Python classes.
- The frontend is a production console for previewing, tuning, generating, and reviewing shows.
- Outputs are deterministic, cacheable, testable, and easy to compare.

## Documentation Map

- [Product Principles](./product-principles.md): what production-grade means for this project.
- [Roadmap](./roadmap.md): phases, epics, and iteration order.
- [Glossary](./glossary.md): shared terms for the engine and UI.
- [Phases](./phases): phase-level goals and exit criteria.
- [Epics](./epics): one file per epic story.

## Current Baseline

The current codebase already has useful foundations:

- Full-track audio analysis with beat times, onset, and five normalized frequency bands.
- A precomputed JSON frame cache.
- A browser player that synchronizes audio playback with cached frames.
- Two prototype shader classes: wave and radial pulse.
- A small tuning UI for generation parameters.

The main gap is architecture depth. Production quality should come from a richer engine model, better musical analysis, a preset/timeline system, stronger low-res rendering techniques, and a more complete preview workflow.

