# ADR-0010 Preserve map v0.2 resolution

## Context
The existing department map is 127 × 120 cells at 0.10 m/cell. The P1 resolution study can calculate 0.05 m and 0.20 m grid sizes from the legacy builder, but Python is unavailable for measured build times, inflation/connectivity checks, or algorithm expansion benchmarks. The original source photo is also missing.

## Decision
Keep the existing v0.2 map and 0.10 m resolution as the provisional baseline. Do not regenerate or modify the map during P1.

## Consequences
The known 0.9 m openings span about nine cells. A 0.05 m grid would have about four times as many cells; 0.20 m would have one quarter as many but only about 4–5 samples across a 0.9 m door. These are formula-based projections, not runtime measurements. The resolution and geometry remain subject to source-photo review and P2 connectivity tests.

## Status
Proposed — reviewer sign-off pending.
