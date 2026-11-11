# P6 usability test (human session pending)

**Human action required:** run this script with a participant unfamiliar with the project, then record observations and questionnaire answers. Do not present the following as completed research.

## Tasks

1. Load the department map v1 and identify the map version and start marker.
2. Change the robot battery and operational lifetime independently, then save the experiment configuration.
3. Select each of two different search algorithms and run the same point-to-point scenario; identify the route and stop reason.
4. Run coverage, pause and resume it, then identify cleaned cells, coverage percentage, remaining battery, and current target.
5. Reset the run, find the results comparison, and export a report.

## Success criteria

- Participant completes each task without editing project files or receiving procedural hints.
- Participant can distinguish occupied, unknown, door, explored, frontier, route, cleaned, robot, and start states without relying on color alone.
- Participant correctly explains that search plans point-to-point routes while the coverage controller selects repeated targets.
- Participant correctly reads independent battery/lifetime values and the final stop reason.
- No unrecoverable input, lost configuration, or UI freeze occurs.

Record completion, elapsed time, errors, requests for help, and confidence (1–5) for each task. Any task not completed is a usability finding, not a participant failure.

## Questionnaire

Rate 1 (strongly disagree) to 5 (strongly agree):

1. I could tell what the next step in the workflow was.
2. The map states and legend were easy to understand.
3. I could tell the difference between route planning and floor coverage.
4. Battery and lifetime information were clear.
5. I could recover from a mistaken setting or action.

Free response: What was confusing? What information was missing? What would you change first?
