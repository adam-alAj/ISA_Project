# P6 manual workflow check (10 minutes)

Run once with a person unfamiliar with the code. Use the department map and
record observations immediately. This is the deferred usability action planned
for P9.16; do not prefill the results table.

1. **Open the app** using `python main.py`. Expect the Project Home screen and
   left navigation with eight sections.
2. **Load department map v1.** Expect a 127 × 120 grid and the stored start
   position in the project summary.
3. **Inspect the map legend.** Locate wall, free, unknown, door, explored,
   frontier, route, cleaned, robot, and start cues; confirm the patterns and
   markers remain distinguishable without relying on color.
4. **Select or confirm the start** in Map Editor. Expect a valid start marker;
   try a wall cell and confirm it is rejected with a message.
5. **Configure the robot.** Set a non-default battery and lifetime. Expect the
   two independent values to remain visible after applying configuration.
6. **Choose BFS and point-to-point mode.** Select the demo goal `(118, 68)`.
   Expect the algorithm and goal to appear in the setup/map views.
7. **Run point-to-point.** Expect explored cells and route to appear, then a
   stop/result summary with steps, resources, and mission outcome.
8. **Switch to coverage and run.** Expect cleaned cells and the coverage value
   to update. Pause/resume or step once if the run lasts long enough.
9. **Inspect termination and results.** Expect a stop-reason banner and a
   dashboard whose displayed values agree with the final HUD/result summary.
10. **Save and reload the experiment.** Expect map, start, robot settings,
    algorithm, mode, and recent run/configuration entries to remain available.

## Results

| Step | Pass/fail | Notes | Date |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |
| 6 |  |  |  |
| 7 |  |  |  |
| 8 |  |  |  |
| 9 |  |  |  |
| 10 |  |  |  |

Participant's first-impression questionnaire: Which step was least clear? What
did you expect to happen? Which result was hardest to find? What would you
change first?
