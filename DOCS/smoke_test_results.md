# P0 dependency smoke-test results

## Status

**Not run.** The current execution shell has no `python`, `py`, or `pip` command. No dependencies were installed and no pass/fail results are claimed.

## Required run

After creating the documented Python 3.12 (or 3.11) environment and installing `requirements.txt`, run:

```powershell
python scripts/smoke_test.py
```

The script prints an individual `PASS` or `FAIL` for PySide6, OpenCV, NumPy, Shapely, Matplotlib, Pandas, ReportLab, Ursina, python-docx, and NetworkX, followed by installed versions and a summary. Copy the actual output and record the interpreter/platform here; pin only versions that pass. The graphical ten-cycle measurement is tracked separately in `docs/three_d_feasibility.md`.
