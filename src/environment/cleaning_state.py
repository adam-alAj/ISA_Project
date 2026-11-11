"""Cleaning progress stored independently from occupancy."""

from collections.abc import Iterable

import numpy as np


class CleaningState:
    """Boolean per-cell cleaning state; changing it never edits a map grid."""

    def __init__(self, shape: tuple[int, int]) -> None:
        if len(shape) != 2 or min(shape) <= 0:
            raise ValueError("shape must contain two positive dimensions")
        self.cleaned = np.zeros(shape, dtype=bool)

    def mark_cleaned(self, cells: Iterable[tuple[int, int]]) -> None:
        """Mark the provided cells as cleaned, rejecting out-of-bounds cells."""
        for row, col in cells:
            if not (0 <= row < self.cleaned.shape[0] and 0 <= col < self.cleaned.shape[1]):
                raise IndexError(f"cell {(row, col)} is outside cleaning-state bounds")
            self.cleaned[row, col] = True

    def is_cleaned(self, cell: tuple[int, int]) -> bool:
        """Return whether a cell has been cleaned."""
        return bool(self.cleaned[cell])

    def count(self) -> int:
        """Return the number of cleaned cells."""
        return int(np.count_nonzero(self.cleaned))
