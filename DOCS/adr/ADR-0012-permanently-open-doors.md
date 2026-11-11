# ADR-0012 Permanently open doors

## Context
The v0.2 map encodes nine door openings as traversable `DOOR` cells; the system does not model door state.

## Decision
Model all doors as permanently open passages in v1.0. The user approved this policy on 2026-11-11. Closed and conditional doors remain future work.

## Consequences
All nine door rectangles remain fixed while room outer dimensions change. Tests compare the v0.2 and v0.3 door-cell sets and confirm every room remains reachable. No dynamic door-state logic is implied.

## Status
Approved by the user on 2026-11-11.
