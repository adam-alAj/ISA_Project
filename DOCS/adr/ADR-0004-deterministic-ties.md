# ADR-0004 Deterministic tie-breaking

## Context
Equal-priority frontier items may otherwise depend on runtime or container ordering.

## Decision
Use a monotonic insertion counter after algorithm priority; preserve the documented U,R,D,L successor insertion order. Coverage targets use Manhattan distance, then row, then column.

## Consequences
The same inputs yield the same selected route and target sequence, except wall-clock runtime.

## Status
Proposed — specify alongside the P4 interface.
