# UI Specification: AI Light Show V3 Frontend

## Purpose

This document defines a standalone frontend UI specification for recreating the current Light Show Player interface with Vite and WaveSurfer.js. The goal is to reproduce the overall structure, look, and interaction model of the existing UI without depending on this repository's implementation details.

The result should feel like a compact technical playback console: dark, dense, borderless where possible, and optimized for monitoring synchronized media playback.

## Target Stack

- Vite
- React
- TypeScript
- WaveSurfer.js

Optional:

- A component library may be used, but the final UI must not look like a generic dashboard template.
- If a design system is used, it must support a hard-edged dark theme with dense spacing.

## Overall Experience

The UI is a single-screen operator console for audio playback and diagnostics.

It should communicate these traits:

- Dark mode only
- High contrast
- Minimal ornamentation
- Hard edges, almost no rounded corners
- Dense spacing rather than large airy cards
- Utility-first, studio-like presentation
- Live system feedback always visible

The interface should appear closer to a playback rack or monitoring station than to a consumer media player.

## Visual Language

### Color Palette

- App background: pure black or near-black, around `#000000`
- Panel background: slightly lifted charcoal, around `#121212`
- Primary accent: vivid purple, `#9000dd`
- Neutral waveform: dark gray, around `#333333`
- Text primary: white or near-white
- Text secondary: muted gray
- Success: green
- Warning: yellow or amber
- Error: red

### Shape and Density

- Border radius should be `0` globally or visually equivalent
- Padding should be tight and consistent, around `0.5rem` to `0.75rem`
- Borders should be avoided on content panes when whitespace can separate regions
- Thin divider lines may be used on structural boundaries such as above or below control bars

### Typography

- Use a mono or technical-looking typeface for the overall app feel
- The transport clock should be visually prominent and use the accent color
- Labels inside diagnostic panels should be small and subdued
- Large headings are not needed; this is an operational UI, not a marketing page

## Application Layout

The app fills the full viewport height and uses a vertical column layout with four main zones:

1. Top bar
2. Waveform area
3. Transport controls row
4. Two-column control and visualizer area

The page should remain on one screen at desktop sizes. Internal panels may scroll, but the app itself should not feel like a long document.

## Zone 1: Top Bar

The top bar spans the full width and has two functional groups:

- Left: song selection and current canvas state
- Right: live system status indicators

The bar should be horizontally aligned, vertically centered, and separated from the rest of the page with a thin accent divider or equivalent visual boundary.

### Left Side: Selectors

Provide one primary inline selector and one passive state display:

- Song selector
- Current canvas or no-canvas indicator

State ownership:

- The backend owns the current song and current canvas or show.
- The frontend should request the backend to load a different song instead of loading song media independently as the source of truth.
- After the backend loads a song, the frontend should update from backend-provided current song and current canvas state.
- If the loaded song has no canvas or show yet, the song should still load successfully and the UI should show a clear no-canvas state until the user renders one.

Selector behavior and styling:

- They should read as integrated inline controls, not heavy form fields
- Use transparent or background-matched styling
- Avoid visible field boxes where possible
- Avoid underline-heavy default styles
- Dropdown chevrons should match surrounding text color
- Minimum width should be enough to display short names without crowding, approximately `120px`
- The current canvas indicator should clearly show either the active canvas name or a muted `no canvas loaded` state

Loading behavior:

- Selecting a song requests a backend song-load action
- The backend response becomes the source of truth for the loaded song state
- The UI should not fail song loading just because no canvas exists yet
- If no canvas exists, the visualizer area may remain empty or show a placeholder until `Render` is triggered

### Right Side: Status Strip

Place status items flush to the right edge.

Include three elements:

- Live drift gauge
- Playback state chip
- Server connection chip

#### Live Drift Gauge

This is a compact horizontal micro-visualization, roughly `4em` wide and about `24px` tall.

Required behavior:

- Display a thin horizontal baseline centered in the gauge
- Overlay a bar extending left or right from the center depending on drift sign
- Overlay numeric drift text directly on top, such as `12ms` or `-34ms`
- If drift is unavailable, show `-`
- The visualization should prioritize readability over visual flourish

#### Playback State Chip

Display the current playback state in a compact chip.

Behavior:

- `LOADED` should display as `READY`
- `READY` and `PLAYING` should use a green/success treatment
- Inactive or idle states may use a muted gray treatment
- Text should be bold and compact

#### Server Chip

Display a compact chip labeled `SERVER`.

Behavior:

- Green when connected/open
- Yellow when connecting
- Red when closed or disconnected
- Text should be bold and compact

## Zone 2: Waveform Area

The waveform region sits directly under the top bar and should have modest padding around it.

This section is the main visual anchor of the interface and must use WaveSurfer.js.

### Waveform Requirements

- Use a single waveform instance for the selected audio track
- Background should blend into the panel system rather than look detached
- Wave color should be dark gray
- Progress color should use the primary purple accent
- Cursor should be thin
- Bars should be narrow and regular
- Wave height should be approximately `128px`
- Normalize waveform amplitude
- Use a zoom density similar to `minPxPerSec: 100` so the track feels inspectable rather than compressed

### Waveform Scrolling

The waveform scroll area should mimic audio workstation scrollbars.

Scrollbar styling:

- Width/height around `0.5em`
- Track color: black
- Thumb color: medium gray
- Hover thumb color: lighter gray

If the WaveSurfer shadow DOM must be styled directly, that is acceptable.

### Waveform Interaction

- Users can scrub/seek by interacting with the waveform
- The current time must update continuously during playback
- Loading a new song resets time and duration state before playback resumes

## Zone 3: Transport Controls Row

The transport row sits below the waveform and above the lower diagnostics grid.

It contains two aligned groups:

- Left: icon-only transport actions
- Right: large playback clock

Use a thin divider above this row to visually separate it from the waveform.

### Transport Buttons

Display exactly three actions in the left cluster:

- Load
- Stop
- Play/Pause toggle

Requirements:

- Use icon-only buttons
- Keep button chrome minimal; text labels are not needed
- The Play/Pause control must be visually dominant and approximately `0.25em` larger than the secondary actions
- Load should use the primary accent treatment
- Stop should use an error/red treatment
- Play should use success/green
- Pause should use warning/yellow
- Disabled states must be visibly muted but still legible

Behavior:

- Play and Pause must occupy the same button position as a toggle
- Stop should be disabled when nothing is active
- Load should be disabled when no song is selected

### Playback Clock

Place a large timer on the right side of the row.

Requirements:

- Use a mono or technical-looking font
- Use the primary purple accent for the text color
- Make it substantially larger than surrounding text
- Format should resemble media transport time, such as `mm:ss`

## Zone 4: Two-Column Control & Visualizer Area

The lower half of the screen is a two-column layout that expands to fill the remaining vertical space.

Columns:

- Math Parameters (Left)
- Canvas Render / Visualizer (Right)

Desktop layout:

- Left column takes 30% of the available width
- Right column takes the remaining 70% of the width
- Tight gaps between columns
- Each column should stretch vertically to fill available height

Panel styling:

- Use slightly raised dark surfaces against the black page background
- Avoid decorative borders
- Internal content can scroll vertically if needed (especially for the math parameters)
- Use compact text and tight line spacing

### Math Parameters Panel (Left)

This panel allows real-time manipulation of the shader math and visual logic.

Requirements:

- Use tabs at the top of the left panel
- The first tab must be `Main`
- The `Main` tab contains only a `show name` text input and a `Render` button
- Each additional tab maps to one shader or one layer property group
- Form elements inside each shader tab should be dense and technical
- Follow the dark theme with the primary purple accent for active/focused elements

Behavior:

- A song can be loaded even if no canvas exists yet
- The `Render` button creates or replaces the current canvas for the loaded song
- Shader or layer tabs should remain available for editing render parameters before render

### Canvas Render / Visualizer Panel (Right)

This is the main visual output area displaying the pre-computed/cached shaders.

Requirements:

- Canvas should scale to fit the available area while maintaining its aspect ratio (based on the 100x50 conceptual resolution)
- Unused space around the canvas should remain black
- The visualizer should dominate the right side of the UI
- Performance-focused: avoid unnecessary DOM overlays on top of the canvas
- Load fixture and POI reference data from `data/fixtures/fixtures.json` and `data/fixtures/pois.json`
- Show fixtures and POIs as a reference overlay on top of the canvas
- Treat the overlay as non-destructive reference data, not as rendered pixel content
- Fixture markers should use their normalized canvas `location`
- POI markers should use their normalized canvas `location`
- The overlay should remain useful even when no rendered canvas is loaded yet

Overlay behavior:

- Fixtures and POIs are visual references for alignment and preview only
- The overlay should not modify the cached frame data
- Fixture markers should be distinguishable from POI markers
- Labels may be compact or optional, but marker identity should be inspectable
- The overlay may be toggled on or off later, but it should be enabled by default for the first iteration

## Responsive Behavior

The design should adapt cleanly to smaller screens while preserving the same visual language.

### Desktop

- All four zones remain visible in one viewport
- Bottom zone uses the 30/70 two-column layout
- Top bar remains a single row

### Tablet

- Top bar may wrap into two lines if needed
- Bottom zone may collapse to a single column if space is limited (Visualizer on top of Math Parameters)
- Waveform and transport remain prominent

### Mobile

- Stack the song selector, canvas state, and status items vertically or in wrapped rows
- Keep transport controls easy to tap
- Move from two columns to a single stacked layout
- Preserve dense dark styling rather than switching to a card-heavy mobile redesign

## Interaction Model

The UI should feel live and stateful.

The following state changes must visibly affect the interface:

- Song selection requests backend song loading and then updates the UI from backend state
- A successful song load updates the waveform source and current canvas state
- Show name editing affects the next render request, not song loading
- Fixture and POI overlays remain aligned to the canvas regardless of the current frame
- Connection status updates the server chip color
- Playback state updates the state chip and the Play/Pause icon
- Current playback time updates the transport clock
- Live drift updates both the numeric text and the drift bar

## Data Model Expectations

The UI assumes access to a lightweight playback state model with fields equivalent to:

- current song
- current canvas or show
- canvas missing state
- fixture reference list
- POI reference list
- playback state
- current time
- duration
- backend time
- live drift
- startup offset
- backend start lag
- speed factor
- controller role
- connection ready state
- last acknowledgement

Exact field names are not important, but the displayed behavior should match.

## Non-Goals

- Do not build a generic streaming music player UI
- Do not add album art, playlists, side navigation, or decorative hero sections
- Do not round corners or soften the design into consumer-app styling
- Do not replace the dense monitoring layout with oversized cards

## Acceptance Criteria

An implementation is successful if:

- The page visually reads as a dark technical playback console
- The top bar contains inline song/show selectors on the left and live status indicators on the right
- A WaveSurfer.js waveform is the dominant center element
- The transport row uses icon-only controls with an emphasized Play/Pause button and a large purple timer
- The bottom region contains the Math Parameters control panel and the main Visualizer canvas that fill the remaining height
- Scrollbars, colors, spacing, and shapes match the hard-edged studio aesthetic described above
- The UI is recognizably similar to the current Light Show Player frontend even if the code structure differs

## Implementation Guidance for an LLM

If another model is generating this UI from scratch, it should:

- Start with a full-height app shell using a column flex layout
- Implement the top bar, waveform, transport row, and the 2-column bottom area in that order
- Integrate WaveSurfer.js early so the layout is built around the waveform instead of treating it as an afterthought
- Use global CSS variables or a theme object for colors, spacing, and border radius
- Keep the styling intentional and restrained; similarity should come from proportions, hierarchy, and behavior rather than pixel-perfect cloning