"""Reference and regression tests for the pure search engine."""

import json
import random

import numpy as np

from src.algorithms import REGISTRY, SearchOptions, SearchProblem, TerminationReason, get_algorithm
from src.algorithms.heuristics import manhattan
from src.environment.grid_map import GridMap


def grid_problem(rows, start, goal, costs=None, heuristic=None):
    grid = GridMap(np.asarray(rows, dtype=np.uint8), cell_m=0.1)
    return SearchProblem.from_grid_map(grid, start, goal, costs=costs, heuristic_fn=heuristic)


def oracle(problem):
    """Independent O(V^2) Dijkstra oracle, intentionally unlike heap search."""
    distance = {problem.start: 0.0}
    remaining = set(problem.all_nodes or (problem.start, problem.goal))
    while remaining:
        available = [node for node in remaining if node in distance]
        if not available:
            break
        node = min(available, key=distance.__getitem__)
        remaining.remove(node)
        if node == problem.goal:
            return distance[node]
        for nxt in problem.neighbors(node):
            candidate = distance[node] + problem.step_cost(node, nxt)
            if candidate < distance.get(nxt, float("inf")):
                distance[nxt] = candidate
    return None


def test_registry_schema_order_and_alias():
    assert set(REGISTRY) == {"bfs", "dfs", "ucs", "greedy", "astar", "iddfs"}
    assert get_algorithm("idfs") is get_algorithm("iddfs")
    problem = grid_problem([[0, 0, 0], [0, 0, 0], [0, 0, 0]], (1, 1), (0, 1))
    for name, search in REGISTRY.items():
        result = search(problem, SearchOptions(collect_trace=True))
        assert result.found and result.path[0] == problem.start and result.path[-1] == problem.goal
        assert result.path_length_steps == 1
        assert result.expanded >= 0 and result.generated >= 0
        json.dumps(result.trace)


def test_bfs_counter_policy_and_neighbor_order():
    problem = grid_problem([[0, 0, 0], [0, 0, 0], [0, 0, 0]], (1, 1), (0, 1))
    result = REGISTRY["bfs"](problem)
    assert result.path == ((1, 1), (0, 1))
    assert (result.expanded, result.generated, result.peak_frontier) == (1, 4, 4)


def test_endpoints_disconnection_and_budgets():
    open_grid = [[0, 0], [0, 0]]
    same = grid_problem(open_grid, (0, 0), (0, 0))
    assert REGISTRY["bfs"](same).expanded == 0
    invalid_start = grid_problem([[1, 0]], (0, 0), (0, 1))
    assert REGISTRY["bfs"](invalid_start).termination_reason is TerminationReason.INVALID_START
    invalid_goal = grid_problem([[0, 1]], (0, 0), (0, 1))
    assert REGISTRY["bfs"](invalid_goal).termination_reason is TerminationReason.INVALID_GOAL
    disconnected = grid_problem([[0, 1, 0]], (0, 0), (0, 2))
    assert REGISTRY["iddfs"](disconnected).termination_reason is TerminationReason.NO_PATH
    assert REGISTRY["bfs"](same, SearchOptions(max_expansions=0)).found
    long = grid_problem([[0, 0, 0]], (0, 0), (0, 2))
    assert REGISTRY["bfs"](long, SearchOptions(max_expansions=0)).termination_reason is TerminationReason.NODE_BUDGET_EXCEEDED
    assert REGISTRY["iddfs"](long, SearchOptions(iddfs_max_depth=0)).termination_reason is TerminationReason.DEPTH_LIMIT_EXCEEDED


def test_weighted_improvement_stale_entries_and_astar_reopen():
    graph = {"S": ("A", "B"), "A": ("G",), "B": ("A",), "G": ()}
    costs = {("S", "A"): 5, ("S", "B"): 1, ("B", "A"): 1, ("A", "G"): 1}
    problem = SearchProblem("S", "G", graph.__getitem__, costs.__getitem__, all_nodes=tuple(graph))
    assert REGISTRY["ucs"](problem).path_cost == 3

    reopen_graph = {"S": ("A", "B"), "A": ("G",), "B": ("A",), "G": ()}
    reopen_cost = {("S", "A"): 3, ("S", "B"): 1, ("B", "A"): 1, ("A", "G"): 10}
    h = {"S": 0, "A": 0, "B": 10, "G": 0}  # admissible, deliberately inconsistent on B->A
    inconsistent = SearchProblem("S", "G", reopen_graph.__getitem__, reopen_cost.__getitem__,
                                 h.__getitem__, all_nodes=tuple(reopen_graph))
    result = REGISTRY["astar"](inconsistent)
    assert result.path_cost == 12
    assert result.repeated_expansions >= 1


def test_greedy_trap_against_astar():
    graph = {"S": ("A", "B"), "A": ("A1",), "A1": ("A2",), "A2": ("A3",),
             "A3": ("G",), "B": ("B2",), "B2": ("G",), "G": ()}
    h = {"S": 0, "A": 1, "A1": 0, "A2": 0, "A3": 0, "B": 2, "B2": 1, "G": 0}
    p = SearchProblem("S", "G", graph.__getitem__, lambda _a, _b: 1, h.__getitem__, all_nodes=tuple(graph))
    assert REGISTRY["greedy"](p).path_cost > REGISTRY["astar"](p).path_cost


def test_seeded_bfs_and_weighted_oracles():
    rng = np.random.default_rng(219)
    for _ in range(200):
        cells = (rng.random((6, 7)) > 0.27).astype(np.uint8)
        cells[0, 0] = cells[-1, -1] = 0
        p = SearchProblem.from_grid_map(GridMap(cells, cell_m=0.1), (0, 0), (5, 6))
        assert REGISTRY["bfs"](p).path_length_steps == oracle(p)
    cost_rng = np.random.default_rng(220)
    for _ in range(50):
        cells = (rng.random((5, 6)) > 0.2).astype(np.uint8)
        cells[0, 0] = cells[-1, -1] = 0
        costs = cost_rng.integers(1, 6, size=cells.shape).astype(float)
        p = SearchProblem.from_grid_map(GridMap(cells, cell_m=0.1), (0, 0), (4, 5), costs=costs)
        ucs, astar = REGISTRY["ucs"](p), REGISTRY["astar"](p)
        assert ucs.path_cost == oracle(p) == astar.path_cost


def test_iddfs_depth_progression_and_trace_sampling():
    p = grid_problem([[0, 0, 0]], (0, 0), (0, 2))
    result = REGISTRY["iddfs"](p, SearchOptions(collect_trace=True, frontier_sample_every=1))
    limits = [event["depth_limit"] for event in result.trace if event["event"] == "DepthIterationStarted"]
    assert limits == [0, 1, 2]
    assert result.path_length_steps == 2 and result.repeated_expansions > 0
    assert any(e["event"] == "FrontierSnapshot" for e in result.trace)
