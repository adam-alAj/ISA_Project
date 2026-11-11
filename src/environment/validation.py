"""Structured validation for start and goal coordinates."""

from dataclasses import dataclass
from typing import Iterable

from .grid_map import GridMap


@dataclass(frozen=True)
class ValidationIssue:
    """One actionable map or coordinate validation finding."""

    code: str
    severity: str
    message: str
    cells: tuple[tuple[int, int], ...] = ()


def validate_cells(grid_map: GridMap, start: tuple[int, int], targets: Iterable[tuple[int, int]]) -> list[ValidationIssue]:
    """Validate start and target cells against map bounds and traversability."""
    issues: list[ValidationIssue] = []
    for label, cell in (("start", start), *(("target", t) for t in targets)):
        if not grid_map.in_bounds(cell):
            issues.append(ValidationIssue("cell_out_of_bounds", "error", f"{label} {cell} is outside the map", (cell,)))
        elif not grid_map.is_traversable(cell):
            issues.append(ValidationIssue("cell_not_traversable", "error", f"{label} {cell} is blocked or unknown", (cell,)))
    return issues


def validate_map(grid_map: GridMap, start: tuple[int, int]) -> list[ValidationIssue]:
    """Check basic map integrity, unknown cells, boundary leaks, start and doors."""
    import numpy as np

    issues: list[ValidationIssue] = []
    grid = grid_map.grid
    if grid.ndim != 2 or min(grid.shape) == 0:
        issues.append(ValidationIssue("invalid_dimensions", "error", "grid must be a non-empty 2D array"))
        return issues
    if not np.isin(grid, (0, 1, 2, 3)).all():
        issues.append(ValidationIssue("invalid_dimensions", "error", "grid contains invalid state codes"))
    traversable = np.isin(grid, (0, 3))
    if not np.any(grid == 0):
        issues.append(ValidationIssue("no_free_cells", "error", "map has no FREE cells"))
    unknown = tuple(map(tuple, np.argwhere(grid == 2).tolist()))
    if unknown:
        issues.append(ValidationIssue("unknown_regions", "warning", "map contains UNKNOWN cells", unknown))
    boundary = np.zeros(grid.shape, dtype=bool)
    boundary[[0, -1], :] = True
    boundary[:, [0, -1]] = True
    leaks = tuple(map(tuple, np.argwhere(boundary & traversable).tolist()))
    if leaks:
        issues.append(ValidationIssue("accidental_opening", "error", "traversable cell touches the map exterior boundary", leaks))
    issues.extend(validate_cells(grid_map, start, ()))

    # A door group should connect to floor on opposing sides of its narrow axis.
    door_mask = grid == 3
    seen = np.zeros(grid.shape, dtype=bool)
    for r, c in zip(*np.nonzero(door_mask)):
        if seen[r, c]:
            continue
        stack = [(int(r), int(c))]
        seen[r, c] = True
        component: list[tuple[int, int]] = []
        while stack:
            rr, cc = stack.pop()
            component.append((rr, cc))
            for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                nr, nc = rr + dr, cc + dc
                if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1] and door_mask[nr, nc] and not seen[nr, nc]:
                    seen[nr, nc] = True
                    stack.append((nr, nc))
        adjacent_dirs: set[tuple[int, int]] = set()
        for rr, cc in component:
            for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                nr, nc = rr + dr, cc + dc
                if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1] and grid[nr, nc] == 0:
                    adjacent_dirs.add((dr, dc))
        vertical = (-1, 0) in adjacent_dirs and (1, 0) in adjacent_dirs
        horizontal = (0, -1) in adjacent_dirs and (0, 1) in adjacent_dirs
        if not (vertical or horizontal):
            issues.append(ValidationIssue("door_not_connecting_regions", "warning", "door component does not touch FREE cells on opposing sides", tuple(component)))
    return issues
