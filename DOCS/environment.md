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
| Python 3.12 / 3.11 available in current shell | PASS | Python 3.12.10 is available for project verification. |
| Dependency installation | NOT RUN | Requires a Python runtime. |
| Dependency smoke test | NOT RUN | Requires installation and an interactive/display-capable Windows target for the GUI cycle check. |
| Optional renderer stability check | Descoped | ADR-0022 removes this feature; retained 2D install verification is tracked under P9.15. |

Do not represent an unexecuted smoke test or integration measurement as a pass.

## P5 verification update (2026-11-11)

The interpreter path found in the user's configured environment is `C:\Users\HP\Desktop\ISA\.venv\Scripts\python.exe`, Python 3.12.10. Its base interpreter lives at `C:\Users\HP\AppData\Local\Programs\Python\Python312\python.exe`; both are present, but sandboxed launches reported the base as missing. Running the project venv through the authorized host command succeeded.

- Dependency smoke test: 12/12 checks passed.
- Full repository suite: 63 passed.
- P5 gate report: `reports/qa/p5_gate_result.md` (PASS).
- The department-map comparison uses explicit bounds (2,000 expansions or 0.5 seconds per planner call and 50 coverage target selections per run). The resulting department rows are partial diagnostics and report the max-iteration stop; they do not claim full-floor completion.
