import numpy as np

from src.algorithms.bfs import bfs
from src.coverage.cleanable import build_cleanable_cells
from src.coverage.controller import CoverageController
from src.coverage.target_policy import NearestUncleanedPolicy
from src.environment.grid_map import GridMap
from src.robot.config import RobotConfig
from src.robot.vacuum_robot import Robot


def test_policy_tie_break_and_controller_completes_small_map():
    grid = GridMap(np.zeros((7, 7), dtype=np.uint8), .1)
    robot = Robot(grid, (3, 3), RobotConfig(diameter_m=.1, cleaning_width_m=.1,
                  battery_capacity_units=100, operational_lifetime_s=1000))
    cleanable = build_cleanable_cells(grid, (3, 3), robot)
    policy = NearestUncleanedPolicy(cleanable.achievable_cells)
    # The current cell is nearest when still uncleaned; after excluding it,
    # the four equally distant neighbors resolve by (row, column).
    assert policy.next_target(robot.state, set()) == (3, 3)
    assert policy.next_target(robot.state, {(3, 3)}) == (2, 3)
    controller = CoverageController(robot, cleanable, policy, bfs, "bfs", max_iterations=1000)
    result = controller.run()
    assert result.raw_coverage_percent == 100
    assert result.stop_reason.value == "mission_complete"
    assert controller.snapshots.maxlen == 256
    assert all(event.schema_version == 1 for event in controller.events.events)
    finished = [event for event in controller.events.snapshot_events() if event.type == "SearchFinished"]
    assert finished
    assert all("expanded" in event.payload and "generated" in event.payload for event in finished)
    assert all("path_length_steps" in event.payload and "path_cost" in event.payload for event in finished)


def test_structural_uncoverable_excludes_regions_without_a_reachable_robot_centre():
    # Two wide chambers are raw-connected through a corridor too narrow for
    # the robot disc. The remote chamber has legal centres, but none reachable
    # from the mission start, so it is structurally uncoverable from this run.
    cells = np.ones((11, 18), dtype=np.uint8)
    cells[2:9, 1:7] = 0
    cells[5, 7:10] = 0
    cells[2:9, 10:17] = 0
    grid = GridMap(cells, .1)
    robot = Robot(grid, (5, 3), RobotConfig(diameter_m=.3, cleaning_width_m=.3))
    cleanable = build_cleanable_cells(grid, (5, 3), robot)
    assert (5, 13) in cleanable.cells
    assert robot.footprint.navigable[5, 13]
    assert (5, 13) in cleanable.structurally_uncoverable
    assert (5, 5) in cleanable.achievable_cells

