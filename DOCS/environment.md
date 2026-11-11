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

### Interpreter search for P5/P6 continuation (2026-11-11)

| Attempt | Result |
|---|---|
| `where.exe python` | No executable found. |
| `where.exe py` | No executable found. |
| `py -0p` | `py` command is not recognized. |
| Repository `.venv\Scripts\python.exe` | File does not exist. |
| `%LOCALAPPDATA%\Programs\Python\Python3*\python.exe` | No matching interpreter found. |

No Microsoft Store alias was found by the command lookup. Next attempted install route: `winget install -e --id Python.Python.3.12` (result to be recorded below).

| Attempt | Result |
|---|---|
| `winget install -e --id Python.Python.3.12` (elevated) | Found Python 3.12.10 and began downloading from python.org. Installer processes remained active but no interpreter was installed. |
| Direct silent installer retry | Returned Windows Installer exit code `1618` while the first installation was active. |
| Silent winget retry with agreement flags | Reached the official package download step; after the process exited, no Python executable appeared in the standard user or Program Files locations and `where.exe python` still found none. |
| `uv python install 3.12` | Not available: `uv` was not found on PATH. |

The installer could not be completed from this managed session. Human action: in a normal PowerShell window run:

```powershell
winget install -e --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python scripts\smoke_test.py
.\.venv\Scripts\python -m pytest -q
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\run_p5_gate.ps1
```

Gate command attempts are recorded in `reports/qa/p5_gate_result.md`. Their results are **FAIL / NOT RUN** because the interpreter prerequisite is absent; the P5 gate remains **pending evidence**, not passed.

The PowerShell gate wrapper itself ran with `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\run_p5_gate.ps1` and wrote the report. The bash wrapper was checked with `bash -n` and invoked, but Windows denied process creation for `bash.exe` (`Bash/Service/CreateInstance/E_ACCESSDENIED`), so its runtime path could not be exercised here.

| Check | Result | Evidence |
|---|---|---|
| Python 3.12 / 3.11 available in current shell | FAIL | `python`, `py`, and `pip` are not on PATH. |
| Dependency installation | NOT RUN | Requires a Python runtime. |
| Dependency smoke test | NOT RUN | Requires installation and an interactive/display-capable Windows target for the GUI cycle check. |
| Ten-cycle PySide6/Ursina stability measurement | NOT RUN | No Python runtime or graphics session is available in this shell. |

Do not represent an unexecuted smoke test or integration measurement as a pass.
