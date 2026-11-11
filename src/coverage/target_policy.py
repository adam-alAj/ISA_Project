"""Deterministic nearest-un-cleaned target policy."""
from collections import defaultdict


class NearestUncleanedPolicy:
    """Use a row/column spatial index and expanding Manhattan rings."""
    policy_id = "nearest_uncleaned_manhattan_v1"

    def __init__(self, cells):
        self.cells = frozenset(cells)
        self._rows = defaultdict(list)
        for r, c in self.cells:
            self._rows[r].append(c)
        self._bounds = (min((r for r, _ in self.cells), default=0),
                        max((r for r, _ in self.cells), default=-1),
                        min((c for _, c in self.cells), default=0),
                        max((c for _, c in self.cells), default=-1))
        for cols in self._rows.values():
            cols.sort()

    def next_target(self, state, cleaned) -> tuple[int, int] | None:
        """Return nearest uncleaned cell, with row then column tie breaking."""
        # Indexed row ranges prune work as Manhattan radius grows; termination is
        # immediate for nearby targets and does not compare every pair up front.
        r0, c0 = state.position
        rmin, rmax, cmin, cmax = self._bounds
        max_radius = max(abs(rmin-r0)+abs(cmin-c0), abs(rmin-r0)+abs(cmax-c0),
                         abs(rmax-r0)+abs(cmin-c0), abs(rmax-r0)+abs(cmax-c0))
        for radius in range(max_radius + 1):
            found = []
            for row in range(r0-radius, r0+radius+1):
                rem = radius - abs(row-r0)
                for col in self._rows.get(row, ()):
                    if abs(col-c0) == rem and (row,col) not in cleaned:
                        found.append((row,col))
            if found:
                return min(found)
        return None
