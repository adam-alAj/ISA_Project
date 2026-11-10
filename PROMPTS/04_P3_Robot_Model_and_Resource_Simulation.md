# Prompt 04 — Phase P3: Robot Model & Resource Simulation

## 1. Role
You are a **Robotics Simulation Engineer** specialized in discrete-event/step simulation, resource models (energy/time) and state machines. You value atomic state transitions, invariants and exhaustive unit tests.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. P2 gate must be met (environment API frozen). P3 may run **in parallel with P4** after agreeing shared data structures (coordinates = `(row, col)` tuples; costs = `float`).

## 3. Inputs
Frozen environment API (`GridMap`, `neighbors`, inflation, cleaning state), `docs/map_spec/robot_params.yaml`, SRS §9.

## 4. Objective
Implement the simulated vacuum cleaner **independently of any UI**. **Exit gate:** robot state updates are deterministic and internally consistent; battery and lifetime stop independently; no invalid move is accepted; robot interface frozen.

## 5. Tasks (ID → concrete instruction)
- **P3.01** `robot/state.py`: `RobotState` (position, heading, battery, elapsed_time, lifetime_remaining, status, cleaned_count, step_count) as an immutable dataclass; mutation via `replace`. Cleaned-cell set lives in the environment layer, referenced by the simulator.
- **P3.02** `robot/config.py`: `RobotConfig` (all SRS §9.2 parameters) with defaults from `robot_params.yaml`, YAML/JSON load, and validation (positive values, cleaning width ≤ a sane maximum).
- **P3.03** Independent fields `battery_capacity` and `operational_lifetime`; each has its own remaining value and its own depletion check.
- **P3.04** Movement duration: `cell_length_m / speed`; `Δt` per step; turning cost optional (off by default).
- **P3.05** Movement energy per step (default) or per meter; documented unit conversion.
- **P3.06** Cleaning energy per newly cleaned cell (default) or per second; no energy for re-cleaning an already clean cell unless configured.
- **P3.07** Optional idle energy: `idle_rate × idle_time` (default 0).
- **P3.08** Battery remaining `= max(0, initial − used)`; never negative; floating-point tolerance policy documented.
- **P3.09** Elapsed time and lifetime countdown updated by every action, using the same clock.
- **P3.10** `robot/footprint.py`: robot centre must lie in the footprint-navigable mask; collision check by disc of `diameter/2`; clearance report for a candidate cell.
- **P3.11** `validate_move(state, target)`: adjacent, traversable, within footprint rules; returns a typed result with reason codes.
- **P3.12** `Robot.step(target) -> StepResult`: one **atomic** transition that updates position, time, energy and cleaned cells together or not at all (compute new state first, commit after all checks).
- **P3.13** Cleaning action: cells covered = disc of `cleaning_width/2` around the robot centre (clipped to traversable cells); returns the *newly* cleaned set.
- **P3.14** Stop conditions enum + evaluation after each action: `MISSION_COMPLETE, BATTERY_DEPLETED, LIFETIME_EXPIRED, NO_REACHABLE_TARGET, USER_STOP, ERROR` (the last four may be raised by the simulator; the robot exposes `check_limits()`).
- **P3.15** Mid-route limit policy: if a step would exceed battery or lifetime, **do not execute it**; stop in the last valid state with the correct reason; if both would be exceeded in the same step, report the one defined by the documented precedence (battery first) and log both.
- **P3.16** Safety reserve / return-to-safe-state: **explicitly omitted** in v1.0; implement only a config flag `safety_reserve_units` defaulting to 0, and document that no return-to-dock logic exists.
- **P3.17** `reset()` and `snapshot()/restore()` (deep copy of state + cleaned layer) for replay and tests.
- **P3.18** Unit tests: battery-only exhaustion (TS-06), lifetime-only expiry (TS-07), both limits, exact-boundary cases (energy == remaining), zero battery, zero lifetime.
- **P3.19** Tests: moves into wall/UNKNOWN/out-of-bounds rejected; non-adjacent move rejected; narrow passage (< diameter) rejected; door passes with 0.9 m; cabinet protrusion leaves enough clearance.
- **P3.20** `docs/robot_model.md`: units, equations, default coefficients, every assumption, and an explicit statement that values are simulation outputs, not measurements of a real appliance.

## 6. Constraints
- No dependency on search algorithms or UI. No randomness.
- State transitions are pure/atomic; invalid actions never corrupt state.
- Energy/time use the same `cell_length_m` as the map metadata (no duplicated constants).

## 7. Deliverables
`src/robot/*`, `tests/robot/*`, `docs/robot_model.md`, ADR "Robot API freeze (Freeze point 2)".

## 8. Acceptance gate (report pass/fail each)
- [ ] Battery and lifetime limits trigger independently and together; reasons are correct.
- [ ] Property test: 10,000 random legal/illegal move attempts never produce an inconsistent state or a wall crossing.
- [ ] Atomicity test: a rejected step leaves state byte-identical.
- [ ] Model documentation lists all coefficients and units.

## 9. Output
Use the report format from Shared Context §8.5. Include a worked numeric example (steps → energy/time) verified by a test.
