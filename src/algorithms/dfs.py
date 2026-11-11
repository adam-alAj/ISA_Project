"""Iterative depth-first graph search with deterministic neighbor order."""

from typing import Hashable, TypeVar

from ._common import SearchContext, endpoint_failure, path_cost, reconstruct, start_is_goal
from .problem import SearchProblem
from .result import SearchOptions, SearchResult, TerminationReason


NodeT = TypeVar("NodeT", bound=Hashable)


def dfs(problem: SearchProblem[NodeT], options: SearchOptions | None = None) -> SearchResult[NodeT]:
    """Run explicit-stack DFS; reverse pushes preserve U,R,D,L expansion order."""
    context = SearchContext(problem, options)
    invalid = endpoint_failure(context)
    if invalid is not None:
        return invalid
    immediate = start_is_goal(context)
    if immediate is not None:
        return immediate

    stack = [problem.start]
    parent: dict[NodeT, NodeT | None] = {problem.start: None}
    discovered = {problem.start}
    depth: dict[NodeT, int] = {problem.start: 0}
    context.set_frontier(1)
    while stack:
        if context.time_budget_hit():
            return context.make_result(TerminationReason.TIME_BUDGET_EXCEEDED)
        node = stack.pop()
        if problem.is_goal(node):
            path = reconstruct(parent, node)
            return context.make_result(TerminationReason.GOAL_FOUND, path, path_cost(problem, path))
        if context.expansion_budget_hit():
            return context.make_result(TerminationReason.NODE_BUDGET_EXCEEDED)
        context.expand(node, depth=depth[node], cost=None, frontier_size=len(stack))
        successors = problem.neighbors(node)
        push_candidates: list[tuple[NodeT, int]] = []
        for successor in successors:
            cost = problem.step_cost(node, successor)
            novel = successor not in discovered
            context.generated_node(node, successor, depth=depth[node] + 1, cost=cost,
                                   frontier_size=len(stack) + len(push_candidates) + int(novel))
            if novel:
                discovered.add(successor)
                parent[successor] = node
                depth[successor] = depth[node] + 1
                push_candidates.append((successor, depth[successor]))
        for successor, _successor_depth in reversed(push_candidates):
            stack.append(successor)
            context.set_frontier(len(stack))
    return context.make_result(TerminationReason.NO_PATH)
