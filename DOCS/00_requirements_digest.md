# Requirements digest

## Purpose and scope

The project is an offline educational desktop simulation for converting a human-reviewed floor plan into an occupancy grid, planning routes with six classical search algorithms, executing those routes with an independently constrained simulated vacuum robot, visualizing the run in 2D, and reporting comparable results. It is not a physical robot controller. Coverage is a separate controller that repeatedly selects reachable uncleaned targets and calls one of the point-to-point planners.

The first complete release includes image import and calibration, editable/validated occupancy maps, BFS/DFS/UCS/Greedy/A*/IDFS (pending instructor interpretation), robot battery and lifetime constraints, collision-safe movement, repeatable search and coverage runs, 2D visualization, analytics, and reports. The department map must be treated as human-assisted digitization and its assumptions labeled.

## Priority counts

| Requirement set | MUST | SHOULD | COULD | Total |
|---|---:|---:|---:|---:|
| Functional requirements FR-01–FR-28 | 22 | 5 | 1 | 28 |
| Non-functional requirements NFR-01–NFR-12 | 7* | 5* | 0 | 12 |
| Acceptance criteria AC-01–AC-09 | 9* | 0 | 0 | 9 |

*The SRS gives explicit MUST/SHOULD/COULD labels only for FRs. NFR and AC priorities above are a working P0 classification inferred from “shall” versus “should” wording; confirm during team review. The detailed rows are in `traceability_matrix.csv`.

## Out of scope for v1

- Physical vacuum control, proprietary firmware, real-time sensing, SLAM, lidar, or camera localization.
- Dynamic people/furniture and moving obstacles.
- Multiple robots, charging stations, and automatic recharging.
- Guaranteed globally optimal coverage for arbitrary floor-plan geometry.
- Unverified automatic architectural interpretation of arbitrary drawings.

## Top risks

| Risk | Why it matters | Initial response |
|---|---|---|
| Ambiguous or incomplete source drawing | A wrong map invalidates paths and measurements. | Preserve the source; manually trace, annotate, and request review. |
| Map scale or grid resolution mismatch | Narrow passages may become impassable or unsafe. | Verify calibration and robot footprint against the narrowest opening. |
| Missing instructor decisions | IDFS meaning and grading expectations can change scope. | Send the questions in `open_questions.md` and record answers. |
| Removed optional 3D visualization | The original requirement is not included in the retained 2D product scope. | ADR-0022 and `SRS_v1.1_deviations.md` record the pending instructor acknowledgement; AC-06 is not passed. |
| Search coupled to movement or UI | Metrics become unfair and tests become difficult. | Keep search headless; execute only the returned route. |
| Coverage misrepresented as pathfinding | Claims about algorithm guarantees become incorrect. | Use an independent coverage controller and state the denominator. |
| Non-deterministic tie handling | Repeated comparisons can disagree. | Fix U,R,D,L neighbor order and all tie-breaks. |
| Arbitrary battery and lifetime coefficients | Resource outcomes may look authoritative without evidence. | Expose and label model assumptions in every run report. |
| Unbounded traces or animation snapshots | Large maps can exhaust memory or freeze the UI. | Bound retained event/frame data and benchmark on the agreed map. |

## Baseline invariants

Search expansion does not move the robot or consume resources. Occupancy and cleaning state remain separate. The robot cannot enter occupied/unknown cells or cross blocked transitions. Battery and operating lifetime stop a run independently. Four-neighbor movement, deterministic U,R,D,L order, and Manhattan heuristic are the baseline. Reports distinguish measured runtime from simulated energy/time and state assumptions.
