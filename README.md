# AI Light Show V3: BeatDrop / MilkDrop Inspired Visualizer

Our goal is to build our own modern implementation inspired by the [BeatDrop Music Visualizer](https://github.com/OfficialIncubo/BeatDrop-Music-Visualizer) (a custom MilkDrop2 engine). Our main difference is that we do not react to audio in real-time. Instead, we analyze the entire audio track first to precisely map beats and frequencies, and then apply our visual logic based on what we analyzed. This carries the spirit of dynamic equations, custom shapes, and rich shaders into a pre-computed web-and-python stack.

## System Architecture

The project consists of a Dockerized environment with two main components:

1. **Python Backend (The Math & Rendering Engine):**
   - Responsible for audio processing (beat detection, frequency analysis) of songs from `data/songs/*.mp3` (example: `data/songs/ayuni.mp3`).
   - Executes complex math calculations (akin to MilkDrop's per-frame/per-pixel equations) to render a 100 by 50 LED-style canvas.
   - Pre-computes the visuals (shaders) and stores the cached final pixel colors in `data/canvas/{song_name}.{show_id}.json`.
   - The first two shaders to implement:
     1. **Wave:** An "under the sea" blue waves effect to mimic an underwater sea shore.
     2. **Pulse:** A circle that expands from random positions around the center of the canvas, triggered by the beat.

2. **Frontend Player (The UI & Playback Console):**
   - Loads, processes, and plays the audio while rendering the canvas on the right content lane.
   - The left content lane provides a control panel to configure the math parameters of the shaders (similar to tweaking visualizer presets).
   - The UI must follow the dark, technical, studio-like aesthetics described in `/ui-specs.md`.

## Features to Incorporate (Inspired by BeatDrop)
- Full-track audio analysis for precise, pre-computed beat and frequency mapping.
- Dynamic wave forms and expanding shapes driven by the initial analysis rather than real-time reaction.
- Configurable math parameters that can be adjusted via the frontend UI.
- Pre-rendered caching to ensure perfectly synchronized playback with zero runtime calculation cost.

## Development

Use `docker compose` to bring up the containers for development and debugging.