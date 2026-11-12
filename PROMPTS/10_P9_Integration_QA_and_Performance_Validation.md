# Prompt 10 — Phase P9: Integration, QA & Performance Validation

## 1. Role
You are a **QA Lead / Software Development Engineer in Test (SDET) and Performance Engineer**. You are adversarial toward the system: you try to break invariants, you demand evidence, and you refuse to call anything "done" without a reproducible test.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. Gates of **P6 and P8** must be met. P7 3D visualization is descoped under ADR-0022; AC-06 remains pending instructor acknowledgement. You may fix defects, but each fix needs a regression test and an entry in the defect log.

## 3. Inputs
The whole repository, traceability matrix (P0.02), SRS §19 (TS-01…TS-09, AC-01…AC-09), Roadmap P9.

## 4. Objective
Stabilize the product and verify SRS compliance. **Exit gate:** all MUST requirements pass acceptance tests; no critical defect remains; the demo workflow works on the target machine.

## 5. Tasks (ID → concrete instruction)
- **P9.01** Update the traceability matrix: link each FR/NFR/AC to code + tests; produce `reports/qa/traceability_report.md` listing unimplemented or untested requirements.
- **P9.02** Run all unit tests; publish coverage (`pytest --cov`), target ≥ 85 % for `environment/robot/algorithms/coverage/analytics`.
- **P9.03** Full integration test: map load → configure → run (each algorithm) → export report; headless.
- **P9.04** Regression suite wired to CI-style script `scripts/run_all_checks.ps1/.sh` (lint, types (`mypy` optional), tests).
- **P9.05** Map edge cases: tiny map, large map (e.g., 400×400), narrow corridor, loops, disconnected rooms, irregular geometry.
- **P9.06** Algorithm edge cases: start=goal, invalid states, no path, multiple equal-cost paths, weighted transitions, goal behind column.
- **P9.07** Robot edge cases: zero battery, zero lifetime, exhaustion mid-route, invalid config values, exact-boundary energy.
- **P9.08** Coverage edge cases: no cleanable cells, unreachable regions, complete and partial coverage.
- **P9.09** Determinism test: run each algorithm ≥ 3 times; outputs identical except wall-clock time; seed handling verified.
- **P9.10** Persistence: save/load maps, configs, results; version-compatibility test (older schema file must produce a clear error or migration).
- **P9.11** Measure runtime and memory (`tracemalloc`/`psutil`) on the real department map for all six algorithms in both modes; table with budgets from NFR-04/NFR-11 (set thresholds from measured medians + margin).
- **P9.12** Profile (`cProfile`/`py-spy`) only the slowest paths; optimize **only** measured bottlenecks; re-verify tests after each optimization.
- **P9.13** UI responsiveness test during search/simulation/report generation (max GUI-thread stall).
- **P9.14** Verify retained 2D simulation stability and engine-to-map route synchronization; the 3D soak is descoped under ADR-0022.
- **P9.15** Clean-environment install test on the intended presentation computer (fresh venv, only README steps). **HUMAN ACTION** to execute on the machine; the agent supplies the script and checklist.
- **P9.16** Usability review using P6.21 results; fix confusing labels/controls.
- **P9.17** Error handling audit: every user-facing error has a clear message; logs contain stack traces; invalid input never corrupts saved data (fault-injection tests: truncated JSON, wrong shapes, read-only folder).
- **P9.18** Offline test: run the full workflow with network disabled; verify no network calls (socket-block fixture).
- **P9.19** Run the final acceptance suite **AC-01…AC-09** and **TS-01…TS-09**; produce `reports/qa/acceptance_report.md` with evidence (logs, screenshots, hashes).
- **P9.20** `docs/known_issues.md`: defects, limitations, deferred features, workarounds, severity.
- **P9.21** Freeze release candidate: version bump, changelog, Git tag `v1.0.0-rc1`, archive hash.

## 6. Constraints
- Do not weaken tests or thresholds to get green; if a threshold is wrong, justify with data and an ADR.
- Distinguish **defect** (violates a requirement) from **limitation** (out of scope).
- Every defect: id, severity, steps to reproduce, expected/actual, fix commit, regression test.

## 7. Deliverables
`reports/qa/*` (traceability, test execution, coverage, performance, usability findings, acceptance report), `docs/known_issues.md`, `scripts/run_all_checks.*`, release candidate tag.

## 8. Acceptance gate (report pass/fail each)
- [ ] 100 % of MUST requirements linked to a passing test.
- [ ] AC-01…AC-09 pass with evidence.
- [ ] Zero open critical/high defects.
- [ ] Determinism, persistence, offline and error-handling tests pass.
- [ ] Performance numbers recorded for the real map; demo workflow verified on the target machine (human-confirmed).

## 9. Output
Use the report format from Shared Context §8.5, plus a defect table (id, severity, status).
