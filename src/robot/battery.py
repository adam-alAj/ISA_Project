"""Independent battery capacity and consumption accounting."""

from dataclasses import dataclass
import math


RESOURCE_TOLERANCE = 1e-12


@dataclass(frozen=True)
class Battery:
    """Immutable battery budget measured in normalized simulation units."""

    capacity_units: float
    remaining_units: float

    def __post_init__(self) -> None:
        """Validate capacity and remaining energy invariants."""
        if (not math.isfinite(self.capacity_units) or not math.isfinite(self.remaining_units)
                or self.capacity_units < 0 or not 0 <= self.remaining_units <= self.capacity_units):
            raise ValueError("battery remaining energy must lie between zero and capacity")

    @classmethod
    def full(cls, capacity_units: float) -> "Battery":
        """Create a full battery after validating its capacity."""
        if capacity_units < 0:
            raise ValueError("battery capacity cannot be negative")
        return cls(capacity_units, capacity_units)

    def can_consume(self, amount: float) -> bool:
        """Return whether a non-negative cost fits within the current budget."""
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("energy cost must be finite and non-negative")
        return amount <= self.remaining_units + RESOURCE_TOLERANCE

    def consume(self, amount: float) -> "Battery":
        """Return a new battery state, clamping floating-point residue at zero."""
        if not self.can_consume(amount):
            raise ValueError("energy cost exceeds the remaining battery")
        return Battery(self.capacity_units, max(0.0, self.remaining_units - amount))

    @property
    def used_units(self) -> float:
        """Energy used, equivalent to capacity minus remaining energy."""
        return max(0.0, self.capacity_units - self.remaining_units)
