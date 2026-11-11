# P6 implementation and validation status

Date: 2026-11-11
Prerequisite: P5 freeze point 4 is accepted in ADR-0016; evidence is `reports/qa/p5_gate_result.md`.

## Acceptance checks

| Check | Status | Evidence / limitation |
|---|---|---|
| End-to-end user workflow with screenshots | Partial | Eight desktop screens captured under `docs/img/`; automated point-to-point metrics and coverage worker tests pass. A person has not yet completed the manual workflow. The 3D screen remains a launcher placeholder. |
| UI event latency below 100 ms during coverage | Pass | `tests/ui/test_desktop_ui.py::test_gui_timer_latency_stays_under_100ms_during_coverage`: 16 timer samples, maximum interval 63.87 ms in the latest isolated run. |
| Displayed metrics equal engine metrics | Pass | `tests/ui/test_desktop_ui.py::test_displayed_point_to_point_metrics_match_engine`; part of the full suite. |
| Cancel/close leaves no worker running | Pass | Safe-boundary cancellation and window teardown tests in `tests/ui/test_desktop_ui.py`. |
| Legend and non-color cues | Pass with limitation | Wall crosshatch, unknown hatch, door stripe, explored dots, frontier diamonds, route line, cleaned dots, and labeled robot/start markers are shown. Golden image checks omit marker text because Qt font rasterization varies across Windows paint devices; label rendering remains visible in the application screenshots. |

## Automated verification

- Command: ` .\.venv\Scripts\python.exe -m pytest `
- Result: **70 passed in 46.58s**.
- Command: ` .\.venv\Scripts\python.exe -m pytest tests\ui\test_desktop_ui.py::test_gui_timer_latency_stays_under_100ms_during_coverage -q -s `
- Result: **1 passed**, max event interval **63.87 ms**.
- Eight screen captures and the map canvas golden are in `docs/img/`.

## Remaining work

- **HUMAN ACTION:** conduct `docs/usability_test.md` with a participant unfamiliar with the code and record task outcomes/questionnaire answers.
- The playback slider changes presentation refresh cadence only; it does not pace worker execution. A direct interactive user session was not performed; the delivered screen captures are headless.
- Calibration reports scale and correctly marks residual as not estimable from one reference segment; a multi-reference residual workflow is still needed for a numeric residual.
- Some user-facing labels remain inline instead of being centralized in `src/app/strings.py`.
- The 3D screen is a placeholder until P7 renderer integration.

P6 is **in progress**, not fully accepted, because the required human usability session and the above items remain.
