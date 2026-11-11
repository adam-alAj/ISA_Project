"""Robot collision and clearance checks against the P2 navigable mask."""

from dataclasses import dataclass
import math

import numpy as np

from src.environment.grid_map import GridMap


@dataclass(frozen=True)
class ClearanceReport:
    """Footprint clearance result for a candidate robot-center cell."""

    cell: tuple[int, int]
    allowed: bool
    required_radius_m: float
    nearest_obstacle_center_m: float | None
    reason: str | None = None


class RobotFootprint:
    """Cache a navigable mask for a robot disc of a configured diameter."""

    def __init__(self, grid_map: GridMap, diameter_m: float) -> None:
        if not math.isfinite(diameter_m) or diameter_m <= 0:
            raise ValueError("robot diameter must be finite and positive")
        self.grid_map = grid_map
        self.diameter_m = diameter_m
        self.radius_m = diameter_m / 2
        self.navigable = grid_map.with_footprint(self.radius_m)

    def report(self, cell: tuple[int, int]) -> ClearanceReport:
        """Report whether the robot disc can be centered at a cell."""
        if not self.grid_map.in_bounds(cell):
            return ClearanceReport(cell, False, self.radius_m, None, "out_of_bounds")
        state = int(self.grid_map.grid[cell])
        if state not in (0, 3):
            return ClearanceReport(cell, False, self.radius_m, None, "blocked_cell")
        allowed = bool(self.navigable[cell])
        radius_cells = int(np.ceil(self.radius_m / self.grid_map.cell_m)) + 1
        row, col = cell
        r0, r1 = max(0, row - radius_cells), min(self.grid_map.shape[0], row + radius_cells + 1)
        c0, c1 = max(0, col - radius_cells), min(self.grid_map.shape[1], col + radius_cells + 1)
        local = np.argwhere(~np.isin(self.grid_map.grid[r0:r1, c0:c1], (0, 3)))
        nearest = None
        if local.size:
            distances = np.sqrt((local[:, 0] + r0 - row) ** 2 + (local[:, 1] + c0 - col) ** 2) * self.grid_map.cell_m
            nearest = float(np.min(distances))
        reason = None if allowed else "insufficient_clearance"
        return ClearanceReport(cell, allowed, self.radius_m, nearest, reason)
