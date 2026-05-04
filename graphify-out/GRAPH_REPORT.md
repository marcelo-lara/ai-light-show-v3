# Graph Report - ai-light-show-v3  (2026-05-03)

## Corpus Check
- 15 files · ~9,520 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 82 nodes · 88 edges · 14 communities detected
- Extraction: 75% EXTRACTED · 24% INFERRED · 1% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]

## God Nodes (most connected - your core abstractions)
1. `FrameRenderer` - 9 edges
2. `AudioAnalyzer` - 9 edges
3. `BaseShader` - 9 edges
4. `LinearWaveShader` - 7 edges
5. `RadialPulseShader` - 7 edges
6. `Light Show Player Frontend` - 7 edges
7. `GenerateRequest` - 4 edges
8. `Compositor` - 4 edges
9. `handleLoad()` - 3 edges
10. `run_generation()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `ai-light-show-v3` --references--> `Light Show Player Frontend`  [AMBIGUOUS]
  README.md → ui-specs.md
- `GenerateRequest` --uses--> `AudioAnalyzer`  [INFERRED]
  backend/api/routes.py → backend/engine/analyzer.py
- `GenerateRequest` --uses--> `FrameRenderer`  [INFERRED]
  backend/api/routes.py → backend/engine/renderer.py
- `run_generation()` --calls--> `FrameRenderer`  [INFERRED]
  backend/api/routes.py → backend/engine/renderer.py
- `run_generation()` --calls--> `AudioAnalyzer`  [INFERRED]
  backend/api/routes.py → backend/engine/analyzer.py

## Hyperedges (group relationships)
- **Application Layout Zones** — ui_specs_top_bar, ui_specs_waveform_area, ui_specs_transport_controls_row, ui_specs_three_column_diagnostics_area [EXTRACTED 1.00]
- **Diagnostics Area Panels** — ui_specs_dmx_monitor_panel, ui_specs_event_log_panel, ui_specs_diagnostics_panel [EXTRACTED 1.00]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.16
Nodes (10): ABC, BaseShader, BaseShader, Abstract base class for all BeatDrop-style visualizer shaders., LinearWaveShader, Generates a smooth linear wave that undulates based on mid-range frequencies., Generates a smooth linear wave that undulates based on mid-range frequencies., RadialPulseShader (+2 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (6): AudioAnalyzer, Helper to interpolate features for a specific timestamp., Performs full track analysis or loads from cache.         Returns tempo, beat fr, blend_max(), Compositor, FrameRenderer

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (11): ai-light-show-v3, Dark Technical Playback Console, Light Show Player Frontend, Playback State Model, React, Top Bar, Transport Controls Row, TypeScript (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.24
Nodes (3): fetchFrames(), handleLoad(), initWavesurfer()

### Community 4 - "Community 4"
Cohesion: 0.25
Nodes (3): GenerateRequest, run_generation(), BaseModel

### Community 5 - "Community 5"
Cohesion: 0.67
Nodes (4): Diagnostics Panel, DMX Monitor Panel, Event Log Panel, Three-Column Diagnostics Area

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (1): Renders the shader effect onto the provided coordinates.                  Args:

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): Helper to interpolate features for a specific timestamp (needed for 50 FPS rende

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): Underwater blue waves effect (Story 2.3) - Optimized with Numpy.

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Expanding circles from random centers, triggered on beats (Story 2.4) - Optimize

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Performs full track analysis.         Returns tempo, beat frames, and onset enve

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Helper to interpolate features for a specific timestamp (needed for 50 FPS rende

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Underwater blue waves effect (Story 2.3) - Optimized with Numpy.

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Expanding circles from random centers, triggered on beats (Story 2.4) - Optimize

## Ambiguous Edges - Review These
- `ai-light-show-v3` → `Light Show Player Frontend`  [AMBIGUOUS]
  ui-specs.md · relation: references

## Knowledge Gaps
- **21 isolated node(s):** `Performs full track analysis or loads from cache.         Returns tempo, beat fr`, `Helper to interpolate features for a specific timestamp.`, `Abstract base class for all BeatDrop-style visualizer shaders.`, `Renders the shader effect onto the provided coordinates.                  Args:`, `Generates a smooth linear wave that undulates based on mid-range frequencies.` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 12`** (1 nodes): `Renders the shader effect onto the provided coordinates.                  Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `Helper to interpolate features for a specific timestamp (needed for 50 FPS rende`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `Underwater blue waves effect (Story 2.3) - Optimized with Numpy.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `Expanding circles from random centers, triggered on beats (Story 2.4) - Optimize`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Performs full track analysis.         Returns tempo, beat frames, and onset enve`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `Helper to interpolate features for a specific timestamp (needed for 50 FPS rende`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Underwater blue waves effect (Story 2.3) - Optimized with Numpy.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Expanding circles from random centers, triggered on beats (Story 2.4) - Optimize`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `ai-light-show-v3` and `Light Show Player Frontend`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `FrameRenderer` connect `Community 1` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `AudioAnalyzer` connect `Community 1` to `Community 4`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `FrameRenderer` (e.g. with `GenerateRequest` and `AudioAnalyzer`) actually correct?**
  _`FrameRenderer` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AudioAnalyzer` (e.g. with `GenerateRequest` and `Compositor`) actually correct?**
  _`AudioAnalyzer` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `BaseShader` (e.g. with `LinearWaveShader` and `Generates a smooth linear wave that undulates based on mid-range frequencies.`) actually correct?**
  _`BaseShader` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `LinearWaveShader` (e.g. with `Compositor` and `FrameRenderer`) actually correct?**
  _`LinearWaveShader` has 4 INFERRED edges - model-reasoned connections that need verification._