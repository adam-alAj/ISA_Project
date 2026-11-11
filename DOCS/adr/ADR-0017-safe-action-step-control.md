# ADR-0017: Safe-action pause and single-step control

* Status: Accepted for P6 integration
* Date: 2026-11-11
* Impacted contracts: P5 `CoverageController` and `RouteExecutor`; P6 worker controls

## Context

P6 requires Pause, Resume, Step, and Cancel without blocking the GUI thread. Freeze point 4 already defines the event/snapshot schema, while the P5 controller previously only paused between target selections.

## Decision

Add a condition-based controller gate that can pause at route action boundaries, allow exactly one validated `Robot.step` per `step_once()` request, wake safely on cancel, and continue waiting on resume. `RouteExecutor` accepts an optional action-boundary callback. Event names and serialized event fields do not change.

## Consequences

The UI worker can expose one-action stepping while movement remains validated through `Robot.step`. Cancellation wakes paused workers. Existing event consumers remain schema-compatible. Regression coverage includes cancellation while paused; the UI step flow receives additional testing as P6 is completed.
