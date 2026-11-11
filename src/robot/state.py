"""Immutable robot state and mission termination enums."""

from dataclasses import dataclass
from enum import Enum
import math


class Heading(str, Enum):
    """Cardinal robot heading in map coordinates."""

    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"


class RobotStatus(str, Enum):
    """Robot lifecycle status."""

    ACTIVE = "active"
    STOPPED = "stopped"


class StopReason(str, Enum):
    """Run termination reasons shared with simulation and coverage layers."""

    MISSION_COMPLETE = "mission_complete"
    BATTERY_DEPLETED = "battery_depleted"
    LIFETIME_EXPIRED = "lifetime_expired"
    NO_REACHABLE_TARGET = "no_reachable_target"
    USER_STOP = "user_stop"
    ERROR = "error"


@dataclass(frozen=True)
class RobotState:
    """Snapshot of robot position, resource budgets and progress."""

    position: tuple[int, int]
    heading: Heading | None
    battery_remaining: float
    elapsed_time_s: float
    lifetime_remaining_s: float
    status: RobotStatus = RobotStatus.ACTIVE
    cleaned_count: int = 0
    step_count: int = 0

    def __post_init__(self) -> None:
        """Enforce non-negative counters and resource values."""
        values = (self.battery_remaining, self.elapsed_time_s, self.lifetime_remaining_s)
        if any(not math.isfinite(value) for value in values):
            raise ValueError("robot resources and elapsed time must be finite")
        if self.battery_remaining < 0 or self.lifetime_remaining_s < 0 or self.elapsed_time_s < 0:
            raise ValueError("robot resources and elapsed time cannot be negative")
        if self.cleaned_count < 0 or self.step_count < 0:
            raise ValueError("robot counters cannot be negative")
