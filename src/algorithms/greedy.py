"""Greedy Best-First Search; complete on finite graphs, but not optimal."""

import heapq
from itertools import count
from typing import Hashable, TypeVar

from ._common import SearchContext, endpoint_failure, path_cost, reconstruct, start_is_goal
from .problem import SearchProblem
from .result import SearchOptions, SearchResult, TerminationReason


NodeT = TypeVar("NodeT", bound=Hashable)


def greedy(problem: SearchProblem[NodeT], options: SearchOptions | None = None) -> SearchResult[NodeT]:
    """Prioritize only h(n), resolving equal values FIFO by insertion counter."""
    context = SearchContext(problem, options)
    invalid = endpoint_failure(context)
    if invalid is not None:
        return invalid
    immediate = start_is_goal(context)
    if immediate is not None:
        return immediate

    order = count()
    frontier: list[tuple[float, int, NodeT]] = [(problem.heuristic(problem.start), next(order), problem.start)]
    discovered = {problem.start}
    parent: dict[NodeT, NodeT | None] = {problem.start: None}
    depth = {problem.start: 0}
    g_score = {problem.start: 0.0}
    context.set_frontier(1)
    while frontier:
        if context.time_budget_hit():
            return context.make_result(TerminationReason.TIME_BUDGET_EXCEEDED)
        _h, _sequence, node = heapq.heappop(frontier)
        context.set_frontier(len(frontier))
        if problem.is_goal(node):
            path = reconstruct(parent, node)
            return context.make_result(TerminationReason.GOAL_FOUND, path, path_cost(problem, path))
        if context.expansion_budget_hit():
            return context.make_result(TerminationReason.NODE_BUDGET_EXCEEDED)
        context.expand(node, depth=depth[node], cost=g_score[node], frontier_size=len(frontier))
        for successor in problem.neighbors(node):
            edge_cost = problem.step_cost(node, successor)
            candidate = g_score[node] + edge_cost
            if successor not in discovered:
                discovered.add(successor)
                parent[successor] = node
                depth[successor] = depth[node] + 1
                g_score[successor] = candidate
                heapq.heappush(frontier, (problem.heuristic(successor), next(order), successor))
            context.generated_node(node, successor, depth=depth[node] + 1, cost=candidate,
                                   frontier_size=len(frontier))
            context.set_frontier(len(frontier))
    return context.make_result(TerminationReason.NO_PATH)
