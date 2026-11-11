"""Validated robot model parameters; all values are simulation assumptions."""

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RobotConfig:
    """Provisional robot configuration with explicit units for every parameter."""

    diameter_m: float = 0.35
    cleaning_width_m: float = 0.30
    speed_m_per_s: float = 0.25
    battery_capacity_units: float = 100.0
    operational_lifetime_s: float = 1800.0
    move_energy_units_per_step: float = 0.05
    clean_energy_units_per_cell: float = 0.02
    idle_energy_units_per_s: float = 0.001
    safety_reserve_units: float = 0.0
    move_energy_units_per_m: float | None = None
    clean_energy_units_per_s: float | None = None
    cleaning_seconds_per_cell: float = 0.0
    turn_energy_units: float = 0.0
    turn_time_s: float = 0.0
    charge_recleaned_cells: bool = False
    provisional: bool = True
    editable_in_ui: bool = True

    def __post_init__(self) -> None:
        """Reject physically nonsensical or internally inconsistent settings."""
        numeric = (
            self.diameter_m, self.cleaning_width_m, self.speed_m_per_s,
            self.battery_capacity_units, self.operational_lifetime_s,
            self.move_energy_units_per_step, self.clean_energy_units_per_cell,
            self.idle_energy_units_per_s, self.safety_reserve_units,
            self.cleaning_seconds_per_cell, self.turn_energy_units, self.turn_time_s,
        ) + tuple(value for value in (self.move_energy_units_per_m, self.clean_energy_units_per_s) if value is not None)
        if any(not math.isfinite(value) for value in numeric):
            raise ValueError("robot parameters must be finite numbers")
        if self.diameter_m <= 0 or self.speed_m_per_s <= 0:
            raise ValueError("robot diameter and speed must be positive")
        if not 0 < self.cleaning_width_m <= 1.0:
            raise ValueError("cleaning width must be positive and no greater than 1.0 m")
        if self.battery_capacity_units < 0 or self.operational_lifetime_s < 0:
            raise ValueError("battery capacity and lifetime cannot be negative")
        nonnegative = (
            self.move_energy_units_per_step, self.clean_energy_units_per_cell,
            self.idle_energy_units_per_s, self.safety_reserve_units,
            self.cleaning_seconds_per_cell, self.turn_energy_units, self.turn_time_s,
        )
        optional_nonnegative = (self.move_energy_units_per_m, self.clean_energy_units_per_s)
        if any(value < 0 for value in nonnegative) or any(value is not None and value < 0 for value in optional_nonnegative):
            raise ValueError("energy, time and safety-reserve coefficients cannot be negative")
        if self.safety_reserve_units > self.battery_capacity_units:
            raise ValueError("safety reserve cannot exceed battery capacity")
        if self.clean_energy_units_per_s is not None and self.cleaning_seconds_per_cell <= 0:
            raise ValueError("cleaning_seconds_per_cell must be positive for per-second cleaning energy")

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> "RobotConfig":
        """Build a configuration from the project's nested robot parameter schema."""
        source = mapping.get("parameters", mapping)

        def value(name: str, default: Any) -> Any:
            raw = source.get(name, default)
            return raw.get("value", default) if isinstance(raw, dict) else raw

        lifetime = value("lifetime_min", None)
        if lifetime is None:
            lifetime = value("operational_lifetime_s", 1800.0) / 60.0
        kwargs = {
            "diameter_m": value("diameter_m", 0.35),
            "cleaning_width_m": value("cleaning_width_m", 0.30),
            "speed_m_per_s": value("speed_m_per_s", 0.25),
            "battery_capacity_units": value("battery_capacity_units", 100.0),
            "operational_lifetime_s": float(lifetime) * 60.0,
            "move_energy_units_per_step": value("move_energy_units_per_step", 0.05),
            "clean_energy_units_per_cell": value("clean_energy_units_per_cell", 0.02),
            "idle_energy_units_per_s": value("idle_energy_units_per_s", 0.001),
            "safety_reserve_units": value("safety_reserve_units", 0.0),
            "move_energy_units_per_m": value("move_energy_units_per_m", None),
            "clean_energy_units_per_s": value("clean_energy_units_per_s", None),
            "cleaning_seconds_per_cell": value("cleaning_seconds_per_cell", 0.0),
            "turn_energy_units": value("turn_energy_units", 0.0),
            "turn_time_s": value("turn_time_s", 0.0),
            "charge_recleaned_cells": bool(value("charge_recleaned_cells", False)),
            "provisional": bool(mapping.get("provisional", mapping.get("status") == "provisional")),
            "editable_in_ui": bool(mapping.get("editable_in_ui", True)),
        }
        return cls(**kwargs)

    @classmethod
    def from_file(cls, path: str | Path) -> "RobotConfig":
        """Load JSON or JSON-compatible YAML using the standard library."""
        text = Path(path).read_text(encoding="utf-8-sig")
        try:
            mapping = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("robot config must use JSON-compatible YAML syntax") from exc
        return cls.from_mapping(mapping)
