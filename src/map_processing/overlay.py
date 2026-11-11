"""Grid overlay rendering for a source image or map preview."""

from pathlib import Path

import numpy as np


def render_grid_overlay(image: np.ndarray, output_path: str | Path, cell_pixels: float) -> None:
    """Save a copy of an image with a configurable-pixel grid overlay."""
    if image.ndim not in (2, 3) or cell_pixels <= 0:
        raise ValueError("image must be 2D/3D and cell_pixels positive")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.imshow(image, cmap="gray" if image.ndim == 2 else None)
    height, width = image.shape[:2]
    ax.set_xticks(np.arange(0, width, cell_pixels), minor=True)
    ax.set_yticks(np.arange(0, height, cell_pixels), minor=True)
    ax.grid(which="minor", color="#00a6a6", linewidth=0.35, alpha=0.65)
    ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)
    fig.tight_layout(pad=0)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
