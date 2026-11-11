"""Raw-grid cleanability and footprint-achievability accounting."""
from dataclasses import dataclass
from collections import deque

from src.environment.grid_map import GridMap

Cell = tuple[int, int]


@dataclass(frozen=True)
class CleanableCells:
    """Reachable raw traversable cells and those no reachable centre can clean."""
    cells: frozenset[Cell]
    structurally_uncoverable: frozenset[Cell]

    @property
    def denominator(self) -> int:
        return len(self.cells)

    @property
    def achievable_cells(self) -> frozenset[Cell]:
        return self.cells - self.structurally_uncoverable


def build_cleanable_cells(grid_map: GridMap, start: Cell, robot) -> CleanableCells:
    """Flood-fill FREE/DOOR from start on raw grid, then inspect reachable centres."""
    if not grid_map.is_traversable(start):
        raise ValueError("start must be a raw-grid traversable cell")
    seen = {start}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        for nxt in grid_map.neighbors(cell):
            if nxt not in seen:
                seen.add(nxt); queue.append(nxt)
    reachable_centres = [tuple(map(int, p)) for p in __import__('numpy').argwhere(robot.footprint.navigable & __import__('numpy').isin(grid_map.grid, (0, 3)))]
    cleanable_by_footprint: set[Cell] = set()
    for centre in reachable_centres:
        cleanable_by_footprint.update(robot._covered_cells(centre))
    return CleanableCells(frozenset(seen), frozenset(seen - cleanable_by_footprint))
