#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
REPORT="$ROOT/reports/qa/p5_gate_result.md"
mkdir -p "$ROOT/reports/qa"
if [[ -x "$ROOT/.venv/bin/python" ]]; then PY="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then PY="$(command -v python)"
else PY=""; fi
{
  echo '# P5 gate results'
  echo
  echo "Generated: $(date --iso-8601=seconds 2>/dev/null || date)"
  echo
  echo 'Gate status: **pending evidence** until every check below has a passing command result.'
  echo
  if [[ -n "$PY" ]]; then echo "Interpreter: `$PY $($PY --version 2>&1)`"; else echo 'Interpreter: **not found** (searched repo .venv, PATH python3, PATH python).'; fi
  echo
} > "$REPORT"
run_check() {
  name="$1"; shift
  echo "## $name" | tee -a "$REPORT"
  echo | tee -a "$REPORT"
  if [[ -n "$PY" ]]; then
    echo "Command: `$PY $*`" | tee -a "$REPORT"
    echo | tee -a "$REPORT"
    echo '```text' | tee -a "$REPORT"
    output=$("$PY" "$@" 2>&1); result=$?
    printf '%s\n' "$output" | tee -a "$REPORT"
    if [[ "$name" == 'Department-map coverage metrics and memory bound' ]]; then DEPARTMENT_OUTPUT="$output"; fi
    echo '```' | tee -a "$REPORT"
    if [[ $result -eq 0 ]]; then echo '**PASS**' | tee -a "$REPORT"; else echo '**FAIL**' | tee -a "$REPORT"; FAIL=1; fi
  else
    echo "Command: `python $*` (not run: no interpreter available)." | tee -a "$REPORT"
    echo | tee -a "$REPORT"
    echo '```text' | tee -a "$REPORT"
    echo 'FAIL: NOT RUN — no interpreter is installed or discoverable.' | tee -a "$REPORT"
    echo '```' | tee -a "$REPORT"
    echo '**FAIL**' | tee -a "$REPORT"
    FAIL=1
  fi
  echo | tee -a "$REPORT"
}
FAIL=0
DEPARTMENT_OUTPUT=''
run_check 'Python dependency smoke test' scripts/smoke_test.py
run_check 'Full repository test suite' -m pytest -q
run_check 'TS-08/TS-09 for six algorithms' -m pytest -q tests/coverage/test_p5_gate.py::test_ts08_ts09_full_and_constrained_coverage_for_each_algorithm
run_check '100 seeded movement invariants' -m pytest -q tests/coverage/test_p5_gate.py::test_invariant_100_seeded_scenarios
run_check 'Planning state immutability for six algorithms' -m pytest -q tests/coverage/test_p5_gate.py::test_planning_preserves_robot_snapshot_for_each_algorithm
run_check 'Event replay equivalence and schema version' -m pytest -q tests/coverage/test_p5_gate.py::test_event_replay_equivalence_and_schema_version
run_check 'Long action stream memory bound' -m pytest -s -q tests/coverage/test_p5_gate.py::test_long_action_stream_has_bounded_event_and_snapshot_memory
run_check 'Department-map coverage metrics and memory bound' -m pytest -s -q tests/coverage/test_p5_gate.py::test_department_headless_runs_report_metrics_and_bounded_memory
{
  echo '## Department-map coverage table'
  echo
  echo '| Algorithm | Coverage % | Steps | Energy | Sim time (s) | Stop reason | Planner wall time (s) | Run wall time (s) |'
  echo '|---|---:|---:|---:|---:|---|---:|'
  for name in bfs dfs ucs greedy astar iddfs; do
    row=$(printf '%s\n' "$DEPARTMENT_OUTPUT" | awk -F, -v alg="$name" '$1==alg {print $0; exit}')
    if [[ -n "$row" ]]; then IFS=, read -r alg cov steps energy sim stop planner runwall <<< "$row"; echo "| $alg | $cov | $steps | $energy | $sim | $stop | $planner | $runwall |"
    else echo "| $name | NOT RUN | NOT RUN | NOT RUN | NOT RUN | pending evidence | NOT RUN | NOT RUN |"; fi
  done
  echo
} >> "$REPORT"
if [[ $FAIL -eq 0 ]]; then sed -i 's/Gate status: \*\*pending evidence\*\*.*/Gate status: **PASS** — all recorded checks exited successfully./' "$REPORT"; else sed -i 's/Gate status: \*\*pending evidence\*\*.*/Gate status: **pending evidence** — one or more checks failed or could not run./' "$REPORT"; fi
exit "$FAIL"
