"""Build the v0.3 traced map through the reusable declarative P2 rasterizer."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.map_processing.rasterizer import rasterize
from src.map_processing.spec_loader import load_spec
from src.visualization.map_preview import render_map_preview


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "data" / "maps" / "department_v1" / "map_spec.yaml"
OUTPUT_DIR = ROOT / "data" / "maps" / "department_v0_3"


def build() -> dict[str, object]:
    """Rasterize the checked-in v1 draft spec and write the P1 v0.3 artifacts."""
    spec = load_spec(SPEC_PATH)
    result = rasterize(spec)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    np.save(OUTPUT_DIR / "department_map.npy", result.grid)
    metadata = dict(result.metadata)
    metadata.pop("spec", None)
    with (OUTPUT_DIR / "department_map.json").open("w", encoding="utf-8") as stream:
        json.dump(metadata, stream, indent=2)
    room_labels = {}
    ppm, cell_m = spec["parameters"]["ppm"], spec["parameters"]["cell_m"]
    xmin, ymin, _, _ = spec["domain_px"]
    for room, (x0, y0, x1, y1) in spec["rooms"].items():
        col = int(((x0 + x1) / 2 - xmin) / (ppm * cell_m))
        row = int(((y0 + y1) / 2 - ymin) / (ppm * cell_m))
        room_labels[room] = (row, col)
    render_map_preview(result.grid, OUTPUT_DIR / "map_preview.png", start=result.start_cell, room_labels=room_labels)
    return {"shape": result.grid.shape, "start": result.start_cell, "output": str(OUTPUT_DIR)}


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
