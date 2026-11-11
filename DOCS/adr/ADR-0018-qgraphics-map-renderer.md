# ADR-0018: QGraphicsView for the embedded 2D map

* Status: Accepted for P6
* Date: 2026-11-11

## Context

The map view must show 127×120 occupancy cells with semantic overlays, cell picking, pan/zoom, and a shared representation for map editing and simulation. Qt is already the desktop toolkit.

## Decision

Use a `QGraphicsView` with scene-coordinate painting for occupancy and overlays. Cell textures/markers accompany colors; the rendering code reads map and snapshot values but does not mutate domain state. This avoids a Matplotlib dependency in the interactive view and uses Qt's built-in scene transform for pan/zoom.

## Measurement

`scripts/measure_map_frame.py` rendered the department v1 127×120 grid at 1100×760 in an offscreen Qt session. Across 12 `grab()` + event-processing samples, median render latency was 1.89 ms and maximum was 2.28 ms on the current machine. These measurements were taken after caching occupancy and overlay layers. The coverage worker event-loop test separately measures timer latency during a run; the latest full-suite run passed its <100 ms requirement.

## Consequences

The rendering stays in the Qt stack and supports accessible patterns and cell interaction. Re-measure if overlay density or grid dimensions grow substantially.
