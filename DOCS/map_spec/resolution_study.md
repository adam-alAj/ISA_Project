# Grid resolution study

## Method

The legacy builder uses a fixed 1290 × 1370 px raster extent, `PPM=108`, and `ceil(extent / (PPM × cell_m))` for columns and rows. The table below is formula-derived from that code; the builder was not run because Python is unavailable. Runtime values are therefore not fabricated. A 0.9 m door is the narrowest specified passage. The robot diameter is 0.35 m, so the builder radius is `ceil((0.35/2) / cell_m)`.

## Comparison

| Cell size | Grid (rows × cols) | Grid cells | 0.9 m opening (cell-width equivalent) | Inflation radius | Disk offsets checked by legacy loop | Full-grid neighbor upper bound (4N) | Build time |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0.05 m | 254 × 239 | 60,706 | 18 cells | 4 cells (0.20 m) | 49 | 242,824 | Not measured; about 3.98× the 0.10 m cell count |
| 0.10 m | 127 × 120 | 15,240 | 9 cells | 2 cells (0.20 m) | 13 | 60,960 | Not measured; reference baseline |
| 0.20 m | 64 × 60 | 3,840 | 4.5 cell-width equivalents (rasterized count may be 4 or 5) | 1 cell (0.20 m) | 5 | 15,360 | Not measured; about 0.25× the 0.10 m cell count |

The `4N` column is a conservative full-grid bound on neighbor checks, not a measured expansion count. For the same physical map, a broad search's state and edge work is expected to scale approximately with cell count: about 4× at 0.05 m and 0.25× at 0.20 m versus 0.10 m. Actual search cost depends on traversability, start/goal, and algorithm.

## Inflation and passage implications

The legacy implementation evaluates 49, 13, or 5 shifted masks per grid cell for its circular integer-radius stencil. Thus its inflation workload proxy is approximately 3.78× the 0.10 m baseline at 0.05 m and 0.25× at 0.20 m, before constant overhead. All resolutions round the 0.175 m physical radius up to 0.20 m in the current implementation. The 0.20 m grid has only about 4–5 samples across a 0.9 m opening, so raster alignment has a larger effect on clearance and doorway representation. The builder must be executed and passage connectivity checked before adopting any resolution change.

The nominal free width after subtracting the 0.35 m robot diameter from a 0.90 m door is 0.55 m. The current 0.20 m inflated radius on each side leaves about 0.50 m in the raster model. That is roughly 10 cells at 0.05 m, 5 cells at 0.10 m, and 2–3 cells at 0.20 m, before raster alignment and obstacle-boundary effects.

## Recommendation

Keep **0.10 m** for the v0.2 baseline. It is the existing map resolution, gives roughly nine cells across a specified 0.9 m door, and retains about one quarter the cell count of a 0.05 m grid. The 0.20 m grid is cheaper but too coarse for a confident doorway/footprint review without a fresh raster connectivity run. These are numeric projections from the builder formulas; measured build times and actual per-algorithm expansion counts remain pending.
