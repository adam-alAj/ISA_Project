# Prompt 06 — Phase P5: Coverage Controller & Simulation Engine

## 1. Role
You are a **Simulation Architect and Coverage-Planning Engineer**. You integrate independent components (environment, robot, planners) through clean interfaces and event streams, and you are meticulous about separating *planning*, *execution* and *policy*.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. Gates of **P3 and P4** must be met. This phase defines the **simulation event/snapshot API** that the 2D visualizer will consume (Freeze point 4).

## 3. Inputs
`GridMap`, `Robot`, `REGISTRY` of algorithms, `SearchResult`, SRS §9–§11, Roadmap P5.

## 4. Objective
Connect search results to actual movement and floor cleaning. **Exit gate:** point-to-point and coverage modes are clearly separated; robot movement follows legal paths; stopping and coverage outcomes are correct; event/snapshot interface frozen.

## 5. Tasks (ID → concrete instruction)
- **P5.01** `simulation/modes.py`: `PointToPointMission(start, goal)` and `CoverageMission(policy)` as separate types; shared `SimulationEngine` but no mixed logic.
- **P5.02** `coverage/cleanable.py`: define **cleanable cells** = `FREE`/`DOOR` cells reachable from start on the raw grid. Define the **coverage denominator** = |cleanable cells|. Record an explicit ADR for the footprint subtlety: the robot *centre* is restricted by inflation, but cleaning footprint may clean cells the centre cannot occupy; report `structurally_uncoverable` (cells no reachable centre position can clean) separately and exclude them from the *achievable* coverage figure while still showing the raw figure.
- **P5.03** `coverage/target_policy.py`: baseline policy = nearest uncleaned **cleanable** cell by Manhattan distance from the current position; ties by `(row, col)`. Interface `TargetPolicy.next_target(state, cleaned) -> cell | None` so alternative policies can be added later. Performance note: use a spatial index / incremental structure so each call is not O(N²) on ~10k cells.
- **P5.04** Enforce identical policy objects/config across all algorithm runs (policy is part of the experiment config and hashed into the run id).
- **P5.05** `coverage/controller.py`: loop — select target → call planner → execute route → update cleaning → check limits → repeat; stop when complete, no target, or limit. Max-iteration guard.
- **P5.06** Target with no route: mark as `unreachable_for_planner`, exclude from further selection, log event, continue.
- **P5.07** Disconnected regions / inaccessible cleanable cells reported in the final result (`remaining_cells`, `unreachable_cells`).
- **P5.08** `simulation/executor.py`: executes the route **one action at a time** through `Robot.step`; never bypasses validation.
- **P5.09** Guarantee (and test) that planning calls change **neither** robot state nor battery/time (compare snapshots before/after search).
- **P5.10** After each action update position, battery, lifetime, cleaning layer via the robot API; emit one event per action.
- **P5.11** Check stop conditions **after every action**; honour precedence rules from P3.15.
- **P5.12** Pre-action affordability check: do not start a step that cannot be completed under the configured policy (no partial steps).
- **P5.13** Event log (`simulation/events.py`, JSON-serializable, versioned schema): `RunStarted, SearchStarted, SearchFinished, TargetSelected, MoveExecuted, CellsCleaned, ResourceUpdated, TargetUnreachable, RunStopped(reason)`; each with `t_sim`, `seq`, payload.
- **P5.14** Pause / resume / reset / cancel at **safe action boundaries** (engine as a generator or a stepper with `run_until(stop_flag)`); thread-safe cancellation token (needed by the UI in P6.18).
- **P5.15** `SimulationSnapshot` (robot state, cleaned-layer reference or delta, current path, explored cells of the *latest* search, coverage %) emitted at a configurable cadence; memory bounded (NFR-11: ring buffer / delta encoding, no unbounded frame lists).
- **P5.16** On early termination compute partial coverage and the list/count of remaining uncleaned cells.
- **P5.17** End-to-end tests on tiny synthetic maps (headless).
- **P5.18** Full coverage with generous resources (TS-08) and partial coverage with constrained resources (TS-09) for **each of the six algorithms**.
- **P5.19** Integrated stop tests: mission complete, battery depleted (TS-06), lifetime expired (TS-07).
- **P5.20** Global invariant test: across all runs, **no executed position is OCCUPIED/UNKNOWN and every consecutive pair is adjacent**.
- Extra: run one coverage mission per algorithm on the real department map in a headless script and record wall-clock time; if any run is impractically slow, add the node/time budgets from P4 and document the effect (e.g., IDDFS/DFS path lengths inflate energy use — this is an expected academic finding, not a bug).

## 6. Constraints
- Search time is measured only around the planner call and reported separately from simulated travel time.
- The coverage controller must not contain algorithm-specific branches.
- Do not implement any UI; emit events only.

## 7. Deliverables
`src/coverage/*`, `src/simulation/*`, `tests/coverage/*`, `tests/simulation/*`, `docs/coverage_policy.md` (why coverage ≠ pathfinding, denominator, uncoverable cells), ADR "Simulation event/snapshot freeze (Freeze point 4)".

## 8. Acceptance gate (report pass/fail each)
- [ ] TS-08 and TS-09 pass for all six algorithms.
- [ ] Invariant test (no illegal cell, adjacency) passes on ≥100 seeded scenarios.
- [ ] Planning leaves robot state untouched (test).
- [ ] Event log schema versioned and replay of the log reproduces the final state exactly.
- [ ] Memory stays bounded on a long coverage run.

## 9. Output
Use the report format from Shared Context §8.5. Include one table: per algorithm — coverage %, steps, energy, sim time, stop reason, planner wall time (department map, default config).
