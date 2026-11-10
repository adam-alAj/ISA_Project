# ADR-0002 Four-neighbor movement

## Context
The initial grid needs safe, simple transitions and transparent distance and energy accounting.

## Decision
Use four-directional movement only in v1.0. Diagonal movement is out of scope unless collision and cost rules are approved.

## Consequences
No diagonal corner cutting; Manhattan distance is the baseline heuristic. Tests and map connectivity use the same transition model.

## Status
Proposed — aligns with shared project rules.
