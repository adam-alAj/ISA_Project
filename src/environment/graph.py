"""Lightweight map-to-graph adapter without a NetworkX dependency."""

from collections.abc import Iterator

from .grid_map import GridMap


def graph_neighbors(grid_map: GridMap, cell: tuple[int, int]) -> Iterator[tuple[int, int]]:
    """Expose a GridMap as an implicit adjacency graph for search algorithms."""
    yield from grid_map.neighbors(cell)
