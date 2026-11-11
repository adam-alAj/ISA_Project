"""Small deterministic maps for environment and search edge cases."""

import numpy as np

from src.map_processing.constants import CellState as S


def open_room() -> np.ndarray:
    """A fully open 5 by 5 room."""
    return np.full((5, 5), S.FREE, dtype=np.uint8)


def corridor() -> np.ndarray:
    """A one-cell-wide corridor with occupied borders."""
    grid = np.full((5, 7), S.OCCUPIED, dtype=np.uint8)
    grid[2, 1:6] = S.FREE
    return grid


def wall_detour() -> np.ndarray:
    """A connected room with a central wall requiring a detour."""
    grid = np.full((7, 7), S.FREE, dtype=np.uint8)
    grid[1:6, 3] = S.OCCUPIED
    grid[3, 3] = S.FREE
    return grid


def disconnected() -> np.ndarray:
    """Two open regions separated by a complete occupied wall."""
    grid = np.full((5, 7), S.FREE, dtype=np.uint8)
    grid[:, 3] = S.OCCUPIED
    return grid


def narrow_passage() -> np.ndarray:
    """Two rooms connected by a 0.2 m passage, narrower than the robot."""
    grid = np.full((7, 9), S.OCCUPIED, dtype=np.uint8)
    grid[1:6, 1:4] = S.FREE
    grid[1:6, 5:8] = S.FREE
    grid[3, 4] = S.DOOR
    return grid


def heuristic_trap() -> np.ndarray:
    """A U-shaped barrier where Manhattan closeness initially misleads."""
    grid = np.full((8, 8), S.FREE, dtype=np.uint8)
    grid[1:7, 2] = S.OCCUPIED
    grid[1, 2:7] = S.OCCUPIED
    grid[6, 2:7] = S.OCCUPIED
    grid[1, 6] = grid[6, 6] = S.FREE
    return grid


def weighted_cost() -> np.ndarray:
    """An open grid intended for later explicit terrain-cost fixtures."""
    return np.full((5, 5), S.FREE, dtype=np.uint8)
