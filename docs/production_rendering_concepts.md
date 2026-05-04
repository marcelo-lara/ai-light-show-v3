# Production-Grade Rendering Concepts (xLights & Resolume)

This document outlines the core architecture principles required to build a production-grade, high-end light show visualizer, drawing inspiration from professional software like xLights, Resolume, and BeatDrop.

## A. The "q-Variable" System (State Buffer)
In engines like BeatDrop, `q1` through `q32` are global variables that carry state between frames.
*   **Implementation:** Create a `q_buffer` that stores persistent values such as `q1 = bass_hit_intensity` or `q2 = cumulative_rotation`. 
*   **Purpose:** Pass this buffer into every shader so they stay "musically aware" across multiple frames, enabling effects that build up or decay over time rather than resetting instantly.

## B. The Compositor (Layer Blending)
Professional software like xLights does not simply draw to a single canvas; it evaluates multiple shaders and merges them using professional layer blending modes. A single-track data structure limits creativity. The DMX canvas must be the result of a Compositor.

### Standard Layer Hierarchy:
1.  **Background Layer:** Slow-moving color gradients (the "Vibe" / "Sea Waves").
2.  **Pulse Layer:** Rapid intensity changes mapped to transients (drum hits, synth stabs).
3.  **Override Layer:** High-priority "Hard Cuts" or Strobes.

### Blending Logic (The xLights Standard):
*   **Additive (`ADD()`):** `final = shader1 + shader2` (Excellent for flashes and intense build-ups).
*   **Max / Lightest (`MAX()`):** `final = np.maximum(shader1, shader2)` (The BeatDrop default, ensures layers don't blow out to pure white instantly while allowing pulses to shine through).
*   **Masking:** Use a slow-moving wave shader as a mask (multiplier) for a fast-moving pulse shader.

This compositor approach allows "Sea Waves" to continue running underneath a strobe hit, rather than being interrupted by it.

## C. Coordinate Transformation (Warping)
Advanced visualizers don't just draw pixels; they warp the underlying coordinate grid.
*   **Implementation:** Before sampling your lighting fixtures, apply a "warp" to their coordinates based on audio energy (e.g., the Mid-range FFT energy).
    *   *Example:* `warped_coords = coords + np.sin(coords * mid_energy)`
*   **Purpose:** This makes the light patterns feel organic, fluid, and "liquified" rather than rigidly geometric.

## Why this approach is "Production-Grade"
1.  **Speed:** By utilizing matrix multiplication (e.g., `coords @ direction_vec` in NumPy), the engine can process 1,000+ lighting fixtures in microseconds.
2.  **Resolution Independent:** You can seamlessly scale from a 10-light home rig to a 500-light festival stage. As long as the `coords` array is updated to reflect the physical fixtures, the shaders will render perfectly without requiring a single line of code change.
3.  **Fluidity:** Utilizing mathematical functions like `sin` and `exp` ensures that the DMX output features perfectly smooth fades, eliminating the choppy "stepping" often seen in manual lighting chasers.
