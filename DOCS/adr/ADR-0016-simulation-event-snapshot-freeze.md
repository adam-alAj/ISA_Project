# ADR-0016: Simulation event and snapshot contract (Freeze point 4)

* Status: Accepted (Freeze point 4)
* Date: 2026-11-11
* Verification: `reports/qa/p5_gate_result.md`
* Implementation commit: `021abae`

## Context

Both visualizers need one UI-independent source for actions and state. Coverage also needs raw-grid accounting distinct from footprint-safe centre movement.

## Decision

Introduce separate point-to-point and coverage mission types; a versioned JSON event with simulation time, sequence and payload; immutable snapshot values; and a bounded deque for snapshots. The executor routes every movement through `Robot.step`. Search is timed independently and guarded by robot snapshot comparisons. Raw reachable FREE/DOOR cells form the denominator; cells no legal reachable centre can clean are separately marked structurally uncoverable and excluded only from achievable coverage.

## Verification

The P5 gate report records a passing smoke test, full suite, TS-08/TS-09 across six planners, 100 seeded movement scenarios, planning-state immutability, replay equivalence with schema versions, and bounded memory. The department-map comparison uses 2,000 expansions or 0.5 seconds per search and a 50-target iteration guard. Its rows are intentionally partial diagnostics and record the guard stop; they do not claim full-floor coverage.

## Consequences

Consumers can replay the action event stream and sample bounded snapshots. Replay beyond the in-memory event-ring capacity requires the optional JSONL sink. Search failure for a selected target is logged and excluded from repeated selection.
