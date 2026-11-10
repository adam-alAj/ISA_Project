# ADR-0008 Cell size

## Context
The existing map metadata records a 0.10 m cell size and P0 must preserve the supplied map.

## Decision
Use 0.10 m as the current map baseline. Treat it as provisional until the map source and narrowest passage are reviewed.

## Consequences
All distance and robot-footprint calculations must use the metadata value and the 4-neighbor model. Any change requires a new map version and impact review.

## Status
Proposed — inherited from map v0.2.
