"""GPU-independent correctness tests for the 3D projection and grid mesher."""

from pathlib import Path

import numpy as np
import pytest

from src.algorithms.registry import REGISTRY
from src.environment.grid_map import GridMap
from src.map_processing.map_io import load_map
from src.map_processing.spec_loader import load_spec
from src.robot.config import RobotConfig
from src.robot.vacuum_robot import Robot
from src.simulation.modes import PointToPointMission
from src.simulation.simulation_engine import SimulationEngine
from src.visualization.three_d.coords import cell_to_world, world_route, world_to_cell
from src.visualization.three_d.meshing import (
    build_scene_layout, expand_rectangles, greedy_rectangles, move_event_cells,
    occupied_border_mask, route_is_clear, traversable_mask,
)

ROOT=Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("cell_m",(.05,.1,.25))
def test_cell_world_round_trip_for_centres_and_edges(cell_m):
    for row in range(0,127,11):
        for col in range(0,120,13):
            world=cell_to_world((row,col),cell_m)
            assert np.allclose(world,(col*cell_m+cell_m/2,0,-(row*cell_m+cell_m/2)))
            assert world_to_cell(world,cell_m)==(row,col)


def test_greedy_rectangle_mesher_is_exact_and_disjoint():
    rng=np.random.default_rng(709)
    for _ in range(30):
        mask=rng.random((23,19))<.43
        rectangles=greedy_rectangles(mask)
        assert np.array_equal(expand_rectangles(mask.shape,rectangles),mask)
        assert len(rectangles)<=int(mask.sum())


def test_department_scene_footprints_match_grid_and_stay_under_entity_budget():
    grid,metadata=load_map(ROOT/"data"/"maps"/"department_v1")
    metadata["spec"]=load_spec(ROOT/"data"/"maps"/"department_v1"/"map_spec.yaml")
    layout=build_scene_layout(grid,float(metadata["cell_m"]),metadata)
    assert np.array_equal(expand_rectangles(grid.shape,layout.floors),traversable_mask(grid))
    assert np.array_equal(expand_rectangles(grid.shape,layout.walls),layout.wall_mask)
    assert np.array_equal(layout.wall_mask,occupied_border_mask(grid)&~layout.object_mask)
    assert not np.any(layout.floor_mask&layout.wall_mask)
    assert not np.any(layout.wall_mask&(grid==3))
    assert np.all(grid[layout.object_mask]==1)
    assert {obj.name for obj in layout.objects}==set(metadata["spec"]["obstacles"])
    # Include camera, lights, robot/body indicator, dynamic mesh entities, text and labels.
    estimated_total=layout.static_entity_count+len(metadata["spec"]["rooms"])+7
    assert estimated_total<2000


def test_three_d_move_event_sequence_matches_engine_route():
    grid,_=load_map(ROOT/"data"/"maps"/"department_v1")
    grid_map=GridMap(grid,.1)
    start=(118,54); goal=(118,68)
    robot=Robot(grid_map,start,RobotConfig())
    result,event_log=SimulationEngine(robot).run_point_to_point(
        PointToPointMission(start,goal),REGISTRY["bfs"])
    cells=move_event_cells(start,event_log.events)
    assert result.found and cells==result.path
    assert route_is_clear(grid,cells)
    assert world_route(cells,.1)==tuple(cell_to_world(cell,.1) for cell in result.path)


def test_movement_route_validator_rejects_door_gap_fill_and_diagonals():
    grid=np.array([[1,1,1,1,1],[1,0,3,0,1],[1,1,1,1,1]],dtype=np.uint8)
    assert route_is_clear(grid,((1,1),(1,2),(1,3)))
    assert not route_is_clear(grid,((1,1),(1,3)))
    assert not route_is_clear(grid,((1,1),(2,2)))
    assert not route_is_clear(grid,((1,2),(0,2)))
