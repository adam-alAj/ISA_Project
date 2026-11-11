"""Atomic, deterministic vacuum robot simulation independent of UI and search."""

from dataclasses import dataclass, replace
from enum import Enum
import math
from typing import Iterable

import numpy as np

from src.environment.cleaning_state import CleaningState
from src.environment.grid_map import GridMap
from .battery import Battery, RESOURCE_TOLERANCE
from .config import RobotConfig
from .footprint import ClearanceReport, RobotFootprint
from .lifetime import Lifetime
from .state import Heading, RobotState, RobotStatus, StopReason


class MoveReason(str, Enum):
    """Reason codes for accepted or rejected movement requests."""

    VALID = "valid"
    OUT_OF_BOUNDS = "out_of_bounds"
    NON_ADJACENT = "non_adjacent"
    BLOCKED = "blocked"
    INSUFFICIENT_CLEARANCE = "insufficient_clearance"
    ROBOT_STOPPED = "robot_stopped"


@dataclass(frozen=True)
class MoveValidation:
    """Typed result of a candidate movement check."""

    valid: bool
    reason: MoveReason
    clearance: ClearanceReport | None = None


@dataclass(frozen=True)
class StepResult:
    """Outcome of one atomic robot action."""

    executed: bool
    action: str
    state: RobotState
    energy_used: float = 0.0
    elapsed_s: float = 0.0
    newly_cleaned: tuple[tuple[int, int], ...] = ()
    move_validation: MoveValidation | None = None
    stop_reason: StopReason | None = None
    limit_reasons: tuple[StopReason, ...] = ()


@dataclass(frozen=True)
class RobotSnapshot:
    """Deep snapshot of immutable state and the separate cleaned-cell layer."""

    state: RobotState
    cleaned: np.ndarray
    termination_reason: StopReason | None


def _heading_for(delta: tuple[int, int]) -> Heading:
    """Map a legal movement delta to its cardinal heading."""
    return {(-1, 0): Heading.NORTH, (0, 1): Heading.EAST,
            (1, 0): Heading.SOUTH, (0, -1): Heading.WEST}[delta]


class Robot:
    """Vacuum robot with atomic movement, cleaning and independent resource limits."""

    def __init__(
        self,
        grid_map: GridMap,
        start: tuple[int, int],
        config: RobotConfig | None = None,
    ) -> None:
        self.grid_map = grid_map
        self.config = config or RobotConfig()
        self.footprint = RobotFootprint(grid_map, self.config.diameter_m)
        self.cleaning = CleaningState(grid_map.shape)
        if not grid_map.in_bounds(start) or int(grid_map.grid[start]) not in (0, 3):
            raise ValueError("robot start must be an in-bounds FREE or DOOR cell")
        if not self.footprint.navigable[start]:
            raise ValueError("robot start does not have enough footprint clearance")
        self._start = start
        self._termination_reason: StopReason | None = None
        self._state = RobotState(
            position=start,
            heading=None,
            battery_remaining=self.config.battery_capacity_units,
            elapsed_time_s=0.0,
            lifetime_remaining_s=self.config.operational_lifetime_s,
        )
        self._finish_if_limited()

    @property
    def state(self) -> RobotState:
        """Current immutable robot state."""
        return self._state

    @property
    def termination_reason(self) -> StopReason | None:
        """Current run stop reason, if a resource or external stop has occurred."""
        return self._termination_reason

    def clearance_report(self, cell: tuple[int, int]) -> ClearanceReport:
        """Return footprint clearance information for a candidate center cell."""
        return self.footprint.report(cell)

    def validate_move(self, state: RobotState, target: tuple[int, int]) -> MoveValidation:
        """Validate one adjacent move, map traversal and robot footprint clearance."""
        if self._termination_reason is not None or state.status is RobotStatus.STOPPED:
            return MoveValidation(False, MoveReason.ROBOT_STOPPED)
        if not self.grid_map.in_bounds(target):
            return MoveValidation(False, MoveReason.OUT_OF_BOUNDS)
        delta = (target[0] - state.position[0], target[1] - state.position[1])
        if abs(delta[0]) + abs(delta[1]) != 1:
            return MoveValidation(False, MoveReason.NON_ADJACENT)
        if not self.grid_map.is_valid_transition(state.position, target):
            return MoveValidation(False, MoveReason.BLOCKED)
        clearance = self.clearance_report(target)
        if not clearance.allowed:
            return MoveValidation(False, MoveReason.INSUFFICIENT_CLEARANCE, clearance)
        return MoveValidation(True, MoveReason.VALID, clearance)

    def step(self, target: tuple[int, int]) -> StepResult:
        """Execute one move and its cleaning as a single atomic state transition."""
        validation = self.validate_move(self._state, target)
        if not validation.valid:
            return StepResult(False, "move", self._state, move_validation=validation,
                              stop_reason=self._termination_reason)
        delta = (target[0] - self._state.position[0], target[1] - self._state.position[1])
        heading = _heading_for(delta)
        turning = self._state.heading is not None and self._state.heading is not heading
        distance_m = self.grid_map.cell_m
        move_time_s = distance_m / self.config.speed_m_per_s
        move_energy = (distance_m * self.config.move_energy_units_per_m
                       if self.config.move_energy_units_per_m is not None
                       else self.config.move_energy_units_per_step)
        if turning:
            move_time_s += self.config.turn_time_s
            move_energy += self.config.turn_energy_units
        covered = self._covered_cells(target)
        newly_cleaned = tuple(cell for cell in covered if not self.cleaning.is_cleaned(cell))
        clean_energy, clean_time = self._cleaning_cost(len(newly_cleaned), len(covered))
        return self._commit_action(
            "move", energy=move_energy + clean_energy, duration_s=move_time_s + clean_time,
            position=target, heading=heading, step_increment=1,
            cleaned_cells=newly_cleaned, move_validation=validation,
        )

    def clean(self) -> StepResult:
        """Clean the disc under the current robot center without moving."""
        if self._termination_reason is not None or self._state.status is RobotStatus.STOPPED:
            validation = MoveValidation(False, MoveReason.ROBOT_STOPPED)
            return StepResult(False, "clean", self._state, move_validation=validation,
                              stop_reason=self._termination_reason)
        covered = self._covered_cells(self._state.position)
        newly_cleaned = tuple(cell for cell in covered if not self.cleaning.is_cleaned(cell))
        energy, duration = self._cleaning_cost(len(newly_cleaned), len(covered))
        return self._commit_action("clean", energy=energy, duration_s=duration,
                                   cleaned_cells=newly_cleaned)

    def idle(self, duration_s: float) -> StepResult:
        """Advance the simulation clock and consume configured idle energy."""
        if not math.isfinite(duration_s) or duration_s < 0:
            raise ValueError("idle duration must be finite and non-negative")
        if self._termination_reason is not None or self._state.status is RobotStatus.STOPPED:
            return StepResult(False, "idle", self._state, stop_reason=self._termination_reason)
        return self._commit_action("idle", energy=self.config.idle_energy_units_per_s * duration_s,
                                   duration_s=duration_s)

    def check_limits_all(self) -> tuple[StopReason, ...]:
        """Return every currently depleted resource limit in defined order."""
        reasons: list[StopReason] = []
        if self._state.battery_remaining <= RESOURCE_TOLERANCE:
            reasons.append(StopReason.BATTERY_DEPLETED)
        if self._state.lifetime_remaining_s <= RESOURCE_TOLERANCE:
            reasons.append(StopReason.LIFETIME_EXPIRED)
        return tuple(reasons)

    def check_limits(self) -> StopReason | None:
        """Return the active limit reason, with battery taking precedence."""
        if self._termination_reason is not None:
            return self._termination_reason
        reasons = self.check_limits_all()
        return reasons[0] if reasons else None

    def stop(self, reason: StopReason) -> None:
        """Stop the robot for a mission-level reason supplied by its simulator."""
        if reason in (StopReason.BATTERY_DEPLETED, StopReason.LIFETIME_EXPIRED):
            raise ValueError("resource stop reasons are determined by check_limits")
        self._termination_reason = reason
        self._state = replace(self._state, status=RobotStatus.STOPPED)

    def reset(self) -> None:
        """Restore the initial position, full resources and empty cleaning layer."""
        self.cleaning = CleaningState(self.grid_map.shape)
        self._termination_reason = None
        self._state = RobotState(
            position=self._start, heading=None,
            battery_remaining=self.config.battery_capacity_units,
            elapsed_time_s=0.0,
            lifetime_remaining_s=self.config.operational_lifetime_s,
        )
        self._finish_if_limited()

    def snapshot(self) -> RobotSnapshot:
        """Capture a deep copy suitable for deterministic replay or restoration."""
        cleaned = np.array(self.cleaning.cleaned, dtype=bool, copy=True)
        cleaned.setflags(write=False)
        return RobotSnapshot(self._state, cleaned, self._termination_reason)

    def restore(self, snapshot: RobotSnapshot) -> None:
        """Restore a compatible snapshot without sharing its mutable cleaning array."""
        if snapshot.cleaned.shape != self.grid_map.shape:
            raise ValueError("snapshot cleaning layer has a different shape")
        if not self.grid_map.in_bounds(snapshot.state.position):
            raise ValueError("snapshot position lies outside the map")
        if not self.grid_map.is_traversable(snapshot.state.position) or not self.footprint.navigable[snapshot.state.position]:
            raise ValueError("snapshot position is not safely traversable")
        restored_cleaning = CleaningState(self.grid_map.shape)
        restored_cleaning.cleaned[:] = snapshot.cleaned
        if restored_cleaning.count() != snapshot.state.cleaned_count:
            raise ValueError("snapshot cleaned_count does not match its cleaning layer")
        self._state = snapshot.state
        self.cleaning = restored_cleaning
        self._termination_reason = snapshot.termination_reason

    def _covered_cells(self, center: tuple[int, int]) -> tuple[tuple[int, int], ...]:
        """Return traversable cell centers inside the cleaning-width disc."""
        radius = self.config.cleaning_width_m / 2
        radius_cells = int(np.ceil(radius / self.grid_map.cell_m))
        cells: list[tuple[int, int]] = []
        for dr in range(-radius_cells, radius_cells + 1):
            for dc in range(-radius_cells, radius_cells + 1):
                if np.hypot(dr * self.grid_map.cell_m, dc * self.grid_map.cell_m) <= radius + RESOURCE_TOLERANCE:
                    cell = (center[0] + dr, center[1] + dc)
                    if self.grid_map.is_traversable(cell):
                        cells.append(cell)
        return tuple(sorted(cells))

    def _cleaning_cost(self, newly_cleaned_count: int, covered_count: int) -> tuple[float, float]:
        """Calculate cleaning energy/time with optional recleaning charges."""
        charged_count = covered_count if self.config.charge_recleaned_cells else newly_cleaned_count
        if self.config.clean_energy_units_per_s is not None:
            duration = charged_count * self.config.cleaning_seconds_per_cell
            energy = duration * self.config.clean_energy_units_per_s
        else:
            duration = 0.0
            energy = charged_count * self.config.clean_energy_units_per_cell
        return energy, duration

    def _commit_action(
        self,
        action: str,
        *,
        energy: float,
        duration_s: float,
        position: tuple[int, int] | None = None,
        heading: Heading | None = None,
        step_increment: int = 0,
        cleaned_cells: Iterable[tuple[int, int]] = (),
        move_validation: MoveValidation | None = None,
    ) -> StepResult:
        """Preflight resources and atomically commit all action effects."""
        if not math.isfinite(energy) or not math.isfinite(duration_s) or energy < 0 or duration_s < 0:
            raise ValueError("action energy and duration must be finite and non-negative")
        battery_exceeded = energy > self._state.battery_remaining + RESOURCE_TOLERANCE
        lifetime_exceeded = duration_s > self._state.lifetime_remaining_s + RESOURCE_TOLERANCE
        if battery_exceeded or lifetime_exceeded:
            reasons = tuple(reason for condition, reason in (
                (battery_exceeded, StopReason.BATTERY_DEPLETED),
                (lifetime_exceeded, StopReason.LIFETIME_EXPIRED),
            ) if condition)
            self._termination_reason = reasons[0]  # battery has precedence
            return StepResult(False, action, self._state, move_validation=move_validation,
                              stop_reason=self._termination_reason, limit_reasons=reasons)

        battery = Battery(self.config.battery_capacity_units, self._state.battery_remaining).consume(energy)
        lifetime = Lifetime(self.config.operational_lifetime_s, self._state.lifetime_remaining_s).consume(duration_s)
        newly_cleaned = tuple(sorted(set(cleaned_cells)))
        projected_cleaned_count = self.cleaning.count() + sum(not self.cleaning.is_cleaned(cell) for cell in newly_cleaned)
        new_state = replace(
            self._state,
            position=position if position is not None else self._state.position,
            heading=heading if heading is not None else self._state.heading,
            battery_remaining=battery.remaining_units,
            elapsed_time_s=self._state.elapsed_time_s + duration_s,
            lifetime_remaining_s=lifetime.remaining_seconds,
            cleaned_count=projected_cleaned_count,
            step_count=self._state.step_count + step_increment,
        )
        limit_reasons = tuple(reason for condition, reason in (
            (new_state.battery_remaining <= RESOURCE_TOLERANCE, StopReason.BATTERY_DEPLETED),
            (new_state.lifetime_remaining_s <= RESOURCE_TOLERANCE, StopReason.LIFETIME_EXPIRED),
        ) if condition)
        if limit_reasons:
            new_state = replace(new_state, status=RobotStatus.STOPPED)
            self._termination_reason = limit_reasons[0]
        self.cleaning.mark_cleaned(newly_cleaned)
        self._state = new_state
        return StepResult(True, action, new_state, energy, duration_s, newly_cleaned,
                          move_validation, self._termination_reason, limit_reasons)

    def _finish_if_limited(self) -> None:
        """Mark a zero-budget robot stopped at construction or reset."""
        reasons = self.check_limits_all()
        if reasons:
            self._termination_reason = reasons[0]
            self._state = replace(self._state, status=RobotStatus.STOPPED)
