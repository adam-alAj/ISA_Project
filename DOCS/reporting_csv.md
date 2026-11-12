# Analytics and report CSV columns

`runs.csv` under each experiment directory is an index with run identity,
timestamp, mode, algorithm, selected summary metrics, termination reason, and
the relative JSON record filename.

The user-exported metrics CSV has one row per persisted run and is UTF-8 with a
byte-order mark for Excel. Column names and units are:

| Column | Meaning | Unit |
| --- | --- | --- |
| `run_id` | Stable experiment identity hash | SHA-256 hex |
| `mode`, `algorithm` | Separate mission mode and registry algorithm id | text |
| `expanded`, `generated`, `repeated_expansions`, `peak_frontier` | Frozen search counters | states/entries |
| `path_length_steps`, `path_length_m`, `path_cost` | Geometric route and configured cost | steps, m, cost units |
| `search_time_s`, `simulated_travel_time_s` | Planner wall time and simulated mission duration | seconds |
| `battery_consumed_units`, `lifetime_consumed_s` | Simulated resource use | abstract energy units, seconds |
| `achievable_coverage_percent`, `raw_coverage_percent` | Coverage with and without structural exclusion | percent |
| `stop_reason` | Engine terminal reason | text |

Use `scripts/generate_sample_reports.py` to run the six algorithms in each
mode with one discarded warm-up and five fixed-seed measurements. It writes
individual records and the median/IQR protocol output alongside sample PDFs.
