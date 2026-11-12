> Historical P6 report. Visualization scope was subsequently removed under ADR-0022; references below to the renderer describe pre-removal evidence only.

# P6 implementation and gate status

Date: 2026-11-11  
Map: department v1, 127 × 120, 0.10 m/cell  
Automated environment: Python 3.12.10, pytest 9.2.0, PySide6 6.12.0, Qt 6.12.0, `QT_QPA_PLATFORM=offscreen`.

## Automated acceptance evidence

| Criterion | Status | Evidence |
|---|---|---|
| Scripted workflow: load department map, select start, configure robot, choose BFS, point-to-point, coverage, overlays and stop banner | PASS | `tests/ui/test_p6_gate.py::test_scripted_p6_end_to_end_workflow_and_screenshots`; ten ordered screenshots in `docs/img/p6_e2e/` |
| UI values match engine: battery, elapsed time, lifetime, coverage, steps, stop reason | PASS | `test_p6_dashboard_numbers_match_engine_state` checks point-to-point display against robot/search values; scripted coverage workflow checks engine coverage, steps and stop reason against dashboard. Exact steps/reason; displayed floats rounded to 0.001 (absolute display tolerance <0.0005), coverage to 0.01 percentage points (<0.005) |
| Responsiveness during a complete department-map coverage attempt | PASS | Default robot config ran to `battery_depleted`: 6.149 s, 130 UI updates (21.14 Hz), max 10 ms heartbeat gap 23.97 ms. Targets: <100 ms and ≤30 Hz |
| Cancel and close leave no worker thread | PASS | `test_p6_cancel_and_close_leaves_no_worker_thread`; cancels active run, closes window, waits for the simulation worker, and asserts the QThread has stopped |
| Legend includes all ten states; occupancy has non-color patterns | PASS | `test_p6_legend_covers_every_state_and_map_states_have_texture`; FREE dots, OCCUPIED crosshatch, UNKNOWN diagonal hatch, DOOR stripe; overlay/marker symbols appear in legend |
| Experiment JSON save/load and recent-runs list | PASS | `tests/ui/test_desktop_ui.py::test_experiment_config_round_trip_and_recent_run_list` |

## Commands and observed outputs

```text
> .\.venv\Scripts\python.exe --version
Python 3.12.10

> .\.venv\Scripts\python.exe -m pytest --version
pytest 9.2.0

> .\.venv\Scripts\python.exe -c "import PySide6; from PySide6.QtCore import qVersion; print('PySide6',PySide6.__version__,'Qt',qVersion())"
PySide6 6.12.0 Qt 6.12.0

> $env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest tests\ui\test_p6_gate.py -q -s
5 passed in 9.36s
department_coverage_elapsed_s=6.859; ui_updates=146; ui_update_rate_hz=21.29; max_gui_timer_gap_ms=20.92; stop_reason=battery_depleted

> .\.venv\Scripts\python.exe -m pytest tests\ui\test_desktop_ui.py::test_experiment_config_round_trip_and_recent_run_list -q
1 passed in 0.33s

> $env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest tests\ui -q -s
12 passed in 10.25s
ui_timer_samples=16; max_event_interval_ms=35.69

> $env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest -q
............................................................................... [100%]
87 passed in 58.50s
```

Latest responsiveness measurement (same current code):

```text
> $env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest tests\ui\test_p6_gate.py::test_p6_department_coverage_responsiveness_through_terminal_stop -q -s
department_coverage_elapsed_s=6.149; ui_updates=130; ui_update_rate_hz=21.14; max_gui_timer_gap_ms=23.97; stop_reason=battery_depleted
1 passed in 6.35s
```

## Remaining items and P8 impact

| Remaining item | Severity/status | Blocks P8? | Reason |
|---|---|---|---|
| Human usability session | Deferred — HUMAN ACTION to P9.16 | No | P8 consumes engine/event records; manual usability feedback is a P9.16 input |
| Calibration residual with one reference segment | Low; known limitation | No | A numeric residual requires a second independent calibration reference; this does not affect simulation records |
| Playback slider changes presentation refresh cadence, not simulation execution pacing | Medium; known limitation | No | Timing metrics are measured inside the planner and from simulation events; presentation pacing is not an input |
| Some user-facing strings remain inline | Low; maintainability | No | Localization polish does not affect engine or persisted result values |
| Former 3D renderer displayed its HUD without world geometry | Removed by descoping under ADR-0022 | N/A | The retained 2D workflow consumes the frozen engine/event data; AC-06 remains pending instructor acknowledgement |

P6.21 is **deferred — HUMAN ACTION**, scheduled for P9.16. Use
`docs/p6_manual_check.md` and record participant outcomes there.

## Gate status

**PASS — automated criteria verified; usability session deferred to P9.16**
