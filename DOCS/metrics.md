# Frozen metric definitions (Freeze point 5)

**Status: Frozen for P8.** Version 1.0; frozen 2026-11-12. These definitions are
the sole metric contract for extraction, run records, comparisons, CSV files,
and reports. The search-counter definitions and goal-test order are specified
in [`search_counters.md`](search_counters.md). Changing a formula requires an
ADR and updates to the affected extraction, golden-result, and report tests.

All metrics describe the simulation model. Search is planning only: a planner
does not move the robot or consume simulated battery, lifetime, or travel time.
Coverage execution calls a planner repeatedly and then executes returned routes.

## 1. Search counters

The following values are copied from `SearchResult` for point-to-point runs and
summed across `SearchFinished` events for coverage missions, except
`peak_frontier`, which is the maximum across planner calls:

- **expanded**: number of states removed from the active frontier whose
  successors are generated. Goal testing precedes expansion, so a popped goal
  does not count. IDDFS nodes at the depth cutoff do not count as expanded.
- **generated**: number of successor states produced during expansion,
  including duplicates, previously discovered states, and successors later
  rejected by duplicate or depth-dominance rules. The initial state is not
  generated. IDDFS successors produced for cutoff detection count.
- **repeated_expansions**: expansions after the first expansion of the same
  state during one planner call. IDDFS repeats across depth iterations count;
  A* re-expansions after a strictly better path cost count when re-expanded.
  Repeated generation without expansion does not count.
- **peak_frontier**: maximum pending frontier entries during one planner call,
  including stale priority-queue entries until popped. For coverage, report the
  maximum over all calls, not their sum.

Counter semantics, invalid endpoints, start-equals-goal, budgets, trace, and
stable neighbor/tie ordering follow the frozen search-counter contract.

## 2. Distance, cost, and time

- **path_length_steps**: number of cardinal transitions in the returned route;
  `null` when no route is returned. A start-equals-goal route has zero steps.
- **path_length_m**: `path_length_steps × cell_m`. This assumes one grid-cell
  cardinal move per step. For a coverage mission, steps are executed
  `MoveExecuted` events and distance is executed steps times `cell_m`.
- **path_cost**: planner-reported sum of transition costs along the returned
  route, in the configured model's cost units. It is `null` when no route was
  returned. It is not inferred from distance. Reports must show both distance
  and cost when the configured transition-cost model makes them different.
  Coverage path cost is the sum of costs for successful planner calls.
- **search_time_s**: point-to-point `SearchResult.execution_time_s`; for
  coverage, sum of planner-only durations from `SearchFinished` events
  (`planner_execution_time_s`, with the legacy `wall_time_s` fallback). It
  excludes UI, rendering, event playback, animation, and robot movement.
- **simulated_travel_time_s**: elapsed simulation clock between `RunStarted`
  and `RunStopped` (or the last event when no stop event exists). This includes
  simulated movement, cleaning, and modeled waits; it is not wall-clock time.

The timing protocol measures only planner invocation duration, discards one
warm-up call, uses a fixed seed, and reports at least five measured repetitions
as median and inclusive-quartile IQR (`Q3 − Q1`). Machine CPU, Python, and OS
are recorded with each timing batch. Single-run elapsed values are not
substitutes for repeated timing summaries.

## 3. Battery and operational lifetime

- **Energy** is expressed in the robot configuration's abstract energy units.
  Consumed energy is `max(0, initial_capacity − final_remaining)`; remaining
  energy is recorded in the same units. Percent values divide by the configured
  initial capacity and multiply by 100. A zero or absent capacity yields
  `null` percent, not a divide-by-zero value.
- **Operational lifetime** is recorded in seconds. Minutes are derived exactly
  as seconds divided by 60. Consumed and remaining percentages use configured
  initial lifetime as the denominator. A zero or absent lifetime yields `null`
  percent.
- Energy capacity and operational lifetime are separate limits. The first
  limit reached determines termination. Energy coefficients and speed are
  simulation assumptions; simulated battery values are not measurements of a
  real appliance.

## 4. Coverage

Coverage is defined for coverage missions only. A **raw cleanable cell** is a
traversable map cell reachable from the mission start in the uninflated
four-neighbor occupancy grid. Occupied and unknown cells are excluded.
`coverage_denominator_cells` is the count of these cells, and
`coverage_numerator_cells` is the number of those cells marked cleaned.
`raw_coverage_percent = 100 × numerator / denominator`. A zero denominator is
reported as 100% by the coverage controller's vacuous-completion convention.

A raw cleanable cell is **structurally uncoverable** if no legal robot-center
cell reachable from the start can place the robot's cleaning footprint over
it. Those cells remain in the raw denominator to preserve the P5.02 raw
coverage definition. `achievable_coverage_percent` excludes structurally
uncoverable cells from both numerator and denominator:

`100 × cleaned achievable cells / achievable cleanable cells`.

The empty achievable set is reported as 100% (there are no achievable cells
left to clean). Cells unreachable by an individual planner call are tracked as
`unreachable_cells`; they are not silently removed from either denominator.
The remaining-cell count is reported separately. Coverage percentages must be
accompanied by numerator and denominator counts in reports so a percentage is
interpretable.

## 5. Repeated runs and comparisons

Run identity is SHA-256 over canonical JSON containing the map hash, complete
experiment configuration, algorithm, policy, and seed. Wall-clock creation
time and measured search duration are metadata and do not change identity.
Records retain raw search results, event-log digest and count, map, settings,
and derived metrics so reports can be regenerated without rerunning a planner.

Cross-algorithm comparisons require identical map hash, robot configuration,
target policy, neighbor order, cost model, heuristic, start, goal, seed,
movement model, search budgets, and mission mode. Point-to-point planning and
coverage missions are separate comparison populations and must never share a
table or chart. A comparison timing summary reports the median and inclusive
IQR over the retained measured repetitions.

## 6. Reproducibility and limitations

CSV exports contain raw per-run metrics, use UTF-8 with BOM, and preserve null
values as empty fields. PDF and CSV renderers consume stored run records; they
do not recalculate metrics or invoke the simulation. Search timing is
machine-dependent. A single map and scenario cannot establish general
algorithm performance. DFS depends on neighbor order, Greedy Best-First is not
guaranteed to return an optimal path, IDDFS may repeat expansions, and
simulated battery output does not predict a physical vacuum's battery life.
