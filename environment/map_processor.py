"""
Smart Vacuum - Department map builder (v0.2)
Traces the hand-drawn plan (pixel coords of the photo) -> metric occupancy grid.
All geometry is in PHOTO PIXELS; PPM converts to metres. Edit the numbers below
to fix any mistake, then re-run.
"""
import json
from pathlib import Path
from collections import deque
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

# ---------------- parameters ----------------
PPM = 108.0          # photo pixels per metre (from 10 m corridor ~ 4.8 m width ~ 2 m)
CELL_M = 0.10        # grid cell size in metres
WALL_PX = 12         # drawn wall thickness (~0.11 m)
ROBOT_DIAMETER_M = 0.35
FREE, OCC, UNK, DOOR = 0, 1, 2, 3

# ---------------- geometry (photo pixels) ----------------
# open walkable zones (x0, y0, x1, y1)
ZONES = {
    # open hall: no left corridor / no inner wall. R6 corner (y=855) -> bottom edge = 6 m
    "hall_top":      (340, 310, 1130, 855),
    "hall_low":      (340, 855, 905, 1370),
    "entrance":      (340, 1370, 860, 1503),
}
# rooms (interior rectangle = wall centre-lines)
ROOMS = {
    "R1 Head of dept (Anas)":      (85, 165, 335, 490),
    "R2 Rawan":                    (395, 165, 595, 310),
    "R3 Abu Ayyash":               (780, 165, 985, 310),
    "R4 Shereen + Nader":          (1130, 215, 1250, 490),
    "R5 Ghattas":                  (1130, 590, 1305, 750),
    "R6 Johnny (dept admin)":      (905, 855, 1285, 1030),
    "R7 Suhail":                   (905, 1105, 1365, 1375),
    "R7b Suhail inner room":       (1175, 1375, 1365, 1520),
    "R8 Mutaghayyir":              (195, 950, 340, 1160),
}
# doors: (x0,y0,x1,y1) carve rectangles across the wall
DOORS = {
    "D R1 (1.2 m)": (323, 360, 347, 490),
    "D R2": (430, 298, 527, 322),
    "D R3": (825, 298, 922, 322),
    "D R4": (1118, 385, 1142, 482),
    "D R5": (1118, 622, 1142, 719),
    "D R6": (985, 843, 1082, 867),
    "D R7": (893, 1175, 917, 1272),
    "D R7b": (1230, 1363, 1327, 1387),
    "D R8": (328, 960, 352, 1057),
}
# extra wall lines: (x0,y0,x1,y1) centre-line segments
EXTRA_WALLS = [
    (1130, 310, 1130, 855),    # right wall of hall (3.6 m wall + bay)
    (1175, 1375, 1365, 1375),  # inner-room divider
]
OBSTACLES = {
    "column 0.5x0.5 m": (833, 528, 887, 582),
    "cabinet 75 cm (left, protrudes 10 cm)": (340, 540, 351, 621),
    "cabinet 60 cm (left, protrudes 10 cm)": (340, 1390, 351, 1455),
}
UNKNOWN_AREAS = {}
START_PX = (665, 1440)

# ---------------- rasterise ----------------
XMIN, YMIN, XMAX, YMAX = 80, 160, 1370, 1530
cell_px = PPM * CELL_M
nx = int(np.ceil((XMAX - XMIN) / cell_px)); ny = int(np.ceil((YMAX - YMIN) / cell_px))
cx = XMIN + (np.arange(nx) + 0.5) * cell_px
cy = YMIN + (np.arange(ny) + 0.5) * cell_px
CX, CY = np.meshgrid(cx, cy)
grid = np.full((ny, nx), OCC, dtype=np.uint8)

def mask(r):
    x0, y0, x1, y1 = r
    return (CX >= x0) & (CX <= x1) & (CY >= y0) & (CY <= y1)

def stamp_line(x0, y0, x1, y1):
    h = WALL_PX / 2
    grid[mask((min(x0, x1) - h, min(y0, y1) - h, max(x0, x1) + h, max(y0, y1) + h))] = OCC

for r in ZONES.values(): grid[mask(r)] = FREE
for r in ROOMS.values(): grid[mask(r)] = FREE
for (x0, y0, x1, y1) in ROOMS.values():
    for seg in [(x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)]:
        stamp_line(*seg)
for seg in EXTRA_WALLS: stamp_line(*seg)
for r in DOORS.values(): grid[mask(r)] = DOOR
for r in OBSTACLES.values(): grid[mask(r)] = OCC
for r in UNKNOWN_AREAS.values(): grid[mask(r)] = UNK

def px2cell(p):
    return int((p[1] - YMIN) // cell_px), int((p[0] - XMIN) // cell_px)
start = px2cell(START_PX)
assert grid[start] in (FREE, DOOR), "start cell not traversable"

# ---------------- validation ----------------
def reach(trav, s):
    seen = np.zeros_like(trav, dtype=bool); seen[s] = True; q = deque([s])
    while q:
        r, c = q.popleft()
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):      # Up, Right, Down, Left
            a, b = r + dr, c + dc
            if 0 <= a < ny and 0 <= b < nx and trav[a, b] and not seen[a, b]:
                seen[a, b] = True; q.append((a, b))
    return seen

trav = (grid == FREE) | (grid == DOOR)
seen = reach(trav, start)
# robot footprint: inflate blocked cells by robot radius (disc)
rad = int(np.ceil(ROBOT_DIAMETER_M / 2 / CELL_M))
blocked = ~trav
infl = blocked.copy()
for dr in range(-rad, rad + 1):
    for dc in range(-rad, rad + 1):
        if dr * dr + dc * dc <= rad * rad:
            infl |= np.roll(np.roll(blocked, dr, 0), dc, 1)
trav_r = ~infl
s2 = start if trav_r[start] else None
seen_r = reach(trav_r, s2) if s2 else np.zeros_like(trav)

report = {"grid_shape": [ny, nx], "cell_m": CELL_M, "free_cells": int(trav.sum()),
          "reachable_from_start": int(seen.sum()), "unreachable_free": int((trav & ~seen).sum()),
          "robot_radius_cells": rad, "reachable_with_robot_footprint": int(seen_r.sum())}
rooms_rep = {}
for name, r in ROOMS.items():
    m = mask(r) & trav
    rooms_rep[name] = {"cells": int(m.sum()), "reachable": bool((m & seen).any()),
                       "reachable_with_footprint": bool((m & seen_r).any())}
report["rooms"] = rooms_rep
print(json.dumps(report, indent=2))

# ---------------- save ----------------
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "original_floor_plan"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
np.save(OUTPUT_DIR / "department_map.npy", grid)
meta = {"cell_m": CELL_M, "origin_px": [XMIN, YMIN], "ppm": PPM, "start_cell": list(start),
        "states": {"FREE": 0, "OCCUPIED": 1, "UNKNOWN": 2, "DOOR": 3}, "version": "0.2-draft"}
with (OUTPUT_DIR / "department_map.json").open("w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

# ---------------- preview ----------------
fig, ax = plt.subplots(figsize=(9, 11))
cmap = ListedColormap(["#f4f4f4", "#1a1a2e", "#f5a623", "#2ecc71"])
ax.imshow(grid, cmap=cmap, vmin=0, vmax=3, interpolation="nearest")
ax.set_xticks(np.arange(0, nx, 10) - .5); ax.set_yticks(np.arange(0, ny, 10) - .5)
ax.set_xticklabels([f"{i*CELL_M:.0f}" for i in range(0, nx, 10)], fontsize=6)
ax.set_yticklabels([f"{i*CELL_M:.0f}" for i in range(0, ny, 10)], fontsize=6)
ax.grid(color="#cccccc", lw=0.3)
for name, (x0, y0, x1, y1) in ROOMS.items():
    ax.text(((x0 + x1) / 2 - XMIN) / cell_px - .5, ((y0 + y1) / 2 - YMIN) / cell_px - .5,
            name.split(" ")[0], ha="center", va="center", fontsize=9, color="#c0392b", weight="bold")
ax.plot(start[1], start[0], "r*", ms=16)
ax.text(start[1] + 2, start[0], "S", color="red", fontsize=12, weight="bold")
ax.legend(handles=[Patch(color="#f4f4f4", label="FREE"), Patch(color="#1a1a2e", label="OCCUPIED/wall"),
                   Patch(color="#2ecc71", label="DOOR")],
          loc="lower left", fontsize=8)
ax.set_title(f"Department map v0.2 - {ny}x{nx} cells @ {CELL_M*100:.0f} cm (axes in metres)")
plt.tight_layout(); plt.savefig(OUTPUT_DIR / "map_preview.png", dpi=110)
