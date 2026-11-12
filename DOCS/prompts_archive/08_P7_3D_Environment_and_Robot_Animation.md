# ARCHIVED ? P7 3D scope descoped

This historical prompt is retained for traceability only. P7 was descoped by ADR-0022; do not execute it unless the instructor restores the requirement.

---

# Prompt 08 — Phase P7: 3D Environment & Robot Animation

## 1. Role
You are a **Real-time 3D Graphics Engineer (Python / Ursina Engine)** focused on procedural geometry, scene optimization and strict synchronization with a simulation's data model. You never re-implement domain logic in the renderer.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. Gate of **P5** must be met. May run **in parallel with P6**. Use the P0.15 feasibility result for the integration mode (default: Ursina in a **separate process**, synchronized with the main app through JSON messages).

## 3. Inputs
`GridMap` (grid, cell size), simulation event/snapshot API, route and cleaning data, feasibility prototype, SRS FR-21, AC-06, Roadmap P7.

## 4. Objective
Create a 3D scene that mirrors the same digital map and robot trajectory. **Exit gate:** 3D geometry corresponds to the approved map; the robot follows the same path as in 2D; playback is stable on the demo machine.

## 5. Tasks (ID → concrete instruction)
- **P7.01** Minimal Ursina prototype in `src/visualization/three_d/`: window, lighting, camera, FPS counter; record FPS on the target laptop (HUMAN ACTION to run on the real hardware; the agent also runs a headless/software check if possible).
- **P7.02** `three_d/coords.py`: conversion `(row, col)` → 3D world `(x, y_up, z)` with 1 unit = 1 m, cell centre at `((col+0.5)·cell_m, 0, −(row+0.5)·cell_m)`; round-trip tests; reuse P2.09 constants (no duplicated scale).
- **P7.03** Floor mesh from `FREE/DOOR` cells; **greedy meshing** (merge adjacent cells into rectangles) to keep the entity count small.
- **P7.04** Wall geometry from `OCCUPIED` cells that border traversable cells (outer void is not rendered); merge into boxes; wall height 2.7 m (configurable); consistent thickness from the grid.
- **P7.05** Door openings rendered as gaps (optionally a lintel/frame); doors are 0.9 m (R1: 1.2 m); verify no wall mesh fills a `DOOR` cell.
- **P7.06** Optional labels: room IDs/names as floating text (ASCII IDs required; Arabic names optional), column and cabinets as distinct boxes (0.5 × 0.5 m column; cabinets 10 cm protrusion, 75 cm / 60 cm).
- **P7.07** Robot model: primitive disc (cylinder) + small bumper/indicator; diameter = `RobotConfig.diameter`.
- **P7.08** Scale from calibration (never hard-coded).
- **P7.09** Camera: orbit, pan, zoom, reset, top-down and follow-robot presets; clamp to avoid clipping through walls.
- **P7.10** Animate along the executed route using **simulation events** (`MoveExecuted`) with linear interpolation per step; speed from the shared playback control.
- **P7.11** Synchronization contract: 3D consumes the same event stream/snapshots as 2D; a **sync test** compares the 3D robot cell sequence against the 2D/engine sequence.
- **P7.12** Cleaned-area visualization: tint floor cells as they are cleaned (instanced quads or a texture updated in batches); fall back to route-only rendering if FPS drops below 30 and document it.
- **P7.13** Playback speed, pause, reset consistent with the UI controls (message protocol: `play, pause, step, reset, speed, seek`).
- **P7.14** Floor height, camera near/far planes, z-fighting prevention (floor slightly below cleaned overlay), wall culling.
- **P7.15** Optimization: entity count budget (< 2,000), batch meshes, no per-frame allocations, FPS ≥ 30 target; report measurements.
- **P7.16** Test: no robot position ever lies inside a wall mesh bounds or a non-door gap (automated geometry test using the grid, not the renderer).
- **P7.17** Test: 3D route coordinates ≈ 2D route coordinates (tolerance 1e-6 m).
- **P7.18** Decide and document the final integration mode (separate synchronized process vs embedded) in an ADR using P0.15 + measured data; implement the launcher in the main app (`Launch 3D` button) and graceful shutdown/reconnect.
- **P7.19** Demo-machine test plan `docs/3d_demo_checklist.md` (drivers, resolution, FPS, fallback to video). **HUMAN ACTION** on the presentation laptop; the agent provides the checklist and a one-command self-test script.

## 6. Constraints
- Ursina must not leak into core packages; 3D process communicates only via the documented message protocol.
- 3D never decides movement; it only plays back events.
- Keep the scene reproducible from `map.json + run log` only (no hidden state).

## 7. Deliverables
`src/visualization/three_d/*`, `tests/three_d/*` (geometry/sync tests that do not require a GPU), `docs/3d_design.md`, `docs/3d_demo_checklist.md`, ADR on integration mode, short screen recording or screenshots.

## 8. Acceptance gate (report pass/fail each)
- [ ] 3D wall/door/column/cabinet layout matches the grid (automated comparison of mesh footprints vs grid).
- [ ] Robot path in 3D equals the engine path (sync test).
- [ ] FPS ≥ 30 on the target machine (measured) or documented fallback.
- [ ] Launch/close from the main app is stable over 10 cycles.

## 9. Output
Use the report format from Shared Context §8.5. Include FPS and entity-count measurements.
