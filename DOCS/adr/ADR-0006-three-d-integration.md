# ADR-0006 3D integration mode

## Context
PySide6 is the desktop shell and Ursina may conflict with embedding or share event-loop constraints.

## Decision
Prototype Ursina as a separate process controlled from the PySide6 window using JSON-lines over QProcess stdin/stdout. Treat separate synchronized windows as the provisional mode pending ten-cycle measurement.

## Consequences
The process boundary isolates event loops and crashes, but requires explicit message handling and synchronization. Do not call the integration stable until measured on the target laptop.

## Status
Proposed — feasibility measurement pending.
