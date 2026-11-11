"""Coordinate transforms for pixel, grid, metric and 3D world frames.

Grid cells are `(row, column)`, row grows down, column grows right. Metric map
coordinates start at the configured pixel origin. World coordinates use x right,
y up, z toward the top of the image (negative row direction).
"""

from typing import Sequence


def pixel_to_cell(point_xy: Sequence[float], origin_xy: Sequence[float], ppm: float, cell_m: float) -> tuple[int, int]:
    """Convert a source pixel point to its containing `(row, column)` cell."""
    if ppm <= 0 or cell_m <= 0:
        raise ValueError("ppm and cell_m must be positive")
    x, y = point_xy
    ox, oy = origin_xy
    step = ppm * cell_m
    return int((y - oy) // step), int((x - ox) // step)


def cell_to_pixel_center(cell: Sequence[int], origin_xy: Sequence[float], ppm: float, cell_m: float) -> tuple[float, float]:
    """Return source pixel coordinates for the center of a grid cell."""
    row, col = cell
    ox, oy = origin_xy
    step = ppm * cell_m
    return ox + (col + 0.5) * step, oy + (row + 0.5) * step


def cell_to_meters(cell: Sequence[int], cell_m: float) -> tuple[float, float]:
    """Return the cell-center `(x,y)` metric coordinates from the map origin."""
    row, col = cell
    return (col + 0.5) * cell_m, (row + 0.5) * cell_m


def meters_to_cell(point_xy_m: Sequence[float], cell_m: float) -> tuple[int, int]:
    """Convert metric map coordinates to the containing `(row,column)` cell."""
    if cell_m <= 0:
        raise ValueError("cell_m must be positive")
    x, y = point_xy_m
    return int(y // cell_m), int(x // cell_m)


def cell_to_world(cell: Sequence[int], cell_m: float, floor_y_m: float = 0.0) -> tuple[float, float, float]:
    """Return center coordinates `(x,y,z)` in a right/up/top-origin 3D frame."""
    row, col = cell
    return (col + 0.5) * cell_m, floor_y_m, -(row + 0.5) * cell_m
