# P1 map artifact checks

## Checks performed against the preserved array

- Read the NumPy v1.0 header directly: dtype `uint8`, shape `(127,120)`, data offset 128 bytes.
- Counted states from the array: `FREE=9,978`, `OCCUPIED=5,064`, `UNKNOWN=0`, `DOOR=198`; total 15,240.
- Confirmed all nine door-rectangle centers map to `DOOR=3` in the existing array.
- Confirmed all 16 endpoint cells for the eight department-map demo scenarios are traversable. A four-neighbor breadth-first traversal from each scenario start found the goals at the step counts recorded in `demo_goals.csv`.
- The around-column scenario starts at `(36,68)` and targets `(36,78)`. On row 36, columns 70–74 are occupied by the C1 column, so the direct horizontal segment is blocked; the alternate 4-neighbor route exists.
- From the supplied start `(118,54)`, independent 4-neighbor BFS reached all 10,176 free/door cells in the array.
- SHA-256 values for the existing map array, metadata, and preview are recorded in `source_manifest.md`; these inputs were not rewritten.

## Checks not performed

The Python builder was not run. No build-time measurement, regenerated resolution variant, robot-inflation connectivity result, Matplotlib rendering, or project test-suite result is claimed. Those checks need a Python 3.11/3.12 environment; the original photo is also required for annotation and scale confirmation.
