# ADR-0016: Simulation event and snapshot contract (Freeze point 4)

* Status: Draft pending P5 acceptance checks
* Date: 2026-11-11

## Context

Both visualizers need one UI-independent source for actions and state. Coverage also needs raw-grid accounting distinct from footprint-safe centre movement.

## Decision

Introduce separate point-to-point and coverage mission types; a versioned JSON event with simulation time, sequence and payload; immutable snapshot values; and a bounded deque for snapshots. The executor routes every movement through `Robot.step`. Search is timed independently and guarded by robot snapshot comparisons. Raw reachable FREE/DOOR cells form the denominator; cells no legal reachable centre can clean are separately marked structurally uncoverable and excluded only from achievable coverage.

## Consequences

Consumers can replay the action event stream and sample bounded snapshots. The schema remains provisional until full replay, algorithm matrix and department-map runs are verified. Search failure for a selected target is logged and excluded from repeated selection.
