# ADR-0005 Separate coverage controller

## Context
The required search algorithms are point-to-point planners and do not guarantee full-area coverage.

## Decision
Keep coverage as a separate controller. It selects the next reachable uncleaned cell by Manhattan distance with stable row/column tie-breaking and calls the selected planner.

## Consequences
Coverage policy is identical across algorithm comparisons and reported separately from planner behavior. The policy is a baseline, not a global coverage-optimality claim.

## Status
Proposed — required by the shared project rules.
