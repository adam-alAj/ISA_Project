# Smart Vacuum Cleaner Simulation

This repository is the foundation for an offline Python desktop simulation of indoor search, navigation, and vacuum-cleaning coverage. It is an educational simulation, not a controller for a physical appliance. The SRS and Roadmap in `docs/` are the requirements authority; project decisions and traceability live alongside them.

## Setup

Use Python 3.12 (Python 3.11 is the fallback) on Windows 10/11. From PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If Python 3.12 is unavailable, replace `-3.12` with `-3.11`. On macOS/Linux use `python3.12 -m venv .venv` and `source .venv/bin/activate`. See [docs/environment.md](docs/environment.md) for dependency and platform notes.

## Run and verify

```powershell
python main.py
python scripts/smoke_test.py
pytest
```

The current `main.py` is a runnable phase-zero skeleton. Core algorithms, simulation, and the production UI are not implemented yet. The smoke script checks the dependency stack, and the separate prototype tests PySide6/Ursina process integration.

## Structure

- `assets/floor_plans/`: untouched original source drawings (the supplied photo still needs to be added).
- `data/maps/department_v0_2/`: supplied v0.2 map array, metadata, and preview.
- `src/`: application, map processing, environment, robot, algorithms, coverage, simulation, visualization, analytics, and reporting packages.
- `tests/`, `scripts/`, `prototypes/`, `reports/`, `docs/`: verification, utilities, feasibility work, outputs, and project records.

See the one-line package READMEs under `src/` for module responsibilities.

## Contributing

Use the `main` / `develop` / `feature/*` workflow and Conventional Commit messages described in [CONTRIBUTING.md](CONTRIBUTING.md). Requirements and human decisions are tracked in `docs/`.

## Known limitations

This baseline has no installed Python runtime in the current workspace environment, so dependency installation, smoke results, pytest, and the ten-cycle graphical feasibility measurement are pending. The original floor-plan photo is not present. Dependency versions remain unpinned until the specified smoke checks pass. The IDFS terminology and project rubric questions remain for the instructor.
