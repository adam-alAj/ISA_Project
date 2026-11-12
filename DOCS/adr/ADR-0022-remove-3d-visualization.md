# ADR-0022: Remove the 3D visualization feature

- **Status:** Accepted — pending instructor acknowledgement
- **Date:** 2026-11-12
- **Decision anchor:** `pre-3d-removal` at `3663f4e06934197fe652741662b58128e1699c5a`
- **Owners:** project team; instructor acknowledgement is still required

## Context

The P7 3D viewer was a separate Ursina/Panda3D process attached to the PySide6 application. The rendering investigation isolated an opaque full-window HUD child under the UI camera that occluded the world. The blank frame was therefore a real P7 defect, not a camera-frustum defect. Reproducing a robust renderer and capture path would add a second graphics stack and maintenance burden late in the project. The feature is not required to retain the tested 2D map, planner, coverage mission, analytics, or report workflows.

The pre-change evidence and full reference inventory are recorded in `docs/3d_removal_inventory.md` and `reports/qa/baseline_before_3d_removal.md`. The investigation showed a functioning Panda3D capture for an isolated primitive, then loss of production geometry after the production HUD/map integration; visible-window inspection agreed with the empty production viewport. These findings establish a defect in the integrated render/UI pipeline. They do not establish that all Ursina render paths are unusable.

## Decision

Remove the 3D visualization feature, its UI entry points, implementation, tests, scripts, assets, and Ursina/Panda3D runtime dependency. Continue the product as a 2D visualization application. Preserve the frozen simulation event and snapshot contracts, plus the shared grid-coordinate helper used by non-3D tests and consumers.

Reclassify FR-21 (SHOULD) as **Descoped** and AC-06 (MUST) as **Descoped — pending instructor acknowledgement**. Keep both rows visible in traceability. P7, the 3D stability part of P9.14, and 3D demo backup work are descoped. This is not an AC-06 pass. If the instructor does not acknowledge the change, AC-06 remains an unmet MUST and the release gate remains blocked.

## Alternatives considered

1. Repair the production HUD/render integration and maintain the separate renderer. This retains the feature but incurs continued graphics, packaging, and testing work.
2. Replace the capture method or use a software renderer. This may resolve headless capture only and does not by itself fix the visible integrated scene.
3. Replace Ursina with a Qt-embedded 3D renderer. This is a larger integration change with additional platform and maintenance risk.

The team selects removal subject to instructor acknowledgement. No rendering-library replacement is authorized by this decision.

## Consequences

- 2D point-to-point planning, coverage simulation, metrics, CSV/PDF exports, and frozen event/snapshot contracts remain in scope.
- Historical SRS/Roadmap source documents remain unchanged; a deviation record and updated traceability/task-board entries explain the change.
- Performance evidence will cover retained 2D workflows only; no 3D FPS or soak claim will be made.
- The instructor must acknowledge this scope change before AC-06 can be closed for release.

## Evidence and reproducibility

The starting source revision is the safety-tagged decision anchor above. Baseline test and coverage output is summarized in `reports/qa/baseline_before_3d_removal.md`; one timing-sensitive GUI test failed once and passed on retry. The 3D investigation artifacts were preserved in the pre-change worktree checkpoint stash and are summarized in `docs/3d_removal_inventory.md`. This ADR deliberately reports the actual integration defect and does not claim that descoping fixes it.
