# ADR-0021: Raw planner metrics in SearchFinished events

* Status: Accepted
* Date: 2026-11-11
* Related freeze: ADR-0016 (Freeze point 4), ADR-0019 (Freeze point 5)
* Regression tests: `tests/test_search_finished_metrics.py` and
  `tests/coverage/test_coverage.py`

## Context

P8 must reproduce aggregate coverage planner counters from stored run data.
Point-to-point callers retain a `SearchResult`, but each coverage planner call
was represented in `SearchFinished` by only a found flag and wall duration.
The coverage result does not retain the per-target SearchResult list, so
expanded/generated/repeated counts and per-call path costs could not be
reconstructed from the event log.

## Decision

Add the following optional raw fields to schema-version-1 `SearchFinished`
payloads in both mission modes: `expanded`, `generated`, `peak_frontier`,
`repeated_expansions`, `path_length_steps`, `path_cost`,
`planner_execution_time_s`, and `termination_reason`. Existing `found` and
`wall_time_s` fields remain. The `search_result_metrics` helper defines the
projection centrally. No full route or trace is copied into the payload; legal
executed movement remains represented by `MoveExecuted` events.

This is an additive payload extension; consumers must ignore unknown optional
keys. Event envelope and replay semantics do not change, so the event schema
version remains 1. A future incompatible change requires a version increment.

## Consequences

P8 can sum per-search counters over a coverage run and take the maximum
per-call peak frontier without retaining unbounded planner objects. `wall_time_s`
continues to represent the outer call duration; `planner_execution_time_s`
is the frozen SearchResult measurement.

## Verification

Tests compare every emitted metric field against point-to-point SearchResult
values and assert coverage `SearchFinished` events carry the same summary
fields.
