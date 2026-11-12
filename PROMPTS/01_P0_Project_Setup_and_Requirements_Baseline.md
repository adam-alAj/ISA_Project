# Prompt 01 — Phase P0: Project Setup & Requirements Baseline

## 1. Role
You are a **Technical Project Lead and Requirements/DevOps Engineer** for a Python AI-simulation project. You turn a requirements document into a controlled, reproducible engineering workflow: repository, environment, traceability, risk and decision records, and a baseline for the desktop application.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. Authority: SRS v1.0 and Roadmap v1.0 (project files). The map v0.2 files already exist and must be imported into the repo (not regenerated).

## 3. Inputs
SRS, Roadmap, the map files (`build_map.py`, `department_map.npy`, `department_map.json`, `map_preview.png`), the original photo of the drawing.

## 4. Objective
Establish a controlled development process and remove ambiguity before implementation. **Exit gate:** a teammate can clone, install and run the skeleton application; requirements and ownership are agreed.

## 5. Tasks (do all; ID → concrete instruction)
- **P0.01** Read SRS + Roadmap fully; produce `docs/00_requirements_digest.md` (≤2 pages): scope, MUST/SHOULD/COULD counts, out-of-scope list, top-10 risks.
- **P0.02** Create `docs/traceability_matrix.csv`: one row per FR-01…FR-28, NFR-01…NFR-12, AC-01…AC-09 with columns `id, type, priority, phase, module, test_case, status` (status initially `Not Started`). Every MUST must map to ≥1 phase and ≥1 planned test.
- **P0.03** Draft the instructor question: confirm the six algorithms and that "IDFS" = IDDFS/IDS. Write it as a ready-to-send message in `docs/open_questions.md`. **HUMAN ACTION** to send/receive.
- **P0.04** Add to `docs/open_questions.md` the grading-rubric/submission-format/demo-expectation questions. **HUMAN ACTION.**
- **P0.05** Create `docs/team_charter.md` with a RACI table (roles: lead, algorithms, map/environment, UI, QA/docs) and a decision owner — leave names as `<TBD>`. **HUMAN ACTION** to fill.
- **P0.06** Initialize Git; define `main/develop/feature/*` workflow in `CONTRIBUTING.md`; add `.gitignore` (venv, caches, reports output, large binaries) and conventional-commit guidance.
- **P0.07** Create the repository tree from Shared Context §5 with `__init__.py` files and a one-line `README` per package describing its responsibility. Place the map assets: photo → `assets/floor_plans/`, `.npy/.json/.png` → `data/maps/department_v0_2/`, `build_map.py` → `src/map_processing/legacy_build_map.py` (kept as reference, refactored in P2).
- **P0.08** Choose Python 3.12 (fallback 3.11); document the choice and create the venv instructions for Windows (PowerShell) and a cross-platform note.
- **P0.09** Create `requirements.txt` (or `pyproject.toml`) with: PySide6, opencv-python, numpy, shapely, matplotlib, pandas, reportlab, python-docx, networkx (optional), pytest, ruff (optional). Pin **only versions that pass P0.10**; record versions in `docs/environment.md`.
- **P0.10** Write `scripts/smoke_test.py` importing and exercising each dependency minimally (create a QApplication offscreen, an OpenCV image op, a NumPy op, a Matplotlib figure saved to PNG, a Pandas frame, a ReportLab one-page PDF). Report pass/fail per package; fix version conflicts.
- **P0.11** Write `README.md`: purpose, setup, run, test, structure, contribution, known limitations.
- **P0.12** Write `docs/coding_standards.md`: style, naming, type hints, docstrings, error handling, determinism rules, "no UI imports in core modules" rule, import-linter-style check script if cheap.
- **P0.13** Implement `src/app/config.py` and `src/app/logging_setup.py`: config location (`%APPDATA%/SmartVacuum` on Windows, `~/.config` elsewhere; overridable via env var), log rotation, log levels.
- **P0.14** Generate `docs/task_board.csv` (importable to GitHub Projects) containing every Roadmap task P0.01–P10.20 with `phase, priority (P0–P3), owner, status, depends_on`. Use Roadmap §5 priorities and §6 dependencies.
- **P0.15** Record the optional visualization descoping decision in ADR-0022; obtain instructor acknowledgement before treating AC-06 as closed. **HUMAN ACTION**.
- **P0.16** Create `docs/adr/` with `ADR-0001` … for: Python version; 4-neighbor model; neighbor order U,R,D,L; deterministic tie-breaking; coverage controller separation; optional visualization scope; map pipeline = human-assisted; cell size 0.10 m; IDDFS interpretation (provisional). Use the standard ADR template (context, decision, consequences, status).

## 6. Constraints
- No algorithm or UI implementation in this phase beyond skeleton/prototype.
- Do not modify the original drawing; do not regenerate the map.
- Every created document must be concise, scannable and free of placeholders that look final (`<TBD>` must be explicit).

## 7. Deliverables
Repo skeleton; `requirements.txt`; `scripts/smoke_test.py` + results; `README.md`; `docs/` (digest, traceability matrix, open questions, team charter, coding standards, environment, ADR log, task board); ADR-0022.

## 8. Acceptance gate (report pass/fail for each)
- [ ] Fresh clone + venv + `pip install -r requirements.txt` + `python scripts/smoke_test.py` succeeds.
- [ ] `pytest` runs (even if only one placeholder test) and passes.
- [ ] Traceability matrix covers 100% of FR/NFR/AC IDs; every MUST has a phase.
- [ ] Task board contains all 221 roadmap tasks.
- [ ] ADR-0022 records the visualization scope decision and approval status.
- [ ] Open questions and HUMAN ACTIONS are listed in one place.

## 9. Output
Use the report format from Shared Context §8.5.
