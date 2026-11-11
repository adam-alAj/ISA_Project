"""A* search with strict-improvement reopens and lazy stale-entry deletion."""

import heapq
from itertools import count
from typing import Hashable, TypeVar

from ._common import SearchContext, endpoint_failure, path_cost, reconstruct, start_is_goal
from .problem import SearchProblem
from .result import SearchOptions, SearchResult, TerminationReason


NodeT = TypeVar("NodeT", bound=Hashable)


def astar(problem: SearchProblem[NodeT], options: SearchOptions | None = None) -> SearchResult[NodeT]:
    """Minimize f=g+h; ties prefer lower h and then earlier insertion."""
    context = SearchContext(problem, options)
    invalid = endpoint_failure(context)
    if invalid is not None:
        return invalid
    immediate = start_is_goal(context)
    if immediate is not None:
        return immediate

    order = count()
    h_start = problem.heuristic(problem.start)
    frontier: list[tuple[float, float, int, float, NodeT]] = [
        (h_start, h_start, next(order), 0.0, problem.start)
    ]
    best_g: dict[NodeT, float] = {problem.start: 0.0}
    expanded_best_g: dict[NodeT, float] = {}
    parent: dict[NodeT, NodeT | None] = {problem.start: None}
    context.set_frontier(1)
    while frontier:
        if context.time_budget_hit():
            return context.make_result(TerminationReason.TIME_BUDGET_EXCEEDED)
        _f, _h, _sequence, g, node = heapq.heappop(frontier)
        context.set_frontier(len(frontier))
        if g != best_g.get(node):  # stale path superseded by a lower g value
            continue
        if node in expanded_best_g and g >= expanded_best_g[node]:
            continue
        if problem.is_goal(node):
            path = reconstruct(parent, node)
            return context.make_result(TerminationReason.GOAL_FOUND, path, path_cost(problem, path))
        if context.expansion_budget_hit():
            return context.make_result(TerminationReason.NODE_BUDGET_EXCEEDED)
        expanded_best_g[node] = g
        context.expand(node, depth=None, cost=g, frontier_size=len(frontier))
        for successor in problem.neighbors(node):
            edge_cost = problem.step_cost(node, successor)
            candidate = g + edge_cost
            if candidate < best_g.get(successor, float("inf")):
                best_g[successor] = candidate
                parent[successor] = node
                h = problem.heuristic(successor)
                heapq.heappush(frontier, (candidate + h, h, next(order), candidate, successor))
            context.generated_node(node, successor, depth=None, cost=candidate,
                                   frontier_size=len(frontier))
            context.set_frontier(len(frontier))
    return context.make_result(TerminationReason.NO_PATH)
