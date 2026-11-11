"""Breadth-first search for minimum-step paths on unweighted graphs."""

from collections import deque
from typing import Hashable, TypeVar

from ._common import SearchContext, endpoint_failure, path_cost, reconstruct, start_is_goal
from .problem import SearchProblem
from .result import SearchOptions, SearchResult, TerminationReason


NodeT = TypeVar("NodeT", bound=Hashable)


def bfs(problem: SearchProblem[NodeT], options: SearchOptions | None = None) -> SearchResult[NodeT]:
    """Run FIFO BFS; test goals when popped, before counting an expansion."""
    context = SearchContext(problem, options)
    invalid = endpoint_failure(context)
    if invalid is not None:
        return invalid
    immediate = start_is_goal(context)
    if immediate is not None:
        return immediate

    queue = deque([problem.start])
    parent: dict[NodeT, NodeT | None] = {problem.start: None}
    discovered = {problem.start}
    depths = {problem.start: 0}
    context.set_frontier(1)
    while queue:
        if context.time_budget_hit():
            return context.make_result(TerminationReason.TIME_BUDGET_EXCEEDED)
        node = queue.popleft()
        if problem.is_goal(node):
            path = reconstruct(parent, node)
            return context.make_result(TerminationReason.GOAL_FOUND, path, path_cost(problem, path))
        if context.expansion_budget_hit():
            return context.make_result(TerminationReason.NODE_BUDGET_EXCEEDED)
        depth = depths[node]
        context.expand(node, depth=depth, cost=None, frontier_size=len(queue))
        for successor in problem.neighbors(node):
            cost = problem.step_cost(node, successor)
            if successor not in discovered:
                discovered.add(successor)
                parent[successor] = node
                depths[successor] = depth + 1
                queue.append(successor)
            context.generated_node(node, successor, depth=depth + 1, cost=cost,
                                   frontier_size=len(queue))
            context.set_frontier(len(queue))
    return context.make_result(TerminationReason.NO_PATH)
