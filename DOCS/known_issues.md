# Known issues

## P5 verification is pending

- Python 3.12 was requested through the official winget package, but the installer did not leave an interpreter available in the current workspace. P5 runtime results are therefore not known. See `reports/qa/p5_gate_result.md` and `docs/environment.md`.
- `EventLog` keeps a bounded in-memory ring and can optionally append JSONL to a sink. Replay equivalence must be verified with the sink configured for any run that can outgrow the in-memory capacity; the P5 gate will expose failures here.
- ADR-0016 remains a draft until the full gate report contains passing evidence.
