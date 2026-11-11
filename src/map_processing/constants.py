"""Shared occupancy-grid constants and state codes."""

from enum import IntEnum


class CellState(IntEnum):
    """Serialized occupancy values. Cleaning state is stored separately."""

    FREE = 0
    OCCUPIED = 1
    UNKNOWN = 2
    DOOR = 3


TRAVERSABLE_STATES = (CellState.FREE, CellState.DOOR)
NEIGHBOR_OFFSETS: tuple[tuple[int, int], ...] = ((-1, 0), (0, 1), (1, 0), (0, -1))
MAP_SCHEMA_VERSION = 1
DEFAULT_WALL_THICKNESS_PX = 12.0
DEFAULT_ROBOT_DIAMETER_M = 0.35
