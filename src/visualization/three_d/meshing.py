"""Pure, GPU-independent grid geometry and greedy rectangle meshing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from src.environment.coords import cell_to_pixel_center
from src.map_processing.constants import CellState


@dataclass(frozen=True, order=True)
class GridRect:
    """A row/column rectangle with height and width measured in cells."""

    row: int
    col: int
    height: int
    width: int


@dataclass(frozen=True)
class SceneObject:
    """A named, low obstacle rendered separately from structural walls."""

    name: str
    rectangles: tuple[GridRect, ...]
    height_m: float


@dataclass(frozen=True)
class SceneLayout:
    """Exact cell-footprint description used by the 3D scene builder."""

    floors: tuple[GridRect, ...]
    walls: tuple[GridRect, ...]
    objects: tuple[SceneObject, ...]
    floor_mask: np.ndarray
    wall_mask: np.ndarray
    object_mask: np.ndarray
    cell_m: float
    wall_height_m: float

    @property
    def static_entity_count(self) -> int:
        """Number of merged scene entities before the robot and dynamic meshes."""
        return len(self.floors) + len(self.walls) + len(self.objects)


def greedy_rectangles(mask: np.ndarray) -> tuple[GridRect, ...]:
    """Cover true cells exactly with non-overlapping greedy rectangles."""
    remaining = np.asarray(mask, dtype=bool).copy()
    if remaining.ndim != 2:
        raise ValueError("meshing mask must be two-dimensional")
    rows, cols = remaining.shape
    result: list[GridRect] = []
    for row in range(rows):
        for col in range(cols):
            if not remaining[row, col]:
                continue
            width = 1
            while col + width < cols and remaining[row, col + width]:
                width += 1
            height = 1
            while row + height < rows and remaining[row + height, col:col + width].all():
                height += 1
            remaining[row:row + height, col:col + width] = False
            result.append(GridRect(row, col, height, width))
    return tuple(result)


def expand_rectangles(shape: tuple[int, int], rectangles: tuple[GridRect, ...]) -> np.ndarray:
    """Reconstruct a boolean grid from rectangles, rejecting overlap/out-of-bounds."""
    result = np.zeros(shape, dtype=bool)
    for rect in rectangles:
        view = result[rect.row:rect.row + rect.height, rect.col:rect.col + rect.width]
        if view.shape != (rect.height, rect.width) or view.any():
            raise ValueError("rectangle set overlaps or exceeds the grid")
        view[:] = True
    return result


def traversable_mask(grid: np.ndarray) -> np.ndarray:
    """Return FREE/DOOR cells, the only cells receiving floor geometry."""
    return np.isin(np.asarray(grid), (CellState.FREE, CellState.DOOR))


def occupied_border_mask(grid: np.ndarray) -> np.ndarray:
    """Return OCCUPIED cells with a four-neighbor traversable cell.

    This suppresses the infinite outer void; only visible walls and obstacles
    bordering walkable floor are represented.
    """
    grid = np.asarray(grid)
    floor = traversable_mask(grid)
    adjacent = np.zeros(grid.shape, dtype=bool)
    adjacent[1:, :] |= floor[:-1, :]
    adjacent[:-1, :] |= floor[1:, :]
    adjacent[:, 1:] |= floor[:, :-1]
    adjacent[:, :-1] |= floor[:, 1:]
    return (grid == CellState.OCCUPIED) & adjacent


def _object_cell_mask(
    shape: tuple[int, int], rect_px: tuple[float, float, float, float], *,
    origin_px: tuple[float, float], ppm: float, cell_m: float,
) -> np.ndarray:
    """Rasterize a spec rectangle using P2 pixel/cell-centre transforms."""
    x0, y0, x1, y1 = rect_px
    result = np.zeros(shape, dtype=bool)
    rows, cols = shape
    for row in range(rows):
        for col in range(cols):
            x, y = cell_to_pixel_center((row, col), origin_px, ppm, cell_m)
            result[row, col] = x0 <= x <= x1 and y0 <= y <= y1
    return result


def build_scene_layout(
    grid: np.ndarray, cell_m: float, metadata: dict[str, Any] | None = None,
    *, wall_height_m: float = 2.7,
) -> SceneLayout:
    """Build meshed floor/walls and explicit column/cabinet footprints."""
    if cell_m <= 0 or wall_height_m <= 0:
        raise ValueError("cell size and wall height must be positive")
    grid = np.asarray(grid, dtype=np.uint8)
    if grid.ndim != 2 or not grid.size:
        raise ValueError("grid must be a non-empty two-dimensional array")
    floor = traversable_mask(grid)
    wall = occupied_border_mask(grid)
    object_mask = np.zeros(grid.shape, dtype=bool)
    objects: list[SceneObject] = []
    metadata = metadata or {}
    spec = metadata.get("spec")
    if isinstance(spec, dict):
        origin = tuple(metadata.get("origin_px", spec.get("domain_px", (0, 0))[:2]))
        ppm = float(metadata.get("ppm", spec.get("parameters", {}).get("ppm", 0)))
        if ppm > 0:
            for name, rect_px in spec.get("obstacles", {}).items():
                cells = _object_cell_mask(grid.shape, tuple(rect_px), origin_px=origin,
                                          ppm=ppm, cell_m=cell_m)
                if not cells.any():
                    continue
                if np.any(cells & (grid != CellState.OCCUPIED)):
                    # An edited grid can invalidate the source spec obstacle;
                    # render its current occupancy as structural map geometry.
                    continue
                overlap = cells & object_mask
                if overlap.any():
                    raise ValueError(f"spec obstacles overlap: {name!r}")
                object_mask |= cells
                height = 1.0 if name.upper() == "C1" or "column" in name.lower() else 0.9
                objects.append(SceneObject(name, greedy_rectangles(cells), height))
    wall &= ~object_mask
    return SceneLayout(
        floors=greedy_rectangles(floor), walls=greedy_rectangles(wall),
        objects=tuple(objects), floor_mask=floor, wall_mask=wall,
        object_mask=object_mask, cell_m=float(cell_m), wall_height_m=float(wall_height_m),
    )


def route_is_clear(grid: np.ndarray, cells: tuple[tuple[int, int], ...]) -> bool:
    """Check that a cell route stays on traversable cells and uses 4-neighbor steps."""
    grid = np.asarray(grid)
    for cell in cells:
        row, col = cell
        if not (0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]):
            return False
        if grid[row, col] not in (CellState.FREE, CellState.DOOR):
            return False
    return all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(cells, cells[1:]))


def move_event_cells(start: tuple[int, int], events) -> tuple[tuple[int, int], ...]:
    """Replay only movement positions from a versioned or dataclass event stream."""
    cells = [tuple(start)]
    for event in events:
        event_type = event.get("type") if isinstance(event, dict) else event.type
        payload = event.get("payload", {}) if isinstance(event, dict) else event.payload
        if event_type == "MoveExecuted":
            cells.append(tuple(payload["position"]))
    return tuple(cells)
