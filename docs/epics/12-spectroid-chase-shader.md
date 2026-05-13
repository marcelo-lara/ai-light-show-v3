# Epic 12: Spectroid Chase Shader

## Story

As a show author, I want a shader that reacts to the central spectroid, notes, or chords by chasing outward from parcan positions, so the canvas can start with anchored color bursts and expand into line motion that moving heads can follow.

## Why This Matters

The current looks do not yet connect harmonic or tonal motion to fixture-aware composition. A spectroid chase shader creates a bridge between note or chord-reactive musical content, static parcan anchors, and outward line motion that can later inform moving-head movement.

## Scope

- Define a `spectroid_chase` shader or layer.
- React to a central spectroid or note or chord-driven trigger signal.
- Use parcan fixture positions as chase origin anchors on the canvas.
- Generate outward line motion from those anchors.
- Shape the output so moving heads can visually follow the resulting lines later.
- Expose controls for trigger sensitivity, line length, spread, fade, and chase speed.
- Keep output deterministic for the same song, params, fixture layout, and seed.
- Make the shader compatible with the preset system and fixture overlay.

## Acceptance Criteria

- The shader reacts visibly to a central spectroid or note or chord-driven signal.
- Chase lines start from parcan anchor positions on the canvas.
- The resulting lines extend outward in a way that supports later moving-head follow behavior.
- The same inputs produce identical output.
- The shader can be loaded through the layer or preset system without special renderer wiring.

## Dependencies

- Analysis IR.
- Preset schema.
- Layer library.
- Modulation system.
- Fixture reference data.

## First Iteration

Implement a deterministic chase layer that starts from parcan anchor positions and emits outward lines in response to a central spectroid or note or chord-reactive trigger.