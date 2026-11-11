"""Static Matplotlib map preview with redundant state cues."""

from pathlib import Path
from typing import Mapping

import numpy as np


def render_map_preview(
    grid: np.ndarray,
    output_path: str | Path,
    *,
    start: tuple[int, int] | None = None,
    room_labels: Mapping[str, tuple[int, int]] | None = None,
) -> None:
    """Save a labeled grid image; door and unknown cells use hatching/markers."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch

    if grid.ndim != 2:
        raise ValueError("grid must be two-dimensional")
    fig, ax = plt.subplots(figsize=(9, 11))
    cmap = ListedColormap(("#f4f4f4", "#272a35", "#f4b942", "#65b96e"))
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=3, interpolation="nearest")
    rows, cols = np.indices(grid.shape)
    doors = grid == 3
    unknown = grid == 2
    ax.scatter(cols[doors], rows[doors], marker="+", s=8, c="black", linewidths=0.4, label="Door cells")
    ax.scatter(cols[unknown], rows[unknown], marker="x", s=8, c="black", linewidths=0.4, label="Unknown cells")
    occupied = np.ma.masked_where(grid != 1, grid)
    ax.contourf(occupied, levels=(0.5, 1.5), colors="none", hatches=("///",), alpha=0)
    ax.set_xticks(np.arange(-0.5, grid.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid.shape[0], 1), minor=True)
    ax.grid(which="minor", color="#777777", linewidth=0.12, alpha=0.35)
    if start is not None:
        ax.plot(start[1], start[0], marker="*", color="red", markersize=12, label="Start S")
    for label, (row, col) in (room_labels or {}).items():
        ax.text(col, row, label, ha="center", va="center", color="darkred", weight="bold")
    ax.legend(handles=[Patch(facecolor="#f4f4f4", edgecolor="black", label="FREE"),
                       Patch(facecolor="#272a35", edgecolor="black", hatch="///", label="OCCUPIED"),
                       Patch(facecolor="#65b96e", edgecolor="black", hatch="xx", label="DOOR"),
                       Patch(facecolor="#f4b942", edgecolor="black", hatch="..", label="UNKNOWN")],
              loc="lower left", fontsize=8)
    ax.set_title(f"Department occupancy grid: {grid.shape[0]} × {grid.shape[1]}")
    ax.set_xlabel("Column (increases right)")
    ax.set_ylabel("Row (increases down)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=130)
    plt.close(fig)
