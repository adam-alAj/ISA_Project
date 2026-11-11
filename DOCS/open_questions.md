# Open questions and recorded decisions

**Decision update date: 2026-11-11.** User answers below are authoritative for project work. Items still marked HUMAN ACTION remain open and must not block unrelated implementation.

## Decisions received

| Item | Decision | Status |
|---|---|---|
| Room areas | Preserve `R7 > R1 > R4 > R6 > {R2,R3,R5,R8}`; the four smaller rooms target about 2.6 mÂ² within Â±5%. R7b is part of R7 and excluded from this comparison. Change only outer room sides; preserve the hall, doors, obstacles, and start. | Applied to v0.3; regression tests added. Independent raster checks reproduced successfully; pytest awaits a Python runtime. |
| 4.8 m and 2 m labels | Informational only; do not use them for calibration or geometry. Confirm against the photo later. | Accepted as a non-blocking working decision. |
| Calibration | Use confirmed dimensions only: 5 m east hall wall, 6 m lower span, door widths, column, and cabinet dimensions. | Applied in the v0.3 calibration notes. |
| Door policy | All doors are permanently open passages in v1.0. | Approved 2026-11-11. |
| Demo goals | Default start is S. The around-column alternate start is allowed only as a named scenario variant in configuration. | Provisionally approved; recorded in `docs/map_spec/demo_config.yaml`. |
| Robot parameters | Values in `robot_params.yaml` are provisional simulation assumptions and must be editable from the UI. | Provisionally approved 2026-11-11. |
| Python and grid | Python 3.12 and 0.10 m cell size remain provisional choices. | Accepted 2026-11-11. |
| Algorithm name | Use canonical ID `iddfs` and alias `idfs` for Iterative Deepening DFS. | Working assumption until instructor reply; registry added. Do not freeze terminology. |
| Map version | Preserve v0.2 and produce adjusted geometry as v0.3. | Applied; v0.3 is not frozen pending human sign-off. |

## Remaining human actions

| Question/action | Owner | Status |
|---|---|---|
| Send the instructor message and record replies about algorithms, grading rubric, submission format, demo format, and backup recording. | Team lead `<TBD>` | HUMAN ACTION â€” open, non-blocking; IDDFS working assumption is recorded. |
| Assign team member names, communication channel, and decision owner. | Team | HUMAN ACTION â€” keep names `<TBD>`; non-blocking for independent work. |
| Copy `WhatsApp_Image_2026-11-10_at_4_27_44_PM.jpeg` into `assets/floor_plans/`. | User/map owner | HUMAN ACTION â€” file not present yet. P1.01/P1.02 remain blocked on this file; other work continues. |
| Check the informational 4.8 m and 2 m labels against the photo. | User/map owner | HUMAN ACTION â€” low priority, non-blocking; not used in calibration or geometry. |
| Review and sign the map checklist and freeze statement. | Authorized reviewer `<TBD>` | HUMAN ACTION â€” required before freeze; does not block P2 work under the stated assumptions. |

## Instructor message ready to send

Hello, we are confirming the project requirements before implementation. The working six algorithms are BFS, DFS, UCS, Greedy Best-First, A*, and Iterative Deepening DFS (canonical ID `iddfs`, alias `idfs`). Please confirm that â€œIDFSâ€ means IDDFS/IDS. Could you also clarify the grading rubric, required submission format/files, live-demo expectations, and whether a backup recording is accepted? We will use your answer to freeze terminology and final submission/demo scope. Thank you.

## Freeze rule

The department map remains **unfrozen** until the v0.3 geometry and regression checks are complete, the review checklist is ready, and an authorized reviewer signs the freeze statement. Regression tests are written; independent raster checks are reproduced, while pytest awaits a Python runtime. Algorithm terminology and final submission/demo scope also remain provisional until the instructor replies. Unanswered HUMAN ACTION items do not block unrelated implementation.

