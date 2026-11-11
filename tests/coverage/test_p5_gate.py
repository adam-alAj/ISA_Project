"""Acceptance evidence checks invoked by scripts/run_p5_gate.*."""
import tracemalloc
from pathlib import Path

import numpy as np
import pytest

from src.algorithms.registry import REGISTRY
from src.algorithms.problem import SearchProblem
from src.algorithms.result import SearchOptions
from src.coverage.cleanable import build_cleanable_cells
from src.coverage.controller import CoverageController
from src.coverage.target_policy import NearestUncleanedPolicy
from src.environment.grid_map import GridMap
from src.robot.config import RobotConfig
from src.robot.vacuum_robot import Robot
from src.simulation.events import replay_actions
from src.map_processing.constants import CellState as S

ALGORITHMS = tuple(REGISTRY)


def _small(robot_config=None):
    grid = GridMap(np.zeros((7, 7), dtype=np.uint8), .1)
    cfg = robot_config or RobotConfig(diameter_m=.1, cleaning_width_m=.1,
                                      battery_capacity_units=10000, operational_lifetime_s=10000)
    robot = Robot(grid, (3, 3), cfg)
    cleanable = build_cleanable_cells(grid, (3, 3), robot)
    return grid, robot, cleanable


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_ts08_ts09_full_and_constrained_coverage_for_each_algorithm(algorithm):
    _, robot, cleanable = _small()
    full = CoverageController(robot, cleanable, NearestUncleanedPolicy(cleanable.cells),
                              REGISTRY[algorithm], algorithm, max_iterations=1000).run()
    assert full.coverage_percent == pytest.approx(100)
    _, constrained_robot, constrained_cleanable = _small(RobotConfig(
        diameter_m=.1, cleaning_width_m=.1, battery_capacity_units=.24,
        operational_lifetime_s=10000))
    partial = CoverageController(constrained_robot, constrained_cleanable,
        NearestUncleanedPolicy(constrained_cleanable.cells), REGISTRY[algorithm], algorithm,
        max_iterations=1000).run()
    assert 0 <= partial.raw_coverage_percent < 100


def test_invariant_100_seeded_scenarios():
    rng = np.random.default_rng(20261111)
    for seed in range(100):
        cells = np.zeros((9, 9), dtype=np.uint8)
        mask = rng.random((9, 9)) < .18
        mask[3:6, 3:6] = False
        cells[mask] = S.OCCUPIED
        grid = GridMap(cells, .1)
        robot = Robot(grid, (4, 4), RobotConfig(diameter_m=.1, cleaning_width_m=.1,
                     battery_capacity_units=1e6, operational_lifetime_s=1e6))
        reachable = [tuple(map(int, p)) for p in np.argwhere(robot.footprint.navigable)]
        target = reachable[seed % len(reachable)]
        base = SearchProblem.from_grid_map(grid, (4, 4), target, heuristic_fn=None)
        nav = robot.footprint.navigable
        problem = SearchProblem(base.start, base.goal,
            lambda cell: (n for n in base.neighbors(cell) if nav[n]), base.step_cost_fn,
            base.heuristic_fn, lambda c: grid.is_traversable(c) and bool(nav[c]),
            tuple(c for c in base.all_nodes if nav[c]), base.min_step_cost)
        result = REGISTRY["bfs"](problem)
        if result.found:
            for a, b in zip(result.path, result.path[1:]):
                step = robot.step(b)
                assert step.executed
                assert grid.is_traversable(robot.state.position)
                assert abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1


def test_planning_preserves_robot_snapshot_for_each_algorithm():
    grid, robot, _ = _small()
    for name, planner in REGISTRY.items():
        before = robot.snapshot()
        planner(SearchProblem.from_grid_map(grid, robot.state.position, (0, 0)))
        after = robot.snapshot()
        assert before.state == after.state
        np.testing.assert_array_equal(before.cleaned, after.cleaned)


def test_event_replay_equivalence_and_schema_version():
    _, robot, cleanable = _small()
    controller = CoverageController(robot, cleanable, NearestUncleanedPolicy(cleanable.cells),
                                    REGISTRY["bfs"], "bfs", max_iterations=1000)
    controller.run()
    replay_robot = Robot(robot.grid_map, (3, 3), robot.config)
    replayed = replay_actions(replay_robot, controller.events.events)
    actual = robot.snapshot()
    assert replayed.state == actual.state
    np.testing.assert_array_equal(replayed.cleaned, actual.cleaned)
    assert all(isinstance(event.schema_version, int) and event.schema_version > 0
               for event in controller.events.events)


def test_department_headless_runs_report_metrics_and_bounded_memory():
    root = Path(__file__).resolve().parents[2]
    map_path = root / "data/maps/department_v1/grid.npz"
    meta = __import__("json").loads((map_path.parent / "map.json").read_text(encoding="utf-8"))
    with np.load(map_path) as archive:
        grid = GridMap(archive["grid"], float(meta["cell_m"]), tuple(meta["origin_px"]))
    start = tuple(meta["start_cell"])
    tracemalloc.start()
    rows = []
    for name, planner in REGISTRY.items():
        robot = Robot(grid, start, RobotConfig())
        cleanable = build_cleanable_cells(grid, start, robot)
        controller = CoverageController(robot, cleanable, NearestUncleanedPolicy(cleanable.cells),
            planner, name, options=SearchOptions(max_expansions=2000, time_budget_s=.5), max_iterations=50,
            snapshot_capacity=8)
        result = controller.run()
        rows.append((name, result.coverage_percent, robot.state.step_count,
                     robot.config.battery_capacity_units - robot.state.battery_remaining,
                     robot.state.elapsed_time_s, result.stop_reason.value, result.planner_wall_time_s))
        assert len(controller.snapshots) <= 8
        assert controller.events.events.maxlen == 10000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print("algorithm,coverage_pct,steps,energy,sim_time_s,stop_reason,planner_wall_s")
    for row in rows:
        print(",".join(str(value) for value in row))
    print(f"tracemalloc_peak_bytes={peak}")
    assert len(rows) == 6
    assert peak < 512 * 1024 * 1024
