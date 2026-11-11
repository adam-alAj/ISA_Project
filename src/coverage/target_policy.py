"""Deterministic nearest-un-cleaned target policy backed by a balanced kd-tree."""
from dataclasses import dataclass

Cell = tuple[int, int]


@dataclass
class _Node:
    cell: Cell
    axis: int
    left: "_Node | None"
    right: "_Node | None"
    bounds: tuple[int, int, int, int]
    active: bool = True
    active_count: int = 1


class NearestUncleanedPolicy:
    """Find the Manhattan-nearest active cell; row/column resolve equal distances.

    A balanced two-dimensional kd-tree is built once. Cleaned and excluded cells
    are removed incrementally, so queries prune inactive subtrees instead of
    scanning the entire cleanable set per target.
    """
    policy_id = "nearest_uncleaned_manhattan_v1"

    def __init__(self, cells):
        self.cells = frozenset(tuple(cell) for cell in cells)
        self.reset()

    def reset(self) -> None:
        """Reactivate every candidate for a new run using the same policy config."""
        self._inactive: set[Cell] = set()
        self._root = self._build(list(self.cells), 0) if self.cells else None

    def _build(self, cells: list[Cell], depth: int) -> _Node | None:
        if not cells:
            return None
        axis = depth % 2
        cells.sort(key=lambda cell: (cell[axis], cell[1-axis]))
        middle = len(cells) // 2
        cell = cells[middle]
        left = self._build(cells[:middle], depth + 1)
        right = self._build(cells[middle+1:], depth + 1)
        rows = [cell[0]]; cols = [cell[1]]
        for child in (left, right):
            if child:
                r0, r1, c0, c1 = child.bounds
                rows.extend((r0, r1)); cols.extend((c0, c1))
        count = 1 + (left.active_count if left else 0) + (right.active_count if right else 0)
        return _Node(cell, axis, left, right, (min(rows), max(rows), min(cols), max(cols)), True, count)

    def _remove(self, node: _Node | None, cell: Cell) -> None:
        if node is None or node.active_count == 0:
            return
        if node.cell == cell:
            node.active = False
        elif cell[node.axis] < node.cell[node.axis] or (
            cell[node.axis] == node.cell[node.axis] and cell[1-node.axis] < node.cell[1-node.axis]
        ):
            self._remove(node.left, cell)
        else:
            self._remove(node.right, cell)
        node.active_count = int(node.active) + (node.left.active_count if node.left else 0) + (
            node.right.active_count if node.right else 0)

    @staticmethod
    def _box_distance(position: Cell, bounds: tuple[int, int, int, int]) -> int:
        r, c = position
        r0, r1, c0, c1 = bounds
        return max(r0-r, 0, r-r1) + max(c0-c, 0, c-c1)

    def next_target(self, state, cleaned) -> Cell | None:
        """Return the nearest uncleaned cell with deterministic `(row, col)` ties."""
        for cell in cleaned:
            cell = tuple(cell)
            if cell in self.cells and cell not in self._inactive:
                self._inactive.add(cell)
                self._remove(self._root, cell)
        if self._root is None or self._root.active_count == 0:
            return None
        best: Cell | None = None
        best_distance = float("inf")

        def visit(node: _Node | None) -> None:
            nonlocal best, best_distance
            if node is None or node.active_count == 0:
                return
            if self._box_distance(state.position, node.bounds) > best_distance:
                return
            distance = abs(node.cell[0]-state.position[0]) + abs(node.cell[1]-state.position[1])
            if node.active and (distance < best_distance or (distance == best_distance and (best is None or node.cell < best))):
                best, best_distance = node.cell, distance
            children = [child for child in (node.left, node.right) if child and child.active_count]
            children.sort(key=lambda child: self._box_distance(state.position, child.bounds))
            for child in children:
                visit(child)

        visit(self._root)
        return best
