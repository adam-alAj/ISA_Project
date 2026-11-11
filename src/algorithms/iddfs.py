"""Iterative Deepening DFS with per-iteration best-depth dominance pruning."""

from typing import Hashable, TypeVar

from ._common import SearchContext, endpoint_failure, path_cost, start_is_goal
from .problem import SearchProblem
from .result import SearchOptions, SearchResult, TerminationReason


NodeT = TypeVar("NodeT", bound=Hashable)


def iddfs(problem: SearchProblem[NodeT], options: SearchOptions | None = None) -> SearchResult[NodeT]:
    """Run depth-limited DFS at limits 0,1,... with best-depth pruning.

    At each iteration a node is re-expanded only if reached at a strictly
    smaller depth. A shallower arrival leaves at least as much remaining depth,
    avoiding the exponential duplicate exploration of path-cycle-only IDDFS
    while preserving finite-graph completeness and shortest-step optimality.
    """
    context = SearchContext(problem, options)
    invalid = endpoint_failure(context)
    if invalid is not None:
        return invalid
    immediate = start_is_goal(context)
    if immediate is not None:
        return immediate

    depth_cap = context.options.iddfs_max_depth
    depth_limit = 0
    while True:
        context.emit("DepthIterationStarted", depth_limit=depth_limit)
        stack: list[tuple[NodeT, float, tuple[NodeT, ...]]] = [(problem.start, 0.0, (problem.start,))]
        best_depth: dict[NodeT, int] = {problem.start: 0}
        expanded_depth: dict[NodeT, int] = {}
        cutoff_possible = False
        context.set_frontier(1)
        while stack:
            if context.time_budget_hit():
                return context.make_result(TerminationReason.TIME_BUDGET_EXCEEDED)
            node, g, path = stack.pop()
            depth = len(path) - 1
            if depth > best_depth.get(node, depth):
                continue
            previous_expansion = expanded_depth.get(node)
            if previous_expansion is not None and depth >= previous_expansion:
                continue
            if problem.is_goal(node):
                return context.make_result(TerminationReason.GOAL_FOUND, path, path_cost(problem, path))

            if depth >= depth_limit:
                # A non-cycle successor not already explored more shallowly means
                # a larger depth bound may reveal more of the finite graph.
                for successor in problem.neighbors(node):
                    edge_cost = problem.step_cost(node, successor)
                    context.generated_node(node, successor, depth=depth + 1,
                                           cost=g + edge_cost, frontier_size=len(stack))
                    if successor not in path and depth + 1 < best_depth.get(successor, float("inf")):
                        cutoff_possible = True
                continue
            if context.expansion_budget_hit():
                return context.make_result(TerminationReason.NODE_BUDGET_EXCEEDED)

            expanded_depth[node] = depth
            context.expand(node, depth=depth, cost=g, frontier_size=len(stack))
            successors = problem.neighbors(node)
            push_candidates: list[tuple[NodeT, float, tuple[NodeT, ...]]] = []
            # Count successors in the environment's canonical U,R,D,L order.
            for successor in successors:
                edge_cost = problem.step_cost(node, successor)
                candidate_g = g + edge_cost
                candidate_depth = depth + 1
                can_visit = successor not in path and candidate_depth < best_depth.get(successor, float("inf"))
                context.generated_node(node, successor, depth=candidate_depth, cost=candidate_g,
                                       frontier_size=len(stack) + len(push_candidates) + int(can_visit))
                if can_visit:
                    best_depth[successor] = candidate_depth
                    push_candidates.append((successor, candidate_g, path + (successor,)))
            for candidate in reversed(push_candidates):
                stack.append(candidate)
            context.set_frontier(len(stack))

        if not cutoff_possible:
            return context.make_result(TerminationReason.NO_PATH)
        if depth_cap is not None and depth_limit >= depth_cap:
            return context.make_result(TerminationReason.DEPTH_LIMIT_EXCEEDED)
        depth_limit += 1
