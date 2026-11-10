# Development environment

## Runtime decision

Use Python 3.12 as the primary runtime. Python 3.11 is the fallback because both versions are within the SRS support range. This decision is provisional until the Windows dependency smoke test is run.

## Create the environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If 3.12 is unavailable, use `py -3.11`. For macOS/Linux, use `python3.12 -m venv .venv`, activate with `source .venv/bin/activate`, then install the same requirements. Run `python scripts/smoke_test.py` and `pytest` after installation.

## Dependency status

The requested stack is listed in `requirements.txt`. Versions are deliberately unpinned until P0.10 passes; no passing version set can be recorded yet because this workspace has no `python`, `py`, or `pip` executable. `networkx` and `ruff` are optional for runtime behavior, but included for the requested baseline smoke and quality workflow. Record exact interpreter and package versions here after a successful smoke run.

## Current verification record

| Check | Result | Evidence |
|---|---|---|
| Python 3.12 / 3.11 available in current shell | FAIL | `python`, `py`, and `pip` are not on PATH. |
| Dependency installation | NOT RUN | Requires a Python runtime. |
| Dependency smoke test | NOT RUN | Requires installation and an interactive/display-capable Windows target for the GUI cycle check. |
| Ten-cycle PySide6/Ursina stability measurement | NOT RUN | No Python runtime or graphics session is available in this shell. |

Do not represent an unexecuted smoke test or integration measurement as a pass.
