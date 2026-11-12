# P6 automated gate results

Date: 2026-11-11  
Map: `data/maps/department_v1`, version 1.0-draft, 127 × 120, 0.10 m/cell  
Display: PySide6 offscreen (headless execution).

## Environment

```text
> .\.venv\Scripts\python.exe --version
Python 3.12.10
> .\.venv\Scripts\python.exe -m pytest --version
pytest 9.2.0
> .\.venv\Scripts\python.exe -c "import PySide6; from PySide6.QtCore import qVersion; print('PySide6',PySide6.__version__,'Qt',qVersion())"
PySide6 6.12.0 Qt 6.12.0
```

## Gate checklist

| # | Check | Result | Evidence |
|---:|---|---|---|
| 1 | Scripted end-to-end workflow on real `MainWindow`: load map, start, robot, BFS, point-to-point, coverage, overlays and stop banner | PASS | `tests/ui/test_p6_gate.py::test_scripted_p6_end_to_end_workflow_and_screenshots`; ten screenshots in `docs/img/p6_e2e/` |
| 2 | UI numbers equal engine numbers: battery, elapsed, lifetime, coverage, steps, stop reason | PASS | `test_p6_dashboard_numbers_match_engine_state` and end-to-end coverage assertions; integers/enums exact, rendered floats within half of their last displayed decimal (battery/time/lifetime <0.0005; coverage <0.005 percentage points) |
| 3 | Department coverage responsiveness through terminal state | PASS | Default configuration, ended `battery_depleted`: 6.149 s, 130 UI refreshes, 21.14 Hz, maximum heartbeat gap 23.97 ms; targets <100 ms and ≤30 Hz |
| 4 | Cancel and close leave no live worker | PASS | `test_p6_cancel_and_close_leaves_no_worker_thread`; active run cancelled, window closed, QThread stopped, no 3D QProcess running |
| 5 | Legend and non-color state cues | PASS | `test_p6_legend_covers_every_state_and_map_states_have_texture`; ten legend entries and patterned FREE/OCCUPIED/UNKNOWN/DOOR cells |
| 6 | Experiment save/load and recent runs | PASS | `tests/ui/test_desktop_ui.py::test_experiment_config_round_trip_and_recent_run_list` |

### Commands and outputs

```text
> $env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest tests\ui\test_p6_gate.py -q -s
5 passed in 9.36s
department_coverage_elapsed_s=6.859; ui_updates=146; ui_update_rate_hz=21.29; max_gui_timer_gap_ms=20.92; stop_reason=battery_depleted

> $env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest tests\ui\test_p6_gate.py::test_p6_department_coverage_responsiveness_through_terminal_stop -q -s
department_coverage_elapsed_s=6.149; ui_updates=130; ui_update_rate_hz=21.14; max_gui_timer_gap_ms=23.97; stop_reason=battery_depleted
1 passed in 6.35s

> .\.venv\Scripts\python.exe -m pytest tests\ui\test_desktop_ui.py::test_experiment_config_round_trip_and_recent_run_list -q
. [100%]
1 passed in 0.33s

> $env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest tests\ui -q -s
............ [100%]
12 passed in 10.25s
ui_timer_samples=16; max_event_interval_ms=35.69

> $env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest -q
............................................................................... [100%]
87 passed in 58.50s
```

## P6 gate status

**PASS — automated criteria verified; usability session deferred to P9.16**

The human usability session is not represented as having run. It is deferred
and scheduled for P9.16. Checklist and blank results table:
`docs/p6_manual_check.md`.
