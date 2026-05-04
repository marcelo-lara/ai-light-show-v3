# Shader Compositor and 5-Band FFT Migration Walkthrough

*This document was generated from an AI Assistant Walkthrough Artifact.*

This document outlines the completed work for implementing the BeatDrop/xLights style rendering architecture.

## What Was Accomplished

### 1. 5-Band FFT Extraction & Caching (.npz)
- Modified `backend/engine/analyzer.py` to extract five precise frequency bands instead of three:
  - `sub_bass` (20-60 Hz)
  - `bass` (60-250 Hz)
  - `low_mid` (250-2000 Hz)
  - `high_mid` (2000-4000 Hz)
  - `treble` (4000+ Hz)
- Added an **Intermediate Representation (IR)** caching system that saves the analyzed arrays to `.npz` files (e.g., `song.mp3.ir.npz`). This avoids running `librosa.load` on subsequent executions, decreasing render setup time from ~10-30 seconds to near-instantaneous.

### 2. Shader Architecture & Q-Buffer
- Created the `backend/engine/shaders` module.
- Built a `BaseShader` abstract class defining the `render(coords, audio_features, q_buffer)` interface.
- Implemented **`RadialPulseShader`**: Detects kicks (`sub_bass` and `bass`) to trigger expanding radial ripples. It uses the `q_buffer` to ensure smooth decay of the pulse radius over multiple frames.
- Implemented **`LinearWaveShader`**: Uses `low_mid` and `high_mid` energy to warp the coordinate grid, creating an organic, fluid undulation that serves as an ambient background layer.

### 3. The Compositor Engine
- Refactored `backend/engine/renderer.py` to utilize a `Compositor`.
- It now renders the `LinearWave` (background) and `RadialPulse` (foreground) separately.
- It blends them perfectly using `np.maximum()` (BeatDrop's style), ensuring intense flashes pop out over the ambient waves without causing screen washout.

## Validation Results
- Tested the pipeline against `data/songs/Cinderella - Ella Lee.mp3`.
- The first run successfully produced `data/songs/Cinderella - Ella Lee.mp3.ir.npz`.
- The second run recognized the `.npz` cache and skipped `librosa` analysis immediately.
- The exported JSON frame data successfully rendered `16972` individual DMX matrices.

> [!NOTE]
> **Regarding Essentia vs. Librosa:** Essentia is highly optimized (C++) and fantastic for real-time applications or massive batch processing. Given that we are now utilizing `.npz` caching, our python-based `librosa` implementation only hits the CPU once per track, and is completely bypassed for all subsequent renders. The caching drastically closes the performance gap. However, if you need more advanced rhythmic descriptors (e.g., danceability, exact chord extraction) in the future, transitioning to `essentia.standard` will fit cleanly into the new `analyzer.py` abstraction.

## Next Steps
The backend JSON output is now highly sophisticated. You can proceed with Phase 3 (Frontend Layout) to consume and visualize these compositor frames over a WebGL Canvas!
