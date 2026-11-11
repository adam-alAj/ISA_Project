# Environment API draft

This document describes the UI-independent environment contract for P2. The API is implemented in `src/environment` and does not import PySide6 or Ursina.

## Occupancy and coordinates

Occupancy is a two-dimensional `numpy.uint8` array with `FREE=0`, `OCCUPIED=1`, `UNKNOWN=2`, and `DOOR=3`. Only `FREE` and `DOOR` are traversable. Cleaning uses a separate boolean array and never modifies occupancy.

Cells are `(row, column)`, rows increase down, and columns increase right. Neighbors are yielded in fixed `Up, Right, Down, Left` order. `GridMap.is_valid_transition(a,b)` requires Manhattan adjacency, in-bounds endpoints, and traversability at both ends. Pixel transforms use source `(x,y)` coordinates, origin `(80,160)` for the department trace, and `108 px/m`; metric coordinates use positive x right and y down. The 3D mapping is `(x, floor_y, z)` with z negative as image rows increase.

`GridMap.with_footprint(radius_m)` returns a read-only robot-center navigation mask. It conservatively rounds the radius outward to whole cells and applies a discrete circular kernel using NumPy. The current robot diameter assumption remains 0.35 m and provisional.

`validate_cells` checks starts and targets. `validate_map` returns structured `ValidationIssue` records. `connected_components` and `reachable_from` use four-neighbor connectivity. `CleaningState` tracks cleaning progress independently from map occupancy.

## Map authoring and persistence

`data/maps/department_v1/map_spec.yaml` is JSON-compatible YAML to allow loading with Python's standard library. `spec_loader.load_spec` validates its required geometry. `rasterizer.rasterize` applies the legacy builder's cell-center and wall-stamping rules. `MapEditor` exposes cell-rectangle edits, door marking and obstacle marking for a later UI.

`save_map` writes `grid.npz` and `map.json` with schema version, timestamp, spec hash, grid hash and metadata using temporary files plus atomic replacement. `load_map` rejects unsupported schemas, shape mismatches and grid hash mismatches.

## Freeze status

This API is implemented as a draft and is **not frozen**. P2 tests still need to run in Python 3.12, the original floor-plan image is still missing for visual comparison, and the user-required map review/signature remains outstanding. Freeze point 1 requires that review and signature.
