# Phase 1: Baseline And Contracts

## Goal

Make the current prototype dependable. Before adding visual complexity, define exactly what a rendered show is, how it is stored, how it is loaded, and how parameter changes are expected to behave.

## Included Epics

- [Epic 01: Render Contract](../epics/01-render-contract.md)
- [Epic 09: Render Diagnostics](../epics/09-render-diagnostics.md)

## Deliverables

- Versioned canvas JSON schema.
- Stable metadata fields.
- Render job lifecycle states.
- Deterministic seeds.
- Basic render diagnostics.
- Golden sample output for at least one short song segment.

## Exit Criteria

- A generated show can be loaded by the frontend without implicit assumptions.
- Missing or incompatible render files produce clear UI errors.
- The same song, preset, params, and seed produce identical frames.
- The docs explain the render artifact format well enough to implement another reader.

