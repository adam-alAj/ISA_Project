"""Immutable-ish occupancy map API for simulation and search consumers."""

from dataclasses import dataclass, field
from typing import Any, Iterator

import numpy as np

from src.map_processing.constants import CellState, NEIGHBOR_OFFSETS, TRAVERSABLE_STATES
from .inflation import navigable_mask


@dataclass(frozen=True)
class GridMap:
    """Read-only occupancy grid plus calibration metadata and safe transitions."""

    grid: np.ndarray
    cell_m: float
    origin_px: tuple[float, float] = (0.0, 0.0)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        data = np.array(self.grid, dtype=np.uint8, copy=True)
        if data.ndim != 2 or 0 in data.shape or self.cell_m <= 0:
            raise ValueError("grid must be a non-empty 2D array and cell_m must be positive")
        if not np.isin(data, [int(s) for s in CellState]).all():
            raise ValueError("grid contains unknown cell-state codes")
        data.setflags(write=False)
        object.__setattr__(self, "grid", data)

    @property
    def shape(self) -> tuple[int, int]:
        """Grid dimensions `(rows, columns)`."""
        return self.grid.shape

    def in_bounds(self, cell: tuple[int, int]) -> bool:
        """Return whether a row/column cell lies inside the map."""
        r, c = cell
        return 0 <= r < self.grid.shape[0] and 0 <= c < self.grid.shape[1]

    def is_traversable(self, cell: tuple[int, int]) -> bool:
        """Return true only for in-bounds FREE and DOOR cells."""
        return self.in_bounds(cell) and int(self.grid[cell]) in tuple(int(s) for s in TRAVERSABLE_STATES)

    def neighbors(self, cell: tuple[int, int]) -> Iterator[tuple[int, int]]:
        """Yield traversable neighbors in deterministic Up, Right, Down, Left order."""
        if not self.in_bounds(cell):
            return
        r, c = cell
        for dr, dc in NEIGHBOR_OFFSETS:
            nxt = (r + dr, c + dc)
            if self.is_valid_transition(cell, nxt):
                yield nxt

    def is_valid_transition(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        """Check adjacent, in-bounds, traversable endpoints; diagonals are rejected."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 and self.is_traversable(a) and self.is_traversable(b)

    def with_footprint(self, radius_m: float) -> np.ndarray:
        """Return a read-only mask of cells where the robot center can safely move."""
        return navigable_mask(self.grid, self.cell_m, radius_m)
