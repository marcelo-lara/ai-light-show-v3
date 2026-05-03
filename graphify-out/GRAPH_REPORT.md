# GRAPH_REPORT

## Corpus Summary

- Path: /home/darkangel/ai-light-show-v3
- Files: 2
- Words: ~1,790
- Code files: 0
- Document files: 2
- Extraction mode: local fallback (graphify package unavailable in this environment)

## Community Labels

- Community 0: Project Frame
- Community 1: Layout Flow
- Community 2: Diagnostics Cluster

## God Nodes

- Light Show Player Frontend [Project Frame] - degree 7 via ui-specs.md
- Three-Column Diagnostics Area [Layout Flow] - degree 6 via ui-specs.md
- Transport Controls Row [Layout Flow] - degree 5 via ui-specs.md
- Waveform Area [Layout Flow] - degree 5 via ui-specs.md
- Diagnostics Panel [Diagnostics Cluster] - degree 4 via ui-specs.md

## Surprising Connections

- Light Show Player Frontend -> Dark Technical Playback Console (EXTRACTED): The UI spec makes visual tone a first-class architectural concern, not just styling polish.
- Top Bar -> Transport Controls Row (INFERRED): Selection and playback control are separated visually, but still operate as one control loop for show loading and execution.
- Event Log Panel -> Diagnostics Panel (INFERRED): These panels monitor different signals yet converge on the same operator-telemetry role, making them strong candidates for shared component patterns.

## Suggested Questions

- How does the playback state model drive updates across the top bar, waveform, transport row, and diagnostics panels?
- Which parts of the UI spec most strongly enforce the dark technical playback console identity?
- What shared telemetry pattern links the event log panel and diagnostics panel?

## Notes

- The repository content is documentation-only at the moment, so the graph emphasizes concepts, layout zones, and UI intent rather than code structure.
- One edge from the UI spec to the repo title is marked ambiguous because the README does not yet describe the product beyond its name.
