# Unresolved map decisions

## Items awaiting the source photo

- The original photo is absent. Its SHA-256, file format, dimensions, EXIF orientation, page size, readability, logos, and watermarks cannot yet be recorded.
- Exact drawing references for the 4.8 m and 2 m labels are uncertain. Current geometry gives plausible candidate spans, but these must be checked against the actual annotations.
- The 10 m corridor label is superseded by the user-confirmed open-hall interpretation; review the source to ensure there is no separate boundary detail that changes the model.
- Proportional room dimensions in the register describe traced geometry, not surveyed dimensions.
- The traced geometry makes R6 about 5.701 m² and R4 about 2.829 m², conflicting with the confirmed size order R4 > R6. The team/map owner must resolve this against the original drawing; do not freeze the map or alter the rectangles without a documented decision/ADR.
- The annotated overlay was assembled from the existing PNG using the built-in Windows drawing API because Python/Matplotlib is unavailable. The output was visually inspected and the source preview was preserved; rerender with Matplotlib when the project environment is available if strict P1.16 tool-method compliance is required.

## Items awaiting team or instructor decisions

- Confirm that all doors are modeled permanently open for the demonstration.
- Approve the proposed demo start/goal scenarios and whether the synthetic unreachable case is sufficient.
- Confirm the provisional robot diameter, cleaning width, speed, battery, lifetime, and energy coefficients.
- Confirm whether cleaning credit is one cell per visit or a physical-width footprint, and whether the around-column demonstration may use its alternate start cell.
- Confirm the 0.10 m resolution after the numeric study; measured builder timing and actual algorithm expansion counts require a Python run.
- Confirm course interpretation of IDFS/IDDFS and any map-specific rubric requirements.
- In P2, verify obstacle inflation and connectivity at map boundaries; the legacy builder shifts masks with `numpy.roll`, which wraps at array edges.

## Freeze statement

I have reviewed the source drawing, map boundaries, dimensions, doors, obstacles, start and goals, resolution, and provisional robot parameters. I approve `department_map_v0_2` as the baseline for P2 environment implementation, subject to the conditions listed above.

Approver: ______________________________  Role: ___________________________

Signature: _____________________________  Date: ___________________________

**Status: NOT APPROVED.** This statement is ready for human sign-off. P1 is not frozen until the source photo is reviewed and an authorized reviewer signs and resolves or accepts the listed conditions.
