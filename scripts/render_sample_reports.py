"""Render benchmark sample PDFs again from stored records without rerunning planners."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.analytics.records import load_run_record
from src.reporting.report_generator import generate_comparison_pdf, generate_run_pdf


def main():
    output = ROOT / "reports" / "sample" / "benchmarks"
    records = {"point_to_point": [], "coverage": []}
    for path in (output / "experiments").glob("run_*.json"):
        record = load_run_record(path)
        if record["map"]["version"] == "p8-sample-v1":
            records[record["experiment"]["mode"]].append(record)
    for mode, runs in records.items():
        if not runs or any(sum(run["experiment"]["algorithm"] == algo for run in runs) < 5
                           for algo in ("bfs", "dfs", "ucs", "greedy", "astar", "iddfs")):
            raise RuntimeError(f"stored {mode} runs do not include five repetitions of all six algorithms")
    generate_run_pdf(next(record for record in records["point_to_point"]
                          if record["experiment"]["algorithm"] == "bfs"), output / "sample_point_to_point_bfs.pdf")
    generate_comparison_pdf(records["point_to_point"], output / "comparison_point_to_point.pdf")
    generate_comparison_pdf(records["coverage"], output / "comparison_coverage.pdf")
    print("Rendered PDFs from versioned run records; no planner was invoked.")


if __name__ == "__main__":
    main()
