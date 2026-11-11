# P7 implementation and verification report

Date: 2026-11-11  
Commit under test: `9364af5b61c2a8395484b608f80c72faeb8806ba` (working tree changes are uncommitted).

## Implemented

- Ursina worker isolated from the PySide6 app with versioned JSONL over QProcess.
- P2 calibration transforms reused by the 3D coordinate adapter.
- Greedy floor and border-wall meshing; DOOR cells remain floor openings;
  calibrated column/cabinet boxes appear only when current occupancy agrees.
- Robot diameter/speed, interpolated `MoveExecuted` playback, cleaned layer,
  route, camera presets/orbit/pan/zoom, speed/pause/step/reset/seek integration.
- GPU-independent geometry, route legality, and event synchronization tests.
- One-command live scene self-test and presentation laptop checklist.

## Acceptance checklist

| Check | Result | Evidence / limitation |
|---|---|---|
| Wall/floor/door/object footprints match grid | PASS | `tests/three_d/test_geometry.py`; exact rectangle expansion and department spec footprints |
| 3D robot route equals engine route | PASS for event-to-world coordinates | Same test extracts `MoveExecuted` cells; 14/14. Rendered path visibility remains blocked by the viewport defect below |
| FPS at least 30 | PARTIAL | Worker samples about 58–60 FPS locally, but captured framebuffer omits world geometry. Presentation laptop must be measured using `docs/3d_demo_checklist.md` |
| Entity budget below 2,000 | PASS | 106 total, 89 static on department scene |
| Renderer launch/close stability | PASS for worker protocol; HUMAN ACTION for full desktop app | 10/10 worker cycles, 0.826–1.147 s startup, exit 0; CSV below. Full Qt-app ten-cycle run is listed in demo checklist |
| Visible 3D scene / cleaned-area low-FPS fallback | FAIL / PARTIAL | Current capture displays HUD only despite populated layout and camera. Automatic below-30-FPS switching also remains unimplemented |
| Full automated suite | PASS | `.venv\\Scripts\\python.exe -m pytest -q`: 81 passed in 54.28 s |

## Department map renderer measurements

| Measure | Result |
|---|---:|
| Map | 127 × 120 at 0.10 m/cell |
| Static scene entities | 89 |
| Total scene entities | 106 |
| Self-test route | 14 movement events, synchronized 14/14 |
| FPS samples (development PC) | about 58–60 |
| 10-cycle worker startup | 0.826–1.147 s; 10/10 exits successful |

Self-test evidence: `scripts/three_d_self_test.py` and `docs/img/three_d_scene.png` (capture currently shows HUD only).  
Cycle evidence: `prototypes/ui_3d_feasibility/cycle_results.csv`.  
Design: `docs/3d_design.md`.  
Target hardware action: `docs/3d_demo_checklist.md`.

## Remaining human action

Fix the missing world rendering in the current capture first. Then run the
checklist on the presentation laptop to record GPU/driver, resolution, minimum
FPS during coverage, and ten full-app launch/close cycles. P7 implementation is
partial and the visual renderer acceptance gate is not met.
