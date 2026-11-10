# Department map v0.2 definition

## Boundary and exclusions

The simulated floor includes the open hall, entrance, and interiors of R1–R8 plus inner room R7b. The model uses the traced geometry in `legacy_build_map.py`: hall zones `(340,310,1130,855)`, `(340,855,905,1370)`, entrance `(340,1370,860,1503)`, and the nine room rectangles in `elements.yaml`. Regions outside these walkable zones and rooms remain `OCCUPIED` in the raster. This is a traced simulation boundary, not proof of the actual building boundary; verify against the source photo when available.

The simulated boundary excludes image margins and areas beyond the traced floor-plan geometry. Logos or watermarks outside the floor are not represented; whether they appear on the source sheet cannot be checked until the photo is supplied.

No cleaning zones are excluded in v0.2. The orange/hatched area was a misreading and is removed. The column and both cabinets are fixed obstacles. The exterior and untraced cells are represented as `OCCUPIED`; the current schema does not separately label “outside.”

## Door and wall policy

All nine doors are **permanently open passages** in v1.0. Closed or conditional doors are future work. Each door rectangle crosses its room wall and has a nominal 24 px thickness, versus 12 px wall thickness. At 0.10 m/cell, 24 px corresponds to 2.22 cells, so the intended crossing band is at least two cells thick. The opening span is 97 px for D2–D9 and 130 px for D1. Check every wall edge is closed except these listed openings; map-connectivity verification belongs to P2.

## Occupancy and cleaning layers

| Occupancy value | Meaning in this map | Traversable? |
|---|---|---|
| `FREE=0` | Hall/entrance/room floor | Yes |
| `OCCUPIED=1` | Walls, column, cabinets, and raster cells outside traced floor regions | No |
| `UNKNOWN=2` | Reserved state; unused in v0.2 | **Never** |
| `DOOR=3` | Open doorway crossing | Yes |

`CLEANED` is a separate boolean layer and is not encoded in the occupancy array. Cleaning never changes traversability.

## Movement and coordinates

Use four-neighbor movement in fixed order Up, Right, Down, Left; no diagonal transitions. A future diagonal extension must define corner-cut prevention, obstacle clearance, transition cost, and a consistent admissible heuristic before implementation. Grid coordinates are `(row, column)` with row increasing downward; pixel coordinates are `(x,y)`. The legacy conversion is floor-based: `row=int((y-160)//10.8)`, `column=int((x-80)//10.8)`.

## Start and demo targets

The supplied start is S at cell `(118,54)`. Proposed department-map goals and the one synthetic no-path case are in `demo_goals.csv`. The around-column scenario uses a separate hall start `(36,68)` and target `(36,78)` so the straight segment crosses the modeled column. An independent 4-neighbor BFS over the existing NumPy array verified that all eight department-map goals are reachable; endpoint states are `FREE`. The P2 project API and robot-footprint clearance still require their own tests.
