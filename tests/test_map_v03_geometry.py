"""Regression tests for the v0.3 room-size correction."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
V02_DIR = ROOT / "data" / "maps" / "department_v0_2"
V03_DIR = ROOT / "data" / "maps" / "department_v0_3"
ROOM_SIZE_TARGET_M2 = 2.6
ROOM_SIZE_TOLERANCE = 0.05
CELL_M = 0.10
PPM = 108.0
ORIGIN_XY = (80.0, 160.0)
ZONES_PX = (
    (340, 310, 1130, 855),
    (340, 855, 905, 1370),
    (340, 1370, 860, 1503),
)
FIXED_OBSTACLES_PX = (
    (833, 528, 887, 582),
    (340, 540, 351, 621),
    (340, 1390, 351, 1455),
)
EQUAL_SIZE_ROOMS = ("R2", "R3", "R5", "R8")
ORDERED_ROOMS = ("R7", "R1", "R4", "R6")


def load_map(directory: Path) -> tuple[np.ndarray, dict]:
    """Load one versioned array and its metadata."""
    grid = np.load(directory / "department_map.npy")
    metadata = json.loads((directory / "department_map.json").read_text(encoding="utf-8"))
    return grid, metadata


def room_mask(grid: np.ndarray, bounds: list[int]) -> np.ndarray:
    """Return cells whose centers lie inside a pixel-coordinate room rectangle."""
    x0, y0, x1, y1 = bounds
    rows, cols = np.indices(grid.shape)
    x = ORIGIN_XY[0] + (cols + 0.5) * PPM * CELL_M
    y = ORIGIN_XY[1] + (rows + 0.5) * PPM * CELL_M
    return (x >= x0) & (x <= x1) & (y >= y0) & (y <= y1)


def reachable(traversable: np.ndarray, start: tuple[int, int]) -> np.ndarray:
    """Compute deterministic four-neighbor reachability in U,R,D,L order."""
    seen = np.zeros(traversable.shape, dtype=bool)
    if not traversable[start]:
        return seen
    seen[start] = True
    queue = deque([start])
    for_r_c = ((-1, 0), (0, 1), (1, 0), (0, -1))
    while queue:
        row, col = queue.popleft()
        for dr, dc in for_r_c:
            nr, nc = row + dr, col + dc
            if (
                0 <= nr < traversable.shape[0]
                and 0 <= nc < traversable.shape[1]
                and traversable[nr, nc]
                and not seen[nr, nc]
            ):
                seen[nr, nc] = True
                queue.append((nr, nc))
    return seen


def footprint_traversable(grid: np.ndarray, diameter_m: float) -> np.ndarray:
    """Inflate blocked cells using the same circular cell-radius rule as the builder."""
    traversable = np.isin(grid, (0, 3))
    blocked = ~traversable
    radius = int(np.ceil(diameter_m / 2 / CELL_M))
    inflated = blocked.copy()
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if dr * dr + dc * dc <= radius * radius:
                inflated |= np.roll(np.roll(blocked, dr, axis=0), dc, axis=1)
    return ~inflated


def hall_mask(shape: tuple[int, int]) -> np.ndarray:
    """Rasterize the three fixed hall/entrance zones using builder cell centers."""
    rows, cols = np.indices(shape)
    x = ORIGIN_XY[0] + (cols + 0.5) * PPM * CELL_M
    y = ORIGIN_XY[1] + (rows + 0.5) * PPM * CELL_M
    mask = np.zeros(shape, dtype=bool)
    for x0, y0, x1, y1 in ZONES_PX:
        mask |= (x >= x0) & (x <= x1) & (y >= y0) & (y <= y1)
    return mask


def test_room_size_order_and_equal_group_tolerance() -> None:
    """The corrected room areas obey the user-confirmed ordering and tolerance."""
    _, metadata = load_map(V03_DIR)
    areas = metadata["room_areas_m2"]
    bounds = metadata["room_bounds_px"]
    low = ROOM_SIZE_TARGET_M2 * (1 - ROOM_SIZE_TOLERANCE)
    high = ROOM_SIZE_TARGET_M2 * (1 + ROOM_SIZE_TOLERANCE)
    equal_group = [areas[room] for room in EQUAL_SIZE_ROOMS]

    assert all(low <= area <= high for area in equal_group)
    assert areas["R7"] > areas["R1"] > areas["R4"] > areas["R6"] > max(equal_group)
    assert "R7b" not in EQUAL_SIZE_ROOMS
    assert bounds["R1"] == [85, 165, 335, 490]
    assert bounds["R7"] == [905, 1105, 1365, 1375]


def test_hall_and_door_cells_are_unchanged_from_v02() -> None:
    """Room edits leave hall-zone states and the complete door-cell set unchanged."""
    v02, _ = load_map(V02_DIR)
    v03, _ = load_map(V03_DIR)
    assert v02.shape == v03.shape

    hall = hall_mask(v02.shape)
    np.testing.assert_array_equal(v02[hall], v03[hall])
    np.testing.assert_array_equal(np.argwhere(v02 == 3), np.argwhere(v03 == 3))

    for bounds in FIXED_OBSTACLES_PX:
        obstacle = room_mask(v02, list(bounds))
        np.testing.assert_array_equal(v02[obstacle], v03[obstacle])
    _, metadata_v02 = load_map(V02_DIR)
    _, metadata_v03 = load_map(V03_DIR)
    assert metadata_v02["start_cell"] == metadata_v03["start_cell"] == [118, 54]


def test_room_bounds_do_not_overlap_or_exceed_map_domain() -> None:
    """Room rectangles remain in-domain and have no positive-area intersections."""
    _, metadata = load_map(V03_DIR)
    bounds = metadata["room_bounds_px"]
    domain = (80, 160, 1370, 1530)
    rooms = list(bounds.items())
    for room_id, (x0, y0, x1, y1) in rooms:
        assert domain[0] <= x0 < x1 <= domain[2], room_id
        assert domain[1] <= y0 < y1 <= domain[3], room_id
    for index, (id_a, a) in enumerate(rooms):
        for id_b, b in rooms[index + 1 :]:
            overlap_x = min(a[2], b[2]) - max(a[0], b[0])
            overlap_y = min(a[3], b[3]) - max(a[1], b[1])
            assert overlap_x <= 0 or overlap_y <= 0, f"{id_a} overlaps {id_b}"


def test_all_rooms_are_reachable_with_and_without_robot_footprint() -> None:
    """Every room has reachable floor cells for point and 0.35 m robot models."""
    grid, metadata = load_map(V03_DIR)
    start = tuple(metadata["start_cell"])
    normal_seen = reachable(np.isin(grid, (0, 3)), start)
    footprint_seen = reachable(footprint_traversable(grid, 0.35), start)

    for room_id, bounds in metadata["room_bounds_px"].items():
        mask = room_mask(grid, bounds)
        assert np.any(mask & normal_seen), f"{room_id} is not reachable without footprint inflation"
        assert np.any(mask & footprint_seen), f"{room_id} is not reachable with footprint inflation"
