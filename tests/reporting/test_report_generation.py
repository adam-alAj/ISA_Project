import csv

import pytest
from pypdf import PdfReader

from src.analytics.records import stable_run_id
from src.reporting.report_generator import (export_metrics_csv, generate_comparison_pdf,
                                             generate_run_pdf)


def _record(algorithm):
    experiment = {"mode": "point_to_point", "algorithm": algorithm, "algorithm_settings": {},
                  "start": [0, 0], "goal": [0, 1], "seed": 4, "robot": {"battery_capacity_units": 10},
                  "policy": None, "neighbor_order": ["up", "right", "down", "left"],
                  "movement_model": "four-neighbor-cardinal", "cost_model": {"transition": "unit"},
                  "heuristic": None}
    return {"run_id": stable_run_id("a" * 64, experiment, algorithm, None, 4),
            "created_utc": "2026-11-12T00:00:00+00:00", "experiment": experiment,
            "map": {"sha256": "a" * 64, "version": "tiny", "rows": 2, "cols": 2,
                    "cell_m": .2, "origin_px": [0, 0], "grid": [[0, 0], [1, 0]]},
            "raw_results": {"search_results": [], "visualization": {"route_cells": [[0, 0], [0, 1]],
                "explored_cells": [[0, 0]], "cleaned_cells": []}},
            "metrics": {"expanded": 2, "generated": 3, "repeated_expansions": 0, "peak_frontier": 1,
                        "path_length_steps": 1, "path_length_m": .2, "path_cost": 1,
                        "search_time_s": .01, "simulated_travel_time_s": .2,
                        "battery_consumed_units": .1, "lifetime_consumed_s": .2,
                        "achievable_coverage_percent": None, "raw_coverage_percent": None,
                        "stop_reason": "mission_complete"}}


def test_pdf_and_csv_reproduce_record_values(tmp_path):
    record = _record("bfs")
    pdf = generate_run_pdf(record, tmp_path / "run.pdf")
    text = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)
    assert record["run_id"] in text
    assert "0.01" in text
    assert "Map snapshot" in text
    csv_path = export_metrics_csv([record], tmp_path / "metrics.csv")
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        row = next(csv.DictReader(stream))
    assert float(row["search_time_s"]) == record["metrics"]["search_time_s"]
    assert int(row["path_length_steps"]) == record["metrics"]["path_length_steps"]


def test_comparison_pdf_parses_and_keeps_runs_separate(tmp_path):
    records = []
    for algorithm in ("bfs", "astar"):
        for repetition in range(5):
            record = _record(algorithm)
            record["metrics"]["search_time_s"] += repetition * .01
            records.append(record)
    pdf = generate_comparison_pdf(records, tmp_path / "comparison.pdf")
    text = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)
    assert "Point To Point comparison" in text
    assert "BFS" in text and "ASTAR" in text
    assert "Search median (s)" in text and "IQR (s)" in text
    assert "0.03" in text and "0.02" in text
    assert (tmp_path / "comparison.png").exists()
