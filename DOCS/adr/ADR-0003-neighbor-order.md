# ADR-0003 Deterministic neighbor order

## Context
Traversal order affects DFS, Greedy, and tie outcomes and must remain reproducible.

## Decision
Generate neighbors in Up, Right, Down, Left order.

## Consequences
Reference tests and comparison runs can reproduce route choices when other inputs match.

## Status
Proposed — baseline rule.
