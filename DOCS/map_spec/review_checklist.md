# Department map review checklist

Review the original untouched floor-plan drawing alongside the v0.2 preview and annotated overlay. Mark each item after checking it against the source. Do not sign off unresolved image or label questions as verified.

## Drawing and scale

- [ ] Source photo is present, unchanged, and SHA-256 is recorded.
- [ ] Photo orientation, dimensions, page boundary, readability, logos, and watermarks are recorded.
- [ ] Simulated boundary includes the open hall, entrance, R1–R8, and inner room R7b; excluded outside areas are clear.
- [ ] Calibration labels 4.8 m, 2 m, and 5 m are matched to the intended drawing segments; residuals are acceptable.
- [ ] Superseded 10 m corridor, 3.6 m, 4.5 m, and 1.4 m labels are visibly understood.

## Room and element geometry

- [ ] R1 Head of Department room outline.
- [ ] R2 room outline.
- [ ] R3 room outline.
- [ ] R4 shared room outline.
- [ ] R5 room outline.
- [ ] R6 room outline.
- [ ] R7 room outline.
- [ ] R7b inner room outline.
- [ ] R8 room outline.
- [ ] Traced room areas agree with the confirmed room-size order, especially R4 versus R6.
- [ ] D1 (R1, 1.2 m) opening.
- [ ] D2 (R2, 0.9 m) opening.
- [ ] D3 (R3, 0.9 m) opening.
- [ ] D4 (R4, 0.9 m) opening.
- [ ] D5 (R5, 0.9 m) opening.
- [ ] D6 (R6, 0.9 m) opening.
- [ ] D7 (R7, 0.9 m) opening.
- [ ] D8 (R7b, 0.9 m) opening.
- [ ] D9 (R8, 0.9 m) opening.
- [ ] HALL_TOP walkable zone.
- [ ] HALL_LOW walkable zone.
- [ ] ENTRANCE walkable zone.
- [ ] W_HALL_EAST wall segment.
- [ ] W_R7B_DIVIDER wall segment.
- [ ] W_R1_N north wall.
- [ ] W_R1_S south wall.
- [ ] W_R1_W west wall.
- [ ] W_R1_E east wall.
- [ ] W_R2_N north wall.
- [ ] W_R2_S south wall.
- [ ] W_R2_W west wall.
- [ ] W_R2_E east wall.
- [ ] W_R3_N north wall.
- [ ] W_R3_S south wall.
- [ ] W_R3_W west wall.
- [ ] W_R3_E east wall.
- [ ] W_R4_N north wall.
- [ ] W_R4_S south wall.
- [ ] W_R4_W west wall.
- [ ] W_R4_E east wall.
- [ ] W_R5_N north wall.
- [ ] W_R5_S south wall.
- [ ] W_R5_W west wall.
- [ ] W_R5_E east wall.
- [ ] W_R6_N north wall.
- [ ] W_R6_S south wall.
- [ ] W_R6_W west wall.
- [ ] W_R6_E east wall.
- [ ] W_R7_N north wall.
- [ ] W_R7_S south wall.
- [ ] W_R7_W west wall.
- [ ] W_R7_E east wall.
- [ ] W_R7b_N north wall.
- [ ] W_R7b_S south wall.
- [ ] W_R7b_W west wall.
- [ ] W_R7b_E east wall.
- [ ] W_R8_N north wall.
- [ ] W_R8_S south wall.
- [ ] W_R8_W west wall.
- [ ] W_R8_E east wall.
- [ ] Raster OCCUPIED exterior/untraced complement is appropriate.
- [ ] C1 column obstacle location and 0.5 × 0.5 m dimensions.
- [ ] CB1 upper cabinet width and 10 cm protrusion.
- [ ] CB2 entrance cabinet width and 10 cm protrusion.
- [ ] Start point S is at cell (118,54) and corresponds to the intended floor location.

## Traversability and operating assumptions

- [ ] All nine doors are intended to be permanently open passages in v1.0.
- [ ] Wall boundaries are closed except at the nine modeled door openings.
- [ ] No cleaning exclusion zones are present in v0.2; the former hatched zone is removed.
- [ ] `UNKNOWN` is not traversable; `CLEANED` is maintained as a separate boolean layer.
- [ ] No `UNKNOWN` cells are present in the v0.2 grid (state reserved for later review workflows).
- [ ] The 0.10 m grid and 0.35 m robot diameter provide acceptable clearance at the narrowest passage.
- [ ] Proposed demo goals are appropriate and safe to use for comparisons.
- [ ] Provisional robot parameters are acceptable for demonstration or updated with rationale.

## Sign-off

Reviewer name / role: ______________________________

Decision:  [ ] Approved  [ ] Approved with changes  [ ] Rejected

Changes / conditions: ______________________________________________________

Signature: ______________________________  Date: __________________________
