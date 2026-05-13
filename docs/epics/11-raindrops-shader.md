# Epic 11: Raindrops Shader

## Story

As a show author, I want a `raindrops` shader that emits radial pulses from configured POIs, passing through or colliding at other POIs, so the canvas can feel like rainfall rippling across meaningful points on the stage map.

## Why This Matters

The current prototype has wave and pulse looks, but it does not yet use the POI map as a visual composition surface. A raindrops shader turns POIs into intentional anchors for motion, impact, and rhythmic flow.

## Scope

- Define a `raindrops` shader or layer.
- Use `pois.json` as selectable pulse origin points.
- Allow pulses to target, pass through, or collide at other POIs.
- Support multiple concurrent pulses.
- Expose controls for pulse rate, size growth, fade, travel behavior, and collision intensity.
- Keep output deterministic for the same song, params, POIs, and seed.
- Make the shader compatible with the preset system and POI reference overlay.

## Acceptance Criteria

- A raindrops look can emit visible radial pulses from one or more POIs.
- Pulses can either pass through or collide at configured POIs.
- The same inputs produce identical output.
- The shader can be loaded through the layer or preset system without special renderer wiring.

## Dependencies

- Preset schema.
- Layer library.
- Modulation system.
- Fixture and POI reference data.

## First Iteration

Implement a POI-driven radial pulse layer that starts from selected POIs and supports a deterministic pass-through or collision mode between POIs.