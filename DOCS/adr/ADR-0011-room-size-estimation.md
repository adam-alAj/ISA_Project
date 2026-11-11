# ADR-0011 Estimate room sizes from proportions and confirmed ordering

## Context
The v0.2 traced rectangles conflict with the user's confirmed room-size order: traced R6 is larger than R4. No original drawing photo is present, and room dimensions are not independently measured. The user confirmed the ordering and target areas on 2026-11-11.

## Decision
Treat room areas as estimates from drawing proportions constrained by the confirmed order `R7 > R1 > R4 > R6 > {R2,R3,R5,R8}`. Exclude R7b from that comparison because it is part of R7. Keep R1 and R7 unchanged; adjust only the outer sides of R4, R5, and R6. Keep the equal-group rooms within Â±5% of 2.6 mÂ². Create map version v0.3 and preserve v0.2 unchanged.

## Consequences
R4 becomes approximately 4.715 mÂ², R6 approximately 3.827 mÂ², and R5 approximately 2.607 mÂ². R2, R3, and R8 remain within the same Â±5% group. Hall zones, door rectangles, column, cabinets, and S must stay unchanged; a regression test compares hall/door cells between v0.2 and v0.3. Reachability is checked with and without the 0.35 m footprint. These are modeled estimates, not surveyed measurements. Do not freeze v0.3 until checks pass and a reviewer signs the freeze statement.

## Status
Geometry decision approved by the user on 2026-11-11; geometry applied to v0.3; regression tests added and independent raster checks reproduced. Python test execution and reviewer freeze sign-off remain pending.

