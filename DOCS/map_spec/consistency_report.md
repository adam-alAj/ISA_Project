# Geometry and dimension consistency

## Method and limits

The traced rectangles and pixel-to-metre comparisons below come from `legacy_build_map.py` using `PPM = 108 px/m`. These are comparisons of the current model to the dimensions recorded in the project context, not a fresh measurement of the paper plan. The source photo is absent, so the label-to-segment associations for 4.8 m and 2 m cannot be visually confirmed. Deviations are `(traced metres - stated metres) / stated metres × 100`.

## Labelled dimension checks

| Stated dimension | Traced segment | Traced size | Deviation | Status |
|---|---|---:|---:|---|
| 4.8 m | Candidate entrance span, x=340..860 (520 px) | 4.815 m | +0.31% | Candidate match; verify label position on source photo |
| 5 m | Hall right wall, y=310..855 (545 px) | 5.046 m | +0.93% | Consistent; user-confirmed dimension |
| 6 m | R6 corner to modeled floor bottom, y=855..1503 (648 px) | 6.000 m | 0.00% | Consistent; user-confirmed combined span |
| 2 m | Candidate R8 interior height, y=950..1160 (210 px) | 1.944 m | -2.78% | Candidate only; confirm the drawing reference |
| 0.9 m | Doors D2-D9 (97 px opening span) | 0.898 m | -0.21% | Consistent at stated precision |
| 1.2 m | Door D1 (130 px opening span) | 1.204 m | +0.31% | Consistent at stated precision |
| 0.5 × 0.5 m | Column rectangle (54 × 54 px) | 0.500 × 0.500 m | 0.00% | Consistent |
| 75 cm / 60 cm | Cabinet along-wall spans (81 / 65 px) | 75.0 / 60.2 cm | 0.00 / +0.31% | Consistent at stated precision |
| 10 cm protrusion | Cabinet protrusion (11 px) | 10.2 cm | +1.85% | Consistent at stated precision |

No directly matched dimension exceeds the 15% review threshold. The 4.8 m and 2 m comparisons remain candidates rather than verified associations. The 10 m, 3.6 m, 4.5 m, and 1.4 m legacy labels are marked superseded in `dimensions.csv` and are not used as acceptance measurements.

## Calibration anchors and residuals

The legacy builder comment says `PPM=108 px/m` was based on a “10 m corridor ~ 4.8 m width ~ 2 m.” It does not store the dimension-line endpoints, and the source photo is missing. The two candidate spans that can be compared to traced geometry are:

| Legacy label | Candidate traced span | Implied scale | Scale residual vs 108 px/m | Dimension residual at 108 px/m | Confidence |
|---|---:|---:|---:|---:|---|
| 4.8 m width | 520 px entrance span | 108.333 px/m | +0.31% | +0.31% (4.815 m) | Candidate only |
| 2 m | 210 px R8 height | 105.000 px/m | -2.78% | -2.78% (1.944 m) | Candidate only |
| 10 m corridor | Superseded; no matching corridor segment in the confirmed open-hall model | — | Not computable | Not applicable | Retired anchor |

The signed scale residual is `(implied scale - 108) / 108 × 100`. These comparisons show a plausible scale consistency, not proof of the annotation locations. Confirm all three labels against the drawing before freezing calibration.

For future maps without a reliable dimension or scale, use abstract grid units and label all resulting distances and reports as grid units; do not imply metric calibration.

## Traced room dimensions

Room sizes are **estimated from traced proportions**, not independently measured from the missing drawing. Values use rectangle edge differences divided by 108 px/m; this describes the model only.

| Room | Traced size (m), width × height | Pixel rectangle |
|---|---:|---|
| R1 | 2.315 × 3.009 | (85,165)–(335,490) |
| R2 | 1.852 × 1.343 | (395,165)–(595,310) |
| R3 | 1.898 × 1.343 | (780,165)–(985,310) |
| R4 | 1.111 × 2.546 | (1130,215)–(1250,490) |
| R5 | 1.620 × 1.481 | (1130,590)–(1305,750) |
| R6 | 3.519 × 1.620 | (905,855)–(1285,1030) |
| R7 | 4.259 × 2.500 | (905,1105)–(1365,1375) |
| R7b | 1.759 × 1.343 | (1175,1375)–(1365,1520) |
| R8 | 1.343 × 1.944 | (195,950)–(340,1160) |

## Findings for review

- The builder's geometry and the accepted layout decisions agree on the open hall, the 5 m east wall, the combined 6 m lower span, nine open doors, one column, and two cabinets.
- The traced room areas conflict with the confirmed room-size order `R7 > R1 > R4 > R6 > the rest`: R6 is 380 × 175 = 66,500 px² (5.701 m²), while R4 is 120 × 275 = 33,000 px² (2.829 m²). The current R6 is about 101.5% larger than R4, despite the confirmed order placing R4 above R6. This is a material geometry discrepancy; do not freeze or silently alter it. The source photo and a user/map-owner decision are needed.
- The 0.10 m grid and obstacle inflation are modeling choices. They do not establish that the real robot fits through a real doorway.
- Because the source photo is missing, this report cannot confirm page orientation, image quality, marks/logos, the location of all written dimensions, or whether any omitted drawing detail was interpreted incorrectly.
- The directly matched linear labels are within 15%, but the R4/R6 area-order discrepancy is flagged for human review. Source-dependent checks remain pending rather than being treated as passed.
