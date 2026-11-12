# UI Audit (Step 0)

Date: 2026-11-12  
Scope: P6 desktop shell pages under Windows using forced Qt color-scheme permutations.

## Reproduction Matrix

- Script: `scripts/ui_screenshots.py`
- Pages: Project Home, Map Editor, Robot Configuration, Algorithm Setup, 2D Simulation, 3D Simulation launcher, Results Dashboard, Report Export
- Resolutions: 1280x720, 1600x900, 1920x1080
- Scale factors: 1.0, 1.25, 1.5 (`QT_SCALE_FACTOR`)
- Forced scheme: `QT_QPA_PLATFORM=windows:darkmode=0|2` plus `QStyleHints.setColorScheme(...)` where available
- Output root: `docs/img/ui_before/`

## Root Cause (Confirmed)

The issue is a hybrid of partial inline QSS and missing global palette ownership:

1. `MainWindow` applied background-only styles and local widget styles, but did not define a complete palette for Active/Inactive/Disabled.
2. Several content cards used explicit white surfaces while child labels inherited dark-scheme foreground from the OS-driven palette under forced dark mode.
3. Standard widgets (`QAbstractSpinBox`, combo popup, lists) fell back to native/OS defaults because styling did not comprehensively cover descendants and states.
4. Net result: white text on white surfaces and very low-contrast subtitle text in multiple pages.

## Contrast Results (Before)

From `docs/img/ui_before/contrast_*.csv`:

- Dark scheme (`scale=1.0/1.25/1.5`): 312 sampled text widgets, 93 AA failures, worst ratio 1.0
- Light scheme (`scale=1.0/1.25/1.5`): 312 sampled text widgets, 24 AA failures, worst ratio 4.483

Top failing pages:

- Dark: `project_home`, `simulation_2d`, `results_dashboard`, `map_editor`
- Light: subtitle labels across all major pages (`project_home`, `map_editor`, `robot_configuration`, `algorithm_setup`)

## Defective Widget Classes Observed

- `QLabel` (titles/subtitles/card labels)
- `QListWidget` content text on white cards under dark mode
- `QAbstractSpinBox` sub-controls and line-edit internals under dark-mode fallback
- `QPushButton` state consistency (hover/focus not explicitly themed)
- `QProgressBar` and status text styling inconsistencies

## Hard-Coded Style and Color Findings

Inline style usage and color literals were concentrated in:

- `src/app/main_window.py` (multiple `setStyleSheet(...)` blocks)
- `src/visualization/two_d/map_canvas.py` (hex palette literals)

These are now being centralized under `src/app/theme/` and the map semantic palette.

## Screenshot Evidence (Before)

Representative failures:

- `docs/img/ui_before/scale_1.0/1280x720/dark/project_home.png`
- `docs/img/ui_before/scale_1.0/1280x720/dark/robot_configuration.png`
- `docs/img/ui_before/scale_1.0/1280x720/light/project_home.png`
