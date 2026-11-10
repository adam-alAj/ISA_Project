# Prompt 07 — Phase P6: 2D Visualization & Desktop UI

## 1. Role
You are a **Senior PySide6 (Qt for Python) Desktop UI Engineer** with strong UX and concurrency discipline. You build responsive, accessible, testable interfaces that never block the GUI thread and never duplicate domain logic.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. Gate of **P5** must be met (event/snapshot API frozen). P6 may run **in parallel with P7**. UI code lives only in `src/app` and `src/visualization`; domain modules stay UI-free.

## 3. Inputs
Frozen APIs (environment, robot, search, simulation events), SRS §15, FR-20…FR-28, AC-05, Roadmap P6.

## 4. Objective
Make the system operable and understandable through a desktop application. **Exit gate:** a user can complete the main workflow without editing code; the 2D display faithfully reflects simulation state; the UI stays responsive.

## 5. Tasks (ID → concrete instruction)
- **P6.01** Write `docs/ui_design.md`: navigation map of the 8 screens (Project Home, Map Editor, Robot Configuration, Algorithm Setup, 2D Simulation, 3D Simulation launcher, Results Dashboard, Report Export), layout sketches (ASCII), and state diagram of the main workflow.
- **P6.02** `app/main_window.py` with `QMainWindow`, left navigation, stacked pages, status bar (map version, run state); MVC/MVVM split: views never call algorithms directly — they call an `AppController` (signals/slots).
- **P6.03** Project Home: open/recent maps, "Load department map v1", create experiment, project info.
- **P6.04** Map import & calibration page: load image, pick two points + distance, show resulting px/m and residual. (The department map comes from the spec; this page serves the generic workflow and shows the original photo with overlay.)
- **P6.05** Map Editor: zoom/pan (`QGraphicsView` or a Matplotlib canvas with a custom navigator), grid overlay, paint tools for FREE/OCCUPIED/DOOR/UNKNOWN using the P2.05 editing API, undo/redo, validation panel.
- **P6.06** Legend and visual states for wall, free, unknown, door, explored, frontier, route, cleaned, robot, start; **color is never the only cue** (patterns/markers/labels); colorblind-safe palette; HiDPI aware.
- **P6.07** Start-position picker (click a cell; invalid cells rejected with a message) and a validation feedback list that jumps to the offending cells.
- **P6.08** Robot configuration panel for battery, lifetime (independent), speed, diameter, cleaning width, energy coefficients; range validation; presets (Default, Low-battery, Short-lifetime for TS-06/07).
- **P6.09** Algorithm & scenario panel: algorithm dropdown (from `REGISTRY`), heuristic display, neighbor order display (read-only), mode toggle (point-to-point / coverage), policy display.
- **P6.10** Point-to-point goal picker (click on map; use the P1.14 demo goals as quick buttons) and coverage-mode controls.
- **P6.11** Embedded 2D map view (Matplotlib `FigureCanvasQTAgg` with blitting, or `QGraphicsScene`; justify the choice in an ADR with a frame-time measurement on the 127×120 grid).
- **P6.12** Progressive rendering of **explored cells** from trace events (sampled playback; speed slider; skip-to-end).
- **P6.13** Render final path and live robot marker.
- **P6.14** Render cleaned layer and coverage progress bar.
- **P6.15** Controls: Run, Pause, Resume, Step, Reset, Stop, playback speed (0.25×…16×).
- **P6.16** Live HUD: battery (bar + number), elapsed time, lifetime remaining, status, coverage %, current target, steps.
- **P6.17** Messages: validation warnings, "no path" outcome, stop reason banner.
- **P6.18** Run search/simulation in a **worker `QThread`/`QRunnable`** with signals; UI never blocks; rate-limit UI updates (≤30 Hz).
- **P6.19** Cancellation via the P5.14 token; safe teardown on window close; no orphan threads.
- **P6.20** Save/load experiment configuration (JSON) and a recent-runs list reading `data/experiments/`.
- **P6.21** Usability test script `docs/usability_test.md` (5 tasks, success criteria, questionnaire). **HUMAN ACTION** to run with a person unfamiliar with the code.
- **P6.22** Consistency tests: UI-displayed numbers equal engine numbers (use `pytest-qt`, offscreen platform); golden-image test of the map rendering at a fixed size.

## 6. Constraints
- No domain logic in views; no `time.sleep` in the GUI thread; no global mutable state.
- All user-facing strings in one module (easy to translate later; English UI is fine, Arabic optional).
- The app must start and work offline.
- Provide keyboard shortcuts for Run/Pause/Step/Reset.

## 7. Deliverables
`src/app/*`, `src/visualization/two_d/*`, `tests/ui/*` (pytest-qt, offscreen), `docs/ui_design.md`, `docs/usability_test.md`, screenshots in `docs/img/`.

## 8. Acceptance gate (report pass/fail each)
- [ ] End-to-end manual script: load map → set start → configure robot → choose algorithm → run → see explored/route/cleaned → stop reason shown (include screenshots).
- [ ] UI thread stays responsive (measured max frame/event latency < 100 ms during a coverage run).
- [ ] Displayed metrics equal engine metrics (automated test).
- [ ] Cancel/close leaves no running thread.
- [ ] Legend present; state distinguishable without color.

## 9. Output
Use the report format from Shared Context §8.5. Attach screenshots of each screen.
