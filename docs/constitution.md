# AI Light Show V3: Constitution

## Architecture Principles
1. **Separation of Concerns:** The backend handles all heavy mathematical computation and audio analysis. The frontend is exclusively for playback and visualization via pre-computed data. They should not share logic.
2. **Pre-computation:** To guarantee smooth playback, visuals are analyzed and pre-computed per song, stored as a cache in `data/canvas/{song_name}.{show_id}.json`.
3. **Target Performance:** Canvas animations should target **50 FPS**.

## File Organization
- `backend/`: Python scripts, audio parsers, math matrix generation.
- `frontend/`: Vite, React, TypeScript, WaveSurfer.js.
- `data/songs/`: Source audio files (`.mp3`).
- `data/canvas/`: JSON array files containing pre-rendered integer frames.
- `docs/`: SDDs, architectural references, and medium-term memory.

## Design Aesthetic (Frontend)
- Dark mode only, high contrast, minimal ornamentation.
- Dense spacing, hard edges (0px border radius where possible).
- Vivid purple accent (`#9000dd`).
- See `ui-specs.md` for specific UI implementation details.

## Antigravity Rules
- ALWAYS save your artifacts to the `/docs` folder.
