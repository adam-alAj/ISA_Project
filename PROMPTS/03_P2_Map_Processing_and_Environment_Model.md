# Prompt 03 — Phase P2: Map Processing & Environment Model

## 1. Role
You are a **Robotics Mapping & Environment-Modeling Engineer** (occupancy grids, state-space graphs, coordinate frames). You write clean, tested, UI-independent Python/NumPy and you treat coordinate conventions as an API contract.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. The v0.2 builder script exists as `legacy_build_map.py` (traced pixel rectangles → grid). **Refactor and harden it into reusable modules; do not rewrite the geometry from scratch and do not change the map output unless a test proves a bug.** The source is a JPEG photo, so PDF input is *not required* (see P2.01).

## 3. Inputs
P1 outputs (`docs/map_spec/*`), `legacy_build_map.py`, `data/maps/department_v0_2/*`, SRS §8, Roadmap P2.

## 4. Objective
Produce the machine-readable map and reusable state-space model. **Exit gate:** digitized map visually matches the drawing; coordinate conversion verified; robot cannot traverse blocked cells; map saves/reloads; environment API frozen.

## 5. Tasks (ID → concrete instruction)
- **P2.01** `map_processing/importer.py`: load PNG/JPG with OpenCV, keep original untouched. PDF rasterization: implement a thin optional function (`pdf_to_image`) guarded by try-import, mark as *optional/not used by the current map*.
- **P2.02** `map_processing/preprocess.py`: EXIF orientation fix, crop and optional resize that **preserve a transform back to source pixels** (store a 3×3 affine/homography matrix).
- **P2.03** `map_processing/calibration.py`: scale from two image points + known distance → `pixels_per_meter`; least-squares calibration from several labelled distances; report residuals. Reproduce `PPM=108`.
- **P2.04** `map_processing/overlay.py`: render grid overlay on the source image/preview at a configurable cell size.
- **P2.05** Replace hard-coded dicts in the builder with a **declarative map spec** (`data/maps/department_v1/map_spec.yaml`: zones, rooms, doors, extra walls, obstacles, start, parameters) + `map_processing/spec_loader.py` + `map_processing/rasterizer.py`. Provide a small **programmatic editing API** (`set_cells(rect, state)`, `add_door`, `add_obstacle`) used later by the UI editor (P6.05). No GUI here.
- **P2.06** `map_processing/suggest.py`: optional OpenCV helpers (threshold/edges) that only *suggest* wall pixels; output is never auto-accepted (human confirmation flag in the API).
- **P2.07** Produce the occupancy grid (`numpy.uint8`) from the spec; the output must be **byte-identical** to `department_map.npy` v0.2 unless a documented bug fix applies (add a regression test comparing hashes).
- **P2.08** `environment/cleaning_state.py`: separate `bool` array `cleaned` same shape as the grid; API `mark_cleaned(cells)`, `is_cleaned`, `count`.
- **P2.09** `environment/coords.py`: transforms pixel ⇄ (row,col) ⇄ meters ⇄ 3D world; unit tests with known dimensions (e.g., 6 m = 60 cells; column 5×5 cells; cabinet 1 cell protrusion).
- **P2.10** `environment/grid_map.py`: immutable-ish `GridMap` (grid, cell_m, origin, metadata) with `is_traversable(cell)`, and `environment/graph.py` for map→graph (NetworkX optional, never required by search code).
- **P2.11** `neighbors(cell)` returns neighbors in fixed order **Up, Right, Down, Left**; documented and tested.
- **P2.12** `is_valid_transition(a, b)`: adjacent, in-bounds, both traversable (`FREE` or `DOOR`), never `OCCUPIED/UNKNOWN`.
- **P2.13** `environment/inflation.py`: obstacle inflation by robot radius (disc kernel via NumPy shifts or `scipy` if allowed; keep dependency optional) producing a *navigable-for-robot-centre* mask; expose `GridMap.with_footprint(radius_m)`. Test: R-rooms stay reachable; the cabinet protrusion does not block the hall.
- **P2.14** `environment/components.py`: connected-component labelling (4-neighbor), `reachable_from(start)`, report of disconnected regions (should be none on v1; test with synthetic maps).
- **P2.15** `environment/validation.py::validate_cells(start, targets)`.
- **P2.16** Map validators returning structured issues (`ValidationIssue(code, severity, message, cells)`): no free cells, invalid dimensions, UNKNOWN regions, accidental openings (free cell adjacent to the outside bounding region), invalid start, door not connecting two free regions.
- **P2.17** `visualization/map_preview.py`: Matplotlib preview with legend (FREE/OCCUPIED/DOOR/UNKNOWN, start, optional room labels). Color must not be the only cue (add hatching or markers). Interactive editing is P6.
- **P2.18** Save/load: `map.json` (metadata, calibration, cell size, start, spec hash, version, timestamp) + `grid.npz` (compressed). Atomic writes (temp file → rename); loader validates schema version.
- **P2.19** `tests/maps/` synthetic maps: open room, corridor, wall detour, disconnected regions, narrow passage (width < robot diameter), heuristic-trap layout, weighted-cost layout, plus the real department map.
- **P2.20** Tests: connectivity, coordinate round-trips (error < 0.5 cell), calibration residuals, determinism (same spec → same hash).
- **P2.21** Freeze: write `data/maps/department_v1/` (version `1.0`), record SHA-256, tag the environment API in an ADR ("Freeze point 1").

## 6. Constraints
- Core modules (`environment`, `map_processing` except the optional OpenCV helpers) must not import PySide6/Ursina.
- Keep the occupancy array and the cleaning array strictly separate.
- All public functions typed and documented; no magic numbers (constants in one module).

## 7. Deliverables
`src/map_processing/*`, `src/environment/*`, `data/maps/department_v1/*`, synthetic test maps, `tests/` for P2, preview PNG, ADR "Environment API freeze".

## 8. Acceptance gate (report pass/fail each)
- [ ] Rasterizer output equals v0.2 grid (hash test) or every difference is explained.
- [ ] No `OCCUPIED/UNKNOWN` cell is reachable through `neighbors`+`is_valid_transition`.
- [ ] Coordinate conversions verified against known dimensions.
- [ ] All rooms reachable from start, also with the 0.35 m footprint; disconnected-region detector works on the synthetic map.
- [ ] Map saves, reloads and validates; version + hash recorded.
- [ ] Environment API documented and frozen.

## 9. Output
Use the report format from Shared Context §8.5. Include the grid shape, free-cell count, and navigable-cell count.
