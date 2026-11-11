"""Backward-compatible alias for Iterative Deepening DFS."""

from .iddfs import iddfs

idfs = iddfs

__all__ = ["idfs", "iddfs"]
