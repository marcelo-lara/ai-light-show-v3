# Glossary

## Canvas

The final `100x50` RGB pixel grid. This is the canonical output resolution.

## Frame

One rendered canvas at a specific timestamp. The current renderer targets `50 FPS`.

## Analysis IR

The intermediate representation created from audio analysis. It should describe beats, energy, sections, phrases, and derived musical signals.

## Preset

A reusable visual recipe made from layers, parameters, modulation sources, palettes, and transition behavior.

## Layer

One visual contribution to a frame, such as a wave, ring, bar field, particle burst, mask, gradient, or texture.

## Modulator

A signal that drives visual parameters over time. Examples: bass energy, onset, beat phase, section energy, phrase progress, smoothed treble, or seeded random walk.

## Scene

A preset instance over a time range in the song timeline.

## Timeline

The arrangement of scenes, transitions, intensity automation, and cue points across a song.

## Look

The visible result of a preset or scene. A look should be nameable and recognizable.

## Transition

The visual bridge between two scenes. Transitions can crossfade, wipe, morph, hard cut, or beat-cut.

## Render Artifact

Any generated file, including analysis caches, frame JSON, preview images, diagnostics, and reports.

