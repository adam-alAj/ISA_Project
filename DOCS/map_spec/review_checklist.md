# Department map review checklist

Review the original untouched floor-plan drawing alongside the v0.3 draft preview and annotated overlay. Mark each item after checking it against the source. Do not sign off unresolved image or label questions as verified.

## Drawing and scale

- [ ] Source photo is present, unchanged, and SHA-256 is recorded.
- [ ] Photo orientation, dimensions, page boundary, readability, logos, and watermarks are recorded.
- [ ] Simulated boundary includes the open hall, entrance, R1â€“R8, and inner room R7b; excluded outside areas are clear.
- [ ] Confirmed calibration dimensions (5 m, 6 m, 0.9/1.2 m doors, 0.5 m column, and 75/60 cm cabinets) match the source; 4.8 m and 2 m are informational only.
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
- [ ] Corrected room areas follow R7 > R1 > R4 > R6 > {R2,R3,R5,R8}; equal group is within 2.6 m² ±5%.
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
- [ ] C1 column obstacle location and 0.5 Ã— 0.5 m dimensions.
- [ ] CB1 upper cabinet width and 10 cm protrusion.
- [ ] CB2 entrance cabinet width and 10 cm protrusion.
- [ ] Start point S is at cell (118,54) and corresponds to the intended floor location.

## Traversability and operating assumptions

- [ ] All nine doors are intended to be permanently open passages in v1.0.
- [ ] Wall boundaries are closed except at the nine modeled door openings.
- [ ] No cleaning exclusion zones are present in v0.3; the former hatched zone is removed.
- [ ] `UNKNOWN` is not traversable; `CLEANED` is maintained as a separate boolean layer.
- [ ] No `UNKNOWN` cells are present in the v0.3 grid (state reserved for later review workflows).
- [ ] The 0.10 m grid and 0.35 m robot diameter provide acceptable clearance at the narrowest passage.
- [ ] Review demo goals: straight_line, around_column (scenario variant), deepest_room, top_room_R2, top_room_R3, top_room_R1, long_diagonal_R4, west_room_R8, unreachable_synthetic. Default start is S.
- [ ] Provisional robot assumptions remain editable from the UI and are not real-appliance specifications.

## Sign-off

Reviewer name / role: ______________________________

Decision:  [ ] Approved  [ ] Approved with changes  [ ] Rejected

Changes / conditions: ______________________________________________________

Signature: ______________________________  Date: __________________________

