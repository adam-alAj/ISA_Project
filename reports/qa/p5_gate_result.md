# P5 gate results

Generated: 2026-11-11 13:49:22 +02:00

Gate status: **PASS** - all recorded checks exited successfully.

Interpreter: `C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe ` - Python 3.12.10

## Python dependency smoke test

Command: `& "C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe" scripts/smoke_test.py`

```text
PASS PySide6 QApplication (offscreen)
PASS opencv-python image operation
PASS numpy operation
PASS shapely geometry
PASS matplotlib PNG output
PASS pandas DataFrame
PASS reportlab one-page PDF
PASS ursina import
PASS python-docx import
PASS networkx graph
PASS pytest import
PASS ruff import
VERSION PySide6 6.12.0
VERSION opencv-python 5.0.0.93
VERSION numpy 2.5.4
VERSION shapely 2.2.0
VERSION matplotlib 3.11.2
VERSION pandas 3.1.1
VERSION ursina 8.3.0
VERSION reportlab 5.1.0
VERSION python-docx 1.2.0
VERSION networkx 3.7
VERSION pytest 9.2.0
VERSION ruff 0.17.4
RESULT 12/12 checks passed
```

**PASS**

## Full repository test suite

Command: `& "C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe" -m pytest -q`

```text
...............................................................          [100%]
63 passed in 175.27s (0:02:55)
```

**PASS**

## TS-08/TS-09 for six algorithms

Command: `& "C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe" -m pytest -q tests/coverage/test_p5_gate.py::test_ts08_ts09_full_and_constrained_coverage_for_each_algorithm`

```text
......                                                                   [100%]
6 passed in 0.28s
```

**PASS**

## 100 seeded movement invariants

Command: `& "C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe" -m pytest -q tests/coverage/test_p5_gate.py::test_invariant_100_seeded_scenarios`

```text
.                                                                        [100%]
1 passed in 0.22s
```

**PASS**

## Planning state immutability for six algorithms

Command: `& "C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe" -m pytest -q tests/coverage/test_p5_gate.py::test_planning_preserves_robot_snapshot_for_each_algorithm`

```text
.                                                                        [100%]
1 passed in 0.33s
```

**PASS**

## Event replay equivalence and schema version

Command: `& "C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe" -m pytest -q tests/coverage/test_p5_gate.py::test_event_replay_equivalence_and_schema_version`

```text
.                                                                        [100%]
1 passed in 0.34s
```

**PASS**

## Long action stream memory bound

Command: `& "C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe" -m pytest -s -q tests/coverage/test_p5_gate.py::test_long_action_stream_has_bounded_event_and_snapshot_memory`

```text
long_action_peak_bytes=202003; retained_events=256; retained_snapshots=8
.
1 passed in 2.13s
```

**PASS**

## Department-map coverage metrics and memory bound

Command: `& "C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe" -m pytest -s -q tests/coverage/test_p5_gate.py::test_department_headless_runs_report_metrics_and_bounded_memory`

```text
algorithm,coverage_pct,steps,energy,sim_time_s,stop_reason,planner_wall_s,run_wall_s
bfs,3.2995194874532836,100,11.17999999999995,39.99999999999992,error,0.03421470010653138,6.956126400036737
dfs,3.2995194874532836,100,11.17999999999995,39.99999999999992,error,0.0200642995769158,6.979385599959642
ucs,3.2995194874532836,100,11.17999999999995,39.99999999999992,error,0.02923710027243942,5.079194699996151
greedy,3.2995194874532836,100,11.17999999999995,39.99999999999992,error,0.016318000154569745,4.878425900009461
astar,3.2995194874532836,100,11.17999999999995,39.99999999999992,error,0.02238939970266074,7.144460199982859
iddfs,3.2995194874532836,100,11.17999999999995,39.99999999999992,error,0.06537670048419386,7.172254599980079
department_run_note=50 target-iteration guard; per-search budget 2000 expansions or 0.5 seconds; partial result
tracemalloc_peak_bytes=8198989
.
1 passed in 58.42s
```

**PASS**

## Department-map coverage table

| Algorithm | Coverage % | Steps | Energy | Sim time (s) | Stop reason | Planner wall time (s) | Run wall time (s) |
|---|---:|---:|---:|---:|---|---:|
| bfs | 3.2995194874532836 | 100 | 11.17999999999995 | 39.99999999999992 | error | 0.03421470010653138 | 6.956126400036737 |
| dfs | 3.2995194874532836 | 100 | 11.17999999999995 | 39.99999999999992 | error | 0.0200642995769158 | 6.979385599959642 |
| ucs | 3.2995194874532836 | 100 | 11.17999999999995 | 39.99999999999992 | error | 0.02923710027243942 | 5.079194699996151 |
| greedy | 3.2995194874532836 | 100 | 11.17999999999995 | 39.99999999999992 | error | 0.016318000154569745 | 4.878425900009461 |
| astar | 3.2995194874532836 | 100 | 11.17999999999995 | 39.99999999999992 | error | 0.02238939970266074 | 7.144460199982859 |
| iddfs | 3.2995194874532836 | 100 | 11.17999999999995 | 39.99999999999992 | error | 0.06537670048419386 | 7.172254599980079 |

