"""Deterministic tests for atomic robot movement and resource limits."""

from __future__ import annotations

from dataclasses import asdict, replace
import json
import random
from pathlib import Path

import numpy as np
import pytest

from src.environment.components import reachable_from
from src.environment.grid_map import GridMap
from src.map_processing.constants import CellState as S
from src.robot.config import RobotConfig
from src.robot.state import RobotStatus, StopReason
from src.robot.vacuum_robot import MoveReason, Robot


ROOT = Path(__file__).resolve().parents[2]


def open_map(shape: tuple[int, int] = (15, 15)) -> GridMap:
    """Create a free occupancy grid for robot behavior tests."""
    return GridMap(np.full(shape, S.FREE, dtype=np.uint8), cell_m=0.1)


def state_bytes(robot: Robot) -> bytes:
    """Serialize the immutable public state for atomicity assertions."""
    return json.dumps(asdict(robot.state), sort_keys=True, default=str).encode("utf-8")


def test_config_loads_provisional_yaml_defaults_and_validates() -> None:
    config = RobotConfig.from_file(ROOT / "docs/map_spec/robot_params.yaml")
    assert config.provisional and config.editable_in_ui
    assert config.diameter_m == pytest.approx(0.35)
    assert config.cleaning_width_m == pytest.approx(0.30)
    assert config.speed_m_per_s == pytest.approx(0.25)
    assert config.battery_capacity_units == pytest.approx(100)
    assert config.operational_lifetime_s == pytest.approx(1800)
    with pytest.raises(ValueError):
        RobotConfig(cleaning_width_m=1.1)
    with pytest.raises(ValueError):
        RobotConfig(speed_m_per_s=float("nan"))


def test_worked_example_one_step_updates_position_cleaning_energy_and_time() -> None:
    robot = Robot(open_map(), (5, 5), RobotConfig())
    result = robot.step((5, 6))
    assert result.executed
    assert result.energy_used == pytest.approx(0.05 + 9 * 0.02)
    assert result.elapsed_s == pytest.approx(0.1 / 0.25)
    assert result.state.position == (5, 6)
    assert result.state.battery_remaining == pytest.approx(99.77)
    assert result.state.lifetime_remaining_s == pytest.approx(1799.6)
    assert result.state.step_count == 1 and result.state.cleaned_count == 9


@pytest.mark.parametrize(
    ("capacity", "lifetime_s", "expected"),
    [
        (0.20, 100.0, StopReason.BATTERY_DEPLETED),
        (100.0, 0.30, StopReason.LIFETIME_EXPIRED),
        (0.20, 0.30, StopReason.BATTERY_DEPLETED),
    ],
)
def test_resource_limits_are_independent_and_battery_precedes_lifetime(
    capacity: float, lifetime_s: float, expected: StopReason
) -> None:
    cfg = RobotConfig(battery_capacity_units=capacity, operational_lifetime_s=lifetime_s)
    robot = Robot(open_map(), (5, 5), cfg)
    before, cleaned = state_bytes(robot), robot.cleaning.cleaned.copy()
    result = robot.step((5, 6))
    assert not result.executed and result.stop_reason is expected
    assert state_bytes(robot) == before
    np.testing.assert_array_equal(robot.cleaning.cleaned, cleaned)
    if capacity == 0.20 and lifetime_s == 0.30:
        assert result.limit_reasons == (StopReason.BATTERY_DEPLETED, StopReason.LIFETIME_EXPIRED)


def test_exact_boundary_step_executes_then_reports_both_limits() -> None:
    config = RobotConfig(
        battery_capacity_units=0.05, operational_lifetime_s=0.4,
        clean_energy_units_per_cell=0.0,
    )
    robot = Robot(open_map(), (5, 5), config)
    result = robot.step((5, 6))
    assert result.executed and result.state.position == (5, 6)
    assert result.state.battery_remaining == pytest.approx(0.0)
    assert result.state.lifetime_remaining_s == pytest.approx(0.0)
    assert result.stop_reason is StopReason.BATTERY_DEPLETED
    assert result.limit_reasons == (StopReason.BATTERY_DEPLETED, StopReason.LIFETIME_EXPIRED)
    assert result.state.status is RobotStatus.STOPPED


@pytest.mark.parametrize(
    ("capacity", "lifetime_s", "reason"),
    [(0.0, 5.0, StopReason.BATTERY_DEPLETED), (5.0, 0.0, StopReason.LIFETIME_EXPIRED)],
)
def test_zero_initial_resource_stops_immediately(capacity: float, lifetime_s: float, reason: StopReason) -> None:
    robot = Robot(open_map(), (5, 5), RobotConfig(battery_capacity_units=capacity, operational_lifetime_s=lifetime_s))
    assert robot.check_limits() is reason
    assert robot.state.status is RobotStatus.STOPPED
    assert not robot.step((5, 6)).executed


def test_invalid_moves_are_atomic_and_reasoned() -> None:
    grid = np.full((7, 7), S.FREE, dtype=np.uint8)
    grid[2, 3], grid[3, 2] = S.OCCUPIED, S.UNKNOWN
    robot = Robot(GridMap(grid, 0.1), (5, 5), RobotConfig(diameter_m=0.1, cleaning_width_m=0.1))
    remote_state = replace(robot.state, position=(2, 2))
    for target in ((2, 3), (3, 2)):
        before = state_bytes(robot)
        result = robot.validate_move(remote_state, target)
        assert not result.valid and result.reason is MoveReason.BLOCKED
        assert state_bytes(robot) == before
    cases = [((5, 7), MoveReason.OUT_OF_BOUNDS), ((3, 3), MoveReason.NON_ADJACENT)]
    for target, reason in cases:
        before = state_bytes(robot)
        cleaned = robot.cleaning.cleaned.copy()
        result = robot.step(target)
        assert not result.executed and result.move_validation is not None
        assert result.move_validation.reason is reason
        assert state_bytes(robot) == before
        np.testing.assert_array_equal(robot.cleaning.cleaned, cleaned)


def test_narrow_passage_rejects_robot_but_department_doors_and_cabinet_pass() -> None:
    narrow = np.full((13, 19), S.FREE, dtype=np.uint8)
    narrow[:, 9] = S.OCCUPIED
    narrow[6, 9] = S.DOOR
    narrow_robot = Robot(GridMap(narrow, 0.1), (6, 6))
    validation = narrow_robot.validate_move(replace(narrow_robot.state, position=(6, 8)), (6, 9))
    assert not validation.valid and validation.reason is MoveReason.INSUFFICIENT_CLEARANCE

    dept_grid = np.load(ROOT / "data/maps/department_v0_3/department_map.npy")
    dept = GridMap(dept_grid, 0.1, (80.0, 160.0))
    door_robot = Robot(dept, (12, 36))
    door_step = door_robot.step((13, 36))
    assert door_step.executed and int(dept_grid[13, 36]) == S.DOOR

    nav = dept.with_footprint(0.175)
    reached = reachable_from(nav, (118, 54))
    assert reached[118, 27]  # clear path past the 10 cm cabinet protrusion


def test_cleaning_is_idempotent_and_snapshot_restore_is_deep() -> None:
    robot = Robot(open_map(), (5, 5), RobotConfig())
    first = robot.clean()
    assert first.executed and len(first.newly_cleaned) == 9
    second = robot.clean()
    assert second.executed and not second.newly_cleaned and second.energy_used == 0
    snapshot = robot.snapshot()
    robot.step((5, 6))
    robot.restore(snapshot)
    assert robot.state == snapshot.state
    np.testing.assert_array_equal(robot.cleaning.cleaned, snapshot.cleaned)
    robot.cleaning.cleaned[:] = False
    assert snapshot.cleaned.any()
    robot.reset()
    assert robot.state.position == (5, 5) and robot.state.cleaned_count == 0
    assert robot.cleaning.count() == 0


def test_idle_energy_updates_clock_and_resource_independently() -> None:
    robot = Robot(open_map(), (5, 5), RobotConfig())
    result = robot.idle(3.0)
    assert result.executed
    assert result.energy_used == pytest.approx(0.003)
    assert result.elapsed_s == pytest.approx(3.0)
    assert robot.state.lifetime_remaining_s == pytest.approx(1797.0)


def test_mission_level_stop_reasons_are_exposed() -> None:
    robot = Robot(open_map(), (5, 5), RobotConfig())
    robot.stop(StopReason.MISSION_COMPLETE)
    assert robot.check_limits() is StopReason.MISSION_COMPLETE
    assert robot.state.status is RobotStatus.STOPPED


def test_ten_thousand_seeded_move_attempts_preserve_invariants() -> None:
    grid = np.full((24, 24), S.FREE, dtype=np.uint8)
    grid[4:20, 12] = S.OCCUPIED
    grid[11, 12] = S.DOOR
    world = GridMap(grid, 0.1)
    cfg = RobotConfig(battery_capacity_units=1e9, operational_lifetime_s=1e9)
    robot = Robot(world, (10, 8), cfg)
    rng = random.Random(20261111)

    for _ in range(10_000):
        target = (rng.randrange(-1, 25), rng.randrange(-1, 25))
        before = state_bytes(robot)
        validation = robot.validate_move(robot.state, target)
        result = robot.step(target)
        if validation.valid:
            assert result.executed
        else:
            assert not result.executed and state_bytes(robot) == before
        assert world.is_traversable(robot.state.position)
        assert robot.footprint.navigable[robot.state.position]
        assert robot.state.battery_remaining >= 0 and robot.state.lifetime_remaining_s >= 0
        assert robot.state.cleaned_count == robot.cleaning.count()
        assert np.all(robot.cleaning.cleaned <= np.isin(world.grid, (S.FREE, S.DOOR)))
