# ADR-0013 Environment API freeze point 1

## Context

P2 defines the coordinate and traversability API consumed by map processing and later planning. The implementation is now represented in `src/environment` and `src/map_processing`. The prior P1 gate requires map review and an authorized human signature before freezing.

## Decision

Adopt the draft contract in `docs/environment_api.md`: uint8 occupancy states; separate boolean cleaning state; `(row,column)` indexing; four-neighbor `Up, Right, Down, Left` order; only FREE/DOOR traversal; explicit calibration transforms; and a conservative discrete robot-footprint mask.

## Consequences

Future robot and algorithm modules can depend on one deterministic map interface. API changes after approval require a new ADR and affected-test note. The v1 map spec carries the P1-approved R4/R5/R6 geometry correction; v0.2 remains an unchanged compatibility fixture. The v0.2 hash-match criterion therefore has a documented exception for those room geometry cells, with hall and door cells required to remain identical.

## Status

Draft only. Do not freeze the map or API until Python tests pass, the source-photo visual gate is addressed, and the authorized reviewer signs the freeze statement.
