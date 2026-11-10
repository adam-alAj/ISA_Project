# Prompt 11 — Phase P10: Documentation, Demo & Final Delivery

## 1. Role
You are a **Technical Writer and Release Manager** who also prepares academic presentations. You write for three audiences — a new developer, an instructor grading algorithmic correctness, and a first-time user — and you never overstate what the system proves.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. Gate of **P9** must be met (release candidate frozen). Source of truth = the code, tests, reports and SRS; documentation must match implemented behaviour, with deviations recorded.

## 3. Inputs
Repository at `v1.0.0-rc1`, QA reports, sample reports, SRS v1.0, Roadmap v1.0, ADR log, usability findings.

## 4. Objective
Prepare a complete academic handover and demonstration package. **Exit gate:** a fresh user can install and run the application using the documentation; the final presentation and submission package are complete.

## 5. Tasks (ID → concrete instruction)
- **P10.01** Final `README.md`: requirements, install (Windows PowerShell), launch, run tests, troubleshooting (PySide6/Ursina/GPU issues), project structure.
- **P10.02** `docs/architecture.md`: layered diagram (Mermaid + exported PNG), module responsibilities, data flow, interface contracts, event schema.
- **P10.03** `docs/map_preparation.md`: from the hand-drawn plan to the grid: calibration, cell size study, human-assisted digitization statement, limitations, how to edit the spec and rebuild.
- **P10.04** `docs/robot_model.md` final: equations, units, parameter table, assumptions (battery is a simulated model).
- **P10.05** `docs/algorithms.md` final: each algorithm's implementation specifics (counters, tie-breaking, IDDFS tractable variant), complexity, observed behaviour.
- **P10.06** `docs/coverage_policy.md` final: why coverage ≠ pathfinding, denominator, uncoverable cells, fairness caveat.
- **P10.07** `docs/experiment_protocol.md`: metrics definitions, fairness controls, timing protocol, how to reproduce every table.
- **P10.08** `docs/test_report.md`: strategy, results, coverage figures, traceability summary, known issues.
- **P10.09** `docs/SRS_v1.1_deviations.md`: list of implemented behaviour vs SRS v1.0 with approved deviations (e.g., declarative map spec, IDDFS variant, 0.10 m cell); do not edit the original SRS silently.
- **P10.10** `docs/user_guide.md` with screenshots: prepare a map, configure robot, run P2P and coverage, read the dashboard, export reports, launch 3D.
- **P10.11** Technical report (`docs/technical_report.md` → export PDF) ≈ 10–15 pages: problem, method, design, algorithms, experiments, results, discussion, limitations, future work, references (cite only what was used).
- **P10.12** Final experiment dataset: regenerate all runs from a clean checkout with fixed seeds into `data/experiments/final/`, plus tables/charts in `reports/final/`; verify hashes.
- **P10.13** Demo scenario file `demo/scenario.json`: fixed map, start S, chosen goals, coverage mode, resource settings (include one battery-limited and one lifetime-limited run).
- **P10.14** Presentation outline + slide content (`docs/presentation_outline.md`, and a .pptx if requested): problem, objectives, architecture, algorithms, simulation, 2D/3D demo, results, limitations. Slides contain **trade-offs, not a single winner**.
- **P10.15** `docs/demo_script.md`: timed steps (target 8–10 min) following SRS §21.1, expected on-screen outcomes, talking points, Q&A cheat-sheet (why coverage ≠ search, why IDDFS repeats, why Greedy is not optimal, battery model caveat).
- **P10.16** Backup assets: screenshots and a recorded video of the full demo (**HUMAN ACTION** to record; the agent provides the shot list and a script to export frames).
- **P10.17** Packaging check: relative/portable paths, no absolute paths, assets included, `scripts/verify_package.py` that runs from a clean folder.
- **P10.18** Create the release: version `v1.0.0`, changelog, Git tag, source archive (zip) with checksum.
- **P10.19** Rehearsal checklist for the presentation machine (**HUMAN ACTION**); agent prepares `docs/rehearsal_checklist.md`.
- **P10.20** Submission package folder `submission/`: source, docs, map assets, reports, test evidence, presentation, README index; verify against Roadmap §9 Final Release Checklist and report each line pass/fail.

## 6. Constraints
- Docs must not claim more than the tests/reports demonstrate; state limitations plainly.
- Every number in docs/slides must be traceable to a stored run record or test.
- Keep one canonical source per fact (link instead of copying).
- Do not include real personal data; the map and names are demo data.

## 7. Deliverables
Final docs set, user guide, technical report (+PDF), presentation material, demo scenario/script, final datasets and reports, release archive, submission package.

## 8. Acceptance gate (report pass/fail each)
- [ ] Fresh-machine install following only the README succeeds (human-confirmed on a clean environment).
- [ ] Every Roadmap §9 release-checklist line is checked with evidence.
- [ ] All figures in docs/slides are reproducible from `data/experiments/final/`.
- [ ] Demo script rehearsed; backup recording exists.
- [ ] Known limitations and future work stated honestly.

## 9. Output
Use the report format from Shared Context §8.5, ending with the filled release checklist.
