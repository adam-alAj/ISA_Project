# 3D demo machine checklist

Run this on the presentation laptop before the demo. It records hardware data;
the development PC's FPS does not substitute for this measurement.

## Before the demo

- [ ] Connect AC power and select the normal/high-performance power profile.
- [ ] Install the project requirements in `.venv`; run `scripts/three_d_self_test.py`.
- [ ] Record Windows version, GPU model/driver, display resolution, Python and
      Ursina versions, and whether Panda3D selected hardware or software GL.
- [ ] Confirm `docs/img/three_d_scene.png` shows the department map, doors,
      obstacles, robot, route, and cleaned floor without missing textures.
      Current development capture shows only the HUD; resolve this renderer
      defect before treating the 3D demo as ready.
- [ ] Record every `fps_sample` from the self-test and report the minimum.
- [ ] Launch 3D from the desktop app, run point-to-point and coverage playback,
      and check that 2D and 3D end on the same robot cell.
- [ ] Pause, step, reset, change speed, close, and relaunch the 3D window.
- [ ] Repeat launch/close ten times; record any failed launch or forced kill.

## Pass criteria and fallback

- Target: at least 30 FPS throughout the representative department-map playback.
- The headless geometry and event-sync tests must pass on the same build.
- If FPS falls below 30 or the renderer fails to start, use the 2D view for
  cleaned coverage and show the saved 3D route screenshot/video as backup.
- Human action: run the checklist on the actual presentation laptop and append
  machine details, minimum FPS, and ten-cycle result to the demo report.

One-command local renderer check:

```powershell
.\.venv\Scripts\python.exe scripts\three_d_self_test.py
```
