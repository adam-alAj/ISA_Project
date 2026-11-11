"""Headless median-time search benchmark on department-map demo pairs."""

from __future__ import annotations

import csv
import statistics
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.algorithms import REGISTRY, SearchOptions, SearchProblem
from src.environment.grid_map import GridMap


def main() -> None:
    map_dir = ROOT / "data/maps/department_v1"
    grid = np.load(map_dir / "department_map.npy")
    metadata = __import__("json").loads((map_dir / "map.json").read_text(encoding="utf-8"))
    grid_map = GridMap(grid, cell_m=float(metadata["cell_m"]))
    demos = ROOT / "docs/map_spec/demo_goals.csv"
    rows = list(csv.DictReader(demos.open(newline="", encoding="utf-8-sig")))
    pairs = [row for row in rows if row["start_mode"] == "default_S" and row["reachable_from_scenario_start"].lower() == "true"][:6]
    start = tuple(map(int, metadata["start_cell"]))
    output = ROOT / "reports/bench_search.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scenario", "algorithm", "runs", "median_time_s", "expanded", "generated", "path_cost", "termination_reason"])
        for pair in pairs:
            goal = (int(pair["goal_row"]), int(pair["goal_col"]))
            problem = SearchProblem.from_grid_map(grid_map, start, goal)
            for name, search in REGISTRY.items():
                durations = []
                last = None
                for _ in range(5):
                    begin = time.perf_counter()
                    last = search(problem, SearchOptions(max_expansions=50_000, time_budget_s=2.0,
                                                         iddfs_max_depth=300))
                    durations.append(time.perf_counter() - begin)
                writer.writerow([pair["scenario"], name, 5, statistics.median(durations),
                                 last.expanded, last.generated, last.path_cost,
                                 last.termination_reason.value])
    print(output)


if __name__ == "__main__":
    main()
