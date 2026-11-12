# Baseline before 3D removal

Date: 2026-11-12  
Branch: `chore/remove-3d`  
Starting commit: `3663f4e06934197fe652741662b58128e1699c5a`  
Safety tag: `pre-3d-removal` points to that commit.  
Previous working-tree P9/P8 changes and generated run logs were preserved in
stash `pre-3d-removal-worktree-checkpoint`; the pre-removal test baseline below
was run against the clean starting commit.

## Tests and coverage

| Run | Result |
|---|---|
| `QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q` | 102 passed, 1 failed in 59.20s. Failure: P6 GUI timer gap 149.70 ms, threshold `<100 ms`. |
| Focused retry of the responsiveness case | 1 passed in 7.08s. The threshold was not changed. |
| Full suite under pytest-cov (`environment`, `robot`, `algorithms`, `coverage`, `analytics`) | 102 passed, 1 failed in 84.82s; 1,715 statements, 199 missed, **88% aggregate**. The same GUI timer case recorded 138.44 ms. |

The intermittent timer case is a baseline failure signal, not treated as a
pass. It must be considered when comparing after-removal runs.

## Lint and wrapper

- `ruff check src tests scripts --output-format=json`: **160 findings**.
- `scripts/run_all_checks.ps1` and `.sh` are not present at the clean starting
  commit, so the requested wrapper baseline could not be run. The wrapper
  existed only in the preserved pre-task stash; its absence is reported rather
  than silently restoring unrelated working-tree changes.

## Environment

Host venv Python 3.12.10 x64; Qt run with `QT_QPA_PLATFORM=offscreen`.
