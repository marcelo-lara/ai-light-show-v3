# Graph Report - ai-light-show-v3  (2026-05-12)

## Corpus Check
- 74 files · ~32,988 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 826 nodes · 1011 edges · 95 communities (71 shown, 24 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 172 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `593bbfe3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]

## God Nodes (most connected - your core abstractions)
1. `PresetSchema` - 26 edges
2. `make_renderer()` - 21 edges
3. `FrameRenderer` - 21 edges
4. `UI Specification: AI Light Show V3 Frontend` - 16 edges
5. `LayerConfig` - 15 edges
6. `WaveShader` - 15 edges
7. `RadialPulseShader` - 15 edges
8. `Development Handoff Stories` - 15 edges
9. `GenerateRequest` - 14 edges
10. `BaseLayer` - 14 edges

## Surprising Connections (you probably didn't know these)
- `North Star` --semantically_similar_to--> `Precomputed Visual Engine`  [INFERRED] [semantically similar]
  docs/README.md → README.md
- `Backend Service` --semantically_similar_to--> `Python Backend`  [INFERRED] [semantically similar]
  docker-compose.yml → README.md
- `Frontend Service` --semantically_similar_to--> `Frontend Player`  [INFERRED] [semantically similar]
  docker-compose.yml → README.md
- `Raindrops Shader` --semantically_similar_to--> `Sash - Raindrops Transcript`  [INFERRED] [semantically similar]
  docs/epics/11-raindrops-shader.md → graphify-out/transcripts/Sash - Raindrops.txt
- `Production Console UI Spec` --conceptually_related_to--> `Epic 08: Preview Console`  [INFERRED]
  ui-specs.md → docs/epics/08-preview-console.md

## Hyperedges (group relationships)
- **System Architecture Form** — readme_precomputed_visual_engine, readme_python_backend, readme_frontend_player [EXTRACTED 1.00]
- **Phase 4 Timeline Bundle** — phase_04_timeline_and_direction, epic_06_timeline_director, epic_07_transition_system [EXTRACTED 1.00]
- **Phase 5 Console Bundle** — phase_05_production_console, epic_08_preview_console, epic_09_render_diagnostics [EXTRACTED 1.00]
- **POI-Driven Raindrops Form** — epic11_raindrops_shader_doc, epic11_raindrops_shader_concept, epic11_poi_driven_pulses [EXTRACTED 1.00]
- **Fixture Export Form** — epic10_fixture_mapping_export_doc, epic10_fixture_mapping_concept, epic10_export_manifest_concept [EXTRACTED 1.00]
- **Frontend Template Form** — frontend_index_html, frontend_readme_doc, frontend_react_typescript_vite [INFERRED 0.78]

## Communities (95 total, 24 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (42): Backend validation tests for pending stories. Tests for Epics 02, 03, 04, 05, 11, Epic 04.V2 & 04.V3 - Layer determinism and visual coverage, Prove seeded layer execution produces identical output, Epic 05.V2 & 05.V3 - Modulator determinism and mapping order, Prove modulator outputs stay stable for same analysis, seed, time, Prove mapping operations apply in declared order, Epic 02.F1 - Analysis type updates for beat phase, bar phase, energy, structure, Epic 11.V1-V4 - Raindrops POI and collision tests (+34 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (29): test_epic_01_validation(), test_v1_v2_parity(), AudioAnalyzer, Helper to interpolate features for a specific timestamp., Performs full track analysis using Essentia or loads from cache.         Returns, AssetGenerator, DiagnosticsSummary, FrameDiagnosticsComputer (+21 more)

### Community 2 - "Community 2"
Cohesion: 0.1
Nodes (22): ABC, BaseShader, BackgroundSweepLayer, BaseLayer, FrameContext, hex_to_rgb(), LegacyRadialPulseLayer, LegacyWaveLayer (+14 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (38): 09.B1: Diagnostics Summary Computation, 09.B2: Variety Metrics, 09.B3: Contact Sheet Generation, 09.B4: Preview Strip Generation, 10.B1: Canonical Pixel Order, 10.B2: Mapping Config (Complete Schema), 10.B2a: Fixture Reference Schema, 10.B2b: POI Reference Schema (+30 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (25): Prove all documented layer types can be loaded by id, AnalysisFeatures, fetchFrames(), FrameData, handleLoad(), initWavesurfer(), ModulatorConfig, PresetParameter (+17 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (34): Acceptance Criteria, Application Layout, Canvas Render / Visualizer Panel (Right), Color Palette, Data Model Expectations, Desktop, Implementation Guidance for an LLM, Interaction Model (+26 more)

### Community 6 - "Community 6"
Cohesion: 0.14
Nodes (25): Epic 01: Render Contract, Epic 02: Analysis IR, Epic 03: Preset Schema, Epic 04: Layer Library, Epic 05: Modulation System, Epic 06: Timeline Director, Epic 07: Transition System, Epic 08: Preview Console (+17 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (18): MappingOp, ModulatorConfig, ModulatorInspection, ModulatorTraceEntry, ModulatorValue, PresetParameter, PresetSummary, SceneSchema (+10 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (18): GenerateRequest, ExportManifest, FixtureInstance, MappingConfig, PixelOrdering, PixelOrigin, PointOfInterest, Fixture mapping and DMX export for lighting control. Epic 10.B1, 10.B2, 10.B3, 1 (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (17): Backend Enhancements ✅, Code Quality Notes, Dependencies & Prerequisites, Deployment Checklist, Files Modified/Created, High Priority (Blocking user workflows), Implementation Summary - May 12, 2026, Low Priority (Polish & optimization) (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (15): apply_gamma_and_brightness(), colors_to_sequence(), generate_manifest(), load_fixture_data(), pixel_order(), Return list of (x,y) pixel coordinates in canonical row-major order.     If serp, Map a flat or 2D color list into output sequence using pixel_order.     Accepts, Return list of (x,y) pixel coordinates in canonical row-major order.     If serp (+7 more)

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (9): find_canvas_for_song(), generate_show(), list_fixtures(), list_points_of_interest(), list_presets(), load_song(), List all available fixtures (Epic 10.B2a)., List all points of interest (Epic 10.B2b). (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (7): CanvasPixelMapper, FixtureMapper, Maps canvas coordinates to flat pixel indices (Epic 10.B1, 10.B3-B4)., Convert normalized canvas coordinates (0..1, 0..1) to flat pixel index., Reverse mapping: flat index to normalized coordinates., Maps fixtures to canvas locations (Epic 10.B2)., Get pixel range for a fixture on canvas.

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (12): Analysis IR, Canvas, Frame, Glossary, Layer, Look, Modulator, Preset (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.18
Nodes (12): Export Manifest, Fixture Mapping, Epic 10: Fixture Mapping And Export, Fixture and POI Reference Data, Deterministic Output, POI-Driven Pulses, Raindrops Shader, Epic 11: Raindrops Shader (+4 more)

### Community 15 - "Community 15"
Cohesion: 0.18
Nodes (10): CanvasPixelMapping, ExportManifest, FixtureInstance, MappingConfig, MappingValidation, ORDERING_TEST_PATTERN, ORIENTATION_TEST_PATTERN, PixelOrderingType (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.2
Nodes (10): Backend Service, Frontend Service, AI Light Show V3 Documentation, Current Baseline, Documentation Map, Epic Checklist, North Star, Frontend Player (+2 more)

### Community 17 - "Community 17"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Dependencies, Epic 08: Preview Console, First Iteration, Next Steps, Scope, Story, Why This Matters

### Community 18 - "Community 18"
Cohesion: 0.22
Nodes (8): Acceptance Criteria, Dependencies, Epic 01: Render Contract, First Iteration, Next Steps, Scope, Story, Why This Matters

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (7): AnalysisDiagnostics, AnalysisFeatures, BarTimingSignal, BeatTimingSignal, GlobalEnergy, MusicalStructure, SmoothedEnvelope

### Community 20 - "Community 20"
Cohesion: 0.32
Nodes (4): BaseModulator, EnvelopeFollowerModulator, get_modulator(), LfoModulator

### Community 21 - "Community 21"
Cohesion: 0.32
Nodes (5): DMXExporter, Exports canvas render data to DMX format (Epic 10.B5-B7)., Apply gamma correction to normalize brightness (Epic 10.B6).                  Ar, Apply brightness limiting (Epic 10.B7).                  Args:             rgb:, Convert canvas frame to DMX data.                  Args:             canvas_pixe

### Community 22 - "Community 22"
Cohesion: 0.25
Nodes (7): Backend Track, Development Handoff Stories, Epic 01: Render Contract, Frontend Track, Handoff Spec, Implementation Order, Validation Track

### Community 23 - "Community 23"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 03: Preset Schema, First Iteration, Scope, Story, Why This Matters

### Community 24 - "Community 24"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 12: Spectroid Chase Shader, First Iteration, Scope, Story, Why This Matters

### Community 25 - "Community 25"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 05: Modulation System, First Iteration, Scope, Story, Why This Matters

### Community 26 - "Community 26"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 02: Analysis IR, First Iteration, Scope, Story, Why This Matters

### Community 27 - "Community 27"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 09: Render Diagnostics, First Iteration, Scope, Story, Why This Matters

### Community 28 - "Community 28"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 07: Transition System, First Iteration, Scope, Story, Why This Matters

### Community 29 - "Community 29"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 04: Layer Library, First Iteration, Scope, Story, Why This Matters

### Community 30 - "Community 30"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 06: Timeline Director, First Iteration, Scope, Story, Why This Matters

### Community 31 - "Community 31"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 11: Raindrops Shader, First Iteration, Scope, Story, Why This Matters

### Community 32 - "Community 32"
Cohesion: 0.25
Nodes (7): Acceptance Criteria, Dependencies, Epic 10: Fixture Mapping And Export, First Iteration, Scope, Story, Why This Matters

### Community 33 - "Community 33"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 02: Analysis IR, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 34 - "Community 34"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 08: Preview Console, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 04: Layer Library, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 07: Transition System, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 10: Fixture Mapping And Export, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 38 - "Community 38"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 11: Raindrops Shader, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 39 - "Community 39"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 03: Preset Schema, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 40 - "Community 40"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 05: Modulation System, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 41 - "Community 41"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 09: Render Diagnostics, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 42 - "Community 42"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 06: Timeline Director, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 43 - "Community 43"
Cohesion: 0.29
Nodes (7): Backend Track, Backend Track, Epic 12: Spectroid Chase Shader, Frontend Track, Frontend Track, Validation Track, Validation Track

### Community 44 - "Community 44"
Cohesion: 0.29
Nodes (7): Bluesky Icon, Discord Icon, Documentation Icon, GitHub Icon, Social Icon, Icons SVG Sprite, X Icon

### Community 45 - "Community 45"
Cohesion: 0.33
Nodes (5): ContactSheetMetadata, DiagnosticsSummary, FrameDiagnostics, PreviewAsset, RenderDiagnosticsOutput

### Community 46 - "Community 46"
Cohesion: 0.33
Nodes (6): export_dmx(), Validate current fixture mapping configuration (Epic 10.B2).          Returns:, Export render to DMX format with gamma correction and brightness limiting (Epic, validate_mapping(), PixelMapping, Canonical pixel coordinate to flat index mapping (Epic 10.B1).          Default:

### Community 47 - "Community 47"
Cohesion: 0.33
Nodes (4): MappingValidation, Validate fixture mapping for errors and coverage (Epic 10.B2)., Validate export configuration before sending., Validation results for fixture mapping.

### Community 48 - "Community 48"
Cohesion: 0.33
Nodes (5): Deliverables, Exit Criteria, Goal, Included Epics, Phase 6: Quality, Performance, And Packaging

### Community 49 - "Community 49"
Cohesion: 0.33
Nodes (5): Deliverables, Exit Criteria, Goal, Included Epics, Phase 4: Timeline And Direction

### Community 50 - "Community 50"
Cohesion: 0.33
Nodes (5): Deliverables, Exit Criteria, Goal, Included Epics, Phase 3: Preset And Layer Engine

### Community 51 - "Community 51"
Cohesion: 0.33
Nodes (5): Deliverables, Exit Criteria, Goal, Included Epics, Phase 2: Musical Analysis IR

### Community 52 - "Community 52"
Cohesion: 0.33
Nodes (5): Deliverables, Exit Criteria, Goal, Included Epics, Phase 5: Production Console

### Community 53 - "Community 53"
Cohesion: 0.33
Nodes (5): Deliverables, Exit Criteria, Goal, Included Epics, Phase 1: Baseline And Contracts

### Community 54 - "Community 54"
Cohesion: 0.33
Nodes (5): code:js (export default defineConfig([), code:js (// eslint.config.js), Expanding the ESLint configuration, React Compiler, React + TypeScript + Vite

### Community 55 - "Community 55"
Cohesion: 0.8
Nodes (4): make_context(), test_background_sweep_and_waveform_ring_determinism(), test_particle_field_layer_seeded_determinism(), to_host()

### Community 56 - "Community 56"
Cohesion: 0.4
Nodes (4): AI Light Show V3: BeatDrop / MilkDrop Inspired Visualizer, Development, Features to Incorporate (Inspired by BeatDrop), System Architecture

### Community 57 - "Community 57"
Cohesion: 0.4
Nodes (4): 100x50 Is The Product, BeatDrop Inspiration, Not Parity, Product Principles, Production Grade Definition

### Community 58 - "Community 58"
Cohesion: 0.4
Nodes (4): Epic Index, Phase Summary, Recommended Iteration Order, Roadmap

### Community 59 - "Community 59"
Cohesion: 0.4
Nodes (5): Backend Requirements, cupy-cuda12x, essentia, fastapi, pydantic

### Community 60 - "Community 60"
Cohesion: 0.4
Nodes (5): React Compiler, React + TypeScript + Vite Template, Frontend README, @vitejs/plugin-react, @vitejs/plugin-react-swc

### Community 63 - "Community 63"
Cohesion: 0.5
Nodes (4): Fearlessness, Personal Power, Pet Shop Boys - I'm Not Scared Transcript, Yonaka - Seize the Power Transcript

## Knowledge Gaps
- **452 isolated node(s):** `FrameData`, `PresetParameter`, `ModulatorConfig`, `AnalysisFeatures`, `TransitionSchema` (+447 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PresetSchema` connect `Community 0` to `Community 8`, `Community 1`, `Community 11`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `FrameRenderer` connect `Community 1` to `Community 0`, `Community 8`, `Community 2`, `Community 11`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `GenerateRequest` connect `Community 8` to `Community 0`, `Community 1`, `Community 11`, `Community 12`, `Community 46`, `Community 21`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `PresetSchema` (e.g. with `TestEpic02AnalysisTypes` and `TestEpic03BaselineParity`) actually correct?**
  _`PresetSchema` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `make_renderer()` (e.g. with `.test_analysis_features_have_beat_phase()` and `.test_analysis_features_have_bar_phase()`) actually correct?**
  _`make_renderer()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `FrameRenderer` (e.g. with `FakeAnalyzer` and `GenerateRequest`) actually correct?**
  _`FrameRenderer` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `LayerConfig` (e.g. with `TestEpic02AnalysisTypes` and `TestEpic03BaselineParity`) actually correct?**
  _`LayerConfig` has 12 INFERRED edges - model-reasoned connections that need verification._