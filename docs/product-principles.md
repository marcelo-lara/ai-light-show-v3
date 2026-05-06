# Product Principles

## 100x50 Is The Product

The fixed canvas is intentional. We should not spend effort trying to make it look like HD video. The right question is: does the light map read clearly, rhythmically, and beautifully on a `100x50` pixel surface?

Design for:

- Bold silhouettes.
- Clean motion.
- Limited but expressive palettes.
- High contrast where the room needs impact.
- Smooth temporal behavior, even when spatial resolution is low.
- Section-aware visual changes.

Avoid:

- Tiny details that collapse into noise.
- Soft photographic effects that require high resolution.
- Randomness that looks accidental.
- Single-look shows that do not evolve over a track.

## Production Grade Definition

A production-grade show is:

- Musical: it follows beats, phrases, drops, breakdowns, energy changes, and tension.
- Legible: it reads from a distance and survives scaling to real lights.
- Varied: it has multiple visual scenes with purposeful transitions.
- Deterministic: the same inputs produce the same output unless randomness is explicitly seeded.
- Tunable: parameters have visible, predictable results.
- Reviewable: generated frames can be inspected, compared, regenerated, and approved.
- Performant: generation time and playback memory are bounded and observable.

## BeatDrop Inspiration, Not Parity

BeatDrop gives us a vocabulary:

- Presets.
- Custom waves.
- Custom shapes.
- Per-frame state.
- Per-pixel equations.
- Audio-reactive parameters.
- Transitions.
- Preset randomization.
- Shader caching.

We should adapt those ideas to a Python/Web precompute pipeline instead of copying the Windows/DirectX/MilkDrop architecture directly.

