# 3D visualization removal verification

Date: 2026-11-12  
Branch: `chore/remove-3d`  
Starting point: `pre-3d-removal` (`3663f4e06934197fe652741662b58128e1699c5a`)  
Decision: ADR-0022, accepted pending instructor acknowledgement. No release tag was created.

## Scope and preserved contracts

The 3D renderer, process client/worker, prototype, renderer tests and scripts, launcher UI page, runtime dependency, and renderer screenshots were removed. The UI now has seven navigation pages. The frozen simulation event/snapshot and coverage implementation paths are byte-for-byte unchanged from the starting commit (`git diff --quiet pre-3d-removal HEAD -- src/simulation src/coverage`: pass). The shared coordinate helper remains for the existing environment API test contract.

FR-21 remains a descoped SHOULD. AC-06 remains a MUST with status ?Descoped ? pending instructor acknowledgement?; it is not passed. P7 and 3D-specific P9.14 work are descoped in the task board. The original SRS/Roadmap DOCX source files were not edited.

## Verification evidence

| Check | Result | Evidence |
|---|---|---|
| Fresh venv install from `requirements.txt` | PASS | New Python 3.12.10 environment installed all listed dependencies. Package list contains neither Ursina nor Panda3D. The temporary venv was removed after verification. |
| Environment check | PASS | `scripts/check_env.py`: all 12 required distributions present; removed graphics packages absent. |
| Dependency smoke test | PASS | `scripts/smoke_test.py`: 11/11 checks passed, including offscreen Qt, OpenCV, NumPy, Shapely, Matplotlib, Pandas, ReportLab, python-docx, NetworkX, pytest and Ruff. |
| Package/removal check | PASS | `scripts/verify_package.py`: `RESULT PASS`; no removed module paths, runtime imports, or discoverable removed packages. |
| Full test suite, clean venv | PASS on repeat | `pytest -q`: **94 passed in 55.10s**. An earlier full run had 93 passes and one timing-threshold failure (181.89 ms vs. 100 ms). The unchanged focused test then passed at **74.00 ms**; the second full run passed. Baseline had the same timing-sensitive test fail once (149.70 ms) and pass on focused retry (7.08s), documented in `baseline_before_3d_removal.md`. No threshold was weakened. |
| UI regressions | PASS | Seven-page count, no renderer navigation label, worker cancellation/close: 3 focused tests passed. |
| UI screenshots and contrast | PASS | Regenerated retained screens at 1280?720, 1600?900 and 1920?1080, light/dark themes, scales 1.0/1.25/1.5. Six batches ? 306 contrast records; **0 failures**. `DOCS/img/ui_after/` contains 126 screenshots and no `simulation_3d_launcher.png`. |
| Search source references | PASS | `rg -n -i 'ursina|panda3d|simulation_3d|three_d' src scripts tests requirements.txt` reports only the explicit negative checks in `check_env.py`, `verify_package.py`, and `test_visualization_descoped.py`. |
| Frozen event/snapshot code | PASS | No diff under `src/simulation` or `src/coverage` from the safety-tagged starting revision. |

The first `verify_package.py` invocation flagged the package names in its environment-check helper; the verifier was corrected to exclude only that helper?s declaration and its own checker code, then passed against the fresh environment. The runtime package scan still covers application and utility modules.

## 2D performance comparison

| Measurement | Before | After | Interpretation |
|---|---:|---:|---|
| Department coverage run elapsed | 7.089 s | 6.881 s in the first full run; 6.898 s in the isolated retry | Similar run duration; this is a single-machine observation, not a statistical performance claim. |
| UI timer gap during full suite | 149.70 ms (baseline, failed) | 181.89 ms (first full run, failed); 74.00 ms (isolated retry, pass); second full suite pass | Timing-sensitive under suite load, as it was before removal. The `<100 ms` threshold was unchanged. |
| UI update rate | Not recorded in baseline | 21.17 Hz in isolated retry | The 2D poller continued updating during the constrained coverage mission. |

The 3D FPS/soak requirement is no longer applicable under ADR-0022; no renderer stability or FPS result is claimed.

## Evidence hashes

SHA-256 values captured after regeneration:

- `requirements.txt`: `0210BBD81B7BDA08C745DF83540BC757DB9636F07753BD06547C6CD73412F731`
- `scripts/check_env.py`: `2E4424BA828C2145FEC7C7E5C40C69880B7C789C3F0DFFFC24763F309739E85C`
- `scripts/verify_package.py`: `06B53FA44177EDA63A5E5A2292D52684EE76B65DB77B92BC284909121AF2017E`
- `DOCS/img/project_home.png`: `3E0A2426F1451470FFC76D2D580E812AF3AFB55AF0BAA61B562215AA7149D584`
- `DOCS/img/2d_simulation.png`: `A58076160B0D48422DFD09B294CF5088A511A2248FDAE0A48B8B6C6AC72FE9C3`

## Human actions and gate

- **Instructor acknowledgement is required** for the FR-21/AC-06 scope change. Until received, AC-06 remains unpassed and release compliance for that MUST is blocked.
- Run the README installation/demo steps on the intended presentation computer and confirm the remaining 2D workflow there.
- Review the regenerated 2D screenshots and confirm the ADR/deviation record matches the course expectations.
- No instructor message was sent by the agent.

Gate: implementation removal and local verification **PASS**; instructor scope approval and target-machine demo confirmation **PENDING HUMAN ACTION**. This report does not claim overall SRS/release compliance.
