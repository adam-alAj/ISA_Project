# Prompt 02 — Phase P1: Floor-Plan Inspection & Digital Map Design

## 1. Role
You are a **Systems Analyst and Floor-Plan Digitization Specialist** (architectural drawings → machine-readable spatial specifications). You are rigorous about units, scale, ambiguity and traceability between a drawing and a model, and you never invent geometry that the drawing does not support.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. **P1 is largely already done in practice**: a v0.2 map exists and the user has confirmed its layout decisions (Shared Context §3). Your job is to **formalize, verify and freeze** the map specification — not to redraw the map. Gate of P0 must be met (repo skeleton exists).

## 3. Inputs
Original photo of the hand-drawn plan (`assets/floor_plans/`), `data/maps/department_v0_2/*`, `src/map_processing/legacy_build_map.py`, SRS §8–9 and Appendix A.

## 4. Objective
Turn the drawing into an **unambiguous map specification** that a reviewer can check against the drawing. **Exit gate:** a reviewer can identify every simulated traversable and blocked region on the annotated drawing; scale assumptions are explicit; unresolved questions are listed.

## 5. Tasks (ID → concrete instruction)
- **P1.01** Verify the untouched source copy exists with a SHA-256 recorded in `docs/map_spec/source_manifest.md`; never edit it.
- **P1.02** Inspect and record image metadata (format, resolution, orientation/EXIF, page size, readability issues such as logos/watermarks on the sheet) in the manifest.
- **P1.03** Define the simulated boundary: hall + entrance + all room interiors R1…R8, R7b. List what is outside (area beyond the photo, logos).
- **P1.04** Build the **dimension inventory table** (`docs/map_spec/dimensions.csv`): every written dimension (10 m, 4.8 m, 5 m wall, 6 m, 2 m, 0.9 m doors, 1.2 m door, column 0.5 m, cabinets 75 cm/60 cm, 10 cm protrusion) with `value, unit, where, used_in_model (yes/no), note`. Mark the obsolete labels (3.6 m, 4.5 m, 1.4 m, 10 m corridor) as *superseded by user decisions* with the reason.
- **P1.05** Produce the **element register** (`docs/map_spec/elements.yaml`): rooms, doors, walls, column, cabinets, start — each with ID, geometry (from the traced pixel rectangles in the builder), metric size, and drawing reference.
- **P1.06** Door policy: all doors are **permanently open passages** in v1.0 (state it; closed/conditional doors are future work).
- **P1.07** Exclusions: record that no zones are excluded from cleaning in v0.2 (the hatched area was a misreading), and that cabinets/column are fixed obstacles.
- **P1.08** Consistency check: compare drawn vs stated dimensions (e.g., pixel-derived 5 m vs written labels), report deviations in % in `docs/map_spec/consistency_report.md`; flag any deviation >15 % for human review.
- **P1.09** Calibration method: documented as `PPM = 108 px/m` derived from several labelled dimensions; list which labels were used and the residuals. Fallback rule: if a future map has no scale, use abstract grid units and label reports accordingly.
- **P1.10** Resolution study: evaluate cell sizes 0.05 / 0.10 / 0.20 m using the existing builder: grid size, build time, narrowest passage in cells, effect of robot inflation, projected search cost. Recommend **0.10 m** (confirm or justify a change) in `docs/map_spec/resolution_study.md` with a table.
- **P1.11** Movement model: 4-neighbor, U/R/D/L, no diagonals; document diagonal extension as future work with the extra collision/cost rules needed.
- **P1.12** State schema: `FREE=0, OCCUPIED=1, UNKNOWN=2, DOOR=3`; `CLEANED` is a **separate boolean layer** (not a cell state in the occupancy array). Document the rule "UNKNOWN is never traversable".
- **P1.13** Door representation: doors are carved across wall thickness (≥2 cells) so no accidental gaps exist; add a check list "wall closed except doors".
- **P1.14** Start and goals: confirm the start cell "S"; define **demo goals** for point-to-point experiments (propose ≥6, covering: straight line, around the column, into R7b (deepest room), into R2/R3 (top rooms), long diagonal-ish route, unreachable-by-design test on a synthetic map). Provide cell coordinates computed from the grid.
- **P1.15** Parameter sheet `docs/map_spec/robot_params.yaml` with *provisional* values: diameter 0.35 m, cleaning width 0.30 m, speed 0.25 m/s, battery 100 units, lifetime 30 min, move energy 0.05 units/step(0.1 m), clean energy 0.02 units/cell, idle 0.001 units/s. Mark every value `provisional: true` with rationale.
- **P1.16** Produce an **annotated overlay** `docs/map_spec/annotated_plan.png`: the grid preview with element IDs, door IDs, dimensions and start (use Matplotlib; Arabic labels not required).
- **P1.17** Create `docs/map_spec/review_checklist.md` for the team/instructor review (one checkbox per element + a signature line). **HUMAN ACTION** to review.
- **P1.18** Create `docs/map_spec/unresolved.md` listing remaining assumptions (room sizes derived from drawing proportions; robot size assumed; instructor expectations) and a "freeze statement" to sign off. **HUMAN ACTION** to approve freeze.

## 6. Constraints
- Do not alter geometry unless a user-confirmed decision requires it; any change goes through an ADR.
- Distinguish **measured/labelled** values from **estimated-from-proportion** values everywhere.
- No new libraries beyond the P0 stack.

## 7. Deliverables
`docs/map_spec/` containing: source manifest, dimensions.csv, elements.yaml, consistency report, resolution study, robot_params.yaml, annotated_plan.png, review checklist, unresolved list; updated ADR log.

## 8. Acceptance gate (report pass/fail each)
- [ ] Every cell class in the grid maps back to a documented element.
- [ ] All written dimensions are either used or explicitly marked superseded.
- [ ] Cell size decision backed by a numeric table.
- [ ] Parameter sheet complete and marked provisional.
- [ ] Review checklist + freeze statement ready for human sign-off.

## 9. Output
Use the report format from Shared Context §8.5.
