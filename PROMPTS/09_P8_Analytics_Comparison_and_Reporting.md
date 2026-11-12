# Prompt 09 — Phase P8: Analytics, Comparison & Reporting

## 1. Role
You are a **Data Analyst and Experiment-Reporting Engineer** with an academic-integrity mindset: precise definitions, reproducible experiments, honest interpretation, and professional report generation (ReportLab/Pandas/Matplotlib).

## 2. Context
Use `00_Shared_Context_and_Rules.md`. Gates of **P5 and P6** must be met. Start by **freezing metric definitions** (Freeze point 5) before building any chart or report.

## 3. Inputs
Run logs/events, `SearchResult`, configs, SRS §14, §16, §19.5, Appendix B, Roadmap P8.

## 4. Objective
Turn run logs into transparent, academically defensible results. **Exit gate:** reports reproduce stored run data, use consistent metric definitions, and clearly state assumptions and limitations.

## 5. Tasks (ID → concrete instruction)
- **P8.01** `docs/metrics.md` §1: exact definitions of expanded, generated, repeated expansions, peak frontier (reuse `docs/search_counters.md`).
- **P8.02** §2: path length (steps and meters), **path cost** (configured cost model — report both when costs differ), search time, travel time (simulated).
- **P8.03** §3: battery and lifetime units (energy units and %, minutes/seconds) and conversions.
- **P8.04** §4: coverage numerator/denominator, treatment of unreachable and structurally-uncoverable cells (match P5.02), plus `achievable_coverage`.
- **P8.05** `analytics/extract.py`: compute all metrics from `SearchResult` + event log; pure functions; unit-tested on hand-built logs.
- **P8.06** Run-record schema (`schemas/run_record.schema.json`, versioned) storing metadata + raw results; JSON per run + one CSV index; stable run id = hash of (map hash, config, algorithm, policy, seed).
- **P8.07** Per-run summary object and text renderer.
- **P8.08** Cross-run comparison: verify comparability (same map hash, robot config, policy, neighbor order, cost model, heuristic); refuse or warn clearly otherwise (FR-24).
- **P8.09** Comparison tables for all six algorithms in two separate sections: **(A) point-to-point planning** and **(B) coverage missions** (never mixed).
- **P8.10** Charts (Matplotlib, labelled axes with units, consistent colors per algorithm, colorblind-safe): explored/expanded nodes, search time, path length & cost, energy, coverage; optional per-goal grouped bars.
- **P8.11** Timing protocol: ≥ 5 repetitions per algorithm per scenario, warm-up run discarded, report **median and IQR**; fixed seeds; machine info recorded (CPU, Python, OS).
- **P8.12** Prove separation: assert that timing excludes UI/animation (code-level test + documentation).
- **P8.13** Per-run **PDF report** (ReportLab): metadata, map + grid resolution, robot config, algorithm settings, policy, route result, node counts, times, energy, lifetime, coverage, termination reason, map snapshot with explored/route/cleaned, short **factual** interpretation.
- **P8.14** **Comparison PDF**: tables, charts, assumptions, limitations; interpretation generated from rules, never "X is best" (see P8.20).
- **P8.15** CSV export of raw metrics (UTF-8 with BOM for Excel, documented columns).
- **P8.16** PDF content: tables, charts, map snapshots, assumptions block (map resolution, neighbor model, heuristic, cost function, tie-breaking, target policy).
- **P8.17** Optional DOCX summary via python-docx (only if required by the course; keep behind a flag).
- **P8.18** Validation tests: re-parse each generated CSV/PDF text and compare key numbers with the run record (tolerance defined).
- **P8.19** Report metadata: project version, map version/hash, date, experiment id, software versions.
- **P8.20** Interpretation guard: automated check that generated text never contains superlatives such as "best", "worst", "always", "universally" without a metric-specific qualifier; mandatory caveats (DFS neighbor-order dependence, Greedy non-optimality, IDDFS repeated expansions, simulated battery ≠ real).

## 6. Constraints
- Reports must be reproducible from stored run data only.
- Do not recompute metrics in the UI or report layer with different formulas; import from `analytics`.
- Arabic text in PDFs is **not required**; if used, shape/reorder properly (arabic-reshaper + python-bidi) and embed a font.

## 7. Deliverables
`src/analytics/*`, `src/reporting/*`, `schemas/*`, `docs/metrics.md`, `tests/analytics/*`, `tests/reporting/*`, sample reports in `reports/sample/`.

## 8. Acceptance gate (report pass/fail each)
- [ ] Metrics doc frozen and referenced by code docstrings.
- [ ] Reports reproduce stored run data exactly (automated).
- [ ] Comparison refuses incomparable runs.
- [ ] Timing protocol implemented with median/IQR and machine info.
- [ ] Interpretation guard passes on all generated text.

## 9. Output
Use the report format from Shared Context §8.5. Attach one sample per-run PDF and one comparison PDF.
