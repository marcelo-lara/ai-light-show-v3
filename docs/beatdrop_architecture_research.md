# BeatDrop Architecture Research

Based on an analysis of the BeatDrop-Music-Visualizer codebase (which builds upon the original MilkDrop2 engine), here is a breakdown of how the application parses audio using a 3-band FFT and uses "random" alongside "apply parameters" to drive its audio-reactive visualizer.

## 1. The 3-Band FFT Audio Ingestion
At its core, BeatDrop continuously captures the system audio buffer and pushes it through a Fast Fourier Transform (FFT). The engine breaks this massive array of frequency data down into three primary variables which are tracked dynamically:
*   `bass`: Low-end frequencies (kicks, 808s, heavy basslines).
*   `mid`: Mid-range frequencies (vocals, synths, snares).
*   `treb`: High-end frequencies (hi-hats, cymbals, sharp transients).

Instead of just using raw volume output, BeatDrop calculates these variables as **relative averages** to the current song (`imm_rel` and `avg_rel` in the C++ backend). A value of `1.0` means the band is hitting at the exact average intensity for that specific song. When a heavy bass drop occurs, the `bass` variable spikes to `1.2`, `1.5`, or higher. This ensures the visualizer auto-scales to the song's volume and never "clips" or "goes dead" just because a track is too loud or too quiet.

## 2. The Role of "Random"
Randomness is essential in generative music visualization to prevent the visuals from becoming a predictable, repetitive loop. BeatDrop leverages randomness in two main ways:
1.  **Expression Evaluator Functions:** Preset creators can use math expressions containing `rand()` alongside the FFT parameters. For example, a preset script might say: `if(bass > 1.3, rand(100), old_value)`. This translates to: *"Whenever a heavy bass kick happens, pick a completely random direction/color to jump to. Otherwise, keep doing what you're doing."*
2.  **Engine-Level Randomization:** The BeatDrop codebase specifically implemented the **Mersenne Twister Pseudo-Random Number Generator**. This provides high-quality randomness for:
    *   Shuffling between different visualization presets.
    *   Transitioning textures and blend modes.
    *   Generating "noise" textures on the GPU shaders so organic, chaotic movements look more fluid rather than blocky or artificial.

## 3. How "Apply Parameters" Work
In the visualizer, everything you see on the screen (zoom, rotation, horizontal/vertical translation, shape colors, wave geometries) is a mathematical parameter (e.g., `zoom`, `rot`, `dx`, `dy`, `r`, `g`, `b`). 

To make the visualizer actually react to the music, BeatDrop uses an evaluator library called `projectm-eval` to process math equations in three stages, ultimately "applying" them to the render pipeline:
*   **Init Equations:** Run once when a preset loads to establish the baseline parameters.
*   **Per-Frame Equations:** Run roughly 60 times a second. These scripts take the live `bass`, `mid`, `treb`, and `rand()` values and calculate what the new global parameters should be for that exact frame.
*   **Per-Vertex Equations:** Run for every single vertex/pixel on the screen's rendering mesh grid. It applies spatial distortion based on the audio variables.

**The Final "Apply" Step (`ApplyShaderParams`):**
Once the C++ engine has calculated the new position, color, and distortion data for the frame, it executes the `ApplyShaderParams()` function. This function takes all the dynamic audio-reactive variables and directly binds them to the **DirectX Pixel Shaders** (PS 4.0/Shader Model 3) as constants. This means the GPU itself is using the `bass`, `mid`, and `treb` variables to calculate the final pixel colors and visual distortions at blazing fast speeds.

---

**Summary:** **FFT** creates auto-scaling math variables (`bass/mid/treb`). **Random** allows those variables to trigger chaotic, unpredictable behavior on heavy beats. The **Evaluator** processes user-written scripts combining these numbers, and **ApplyShaderParams** injects the resulting math directly into the GPU to render the frame.
