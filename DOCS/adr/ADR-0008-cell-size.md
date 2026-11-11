# ADR-0008 Cell size

## Context
The existing map metadata records a 0.10 m cell size and P0 must preserve the supplied map.

## Decision
Use 0.10 m as the current map baseline. The user accepted this provisionally on 2026-11-11; revisit only if a conflict appears.

## Consequences
All distance and robot-footprint calculations must use the metadata value and the 4-neighbor model. Any change requires a new map version and impact review.

## Status
Accepted provisionally by the user on 2026-11-11. Map review/sign-off is still pending.
