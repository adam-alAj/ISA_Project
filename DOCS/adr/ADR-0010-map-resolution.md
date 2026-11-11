# ADR-0010 Preserve the 0.10 m grid resolution

## Context
The v0.2 department map is 127 × 120 cells at 0.10 m/cell. The P1 resolution study calculated 0.05 m and 0.20 m alternatives. The user accepted 0.10 m provisionally on 2026-11-11. Python is unavailable for measured build times or algorithm expansion benchmarks, and the original source photo remains missing.

## Decision
Preserve v0.2 unchanged and use 0.10 m for the new v0.3 map.

## Consequences
The known 0.9 m openings span about nine cells. A 0.05 m grid would have about four times as many cells; 0.20 m would have one quarter as many but only about 4–5 samples across a 0.9 m door. These are formula-based projections, not runtime measurements. The geometry remains subject to source-photo review and human sign-off.

## Status
Accepted provisionally by the user on 2026-11-11. Map freeze remains pending review/sign-off.
