"""Heuristics for deterministic four-neighbor grid search."""

import heapq
import math
from typing import Hashable

from .problem import SearchProblem


def manhattan(node: tuple[int, int], goal: tuple[int, int], min_step_cost: float = 1.0) -> float:
    """Return Manhattan distance scaled by the minimum transition cost."""
    if min_step_cost < 0 or not math.isfinite(min_step_cost):
        raise ValueError("min_step_cost must be finite and non-negative")
    return (abs(node[0] - goal[0]) + abs(node[1] - goal[1])) * min_step_cost


def assert_heuristic_admissible_and_consistent(
    problem: SearchProblem[Hashable], *, tolerance: float = 1e-9
) -> None:
    """Raise AssertionError if a finite problem's heuristic violates either property."""
    if problem.all_nodes is None:
        raise ValueError("all_nodes is required to verify a finite problem")
    nodes = problem.all_nodes
    reverse: dict[Hashable, list[tuple[Hashable, float]]] = {node: [] for node in nodes}
    if abs(problem.heuristic(problem.goal)) > tolerance:
        raise AssertionError("heuristic must be zero at the goal")
    for node in nodes:
        for successor in problem.neighbors(node):
            cost = problem.step_cost(node, successor)
            if problem.heuristic(node) > cost + problem.heuristic(successor) + tolerance:
                raise AssertionError(f"heuristic is inconsistent on edge {node!r}->{successor!r}")
            reverse.setdefault(successor, []).append((node, cost))
    # Dijkstra on reversed edges gives exact cost-to-go values for all reachable nodes.
    distance: dict[Hashable, float] = {problem.goal: 0.0}
    heap: list[tuple[float, int, Hashable]] = [(0.0, 0, problem.goal)]
    sequence = 1
    while heap:
        cost_so_far, _order, node = heapq.heappop(heap)
        if cost_so_far != distance.get(node):
            continue
        for predecessor, edge_cost in reverse.get(node, ()):
            candidate = cost_so_far + edge_cost
            if candidate < distance.get(predecessor, math.inf):
                distance[predecessor] = candidate
                heapq.heappush(heap, (candidate, sequence, predecessor))
                sequence += 1
    for node, exact_cost in distance.items():
        if problem.heuristic(node) > exact_cost + tolerance:
            raise AssertionError(f"heuristic overestimates from {node!r}: {problem.heuristic(node)} > {exact_cost}")
