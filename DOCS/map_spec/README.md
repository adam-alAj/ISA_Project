# Department map v0.2 specification

This directory records the current human-assisted traced map as a reviewable specification. The source photo is missing, so drawing-specific visual claims, original image metadata, and final approval remain open. The existing map artifacts are preserved unchanged; the geometry source is `src/map_processing/legacy_build_map.py`.

Start with `map_definition.md`, then review `elements.yaml`, `dimensions.csv`, `consistency_report.md`, and `annotated_plan.png`. Proposed targets and array-level checks are in `demo_goals.csv` and `validation.md`; the resolution comparison is in `resolution_study.md`. `review_checklist.md` and the freeze statement in `unresolved.md` require human sign-off. The overlay was produced from the existing preview using the built-in Windows drawing API because Python/Matplotlib is not installed in this environment.
