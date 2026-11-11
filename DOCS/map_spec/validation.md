# P1 map artifact checks — v0.3 draft

## Generated raster and geometry

The v0.3 array is `(127,120)`, `uint8`, cell size 0.10 m. It was rasterized in this workspace with an independent PowerShell reproduction of the builder's cell-center masks because Python is not installed here. The committed Python builder and pytest regression suite are present but could not be executed in this environment.

| Validation | v0.2 | v0.3 draft |
|---|---:|---:|
| FREE cells | 9,978 | 9,980 |
| OCCUPIED cells | 5,064 | 5,062 |
| UNKNOWN cells | 0 | 0 |
| DOOR cells | 198 | 198 |
| Traversable FREE+DOOR cells | 10,176 | 10,178 |
| Reachable from S, four-neighbor | 10,176 | 10,178 |
| Reachable with 0.35 m footprint | 8,435 | 8,453 |

Every one of the nine rooms has reachable cells from S both without footprint inflation and with the 0.35 m footprint. The hall mask contains 6,722 cells in the comparison; zero hall cell states changed. Door-cell set symmetric difference is zero. The start remains `(118,54)` and obstacle rectangles are unchanged. R4/R5/R6 remain within map bounds; room rectangles do not overlap. Regression coverage for these conditions is in `tests/test_map_v03_geometry.py`.

## Demo scenarios

The eight department-map scenarios retain the reviewed v0.2 goal cells. Default start is S `(118,54)`; `around_column` uses `(36,68)` only under the configured `around_column_alternate_start` scenario variant. The synthetic no-path scenario is not a department-map coordinate. Recompute shortest paths after a Python runtime becomes available; P1 validation counts above concern the generated map and room reachability.

## Not performed / pending

Python builder execution, pytest, Matplotlib preview generation, and source-photo-dependent checks were not performed: Python and the named original image are absent. P1.01/P1.02 remain blocked on the photo. This does not block P2 work using the recorded working assumptions. The map is not frozen.
