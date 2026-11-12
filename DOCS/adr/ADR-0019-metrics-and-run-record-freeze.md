# ADR-0019: Metrics and run-record contract (Freeze point 5)

* Status: Accepted
* Date: 2026-11-11
* Repository HEAD at freeze review: `3b7a269258746289888c609634838ea9d4047155`
* Contract: `docs/metrics.md`, `docs/search_counters.md`, `docs/run_record.md`
* Run-record schema: `schemas/run_record.schema.json`, version 1

The recorded commit hash identifies the repository HEAD reviewed when this
ADR was authored. The P6 gate evidence, P8 freeze documents, and subsequent
implementation work were still uncommitted in the shared working tree at that
time; this hash is not represented as a commit containing those edits.

## Context

P8 requires a single set of definitions before analytics, charts, or reports
can consume search results and simulation events. The SRS §14, §16, §19.5 and
Appendix B require reproducible raw runs, separate search and travel timing,
geometric length and configured cost, coverage denominator disclosure, and
factual interpretation. P6 automated gate evidence is recorded in
`reports/qa/p6_gate_result.md`; human usability remains deferred to P9.16.

## Decision

Freeze the search counter/goal-test semantics in `docs/search_counters.md` and
the cross-layer formulas and units in `docs/metrics.md`. Freeze the version-1
run record fields in `schemas/run_record.schema.json`. Compute a stable
run identifier as SHA-256 over canonical UTF-8 JSON containing exactly the
map-content hash, normalized experiment configuration, algorithm ID, policy
ID/configuration (or null for point-to-point), and seed. Exclude wall-clock
timestamps, result values, host details, and generated IDs from that hash.

The schema records both raw search results and a content-hashed event-log
artifact reference. Reports must be reproducible from those persisted records
and referenced files, without querying live UI state or rerunning a planner.

## Consequences

Search time and simulated action time are separately represented. Coverage
reports carry raw and achievable coverage together with their denominators and
structurally-uncoverable counts. Cost and distance cannot be substituted for
each other. Schema or metric semantic changes require a new ADR and schema
version where compatibility is affected.

## Verification

The search counter behavior is exercised in `tests/algorithms/test_search.py`;
the P6 prerequisite and full repository suite passed at freeze review (87
tests). Run-record hash determinism and schema validation are implemented and
tested as P8 work proceeds.
