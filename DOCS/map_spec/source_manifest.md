# Map source manifest

## Source drawing

| Field | Record |
|---|---|
| Expected source | Original hand-drawn department floor-plan photo |
| Expected location | `assets/floor_plans/` |
| Present | **No** — no PNG, JPG/JPEG, or PDF source drawing is in the workspace |
| SHA-256 | Not available; do not substitute the derived preview as the original |
| Format, dimensions, EXIF orientation, page size | Cannot inspect until the original is supplied |
| Readability, logos, watermarks, clipping | Cannot inspect until the original is supplied |
| Preservation | `assets/floor_plans/README.md` requires source copies to remain untouched |

**P1.01–P1.02 are blocked on the missing source photo.** Existing v0.2 geometry can still be documented, but the preview is not evidence of the original drawing or its annotations.

## Existing derived inputs

SHA-256 values are recorded from the files in the repository. The map array, metadata, and preview match the previously committed v0.2 artifacts and were not regenerated in P1.

| File | Size | SHA-256 | Role |
|---|---:|---|---|
| `data/maps/department_v0_2/department_map.npy` | 15,368 bytes | `4A9653FFFA536926CA5FA06FE833C96429D6FB30F98391F1518DE7FBE1127EDB` | `uint8` occupancy array, 127 × 120 |
| `data/maps/department_v0_2/department_map.json` | 223 bytes | `9791874F80933079BDB700DE3AE408FE58910BC78413C6502652DC5695813129` | Cell size, origin, PPM, start, states, draft version |
| `data/maps/department_v0_2/map_preview.png` | 43,676 bytes | `A26692F2A4D41E4E785411BC43400AFE1ED68A048145AE1985531582FF54A15F` | Derived grid preview, 990 × 1210 pixels |
| `src/map_processing/legacy_build_map.py` | — | `A7245325C2D18E39F0E6B32F08D03AB9648228FF818F58BE0CC5C8EBB827E13A` | Traced-geometry source; not executed in P1 |

## Map metadata

- Version: `0.2-draft`; array shape `(127, 120)`; `uint8` cell states.
- Pixel-coordinate origin `(80, 160)`; scale `108 px/m`; cell size `0.10 m`.
- State values: `FREE=0`, `OCCUPIED=1`, `UNKNOWN=2`, `DOOR=3`.
- Serialized cell counts: `FREE=9,978`, `OCCUPIED=5,064`, `UNKNOWN=0`, `DOOR=198` (15,240 total). Thus 10,176 cells are free or door passages.
- Start pixel `(665, 1440)` maps to start cell `(118, 54)` using the builder's floor-based conversion.
- Source description in the shared context identifies the drawing as a hand-drawn demo/fake-data plan.
