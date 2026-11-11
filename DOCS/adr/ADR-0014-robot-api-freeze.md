# ADR-0014 Robot API freeze point 2

## Context

The robot model consumes `GridMap`, its `cell_m`, footprint masks and separate cleaning state. The P2 environment API has been implemented but remains a draft because Python validation, source-photo review and the P1 freeze signature are outstanding. P3 is proceeding against that documented contract under the user's instruction to continue later work without blocking on HUMAN ACTION items.

## Decision

Define the provisional robot contract with immutable `RobotState`, typed movement validation, atomic step/clean/idle actions, independent battery and operational lifetime budgets, radius-based footprint checks, separate cleaning state, and snapshots for replay. Battery depletion takes precedence when one action exceeds or exactly exhausts both limits; the result also reports both reasons.

Robot parameters stay provisional and UI-editable. Safety reserve defaults to zero, and no return-to-dock logic is included. Simulation coefficients are not real-appliance measurements.

## Consequences

Movement consumes `grid_map.cell_m / speed_m_per_s` seconds and the configured per-step or per-metre energy. Cleaning marks cell centers within the configured cleaning-width disc and charges only newly cleaned cells by default. An action that cannot fit within either remaining resource budget is rejected without changing the state or cleaned layer.

## Status

Draft only; P3 tests are written but not executable in the current workspace because Python is unavailable. Do not freeze the robot API until tests pass and the upstream P2 API/freeze review is resolved.
