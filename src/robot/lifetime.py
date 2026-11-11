"""Operational lifetime budget, independent from battery energy."""

from dataclasses import dataclass
import math

from .battery import RESOURCE_TOLERANCE


@dataclass(frozen=True)
class Lifetime:
    """Immutable operating-time budget, measured in seconds."""

    total_seconds: float
    remaining_seconds: float

    def __post_init__(self) -> None:
        """Validate total and remaining lifetime invariants."""
        if (not math.isfinite(self.total_seconds) or not math.isfinite(self.remaining_seconds)
                or self.total_seconds < 0 or not 0 <= self.remaining_seconds <= self.total_seconds):
            raise ValueError("remaining lifetime must lie between zero and its configured total")

    @classmethod
    def fresh(cls, total_seconds: float) -> "Lifetime":
        """Create a fresh lifetime budget after validating its duration."""
        if total_seconds < 0:
            raise ValueError("operational lifetime cannot be negative")
        return cls(total_seconds, total_seconds)

    def can_consume(self, duration_s: float) -> bool:
        """Return whether a non-negative duration fits the remaining lifetime."""
        if not math.isfinite(duration_s) or duration_s < 0:
            raise ValueError("duration must be finite and non-negative")
        return duration_s <= self.remaining_seconds + RESOURCE_TOLERANCE

    def consume(self, duration_s: float) -> "Lifetime":
        """Return a new lifetime state clamped at zero."""
        if not self.can_consume(duration_s):
            raise ValueError("duration exceeds remaining operational lifetime")
        return Lifetime(self.total_seconds, max(0.0, self.remaining_seconds - duration_s))
