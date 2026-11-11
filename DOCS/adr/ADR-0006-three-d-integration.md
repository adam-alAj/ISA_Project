# ADR-0006: 3D integration mode

## Context

PySide6 is the desktop shell and Ursina/Panda3D owns a separate render and
input loop. Embedding it would couple the render loop and GUI lifecycle. The
P0.15 feasibility prototype and P7 measured implementation are in
`prototypes/ui_3d_feasibility/` and `scripts/three_d_self_test.py`.

## Decision

Use Ursina as a separate process, launched and supervised by the Qt app through
`QProcess`. Exchange schema-versioned JSON Lines over stdin/stdout. The process
renders the map and plays the same simulation events/snapshots as the 2D app;
it does not make simulation decisions.

## Evidence

On the development PC on 2026-11-11, the current worker completed 10/10
startup/close cycles (0.826–1.147 seconds to ready, exit code 0); raw output is
`prototypes/ui_3d_feasibility/cycle_results.csv`. The real scene self-test
loaded the department map, replayed 14 moves, reported 106 entities (89
static), and sampled about 58–60 FPS. Its framebuffer capture currently
contains only the Ursina HUD; the world-visibility defect is tracked in
`reports/qa/p7_implementation_report.md`. The GPU-independent suite passed
81/81. The cycle benchmark measures the same worker process protocol used by
QProcess, but is not a ten-cycle manual desktop-app test.

## Consequences

The process boundary isolates GUI and renderer event loops and permits a
renderer restart without restarting the simulation. Qt must handle protocol
versioning, bounded event history, reconnect, and graceful close. The
presentation laptop still requires the hardware FPS and full app ten-cycle
checks in `docs/3d_demo_checklist.md`; local measurements do not establish
target-machine performance.

## Status

Accepted for implementation on 2026-11-11. Target-laptop performance
verification remains a human action.
