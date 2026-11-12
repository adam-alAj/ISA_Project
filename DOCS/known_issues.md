# Known issues

## Severity definitions

- **High:** a required user-facing result or acceptance gate is unreliable.
- **Medium:** a feature behaves differently from the expected interaction but a documented workflow remains usable.
- **Low:** limitation or maintenance debt with a safe, documented fallback.

## Open issues

| ID | Severity | Issue | P8 impact | Workaround / follow-up |
|---|---|---|---|---|
| KI-3D-01 | High for P7 demo | Development 3D framebuffer capture displays the Ursina HUD but not the world geometry; worker scene layout and camera transforms are populated. | None. Analytics uses engine state/events and the 2D view. | Use 2D for demo until the Ursina camera/render issue is resolved; investigate under P7/P9. |
| KI-P6-01 | Medium | Playback slider controls presentation refresh cadence and does not pace simulation execution. | None. Planner and simulation timing remain separately recorded. | Use pause/step controls to inspect discrete actions. |
| KI-P6-02 | Low | A single calibration reference segment cannot provide an independent residual estimate. | None. Map calibration and run records still retain the configured scale. | UI displays “n/a”; add a second independent reference measurement in a later UI improvement. |
| KI-P6-03 | Low | Some user-facing strings remain inline rather than centralized for translation. | None. | English workflow is usable; move remaining strings to `src/app/strings.py` as polish. |
| KI-P6-04 | Deferred | Usability session with a participant unfamiliar with the code has not been performed. | None for P8; its results are scheduled as input to P9.16. | Execute `docs/p6_manual_check.md` during P9.16 and record results. |

## Previously recorded P5 limitations

- The department-map comparison in `reports/qa/p5_gate_result.md` is deliberately
  capped at 50 target selections per algorithm, with a per-search budget of
  2,000 expansions or 0.5 seconds. Those rows are partial results, not full
  floor coverage. Synthetic TS-08/TS-09 tests cover complete and constrained
  outcomes separately.
- `EventLog` retains a bounded in-memory ring and can optionally append all
  emitted events as JSONL. Full replay of a run longer than the ring capacity
  requires configuring that sink.

## Resolved during P6 gate verification

- The Qt poller could iterate the worker-mutated event deque and raise
  `RuntimeError: deque mutated during iteration`. `EventLog.snapshot_events()`
  now provides a lock-protected copy, and
  `tests/test_event_log_thread_safety.py` covers concurrent emit/read access.
- Structural coverage previously counted navigable robot-centre cells in
  disconnected inflated-map components as achievable. `build_cleanable_cells`
  now floods legal centres from the start; ADR-0020 and a narrow-corridor
  regression fixture document and verify the correction.
