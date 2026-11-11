# P6 UI design (provisional until ADR-0016 is accepted)

**Status:** P6.01 draft only. The P5 event/snapshot API is not frozen; no UI code may consume it until the P5 gate passes.

## Navigation

```text
Project Home
  ├─ Map Editor / Import & Calibration
  ├─ Robot Configuration
  ├─ Algorithm Setup
  ├─ 2D Simulation ── 3D Simulation launcher
  ├─ Results Dashboard
  └─ Report Export
```

The eight screens are Project Home, Map Editor (including import/calibration), Robot Configuration, Algorithm Setup, 2D Simulation, 3D Simulation launcher, Results Dashboard, and Report Export. A persistent left rail selects screens; the status bar shows the loaded map version and experiment run state. Views bind to an `AppController`; they never invoke search algorithms or mutate robot state.

## Layout sketches

```text
┌───────────────┬──────────────────────────────────────────┐
│ Navigation    │ Project Home                              │
│ Home          │ [Load department map v1] [Open map…]      │
│ Map Editor    │ Recent maps / runs     Project information│
│ Robot         │                                           │
│ Algorithms    │                                           │
│ Simulation    │                                           │
│ Results       │                                           │
│ Export        │                                           │
├───────────────┴──────────────────────────────────────────┤
│ Map v1 • Idle                                             │
└──────────────────────────────────────────────────────────┘
```

```text
┌───────────────┬─────────────────────────────┬────────────┐
│ Navigation    │ Map canvas                  │ Inspector  │
│               │ zoom / pan / grid           │ Paint tool │
│               │ occupancy + semantic marks  │ Validation │
│               │ click to choose start/goal  │ Undo/Redo  │
└───────────────┴─────────────────────────────┴────────────┘
```

```text
┌───────────────┬─────────────────────────────┬────────────┐
│ Navigation    │ 2D map                      │ Live HUD   │
│               │ explored / frontier         │ Battery    │
│               │ path / cleaned / robot      │ Time       │
│               │ legend uses symbols/patterns│ Lifetime   │
│               │                             │ Coverage   │
├───────────────┴─────────────────────────────┴────────────┤
│ Run  Pause  Resume  Step  Reset  Stop   Speed 0.25×–16× │
└─────────────────────────────────────────────────────────┘
```

Configuration screens use a central form and a right-side contextual explanation/validation area. Algorithm Setup shows registered algorithms, read-only heuristic and U,R,D,L order, mission mode, target policy, and point-to-point goal controls. Results uses a comparison table and selectable run detail; Report Export previews the chosen CSV/PDF output and destination.

## Visual language and accessibility

Occupancy uses both color and texture: occupied cells are dark crosshatch, unknown cells diagonal hatch with `?`, doors receive a labeled gap marker, explored cells use dots, frontier uses an outlined diamond, route uses a solid line with arrows, cleaned cells use a stipple, robot is a circle with heading, and start is a labeled `S`. Colors use a colorblind-safe palette and remain distinguishable in grayscale. Scale strokes, labels, and hit targets with device-pixel ratio.

## Workflow state diagram

```text
[Home]
   │ load/create project
   ▼
[Map ready] ── edit/import/calibrate ──► [Map validation]
   │ valid map + start
   ▼
[Configure robot] ──► [Choose algorithm + mission]
                           │ valid experiment
                           ▼
                        [Ready]
                           │ Run
                           ▼
                 [Running] ◄── Resume ── [Paused]
                  │  │  │                   ▲
                  │  │  └── Pause ──────────┘
                  │  └── Stop/Cancel
                  ├── mission/resource stop
                  ▼
               [Completed] ──► [Results] ──► [Export]
                  │ Reset
                  └────────────► [Ready]
```

Invalid configuration stays on its screen with field-level feedback. A worker owns the run; queued, rate-limited signals deliver events/snapshots to the controller and view. Window close requests cancellation and waits for worker teardown before exit. This lifecycle is a design constraint only until ADR-0016 and P6 implementation are accepted.
