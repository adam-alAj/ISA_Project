"""NumPy-only obstacle inflation for circular robot footprints."""

import numpy as np


def navigable_mask(grid: np.ndarray, cell_m: float, radius_m: float) -> np.ndarray:
    """Return traversable robot-center cells after disc-kernel obstacle inflation."""
    if grid.ndim != 2 or cell_m <= 0 or radius_m < 0:
        raise ValueError("grid must be 2D, cell_m positive, and radius_m non-negative")
    traversable = np.isin(grid, (0, 3))
    blocked = ~traversable
    radius_cells = int(np.ceil(radius_m / cell_m))
    inflated = blocked.copy()
    # Quantize outward to whole cells, matching the conservative project rule.
    for dr in range(-radius_cells, radius_cells + 1):
        for dc in range(-radius_cells, radius_cells + 1):
            if dr * dr + dc * dc > radius_cells * radius_cells:
                continue
            src_r0, src_r1 = max(0, -dr), min(grid.shape[0], grid.shape[0] - dr)
            src_c0, src_c1 = max(0, -dc), min(grid.shape[1], grid.shape[1] - dc)
            dst_r0, dst_r1 = src_r0 + dr, src_r1 + dr
            dst_c0, dst_c1 = src_c0 + dc, src_c1 + dc
            inflated[dst_r0:dst_r1, dst_c0:dst_c1] |= blocked[src_r0:src_r1, src_c0:src_c1]
    result = ~inflated
    result.setflags(write=False)
    return result
