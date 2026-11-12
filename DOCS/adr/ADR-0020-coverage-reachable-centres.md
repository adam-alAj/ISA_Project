# ADR-0020: Reachable robot centres in structural coverage accounting

* Status: Accepted
* Date: 2026-11-11
* Related freeze: ADR-0016 (P5 simulation contract), ADR-0019 (P8 metrics)
* Regression: `tests/coverage/test_coverage.py::test_structural_uncoverable_excludes_regions_without_a_reachable_robot_centre`

## Context

P5 defines structurally-uncoverable cells as raw-reachable cells that no legal
robot centre reachable from the mission start can clean. The prior
`build_cleanable_cells` implementation considered every footprint-navigable
cell on the map, including isolated navigable components behind corridors too
narrow for the robot. Such cells made `achievable_cells` too large and lowered
the reported achievable coverage incorrectly.

## Decision

Flood-fill the robot-centre graph from the mission start using only traversable
cells in the footprint-inflated navigable mask. Only these start-reachable
centres contribute to the footprint-cleanable set. The raw cleanable
denominator remains the four-neighbor component of FREE/DOOR cells on the
uninflated grid. No P5 event/snapshot schema fields change.

## Consequences

Disconnected narrow passages are reported structurally-uncoverable from the
configured start even when the remote region itself contains valid centre
positions. Raw coverage still reports those cells in its denominator; achievable
coverage excludes them as defined in `docs/metrics.md` §4.

## Verification

The regression fixture proves a remote chamber is raw-reachable and has legal
centre cells, but is not in the start-reachable centre component. Its cells are
classified structurally-uncoverable. The focused regression passed on
2026-11-11.
