# Robot model and resource assumptions

The robot is a deterministic software simulation. Its coefficients are provisional assumptions, not measurements or specifications for a commercial appliance. Values are loaded from `docs/map_spec/robot_params.yaml`; the UI may edit them in run configuration. The robot consumes the P2 `GridMap` and its `cell_m`, so movement distance is never configured a second time.

## State and movement

`RobotState` is an immutable value containing position `(row,column)`, optional cardinal heading, battery remaining, elapsed simulation seconds, operational lifetime remaining, status, cleaned-cell count and movement-step count. Cleaning occupancy is kept in a separate `CleaningState.cleaned` boolean array. A route search does not call robot methods; only an executed robot action changes this state.

A move is legal only when the target is one four-neighbor step away, both endpoints are FREE or DOOR, and the robot center is in the footprint-navigable mask for radius `diameter_m / 2`. Movement distance is `grid_map.cell_m` metres. Movement time is `distance / speed_m_per_s`. Optional turning time and energy default to zero.

## Coefficients and units

| Parameter | Default | Unit / meaning |
|---|---:|---|
| `diameter_m` | 0.35 | metres; footprint diameter |
| `cleaning_width_m` | 0.30 | metres; diameter of cleaning disc |
| `speed_m_per_s` | 0.25 | metres per simulation second |
| `battery_capacity_units` | 100 | normalized energy units |
| `lifetime_min` | 30 | minutes; converted to 1,800 seconds internally |
| `move_energy_units_per_step` | 0.05 | normalized units per grid step |
| `clean_energy_units_per_cell` | 0.02 | normalized units per newly cleaned cell |
| `idle_energy_units_per_s` | 0.001 | normalized units per idle second |
| `safety_reserve_units` | 0 | reserved units; no return-to-dock behavior is implemented |
| `turn_energy_units` | 0 | optional units per heading change |
| `turn_time_s` | 0 | optional seconds per heading change |

Optional `move_energy_units_per_m` overrides per-step movement energy. Optional `clean_energy_units_per_s` overrides per-cell cleaning energy and requires positive `cleaning_seconds_per_cell`. With defaults, movement cost is `move_energy_units_per_step`; cleaning cost is charged only for cells not previously cleaned; idle cost is `idle_energy_units_per_s × idle_seconds`.

The default cleaning area is a disc centered on the robot, radius `cleaning_width_m / 2`. Cell centers inside the disc are selected, clipped to FREE/DOOR cells, then newly cleaned cells are marked in row/column order. Re-cleaning costs no energy unless `charge_recleaned_cells` is enabled.

## Atomic resource update

For one move:

`distance_m = grid_map.cell_m`

`move_time_s = distance_m / speed_m_per_s + optional_turn_time`

`energy_units = movement_cost + new_cleaned_cells × clean_energy_units_per_cell + optional_turn_cost`

The robot preflights the complete action before committing position, heading, counters, cleaning marks, battery, elapsed time and remaining lifetime. If the action would exceed either remaining budget, it is rejected without changing `RobotState` or the cleaning layer; the robot object records the stop reason, while the last valid state snapshot remains byte-identical. If both limits are exceeded together, battery depletion takes precedence and both reasons are returned. Exact-budget actions execute and then stop with the corresponding reason. Floating-point tolerance is `1e-12` units/seconds and remaining values clamp to zero.

Battery and lifetime are independent. The battery equation is `remaining = max(0, initial_capacity - energy_used)`. Lifetime is `remaining_seconds = max(0, initial_seconds - elapsed_simulation_seconds)`. Zero initial resources stop the robot immediately. Mission completion, no reachable target, user stop and error are mission-level stop reasons supplied by the simulator.

Safety reserve is recorded as a provisional configuration field defaulting to zero. Return-to-dock or return-to-safe-state behavior is intentionally omitted in v1.0.

## Worked example

At a 0.10 m grid, speed 0.25 m/s and default energy coefficients, one eastward step takes `0.10 / 0.25 = 0.4 s`. A 0.30 m cleaning disc covers nine traversable cell centers in an open area. The action costs `0.05 + 9 × 0.02 = 0.23` units. From the defaults, battery becomes `99.77` units and lifetime becomes `1,799.6` seconds. `tests/robot/test_robot.py` encodes this example.

## Freeze status

P3 robot behavior is implemented against the documented P2 draft interface. The P2 API/map and this robot API remain unfrozen until the required tests run in Python 3.12 and the authorized reviewer signs the applicable freeze statements.
