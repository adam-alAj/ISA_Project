# Geometry and dimension consistency — department map v0.3 draft

## Method and limits

Room areas are estimates from traced rectangle proportions at 108 px/m, constrained by the user-confirmed ordering. They are not measured from the drawing. The source photo is not yet present, so source-dependent checks remain pending. Areas use the interior rectangle dimensions before raster wall stamping.

## Calibration

Only confirmed values calibrate the model: right hall wall 5 m; lower span from the R6 corner to the floor bottom 6 m; doors 0.9 m/1.2 m; column 0.5 m; cabinets 75 cm/60 cm. The 4.8 m and 2 m labels are informational only and are excluded from calibration and geometry.

| Confirmed value | Traced extent | Implied scale | Residual vs 108 px/m | Traced extent at model scale |
|---|---:|---:|---:|---:|
| 5 m right hall wall | 545 px | 109 px/m | +0.93% | 5.046 m (+0.93%) |
| 6 m lower span | 648 px | 108 px/m | 0.00% | 6.000 m (0.00%) |
| 0.9 m doors D2-D9 | 97 px | 107.778 px/m | -0.21% | 0.898 m (-0.21%) |
| 1.2 m door D1 | 130 px | 108.333 px/m | +0.31% | 1.204 m (+0.31%) |
| 0.5 m column | 54 px | 108 px/m | 0.00% | 0.500 m (0.00%) |
| 75 cm cabinet | 81 px | 108 px/m | 0.00% | 75.0 cm (0.00%) |
| 60 cm cabinet | 65 px | 108.333 px/m | +0.31% | 60.2 cm (+0.31%) |

The 10 cm cabinet protrusion traces to 11 px = 10.2 cm (+1.85%). The 0.10 m cell is provisional. The 4.8 m and 2 m drawing labels are not used; photo review remains a low-priority human action. The old 10 m, 3.6 m, 4.5 m and 1.4 m labels are superseded.

## Room areas before and after geometry correction

Interior areas are calculated as `(x1-x0)*(y1-y0)/108²`. R7b belongs to R7 and is listed for reference only, excluded from the order comparison. Only the outer sides of R4, R5, and R6 changed; R1 and R7 remain as traced. Hall zones, doors, column, cabinets, and start remain fixed.

| Room | v0.2 area (m²) | v0.3 area (m²) | v0.3 bounds (photo px) |
|---|---:|---:|---|
| R7 | 10.6481 | 10.6481 | (905,1105)-(1365,1375) |
| R1 | 6.9659 | 6.9659 | (85,165)-(335,490) |
| R4 | 2.8292 | 4.7154 | (1130,215)-(1330,490) |
| R6 | 5.7013 | 3.8259 | (905,855)-(1160,1030) |
| R2 | 2.4863 | 2.4863 | (395,165)-(595,310) |
| R3 | 2.5484 | 2.5484 | (780,165)-(985,310) |
| R5 | 2.4005 | 2.6063 | (1130,590)-(1320,750) |
| R8 | 2.6106 | 2.6106 | (195,950)-(340,1160) |
| R7b (excluded) | 2.3620 | 2.3620 | (1175,1375)-(1365,1520) |

The equal group R2/R3/R5/R8 ranges from 2.4863 to 2.6106 m², within 2.47–2.73 m² (2.6 m² ±5%). Strict order is R7 > R1 > R4 > R6 > max(R2,R3,R5,R8). No room rectangles overlap or leave map bounds.

## Regression evidence and remaining limits

The added regression test compares v0.2 and v0.3 hall-zone states and door-cell sets, checks fixed start/obstacle positions, bounds and room overlap, area ordering, and room reachability with and without the 0.35 m footprint. Independent raster reproduction produced 6,722 hall cells with zero state changes and zero door-cell symmetric difference. Reachability is recorded in `validation.md`.

The source image is absent, so orientation, exact label association, drawing marks, and omitted features cannot yet be checked. Geometry estimates do not claim measured room dimensions. The map remains unfrozen pending source review, review checklist sign-off, and the signed freeze statement.
