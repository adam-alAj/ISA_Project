"""Four-neighbor connected components and reachability reports."""

from collections import deque

import numpy as np


def reachable_from(mask: np.ndarray, start: tuple[int, int]) -> np.ndarray:
    """Return a bool mask of cells connected to start in Up, Right, Down, Left order."""
    if mask.ndim != 2:
        raise ValueError("mask must be two-dimensional")
    reached = np.zeros(mask.shape, dtype=bool)
    r, c = start
    if not (0 <= r < mask.shape[0] and 0 <= c < mask.shape[1]) or not mask[start]:
        return reached
    reached[start] = True
    queue = deque([start])
    offsets = ((-1, 0), (0, 1), (1, 0), (0, -1))
    while queue:
        row, col = queue.popleft()
        for dr, dc in offsets:
            nr, nc = row + dr, col + dc
            if 0 <= nr < mask.shape[0] and 0 <= nc < mask.shape[1] and mask[nr, nc] and not reached[nr, nc]:
                reached[nr, nc] = True
                queue.append((nr, nc))
    return reached


def connected_components(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """Label true cells by 4-connectivity; background has label zero."""
    if mask.ndim != 2:
        raise ValueError("mask must be two-dimensional")
    labels = np.zeros(mask.shape, dtype=np.int32)
    count = 0
    for row, col in zip(*np.nonzero(mask)):
        if labels[row, col]:
            continue
        count += 1
        labels[row, col] = count
        queue = deque([(int(row), int(col))])
        while queue:
            r, c = queue.popleft()
            for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < mask.shape[0] and 0 <= nc < mask.shape[1] and mask[nr, nc] and not labels[nr, nc]:
                    labels[nr, nc] = count
                    queue.append((nr, nc))
    return labels, count
