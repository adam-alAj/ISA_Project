"""Canonical names and aliases for the required search algorithms."""

from __future__ import annotations

CANONICAL_ALGORITHM_IDS = ("bfs", "dfs", "ucs", "greedy", "astar", "iddfs")
ALGORITHM_ALIASES = {"idfs": "iddfs"}


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
