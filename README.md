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

The current `main.py` launches the PySide6 desktop application. The P2?P5 environment, robot, search and simulation layers are implemented; P6 provides the 2D workflow and UI. The 3D screen is currently a launcher placeholder while P7 integration proceeds. Run `pytest` for the automated checks.

## Structure

- `assets/floor_plans/`: untouched original source drawings (the supplied photo still needs to be added).
- `data/maps/department_v0_2/`: supplied v0.2 map array, metadata, and preview.
- `src/`: application, map processing, environment, robot, algorithms, coverage, simulation, visualization, analytics, and reporting packages.
- `tests/`, `scripts/`, `prototypes/`, `reports/`, `docs/`: verification, utilities, feasibility work, outputs, and project records.

See the one-line package READMEs under `src/` for module responsibilities.

## Contributing

Use the `main` / `develop` / `feature/*` workflow and Conventional Commit messages described in [CONTRIBUTING.md](CONTRIBUTING.md). Requirements and human decisions are tracked in `docs/`.

## Known limitations

The original source floor-plan photo is not present. The usability session with an unfamiliar participant remains a human action. The course terminology and project rubric questions remain for instructor clarification.
