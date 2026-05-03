# AI Light Show V3: Phases and Stories

This document outlines the development phases, epics, and user stories for building the AI Light Show V3 project. It serves as a handoff and implementation guide to ensure all components are built methodically and align with the `README.md`, `constitution.md`, and `ui-specs.md`.

---

## Phase 1: Project Setup & Infrastructure

**Epic: Establish the Foundation**
The goal of this phase is to set up the containerized environment, establish the base frontend and backend projects, and confirm that both services can communicate and access shared data volumes.

*   **Story 1.1: Docker Environment Setup**
    *   Create a `docker-compose.yml` to orchestrate a Python backend container and a Node/Vite frontend container.
    *   Set up volume mappings so both containers can access `data/songs/` and `data/canvas/`.
*   **Story 1.2: Backend Skeleton**
    *   Initialize the Python application structure in `backend/`.
    *   Install baseline dependencies (e.g., `numpy`, `librosa`, `scipy`) for audio analysis and math operations.
    *   Set up a basic entry point (CLI or HTTP server) to trigger processing jobs.
*   **Story 1.3: Frontend Skeleton**
    *   Initialize a Vite + React + TypeScript project in `frontend/`.
    *   Configure global CSS applying the baseline aesthetics: dark mode (`#000000` background, `#121212` panels), `#9000dd` vivid purple accent, and 0px border-radius globally.

---

## Phase 2: Backend Engine & Pre-computation

**Epic: The Math & Rendering Engine**
This phase focuses on the Python backend analyzing `.mp3` files, calculating visual data frame-by-frame, and caching the output into JSON files for the frontend to consume.

*   **Story 2.1: Audio Analysis Core**
    *   Implement logic to load a selected `.mp3` track from `data/songs/`.
    *   Perform full-track analysis for beat detection, tempo extraction, and frequency domain mapping.
*   **Story 2.2: Matrix Generation & Caching System**
    *   Develop the base loop to pre-compute frames targeting a 100x50 resolution at 50 FPS.
    *   Implement the exporter to save the generated frame arrays to `data/canvas/{song_name}.{show_id}.json`.
*   **Story 2.3: "Wave" Shader Implementation**
    *   Implement the math logic for the "Wave" visualizer (underwater blue waves effect).
    *   Ensure the wave dynamics respond to the pre-analyzed audio frequencies.
*   **Story 2.4: "Pulse" Shader Implementation**
    *   Implement the math logic for the "Pulse" visualizer (circles expanding from random center positions, triggered precisely on beats).

---

## Phase 3: Frontend Layout & Audio Playback

**Epic: The Operator Console & Audio**
This phase builds the frontend UI layout based on the technical, dense, studio-like aesthetic requested in `ui-specs.md`, integrating audio playback via WaveSurfer.js.

*   **Story 3.1: Structural Layout (The 4 Zones)**
    *   Implement the vertical column layout matching the spec: Top Bar, Waveform Area, Transport Row, and the bottom Two-Column Area (Math Parameters left, Canvas right).
*   **Story 3.2: Top Bar & Status Indicators**
    *   Build inline selectors for choosing the "Song" and the "Show".
    *   Build the status strip on the right: Live Drift Gauge, Playback State Chip, and Server Connection Chip.
*   **Story 3.3: WaveSurfer.js Integration**
    *   Integrate WaveSurfer.js in the Waveform Area, using the dark gray and primary purple color scheme.
    *   Enable scrubbing, seeking, and custom scrollbar styling.
*   **Story 3.4: Transport Controls & Clock**
    *   Implement Load, Stop, and Play/Pause toggle buttons using icon-only treatments.
    *   Add a large, prominent digital clock (`mm:ss`) that updates with playback progress.

---

## Phase 4: Visualization & Parameter Tuning

**Epic: Canvas Rendering & Sync**
This phase brings the pre-computed visuals to the frontend, syncing the 50 FPS animation exactly to the audio playback, and providing UI to tweak shader parameters.

*   **Story 4.1: Canvas Renderer**
    *   Implement the HTML5 Canvas in the right column of the bottom zone.
    *   Fetch the `data/canvas/{song_name}.{show_id}.json` file and render the 100x50 integer arrays onto the canvas, scaling to fit the layout.
*   **Story 4.2: Playback Synchronization Engine**
    *   Build a rendering loop (e.g., using `requestAnimationFrame`) that maps the current audio playback time to the corresponding JSON frame.
    *   Ensure 50 FPS target and implement live drift detection logic to display in the Top Bar.
*   **Story 4.3: Math Parameters Panel**
    *   Build dense, technical form controls in the left column for tweaking variables (Beat Detection sensitivity, Wave height/speed, Shape parameters).
    *   Connect this panel so that parameter changes can be sent to the backend to trigger a re-render/re-computation of the canvas JSON.

---

## Phase 5: Refinement, Polish, and Handoff

**Epic: System Tuning**
Final pass to ensure visual excellence, performance, and stability.

*   **Story 5.1: Aesthetic Verification**
    *   Audit the frontend against `ui-specs.md` ensuring no rounded corners, correct tight padding (`0.5rem` - `0.75rem`), and appropriate mono typography.
*   **Story 5.2: Performance Optimization**
    *   Ensure the JSON payload loading is efficient and the canvas drawing loop does not drop frames.
*   **Story 5.3: End-to-End Testing**
    *   Verify the full workflow: Select a song -> Tweak parameters -> Compute -> Load JSON -> Play synchronized audio and video.

---

## Model Assignment Strategy

Given the different strengths of the Gemini models, here is the recommended approach for assigning these stories:

### 🤖 Gemini Pro (Frontend Focus)
Gemini 1.5 Pro excels at complex reasoning, visual-spatial understanding for UI layouts, and adhering to strict design requirements (like those in `ui-specs.md`). Assign Pro to:
*   **Phase 1:** Story 1.3 (Frontend Skeleton)
*   **Phase 3:** Stories 3.1, 3.2, 3.3, 3.4 (All structural layout, UI components, and WaveSurfer.js integration)
*   **Phase 4:** Stories 4.1, 4.2, 4.3 (Canvas rendering, synchronization logic, and Math Parameters UI)
*   **Phase 5:** Story 5.1 (Aesthetic verification and styling polish)

### ⚡ Gemini Flash (Backend Focus)
Gemini 1.5 Flash is exceptionally fast and efficient, making it ideal for data processing pipelines, mathematical algorithms, and file I/O operations. Assign Flash to:
*   **Phase 1:** Stories 1.1, 1.2 (Docker infrastructure and Python skeleton)
*   **Phase 2:** Stories 2.1, 2.2, 2.3, 2.4 (Audio analysis, matrix caching, and Python math/shader logic)
*   **Phase 5:** Story 5.2 (Performance optimization of the Python backend)
