# Metric definitions (Freeze point 5)

**Status: Frozen for P8**  
**Date: 2026-11-11**  
Search counters: [`search_counters.md`](search_counters.md). Coverage
denominator: [`coverage_policy.md`](coverage_policy.md). Units and formulas
below are the only definitions used by analytics, UI, CSV, and PDF output.

## 1. Search effort

- **expanded**: count of expanded states per `docs/search_counters.md`.
- **generated**: count of all successor-generation events, duplicates included.
- **repeated_expansions**: expansion count after a state's first expansion in
  that planner call.
- **peak_frontier**: greatest pending frontier-entry count during a call,
  including stale priority entries.
- For a coverage mission, search counters aggregate across planner calls by
  summing expanded, generated, and repeated expansions. `peak_frontier` is the
  maximum of each call's peak, not a sum. Counts are never mixed with robot
  movement actions.

## 2. Route length, cost, and time

- **path_length_steps**: number of legal four-neighbor transitions. For a
  found point-to-point route it equals `len(path) - 1`; for an unfound route it
  is null. Coverage route steps equal executed `MoveExecuted` events.
- **path_length_m**: route steps multiplied by calibrated `cell_m`. All
  v1 routes use cardinal one-cell moves; a non-cardinal movement model would
  require a new metric contract.
- **path_cost**: `SearchResult.path_cost`, the sum of configured transition
  costs along the returned path. The current default unweighted grid charges
  1.0 per transition. With a nonuniform cost layer, report geometric meters
  and accumulated cost separately; never infer one from the other. For a
  coverage mission, aggregate path cost is the sum over successful target
  planner calls. An unsuccessful call has null path cost.
- **search_time_s**: wall-clock duration inside a planner call, reported from
  `SearchResult.execution_time_s`. For coverage, total planner wall time is the
  sum of durations for all target-planning calls. This excludes event polling,
  UI, 2D/3D rendering, animation, PDF/CSV generation, and simulated travel.
- **simulated_travel_time_s**: simulated action time elapsed during mission
  execution, read from `RunStarted` to the terminal `RunStopped` event's
  `t_sim`. It includes configured move, turn, cleaning, and other robot action
  durations; it is not CPU wall time and excludes planner wall time. If a log
  lacks the start or terminal event, this metric is unavailable rather than
  guessed.

## 3. Battery and lifetime

- **battery unit**: the robot model's abstract energy unit. It is not Wh, mAh,
  or a measured appliance quantity. Energy coefficients and initial capacity
  are stored with each run.
- **battery_consumed_units**: configured initial capacity minus final
  `battery_remaining`, clamped to the interval `[0, initial capacity]` to
  absorb floating-point residue.
- **battery_remaining_units**: final robot state value.
- **battery_consumed_percent**: `100 * consumed / initial capacity`; remaining
  percent is `100 * remaining / capacity`. If capacity is zero both percentages
  are null (undefined), while raw energy values remain zero.
- **lifetime**: operational duration in seconds in the engine. Reports include
  seconds and minutes (`minutes = seconds / 60`).
- **lifetime_consumed_s**: configured lifetime minus final remaining lifetime;
  lifetime consumed percent is `100 * consumed / configured lifetime`. If
  configured lifetime is zero, percentage is null.
- Battery and lifetime are independent. The stop reason follows the engine's
  precedence when both limits are reached by one atomic action. These are
  simulated model outputs, not measured real-vacuum performance.

## 4. Coverage

- **raw cleanable set / denominator**: `CleanableCells.cells`, FREE/DOOR cells
  four-neighbor reachable from the start on the uninflated occupancy grid.
  `coverage_denominator_cells = len(cells)`; walls and UNKNOWN are excluded.
- **cleaned numerator**: distinct cells in the robot cleaning layer intersected
  with the raw cleanable set. Re-cleaning a cell does not increase the count.
- **raw_coverage_percent**: `100 * cleaned_raw / raw_denominator`.
- **structurally_uncoverable**: raw cleanable cells no legal centre position
  reachable from the mission start can clean with the configured footprint.
  Report set/count separately. They remain included in raw coverage's
  denominator.
- **achievable set**: raw cleanable set minus structurally-uncoverable cells.
  **achievable_coverage_percent**: `100 * cleaned_achievable /
  achievable_denominator`. This is `CoverageResult.coverage_percent`.
  Planner-specific `unreachable_cells` are reported separately and do not
  change the structural denominator: they describe a planner outcome, not map
  geometry.
- **remaining_cells**: raw cleanable cells not cleaned at termination,
  including structurally-uncoverable cells. Report total and optionally split
  into structurally-uncoverable, planner-unreachable, and other remaining
  cells; sets may overlap only where the engine explicitly reports that fact.
- If a denominator is zero, the engine's current convention reports 100% and
  reports denominator 0 alongside it. Consumers must preserve that convention
  and display the denominator to avoid implying any cells were cleaned.

## Timing protocol and interpretation caveats

For each algorithm/scenario, perform at least five measured repetitions after
one discarded warm-up, using identical map/config/scenario and fixed seeds.
Report median and IQR (`Q3 - Q1`) of planner wall time, plus CPU model, Python
version, and OS. Preserve individual raw runs. If a planner budget stops a run,
record the budget and termination reason; do not compare its partial result as
if it completed.

Always report DFS neighbor-order dependence, Greedy non-optimality, IDDFS
repeated expansions, and that simulated battery is not a real appliance
measurement. Do not state universal algorithm superiority from one metric or
scenario.
