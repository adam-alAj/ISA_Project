# Known issues

## P5 bounded department diagnostic

- The department-map comparison is deliberately capped at 50 target selections per algorithm, with a per-search budget of 2,000 expansions or 0.5 seconds. Those rows are partial results and stop with the iteration guard; they are not full-floor department coverage. The synthetic TS-08/TS-09 matrix verifies complete and resource-limited outcomes separately.
- `EventLog` retains a bounded in-memory ring and can optionally append all emitted events as JSONL. Full replay of a run longer than the ring capacity requires configuring that sink.

## Resolved during the command-output repair

- `SearchProblem.step_cost` now supports both the documented two-argument callback and mapping-style callbacks keyed by `(source, target)`.
- Metric-to-cell conversion snaps floating-point values within `1e-12` of grid lines before flooring, preserving exact boundaries such as 6.0 m at 0.1 m resolution.
- The weighted-search and seeded-oracle fixtures now exercise the intended callback and RNG APIs. Coverage tie-break assertions now test nearest Manhattan targets, and the footprint reachability fixture checks the first safe centre beyond the cabinet (column 27).
