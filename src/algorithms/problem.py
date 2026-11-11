"""Search problem definition and GridMap adapter."""

from dataclasses import dataclass
import math
from typing import Callable, Generic, Hashable, Iterable, TypeVar

import numpy as np

from src.environment.grid_map import GridMap


NodeT = TypeVar("NodeT", bound=Hashable)


@dataclass(frozen=True)
class SearchProblem(Generic[NodeT]):
    """A deterministic point-to-point graph problem with non-negative costs."""

    start: NodeT
    goal: NodeT
    neighbors_fn: Callable[[NodeT], Iterable[NodeT]]
    step_cost_fn: Callable[[NodeT, NodeT], float]
    heuristic_fn: Callable[[NodeT], float] | None = None
    valid_node_fn: Callable[[NodeT], bool] | None = None
    all_nodes: tuple[NodeT, ...] | None = None
    min_step_cost: float = 1.0

    def __post_init__(self) -> None:
        """Validate callbacks and lower-bound cost metadata."""
        if not callable(self.neighbors_fn) or not callable(self.step_cost_fn):
            raise TypeError("neighbors_fn and step_cost_fn must be callable")
        if not math.isfinite(self.min_step_cost) or self.min_step_cost < 0:
            raise ValueError("min_step_cost must be finite and non-negative")

    def neighbors(self, node: NodeT) -> tuple[NodeT, ...]:
        """Return successors in the caller-provided deterministic order."""
        return tuple(self.neighbors_fn(node))

    def step_cost(self, source: NodeT, target: NodeT) -> float:
        """Return a finite non-negative transition cost."""
        try:
            raw_cost = self.step_cost_fn(source, target)
        except TypeError as two_argument_error:
            # Accept mapping-style callables keyed by (source, target), while
            # keeping the documented two-argument callback as the primary API.
            try:
                raw_cost = self.step_cost_fn((source, target))  # type: ignore[call-arg]
            except TypeError:
                raise two_argument_error
        cost = float(raw_cost)
        if not math.isfinite(cost) or cost < 0:
            raise ValueError("step costs must be finite and non-negative")
        return cost

    def is_goal(self, node: NodeT) -> bool:
        """Test whether a node is the requested goal."""
        return node == self.goal

    def heuristic(self, node: NodeT) -> float:
        """Return the configured heuristic or zero when none is provided."""
        if self.heuristic_fn is None:
            return 0.0
        value = float(self.heuristic_fn(node))
        if not math.isfinite(value) or value < 0:
            raise ValueError("heuristic values must be finite and non-negative")
        return value

    def is_valid_node(self, node: NodeT) -> bool:
        """Check endpoint validity when a validator was supplied."""
        return self.valid_node_fn(node) if self.valid_node_fn is not None else True

    @classmethod
    def from_grid_map(
        cls,
        grid_map: GridMap,
        start: tuple[int, int],
        goal: tuple[int, int],
        *,
        costs: np.ndarray | None = None,
        heuristic_fn: Callable[[tuple[int, int]], float] | None = None,
    ) -> "SearchProblem[tuple[int, int]]":
        """Build a four-neighbor problem; optional costs charge entry into a cell."""
        cost_layer: np.ndarray | None = None
        if costs is not None:
            cost_layer = np.array(costs, dtype=float, copy=True)
            if cost_layer.shape != grid_map.shape or not np.isfinite(cost_layer).all() or (cost_layer < 0).any():
                raise ValueError("cost layer must match the grid and contain finite non-negative values")
            traversable_costs = cost_layer[np.isin(grid_map.grid, (0, 3))]
            minimum = float(traversable_costs.min()) if traversable_costs.size else 0.0
            cost_layer.setflags(write=False)
        else:
            minimum = 1.0

        def step_cost(_source: tuple[int, int], target: tuple[int, int]) -> float:
            return 1.0 if cost_layer is None else float(cost_layer[target])

        if heuristic_fn is None:
            from .heuristics import manhattan
            h_fn = lambda node: manhattan(node, goal, minimum)
        else:
            h_fn = heuristic_fn
        nodes = tuple(map(tuple, np.argwhere(np.isin(grid_map.grid, (0, 3)))))
        return cls(
            start=start,
            goal=goal,
            neighbors_fn=grid_map.neighbors,
            step_cost_fn=step_cost,
            heuristic_fn=h_fn,
            valid_node_fn=grid_map.is_traversable,
            all_nodes=nodes,
            min_step_cost=minimum,
        )
