"""3D projection helpers shared with the environment coordinate API."""

from __future__ import annotations

from collections.abc import Sequence

from src.environment.coords import cell_to_world as _cell_to_world
from src.environment.coords import meters_to_cell


def cell_to_world(cell: Sequence[int], cell_m: float) -> tuple[float, float, float]:
    """Project `(row, col)` to metric `(x, y_up, z)` world coordinates."""
    return _cell_to_world(cell, cell_m, floor_y_m=0.0)


def world_to_cell(position: Sequence[float], cell_m: float) -> tuple[int, int]:
    """Map an `(x, y, z)` world point to the containing grid cell."""
    x, _y, z = position
    return meters_to_cell((x, -z), cell_m)


def world_route(cells: Sequence[Sequence[int]], cell_m: float) -> tuple[tuple[float, float, float], ...]:
    """Project a cell route to cell-centred metric world coordinates."""
    return tuple(cell_to_world(cell, cell_m) for cell in cells)
