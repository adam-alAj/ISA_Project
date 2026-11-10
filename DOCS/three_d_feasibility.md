# PySide6 and Ursina feasibility

## Prototype design

The PySide6 controller starts Ursina in a separate process with `QProcess`. It sends newline-delimited JSON on stdin using `{"cmd":"move","cell":[r,c]}` and `{"cmd":"close"}`. The worker reads commands on a background stdin thread and applies scene changes on Ursina's main loop. This isolates the event loops and makes worker shutdown explicit.

## Measurement

The ten-cycle driver is `prototypes/ui_3d_feasibility/cycle_benchmark.py`; it records readiness time, exit status, and errors in `cycle_results.csv`.

**Result: NOT MEASURED.** The current workspace shell has no Python executable and no target-machine graphics session, so the launch/close cycles could not be run. Do not infer stability from the code alone. Run the benchmark on the presentation laptop and add its actual CSV and environment details before freezing the integration decision.

## Recommendation

Use the separate synchronized process as the provisional design because it avoids embedding Ursina's event loop in Qt. Keep this decision provisional until ten launch/close cycles complete successfully on the target laptop and the route-message synchronization is reviewed. If process startup is too slow or shutdown is unreliable, revisit the ADR before production UI integration.
