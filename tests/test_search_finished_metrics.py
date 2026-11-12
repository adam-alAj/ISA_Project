"""P8 analytics needs raw planner summaries on frozen simulation events."""

import numpy as np

from src.algorithms.bfs import bfs
from src.environment.grid_map import GridMap
from src.robot.config import RobotConfig
from src.robot.vacuum_robot import Robot
from src.simulation.modes import PointToPointMission
from src.simulation.simulation_engine import SimulationEngine


def test_point_to_point_search_finished_event_contains_result_counters():
    robot = Robot(GridMap(np.zeros((5, 5), dtype=np.uint8), .1), (2, 1),
                  RobotConfig(diameter_m=.1, cleaning_width_m=.1))
    result, event_log = SimulationEngine(robot).run_point_to_point(
        PointToPointMission((2, 1), (2, 3)), bfs)
    finished = next(event for event in event_log.snapshot_events() if event.type == "SearchFinished")
    assert finished.schema_version == 1
    assert finished.payload["expanded"] == result.expanded
    assert finished.payload["generated"] == result.generated
    assert finished.payload["peak_frontier"] == result.peak_frontier
    assert finished.payload["repeated_expansions"] == result.repeated_expansions
    assert finished.payload["path_length_steps"] == result.path_length_steps
    assert finished.payload["path_cost"] == result.path_cost
    assert finished.payload["planner_execution_time_s"] == result.execution_time_s
    assert finished.payload["termination_reason"] == result.termination_reason.value
