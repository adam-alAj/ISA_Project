# P5 gate results

Generated: 2026-11-11 03:35:45 +02:00

Gate status: **pending evidence** - one or more checks failed or could not run.

Interpreter: **not found** (searched repo .venv, PATH python, PATH py).

## Python dependency smoke test

Command: `python scripts/smoke_test.py`

```text
FAIL: NOT RUN — no interpreter is installed or discoverable.
```

**FAIL**

## Full repository test suite

Command: `python -m pytest -q`

```text
FAIL: NOT RUN — no interpreter is installed or discoverable.
```

**FAIL**

## TS-08/TS-09 for six algorithms

Command: `python -m pytest -q tests/coverage/test_p5_gate.py::test_ts08_ts09_full_and_constrained_coverage_for_each_algorithm`

```text
FAIL: NOT RUN — no interpreter is installed or discoverable.
```

**FAIL**

## 100 seeded movement invariants

Command: `python -m pytest -q tests/coverage/test_p5_gate.py::test_invariant_100_seeded_scenarios`

```text
FAIL: NOT RUN — no interpreter is installed or discoverable.
```

**FAIL**

## Planning state immutability for six algorithms

Command: `python -m pytest -q tests/coverage/test_p5_gate.py::test_planning_preserves_robot_snapshot_for_each_algorithm`

```text
FAIL: NOT RUN — no interpreter is installed or discoverable.
```

**FAIL**

## Event replay equivalence and schema version

Command: `python -m pytest -q tests/coverage/test_p5_gate.py::test_event_replay_equivalence_and_schema_version`

```text
FAIL: NOT RUN — no interpreter is installed or discoverable.
```

**FAIL**

## Department-map coverage metrics and memory bound

Command: `python -s -m pytest -q tests/coverage/test_p5_gate.py::test_department_headless_runs_report_metrics_and_bounded_memory`

```text
FAIL: NOT RUN — no interpreter is installed or discoverable.
```

**FAIL**

## Department-map coverage table

| Algorithm | Coverage % | Steps | Energy | Sim time (s) | Stop reason | Planner wall time (s) |
|---|---:|---:|---:|---:|---|---:|
| bfs | NOT RUN | NOT RUN | NOT RUN | NOT RUN | pending evidence | NOT RUN |
| dfs | NOT RUN | NOT RUN | NOT RUN | NOT RUN | pending evidence | NOT RUN |
| ucs | NOT RUN | NOT RUN | NOT RUN | NOT RUN | pending evidence | NOT RUN |
| greedy | NOT RUN | NOT RUN | NOT RUN | NOT RUN | pending evidence | NOT RUN |
| astar | NOT RUN | NOT RUN | NOT RUN | NOT RUN | pending evidence | NOT RUN |
| iddfs | NOT RUN | NOT RUN | NOT RUN | NOT RUN | pending evidence | NOT RUN |

