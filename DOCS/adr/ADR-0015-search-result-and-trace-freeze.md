# ADR-0015: Search result and trace contract

* Status: Draft; validation pending
* Date: 2026-11-11

## Context

P4 requires six deterministic classical search algorithms with comparable results, explicit counters, and optional JSON-serializable traces. The upstream environment API has not passed its freeze gate, and a Python runtime was unavailable for executing the reference tests in this workspace.

## Decision

Implement a provisional common `SearchProblem`, `SearchResult`, `SearchOptions`, termination enum, counter definitions, U,R,D,L successor order, insertion-counter priority tie breaks, and optional event trace. Register `iddfs` as the canonical iterative-deepening DFS name and retain `idfs` as an alias, consistent with the current working assumption.

## Consequences

The implementation is reviewable and can be used for ongoing integration, but callers must treat the schema as draft. This ADR does not freeze course terminology or final submission scope. Accept only after P2 environment API validation and the P4 test suite and benchmarks run successfully; human confirmation gates remain in force.
