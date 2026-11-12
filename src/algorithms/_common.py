"""Shared budget, trace, counters and path helpers for search implementations."""

from time import perf_counter
from typing import Any, Generic, Hashable, Iterable, TypeVar

from .problem import SearchProblem
from .result import SearchOptions, SearchResult, TerminationReason


NodeT = TypeVar("NodeT", bound=Hashable)


def json_node(node: Any) -> Any:
    """Convert common state types to JSON-safe trace values."""
    if node is None or isinstance(node, (str, int, float, bool)):
        return node
    if isinstance(node, tuple):
        return [json_node(item) for item in node]
    if isinstance(node, list):
        return [json_node(item) for item in node]
    return repr(node)


class SearchContext(Generic[NodeT]):
    """Per-call mutable counters per ``docs/search_counters.md``.

    These values are raw planner accounting; see ``docs/metrics.md`` for the
    aggregate semantics used by reports. Context state is never shared across
    invocations.
    """

    def __init__(self, problem: SearchProblem[NodeT], options: SearchOptions | None) -> None:
        self.problem = problem
        self.options = options or SearchOptions()
        self.started = perf_counter()
        self.expanded = 0
        self.generated = 0
        self.peak_frontier = 0
        self.repeated_expansions = 0
        self.expanded_nodes: set[NodeT] = set()
        self.events: list[dict[str, Any]] | None = [] if self.options.collect_trace else None
        self.trace_enabled = self.options.collect_trace or self.options.trace_callback is not None
        self.last_snapshot_expansion = -1

    def elapsed(self) -> float:
        """Return elapsed search-only wall-clock seconds."""
        return max(0.0, perf_counter() - self.started)

    def time_budget_hit(self) -> bool:
        """Return whether the configured time budget has elapsed."""
        limit = self.options.time_budget_s
        return limit is not None and self.elapsed() >= limit

    def expansion_budget_hit(self) -> bool:
        """Return whether another node expansion would exceed the budget."""
        limit = self.options.max_expansions
        return limit is not None and self.expanded >= limit

    def emit(self, event: str, **fields: Any) -> None:
        """Emit a JSON-serializable trace event only when tracing is enabled."""
        if not self.trace_enabled:
            return
        value = {"event": event, **fields}
        if self.events is not None:
            self.events.append(value)
        if self.options.trace_callback is not None:
            self.options.trace_callback(dict(value))

    def set_frontier(self, size: int) -> None:
        """Update peak frontier and emit a sampled snapshot if requested."""
        self.peak_frontier = max(self.peak_frontier, size)
        interval = self.options.frontier_sample_every
        if (interval and self.expanded and self.expanded % interval == 0
                and self.last_snapshot_expansion != self.expanded):
            self.last_snapshot_expansion = self.expanded
            self.emit("FrontierSnapshot", expanded=self.expanded, size=size)

    def expand(self, node: NodeT, *, depth: int | None, cost: float | None, frontier_size: int) -> None:
        """Count one expansion and any repeated expansion of this node."""
        if node in self.expanded_nodes:
            self.repeated_expansions += 1
        else:
            self.expanded_nodes.add(node)
        self.expanded += 1
        self.emit("NodeExpanded", node=json_node(node), depth=depth, path_cost=cost,
                  expanded=self.expanded, frontier_size=frontier_size)

    def generated_node(self, source: NodeT, target: NodeT, *, depth: int | None,
                       cost: float, frontier_size: int) -> None:
        """Count and optionally emit a generated successor, duplicates included."""
        self.generated += 1
        self.emit("NodeGenerated", source=json_node(source), node=json_node(target),
                  depth=depth, path_cost=cost, generated=self.generated, frontier_size=frontier_size)

    def make_result(self, reason: TerminationReason, path: Iterable[NodeT] = (),
                    path_cost: float | None = None) -> SearchResult[NodeT]:
        """Freeze counters, duration, path and optional collected trace."""
        path_tuple = tuple(path)
        found = reason is TerminationReason.GOAL_FOUND
        if found:
            self.emit("GoalReached", node=json_node(path_tuple[-1]) if path_tuple else None,
                      path_length_steps=max(0, len(path_tuple) - 1), path_cost=path_cost)
        return SearchResult(
            found=found,
            path=path_tuple,
            path_length_steps=max(0, len(path_tuple) - 1) if found else None,
            path_cost=float(path_cost) if found and path_cost is not None else (0.0 if found else None),
            expanded=self.expanded,
            generated=self.generated,
            peak_frontier=self.peak_frontier,
            repeated_expansions=self.repeated_expansions,
            execution_time_s=self.elapsed(),
            termination_reason=reason,
            trace=tuple(self.events) if self.events is not None else None,
        )


def endpoint_failure(context: SearchContext[NodeT]) -> SearchResult[NodeT] | None:
    """Return a common-schema invalid endpoint result, if required."""
    if not context.problem.is_valid_node(context.problem.start):
        return context.make_result(TerminationReason.INVALID_START)
    if not context.problem.is_valid_node(context.problem.goal):
        return context.make_result(TerminationReason.INVALID_GOAL)
    return None


def start_is_goal(context: SearchContext[NodeT]) -> SearchResult[NodeT] | None:
    """Apply the shared zero-expansion policy for a valid start==goal call."""
    if context.problem.is_goal(context.problem.start):
        return context.make_result(TerminationReason.GOAL_FOUND, (context.problem.start,), 0.0)
    return None


def reconstruct(parent: dict[NodeT, NodeT | None], goal: NodeT) -> tuple[NodeT, ...]:
    """Reconstruct a path from parent pointers, including both endpoints."""
    path: list[NodeT] = []
    current: NodeT | None = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return tuple(path)


def path_cost(problem: SearchProblem[NodeT], path: Iterable[NodeT]) -> float:
    """Sum transition costs along a completed path."""
    nodes = tuple(path)
    return sum(problem.step_cost(a, b) for a, b in zip(nodes, nodes[1:]))
