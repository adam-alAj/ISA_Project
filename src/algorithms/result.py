"""Shared search result, budgets, termination reasons and trace schema."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generic, Hashable, TypeVar


NodeT = TypeVar("NodeT", bound=Hashable)
TraceCallback = Callable[[dict[str, Any]], None]


class TerminationReason(str, Enum):
    """Why a search call returned."""

    GOAL_FOUND = "goal_found"
    NO_PATH = "no_path"
    INVALID_START = "invalid_start"
    INVALID_GOAL = "invalid_goal"
    NODE_BUDGET_EXCEEDED = "node_budget_exceeded"
    TIME_BUDGET_EXCEEDED = "time_budget_exceeded"
    DEPTH_LIMIT_EXCEEDED = "depth_limit_exceeded"


@dataclass(frozen=True)
class SearchOptions:
    """Per-call resource and tracing controls; no state is shared across runs."""

    max_expansions: int | None = None
    time_budget_s: float | None = None
    iddfs_max_depth: int | None = None
    collect_trace: bool = False
    trace_callback: TraceCallback | None = None
    frontier_sample_every: int = 0

    def __post_init__(self) -> None:
        """Validate non-negative search budgets and trace sampling interval."""
        import math

        if self.max_expansions is not None and self.max_expansions < 0:
            raise ValueError("max_expansions cannot be negative")
        if self.time_budget_s is not None and (not math.isfinite(self.time_budget_s) or self.time_budget_s < 0):
            raise ValueError("time_budget_s must be finite and non-negative")
        if self.iddfs_max_depth is not None and self.iddfs_max_depth < 0:
            raise ValueError("iddfs_max_depth cannot be negative")
        if self.frontier_sample_every < 0:
            raise ValueError("frontier_sample_every cannot be negative")


@dataclass(frozen=True)
class SearchResult(Generic[NodeT]):
    """Comparable point-to-point result; counter semantics are frozen in docs/search_counters.md.

    Metric names, path length/cost, and timing interpretation are defined in
    ``docs/metrics.md``. These fields are raw planner output, not robot travel
    or simulated action time.
    """

    found: bool
    path: tuple[NodeT, ...]
    path_length_steps: int | None
    path_cost: float | None
    expanded: int
    generated: int
    peak_frontier: int
    repeated_expansions: int
    execution_time_s: float
    termination_reason: TerminationReason
    trace: tuple[dict[str, Any], ...] | None = None


SearchFn = Callable[[Any, SearchOptions | None], SearchResult[Any]]
