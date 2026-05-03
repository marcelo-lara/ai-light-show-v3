# Graph Report - ai-light-show-v3  (2026-05-03)

## Corpus Check
- 5 files · ~6,426 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 22 nodes · 18 edges · 4 communities detected
- Extraction: 83% EXTRACTED · 11% INFERRED · 6% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]

## God Nodes (most connected - your core abstractions)
1. `Light Show Player Frontend` - 7 edges
2. `Three-Column Diagnostics Area` - 3 edges
3. `generate_frame()` - 2 edges
4. `main()` - 2 edges
5. `WaveSurfer.js` - 2 edges
6. `Waveform Area` - 2 edges
7. `Transport Controls Row` - 2 edges
8. `Event Log Panel` - 2 edges
9. `Diagnostics Panel` - 2 edges
10. `ai-light-show-v3` - 1 edges

## Surprising Connections (you probably didn't know these)
- `ai-light-show-v3` --references--> `Light Show Player Frontend`  [AMBIGUOUS]
  README.md → ui-specs.md

## Hyperedges (group relationships)
- **Application Layout Zones** — ui_specs_top_bar, ui_specs_waveform_area, ui_specs_transport_controls_row, ui_specs_three_column_diagnostics_area [EXTRACTED 1.00]
- **Diagnostics Area Panels** — ui_specs_dmx_monitor_panel, ui_specs_event_log_panel, ui_specs_diagnostics_panel [EXTRACTED 1.00]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.29
Nodes (7): ai-light-show-v3, Dark Technical Playback Console, Light Show Player Frontend, Playback State Model, React, TypeScript, Vite

### Community 1 - "Community 1"
Cohesion: 0.5
Nodes (4): Top Bar, Transport Controls Row, Waveform Area, WaveSurfer.js

### Community 2 - "Community 2"
Cohesion: 0.67
Nodes (4): Diagnostics Panel, DMX Monitor Panel, Event Log Panel, Three-Column Diagnostics Area

### Community 3 - "Community 3"
Cohesion: 1.0
Nodes (2): generate_frame(), main()

## Ambiguous Edges - Review These
- `ai-light-show-v3` → `Light Show Player Frontend`  [AMBIGUOUS]
  ui-specs.md · relation: references

## Knowledge Gaps
- **8 isolated node(s):** `ai-light-show-v3`, `Vite`, `React`, `TypeScript`, `Top Bar` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 3`** (3 nodes): `generate_frame()`, `main()`, `generator.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `ai-light-show-v3` and `Light Show Player Frontend`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Light Show Player Frontend` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `WaveSurfer.js` connect `Community 1` to `Community 0`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **What connects `ai-light-show-v3`, `Vite`, `React` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._