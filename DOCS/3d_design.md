# P7 3D scene and playback design

## Scene contract

The 3D process is a renderer. It receives the current map and calibration plus
the simulation's versioned events over JSON Lines; it does not choose targets,
plan routes, or execute robot actions. The coordinate adapter delegates cell
and pixel transforms to `src.environment.coords`, keeping the calibrated scale
shared with the 2D map.

For a cell `(row, col)` and cell width `s` metres, the rendered centre is
`((col + 0.5) * s, 0, -(row + 0.5) * s)`. FREE and DOOR form the floor mask.
Greedy rectangles tile that mask exactly. Walls are OCCUPIED cells adjacent to
the floor; outer UNKNOWN/void cells do not become geometry. Spec columns and
cabinets are separated from wall boxes when their calibrated raster footprint
still agrees with the current occupied grid. A mismatch means the map was
edited, so the edited occupancy is rendered as regular wall geometry instead.
Door cells never enter the wall mask.

The floor is at y=-0.02 m, the cleaned overlay at y=0.008 m, and the route at
y=0.012 m to avoid z-fighting. Structural wall height defaults to 2.7 m.
Robot diameter and speed come from `RobotConfig`. The scene builder exposes
merged masks for tests and reports 89 static entities on the department map;
the live worker reported 106 entities total, below the 2,000 entity budget.

## Playback and synchronization

The Qt client launches `worker.py` through `QProcess`. Schema 1 JSONL carries
`init`, `event`, `play`, `pause`, `step`, `reset`, `speed`, `seek`, `capture`,
and `close` messages. The event player interpolates between `MoveExecuted`
cell centres using the event's simulation duration and the shared playback
multiplier. Cleaning cells update in batches; the 3D process receives no
independent simulation state transitions. If the bounded P5 event ring has
already advanced past a renderer's next sequence, the Qt side sends a `seek`
snapshot to resynchronize rather than animate an incomplete route.

Camera presets are reset, top-down, and follow. The bundled Ursina
`EditorCamera` supplies orbit, pan, and zoom; camera height/target depth are
clamped and lens near/far planes are set for the full map. `T`, `F`, and `R`
select top, follow, and reset.

## Measurements and limitations

On the development PC (Windows, Python 3.12.10, Ursina 8.3.0, PySide6 6.12.0),
`python scripts/three_d_self_test.py` loaded the department map, created 106
entities (89 static), replayed 14 movement events, and sampled about 58–60 FPS.
However, inspection of `docs/img/three_d_scene.png` found only the Ursina HUD;
the world geometry is absent from the captured framebuffer even though the
scene layout and camera transform are populated. Visual rendering is therefore
not accepted and needs a renderer/view investigation before demo use. These
local FPS measurements do not establish target-machine performance. Cleaned
floor rendering is batched and route geometry is retained; route-only fallback
below 30 FPS is not automatic.

## Verification

`tests/three_d` checks calibration round trips, exact greedy tiling, department
map floor/wall/object footprints, route legality and synchronization with
engine `MoveExecuted` positions. These tests do not require a GPU. The live
self-test exercises Ursina, takes the screenshot, and closes the process. A
separate 10-cycle worker lifecycle benchmark is recorded in
`prototypes/ui_3d_feasibility/cycle_results.csv`.
