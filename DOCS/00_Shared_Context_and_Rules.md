# 00 — Shared Context & Rules (paste BEFORE every phase prompt)

> **How to use this prompt pack**
> 1. Start a fresh session with your AI coding agent (Claude Code recommended; any agent with file + shell access works).
> 2. Paste **this file first**, then paste **one phase prompt** (`01_…` to `11_…`). Execute phases in numeric order; P3 ∥ P4 and P6 ∥ P7 may run in parallel once their freeze points are met.
> 3. Before starting a phase, the agent must verify the **exit gate of the previous phase** (listed inside each prompt). If the gate is not met, stop and report.
> 4. Items marked **HUMAN ACTION** cannot be done by the agent (instructor approval, physical testing, team decisions). The agent must produce the material needed for the human (checklist, draft, question list) and continue with what it can do.

---

## 1. Project in one paragraph
**Smart Vacuum Cleaner — Intelligent Search, Navigation & 3D Simulation** (course: *Intelligence Systems*). A Python desktop **simulation** (not a physical robot) that converts a hand-drawn floor plan of a university department into an occupancy grid, simulates a vacuum robot with **independent battery capacity and operational lifetime**, runs **six search algorithms** (BFS, DFS, UCS, Greedy Best-First, A*, IDFS/IDDFS) on identical scenarios, visualizes exploration/movement/cleaning in **2D and 3D**, and produces metrics, comparison charts and PDF/CSV reports. Baseline documents: `Smart_Vacuum_Intelligent_Search_SRS.docx` (SRS v1.0) and `Smart_Vacuum_Project_Roadmap.docx` (Roadmap v1.0) — both are in the project files and are the **requirements authority**.

## 2. Non-negotiable rules (violating any of these = defect)
1. **Search ≠ movement.** Search expansion never moves the robot and never consumes battery/time. Only executing the *returned route* changes robot state.
2. **Search ≠ coverage.** The six algorithms are *point-to-point route planners*. Full-floor cleaning is done by a separate **Coverage Controller** that repeatedly picks the next uncleaned reachable target and calls the selected planner. Never claim that BFS/DFS/UCS/Greedy/A*/IDDFS alone guarantee coverage.
3. **Determinism.** Neighbor order is fixed: **Up, Right, Down, Left**. Tie-breaking is deterministic and documented. Same inputs ⇒ same outputs (except wall-clock time).
4. **Fair comparison.** Same map version, start, goal/target policy, movement model, cost model, heuristic and neighbor order across all algorithms.
5. **Occupancy ≠ cleaning state.** Store them in separate arrays. Cleaning never changes traversability.
6. **Robot never enters OCCUPIED or UNKNOWN cells; never crosses a wall; never teleports.** If a resource limit hits mid-route, stop at the last valid cell.
7. **Battery and operational lifetime are independent limits**; a run ends when either is reached first, and the termination reason is recorded.
8. **Movement model:** 4-directional only (no diagonals) in v1.0.
9. **Heuristic:** Manhattan distance × minimum step cost (admissible & consistent for the 4-neighbor model; must stay a lower bound if costs vary).
10. **Metrics must be defined once and used everywhere** (see P8). Search execution time excludes UI, 3D rendering and animation delays.
11. **Simulated values are model outputs**, not measurements of a real appliance. State units and coefficients in every report.
12. **Human-assisted digitization** of the map must be described honestly as such (no claim of automatic floor-plan recognition).
13. Core workflow must run **offline** on **Windows 10/11**, Python **3.11 or 3.12**.
14. 2D and 3D visualizers consume the **same simulation events/snapshots**; neither re-implements movement logic.

## 3. Current state of the map (already produced — do NOT redo from scratch)
Files delivered by the previous work session (place them in the repo as shown in §5):
`build_map.py` (traced-geometry → grid builder, v0.2), `department_map.npy` (grid), `department_map.json` (metadata), `map_preview.png` (preview), and the original hand-drawn photo (preserve untouched in `assets/floor_plans/`).

| Item | Value |
|---|---|
| Source | Hand-drawn paper plan, **fake/demo data**, department only |
| Grid | **127 rows × 120 cols**, **cell = 0.10 m**, row = y (down), col = x (right) |
| Cell states | `FREE=0, OCCUPIED=1, UNKNOWN=2, DOOR=3` (UNKNOWN is kept in the schema but unused in v0.2) |
| Geometry origin | photo pixel (80,160); scale `PPM = 108 px/m`; drawn wall ≈ 12 px (~0.11 m) |
| Robot diameter (assumption) | 0.35 m → inflation radius 2 cells |
| Validation result v0.2 | 10,176 free/door cells, all reachable from start; all 9 rooms reachable also with footprint inflation (8,435 cells navigable for the robot centre) |
| Start | cell stored in `department_map.json → start_cell` (the "S" in the drawing, bottom open area) |

**Layout decisions already confirmed by the user (authoritative):**
- One large **open hall** (empty space) — **no left corridor, no inner wall, no opening-line**. The robot can and must pass through it.
- Right wall of the hall containing the doors of R4 and R5 is kept at **5 m**. (The handwritten "3.6 m" label is *not* used.)
- The former "4.5 m + 1.4 m" measures are merged into **6 m**: from the R6 corner to the bottom edge of the map.
- The orange/hatched area was a misreading and is **removed**.
- Doors are **0.9 m**, except R1 (Head of Dept) = **1.2 m**. R8 door = 0.9 m.
- One **column** (“شمعة”) 0.5 m × 0.5 m inside the hall.
- Two **cabinets** on the left wall: widths **75 cm** and **60 cm**, each protruding **10 cm** from the wall.
- Rooms (8 + 1 inner room): R1 Head of Dept (Dr. Anas) · R2 Dr. Rawan · R3 Dr. Mohammad Abu Ayyash · R4 Dr. Shereen + Dr. Nader (one shared room) · R5 Dr. Mohammad Ghattas · R6 Johnny (department admin office) · R7 Dr. Suhail (largest room) **with inner room R7b** · R8 "Mutaghayyir" office. Size order: R7 > R1 > R4 > R6 > the rest (equal).
- Use ASCII room IDs (`R1…R8`, `R7b`) in code; Arabic names only in display metadata (RTL rendering caveat).

## 4. Key requirement anchors (from SRS v1.0)
- **FR-01…FR-28**, **NFR-01…NFR-12**, **AC-01…AC-09**, test scenarios **TS-01…TS-09** (straight corridor, wall detour, disconnected goal, unequal costs, heuristic trap, battery exhaustion, lifetime expiry, coverage completion, partial coverage).
- Energy model: `energy = steps × move_energy + cleaned_cells × clean_energy + idle_time × idle_rate`; `battery = max(0, initial − energy)`; `move_time = distance / speed`.
- Stop reasons (enum): `MISSION_COMPLETE, BATTERY_DEPLETED, LIFETIME_EXPIRED, NO_REACHABLE_TARGET, USER_STOP, ERROR`.
- Coverage % = cleaned reachable cleanable cells ÷ reachable cleanable cells × 100 (walls/unknown excluded; denominator stated in every report).
- Coverage target policy (baseline): nearest uncleaned reachable cell by Manhattan distance, stable tie-break (row, then col); identical for all six algorithms.
- Common search interface returns: path, found, expanded, generated, peak frontier, path cost, execution time, termination reason (+ optional trace).
- "IDFS" in the course = **Iterative Deepening DFS (IDDFS/IDS)** — pending instructor confirmation (P0 HUMAN ACTION).

## 5. Repository layout (SRS §6.1)
```
smart_vacuum_ai/
├── assets/floor_plans/        # original photo (never edited)
├── data/{maps,experiments}/
├── src/{app,map_processing,environment,robot,algorithms,coverage,simulation,visualization,analytics,reporting}/
├── tests/   reports/   docs/  (docs/adr/ for ADRs)
├── requirements.txt (or pyproject.toml)   README.md   main.py
```

## 6. Engineering conventions
- Python 3.11/3.12, full type hints, `dataclass(frozen=True)` for value objects, docstrings (Google style), `pathlib`, no hidden globals, no randomness without a seed.
- Layered: algorithms/environment/robot/simulation are **UI-free** and import nothing from PySide6/Ursina/Matplotlib.
- `pytest` for everything; each task that adds behaviour adds/updates a test. Optional `ruff`.
- Logging via `logging` (no bare `print` in library code). Errors are explicit exceptions with clear messages.
- Pin dependency versions only after smoke-testing them (P0).

## 7. Interface freeze points
After **P2** environment API · after **P3** robot/stop-condition API · after **P4** `SearchResult` + trace-event format · after **P5** simulation event/snapshot API · before **P8** metric definitions + run-record schema. After a freeze, changes require an ADR entry and a note of impacted tests.

## 8. Mandatory working protocol for the agent (every phase)
1. **Read first:** the SRS, Roadmap, this file, the phase prompt, and the existing repo. Summarize in ≤10 lines what already exists and what is missing.
2. **Plan:** list the tasks you will do in order, flag dependencies, assumptions and any **HUMAN ACTION**. Ask at most the minimum blocking questions; otherwise make a documented assumption (record it as an ADR) and proceed.
3. **Implement incrementally:** small commits, tests alongside code, run the test suite after each task.
4. **Verify:** run the phase's acceptance checks; paste real command output (not claims).
5. **Report** using this format: `✅ Done tasks (IDs)` · `⚠️ Partial/Deferred (IDs + reason)` · `🧑 HUMAN ACTIONS` · `📁 Files created/changed` · `🧪 Test results` · `📌 Assumptions & ADRs` · `➡️ Gate status (pass/fail per criterion)`.
6. Never mark a task done without an observable outcome (merged code, passing test, generated file, reviewed document).
7. Do not silently drop a MUST requirement. If something must change, record: reason, affected FR/NFR, impact on tests, approval needed.
