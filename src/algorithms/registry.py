"""Canonical names and aliases for the required search algorithms."""

from __future__ import annotations

CANONICAL_ALGORITHM_IDS = ("bfs", "dfs", "ucs", "greedy", "astar", "iddfs")
ALGORITHM_ALIASES = {"idfs": "iddfs"}

from .astar import astar
from .bfs import bfs
from .dfs import dfs
from .greedy import greedy
from .iddfs import iddfs
from .result import SearchFn
from .ucs import ucs

REGISTRY: dict[str, SearchFn] = {
    "bfs": bfs,
    "dfs": dfs,
    "ucs": ucs,
    "greedy": greedy,
    "astar": astar,
    "iddfs": iddfs,
}


def get_algorithm(name: str) -> SearchFn:
    """Resolve a canonical algorithm name or the legacy `idfs` alias."""
    return REGISTRY[canonical_algorithm_id(name)]


def canonical_algorithm_id(name: str) -> str:
    """Return a canonical algorithm ID for a name or alias.

    Raises:
        ValueError: If ``name`` is not a required algorithm ID or alias.
    """
    normalized = name.strip().lower().replace("-", "_").replace(" ", "_")
    canonical = ALGORITHM_ALIASES.get(normalized, normalized)
    if canonical not in CANONICAL_ALGORITHM_IDS:
        raise ValueError(f"Unknown search algorithm: {name!r}")
    return canonical
