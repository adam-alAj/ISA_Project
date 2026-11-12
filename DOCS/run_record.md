# Run record and reproducibility contract

Schema: [`schemas/run_record.schema.json`](../schemas/run_record.schema.json),
version 1. One JSON record is stored per completed run. The CSV index contains
one row per run and points to the record; the full event stream is stored as a
UTF-8 JSONL sidecar referenced by a relative path and SHA-256 digest.
Records and sidecars use a timestamped filename while retaining the stable
configuration `run_id`, so repeated executions never overwrite one another.
The app persists the event sink directly; its bounded in-memory ring is not
treated as the complete event history.

## Stable run ID

Construct the canonical identity object:

```json
{
  "map_sha256": "<canonical map content hash>",
  "experiment": "<normalized configuration object>",
  "algorithm": "<registry algorithm id>",
  "policy": "<policy id and normalized configuration, or null>",
"seed": 17
}
```

Canonicalize recursively with sorted object keys, compact separators, UTF-8,
and JSON numeric values as stored in the normalized configuration. The map
hash covers shape, canonical uint8 occupancy bytes, `cell_m`, and pixel origin;
presentation-only metadata such as timestamps and room-label spelling does
not change map identity. Compute `run_id = lowercase_hex(SHA256(canonical_bytes))`.
Creation date, host, software versions, and results are recorded but excluded
from identity so equivalent experiments share a stable ID.

## Persisted data

- `map`: identifier/version, canonical SHA-256, dimensions, cell scale, and
  origin and canonical grid values needed to render stored map snapshots.
- `experiment`: mode, algorithm/settings, endpoints, seed, robot config,
  policy, neighbor order, movement model, cost model, heuristic, and budgets.
- `raw_results`: full SearchResult value(s), coverage outcome when applicable,
  final robot state, and stored explored/route/cleaned cell layers. Derived report values may be cached but must be
  reproducible from these raw values and events.
- `event_log`: relative JSONL path, event schema version, SHA-256, and count.
  The file is part of the run record's immutable data bundle.
- `project`: software/project version, Python, OS, CPU, and relevant dependency
  versions for benchmark context. Current recorded packages include NumPy,
  Matplotlib, ReportLab, PySide6, jsonschema, and pypdf when installed.

Run-record schema validation is strict at the top-level boundaries. Additive
raw algorithm diagnostics may be preserved in `search_results` while the
required fields remain validated.

## CSV and benchmark outputs

`runs.csv` is an append-only UTF-8-with-BOM index. Report CSV exports contain
one row per raw measured run and the frozen metric columns documented in
`docs/metrics.md`. Timing summaries are separate JSON outputs containing the
discarded warm-up duration, five or more fixed-seed planner-only samples,
median, inclusive-quartile IQR, Python/OS/CPU, and preserved source records.
The schema validator is `jsonschema` against `schemas/run_record.schema.json`;
the loader additionally verifies stable identity and the event sidecar digest,
count, and versioned event fields.
