"""Deterministic declarative geometry rasterizer and programmatic editor."""

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np

from .constants import CellState


@dataclass(frozen=True)
class RasterizedMap:
    """Occupancy array and coordinate metadata derived from a map spec."""

    grid: np.ndarray
    start_cell: tuple[int, int]
    metadata: dict[str, Any]


def _cell_centers(spec: dict[str, Any]) -> tuple[tuple[np.ndarray, np.ndarray], int, int]:
    xmin, ymin, xmax, ymax = spec["domain_px"]
    ppm, cell_m = spec["parameters"]["ppm"], spec["parameters"]["cell_m"]
    step = ppm * cell_m
    nx, ny = int(np.ceil((xmax - xmin) / step)), int(np.ceil((ymax - ymin) / step))
    x = xmin + (np.arange(nx, dtype=float) + 0.5) * step
    y = ymin + (np.arange(ny, dtype=float) + 0.5) * step
    return np.meshgrid(x, y), nx, ny


def rasterize(spec: dict[str, Any]) -> RasterizedMap:
    """Rasterize zones, rooms, walls, doors, obstacles and unknown regions."""
    (cx, cy), nx, ny = _cell_centers(spec)
    grid = np.full((ny, nx), CellState.OCCUPIED, dtype=np.uint8)

    def mask(rect: Iterable[float]) -> np.ndarray:
        x0, y0, x1, y1 = rect
        return (cx >= x0) & (cx <= x1) & (cy >= y0) & (cy <= y1)

    def stamp_line(x0: float, y0: float, x1: float, y1: float) -> None:
        half = spec["parameters"]["wall_thickness_px"] / 2
        rect = (min(x0, x1) - half, min(y0, y1) - half, max(x0, x1) + half, max(y0, y1) + half)
        grid[mask(rect)] = CellState.OCCUPIED

    for rect in spec["zones"].values():
        grid[mask(rect)] = CellState.FREE
    for rect in spec["rooms"].values():
        grid[mask(rect)] = CellState.FREE
    for x0, y0, x1, y1 in spec["rooms"].values():
        for segment in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
            stamp_line(*segment)
    for segment in spec["extra_walls"]:
        stamp_line(*segment)
    for rect in spec["doors"].values():
        grid[mask(rect)] = CellState.DOOR
    for rect in spec["obstacles"].values():
        grid[mask(rect)] = CellState.OCCUPIED
    for rect in spec.get("unknown_areas", {}).values():
        grid[mask(rect)] = CellState.UNKNOWN

    xmin, ymin, _, _ = spec["domain_px"]
    step = spec["parameters"]["ppm"] * spec["parameters"]["cell_m"]
    x, y = spec["start_px"]
    start = (int((y - ymin) // step), int((x - xmin) // step))
    if not (0 <= start[0] < ny and 0 <= start[1] < nx) or grid[start] not in (CellState.FREE, CellState.DOOR):
        raise ValueError("start pixel does not map to a traversable cell")
    grid.setflags(write=False)
    metadata = {
        "cell_m": spec["parameters"]["cell_m"], "origin_px": [xmin, ymin],
        "ppm": spec["parameters"]["ppm"], "start_cell": list(start),
        "states": {"FREE": 0, "OCCUPIED": 1, "UNKNOWN": 2, "DOOR": 3},
        "version": spec["version"], "robot_diameter_m": spec["parameters"]["robot_diameter_m"],
        "spec": spec,
        "room_bounds_px": {name: list(bounds) for name, bounds in spec["rooms"].items()},
        "room_areas_m2": {
            name: (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]) / spec["parameters"]["ppm"] ** 2
            for name, bounds in spec["rooms"].items()
        },
    }
    return RasterizedMap(grid, start, metadata)


class MapEditor:
    """Small mutable editing facade for later UI integration."""

    def __init__(self, grid: np.ndarray) -> None:
        self.grid = np.array(grid, dtype=np.uint8, copy=True)

    def set_cells(self, rect: tuple[int, int, int, int], state: int | CellState) -> None:
        """Set an array-index rectangle `(row0,col0,row1,col1)`, end-exclusive."""
        r0, c0, r1, c1 = rect
        if not (0 <= r0 <= r1 <= self.grid.shape[0] and 0 <= c0 <= c1 <= self.grid.shape[1]):
            raise ValueError("cell rectangle is outside the grid")
        self.grid[r0:r1, c0:c1] = int(state)

    def add_door(self, rect: tuple[int, int, int, int]) -> None:
        """Mark a cell-index rectangle as a traversable door passage."""
        self.set_cells(rect, CellState.DOOR)

    def add_obstacle(self, rect: tuple[int, int, int, int]) -> None:
        """Mark a cell-index rectangle as occupied."""
        self.set_cells(rect, CellState.OCCUPIED)
