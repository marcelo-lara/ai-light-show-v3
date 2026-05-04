# Backend Shader Architecture Plan

*This document was generated from an approved implementation plan for the 5-band FFT migration and shader compositor refactor.*

## Overview
This plan covers updating the backend audio analyzer to use a 5-band FFT, caching the results in `.npz` (Numpy Compressed) Intermediate Representation (IR) files, and establishing a robust, production-grade shader architecture using the compositor and Q-Variable concepts.

## Changes

### 1. Audio Analyzer (`backend/engine/analyzer.py`)
*   **5-Band FFT Extraction:** Update the STFT analysis to extract 5 bands instead of 3:
    *   `sub_bass` (20 - 60 Hz)
    *   `bass` (60 - 250 Hz)
    *   `low_mid` (250 - 2000 Hz)
    *   `high_mid` (2000 - 4000 Hz)
    *   `treble` (4000+ Hz)
*   **IR Caching Logic (.npz):**
    *   Modify `analyze()` to accept/generate an IR file path (e.g., `song_name.ir.npz`).
    *   Before running `librosa`, check if the IR file exists. If so, load and return it.
    *   If it does not exist, run the full librosa analysis and save the output to the `.npz` file to avoid re-analysis in the future.
*   **Update `get_features_at_time`:** Ensure it interpolates all 5 new bands correctly.

### 2. Shader Architecture (`backend/engine/shaders/`)
*   **`base_shader.py`**: Define a `BaseShader` abstract class. Requires a `render(self, coords, audio_features, q_buffer, **kwargs)` method.
*   **`radial_pulse.py`**: Implements `RadialPulseShader`. Uses `sub_bass` or `bass` transients to trigger intense radial bursts from a center point.
*   **`linear_wave.py`**: Implements `LinearWaveShader`. Uses `low_mid` and `high_mid` to drive a smooth, continuous wave effect across the fixture coordinates.

### 3. Renderer Refactor (`backend/engine/renderer.py`)
*   **Implement the Compositor:** Refactor the renderer to evaluate multiple shaders and blend their outputs.
*   **Layer Blending:** Implement `ADD` and `MAX` blending functions.
*   **Q-Buffer:** Introduce a `q_buffer` dictionary that persists across frames and is passed to all shaders.

### 4. Verification
*   Test with `data/songs/Cinderella - Ella Lee.mp3`.
*   Ensure IR `.npz` files are created and loaded successfully.
