"""Generate reproducible P8 sample records and PDFs from real tiny-map runs."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.analytics.records import load_run_record
from src.analytics.benchmark import benchmark_repetitions
from src.app.app_controller import AppController
from src.reporting.report_generator import generate_comparison_pdf, generate_run_pdf
OUTPUT = ROOT / "reports" / "sample" / "benchmarks"
ALGORITHMS = ("bfs", "dfs", "ucs", "greedy", "astar", "iddfs")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = {"point_to_point": [], "coverage": []}
    timing = {}
    grid = np.zeros((6, 6), dtype=np.uint8)
    grid[2, 2] = 1
    for mode in records:
        for algorithm in ALGORITHMS:
            measured = 0
            record_paths = []
            def run_once(seed):
                nonlocal measured
                controller = AppController(data_root=OUTPUT)
                controller.import_grid(grid, cell_m=1.0, version="p8-sample-v1")
                if not controller.set_start((0, 0)):
                    raise RuntimeError("sample map start rejected")
                controller.algorithm, controller.mode = algorithm, mode
                controller.experiment_seed = seed
                if mode == "point_to_point" and not controller.set_goal((5, 5)):
                    raise RuntimeError("sample goal rejected")
                result = controller.run()
                planner_time = (result.execution_time_s if mode == "point_to_point"
                                else result.planner_wall_time_s)
                measured += 1
                # Call one is the discarded warm-up. Persist only the five measured runs.
                if measured > 1:
                    record_paths.append(controller.record_completed_run(result))
                return result, planner_time
            summary = benchmark_repetitions(run_once, repetitions=5, seed=17)
            timing[f"{mode}:{algorithm}"] = {key: summary[key] for key in
                ("seed", "warmup_discarded", "warmup_seconds_discarded", "repetitions", "samples_s",
                 "median_s", "q1_s", "q3_s", "iqr_s", "machine")}
            records[mode].extend(load_run_record(path) for path in record_paths)
    (OUTPUT / "timing_protocol.json").write_text(__import__("json").dumps(timing, indent=2), encoding="utf-8")
    generate_run_pdf(records["point_to_point"][0], OUTPUT / "sample_point_to_point_bfs.pdf")
    generate_comparison_pdf(records["point_to_point"], OUTPUT / "comparison_point_to_point.pdf")
    generate_comparison_pdf(records["coverage"], OUTPUT / "comparison_coverage.pdf")
    print(f"Generated {sum(map(len, records.values()))} measured real engine run records (12 discarded warm-ups) in {OUTPUT / 'experiments'}")
    print(f"Per-run PDF: {OUTPUT / 'sample_point_to_point_bfs.pdf'}")
    print(f"Point-to-point comparison PDF: {OUTPUT / 'comparison_point_to_point.pdf'}")
    print(f"Coverage comparison PDF: {OUTPUT / 'comparison_coverage.pdf'}")


if __name__ == "__main__":
    main()
