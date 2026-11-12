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
    """Flood-fill raw cells and legal robot centres from the mission start."""
    if not grid_map.is_traversable(start):
        raise ValueError("start must be a raw-grid traversable cell")
    seen = {start}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        for nxt in grid_map.neighbors(cell):
            if nxt not in seen:
                seen.add(nxt); queue.append(nxt)
    if not robot.footprint.navigable[start]:
        raise ValueError("start must be navigable for the configured robot footprint")
    centre_seen = {start}
    centre_queue = deque([start])
    while centre_queue:
        cell = centre_queue.popleft()
        for nxt in grid_map.neighbors(cell):
            if robot.footprint.navigable[nxt] and nxt not in centre_seen:
                centre_seen.add(nxt)
                centre_queue.append(nxt)
    cleanable_by_footprint: set[Cell] = set()
    for centre in centre_seen:
        cleanable_by_footprint.update(robot._covered_cells(centre))
    return CleanableCells(frozenset(seen), frozenset(seen - cleanable_by_footprint))
