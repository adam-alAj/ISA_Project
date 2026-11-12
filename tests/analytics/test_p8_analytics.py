import csv
import json

import pytest

from src.analytics.comparison import IncomparableRuns, comparison_rows
from src.analytics.metrics import summarize_timings, extract_metrics
from src.analytics.benchmark import benchmark_repetitions
from src.analytics.records import load_run_record, save_run_record, stable_run_id
from src.analytics.summary import RunSummary
from src.reporting.report_generator import export_metrics_csv, factual_interpretation, guard_interpretation


def _record(mode="point_to_point", algorithm="bfs"):
    experiment = {"mode": mode, "algorithm": algorithm, "robot": {"battery_capacity_units": 10},
                  "seed": 7,
                  "start": [0, 0], "goal": [0, 1] if mode == "point_to_point" else None,
                  "movement_model": "four-neighbor-cardinal", "search_budgets": {},
                  "policy": {"id": "nearest"} if mode == "coverage" else None,
                  "neighbor_order": ["up", "right", "down", "left"], "cost_model": {"step": 1},
                  "heuristic": "manhattan", "algorithm_settings": {}}
    return {"schema_version": 1, "kind": "run_record", "run_id": stable_run_id("a" * 64, experiment, algorithm,
            experiment["policy"], 7), "created_utc": "2026-11-12T00:00:00+00:00",
            "map": {"sha256": "a" * 64, "version": "test", "rows": 2, "cols": 2, "cell_m": .5,
                    "origin_px": [0, 0], "id": "tiny", "grid": [[0, 0], [1, 0]]}, "experiment": experiment,
            "metrics": {"expanded": 4, "generated": 8, "repeated_expansions": 0, "peak_frontier": 3,
                        "path_length_steps": 2, "path_length_m": 1.0, "path_cost": 2.0,
                        "search_time_s": .25, "simulated_travel_time_s": 8.0,
                        "battery_consumed_units": 1.2, "lifetime_consumed_s": 8,
                        "achievable_coverage_percent": 80.0, "raw_coverage_percent": 75.0,
                        "coverage_numerator_cells": 3, "coverage_denominator_cells": 4,
                        "stop_reason": "mission_complete"},
            "raw_results": {"search_results": [], "coverage_result": None, "final_robot_state": {},
                            "cleaned_cells": []},
            "project": {"name": "Smart Vacuum", "version": "test", "python": "3.12", "os": "test", "cpu": "test"}}


def test_run_record_sidecar_roundtrip_and_digest(tmp_path):
    record = _record()
    path = save_run_record(record, tmp_path, [{"type": "RunStarted", "schema_version": 1,
        "seq": 0, "t_sim": 0, "payload": {}}])
    loaded = load_run_record(path)
    assert loaded["event_log"]["event_count"] == 1
    assert loaded["run_id"] == record["run_id"]
    second = save_run_record(record, tmp_path, [])
    assert second != path
    assert (tmp_path / "runs.csv").read_bytes().count(b"\xef\xbb\xbf") == 1
    sidecar = tmp_path / loaded["event_log"]["path"]
    sidecar.write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        load_run_record(path)


def test_comparison_requires_same_context_and_mode():
    a, b = _record(algorithm="bfs"), _record(algorithm="astar")
    assert len(comparison_rows([a, b])["rows"]) == 2
    b["map"]["sha256"] = "b" * 64
    with pytest.raises(IncomparableRuns, match="map.sha256"):
        comparison_rows([a, b])
    b = _record("coverage", "astar")
    with pytest.raises(IncomparableRuns, match="modes differ"):
        comparison_rows([a, b])


def test_comparability_checks_cost_heuristic_neighbor_and_robot():
    a, b = _record(), _record(algorithm="astar")
    b["experiment"]["robot"] = {"battery_capacity_units": 11}
    b["experiment"]["cost_model"] = {"step": 2}
    b["experiment"]["heuristic"] = "euclidean"
    b["experiment"]["neighbor_order"] = ["right", "up", "left", "down"]
    from src.analytics.comparison import comparability_issues
    issues = comparability_issues([a, b])
    assert "experiment.robot differs across runs" in issues
    assert "experiment.cost_model differs across runs" in issues
    assert "experiment.heuristic differs across runs" in issues
    assert "experiment.neighbor_order differs across runs" in issues


def test_interpretation_contains_required_caveats_and_no_global_claim():
    text = factual_interpretation(_record())
    assert "returned a route of 2 steps" in text
    assert "universally" not in text.lower()
    assert RunSummary.from_record(_record()).render_text().startswith("Point To Point · BFS")
    with pytest.raises(ValueError, match="superlative"):
        guard_interpretation("BFS is the best. " + text[text.index("DFS depends"):])


def test_csv_bom_columns_and_values_roundtrip(tmp_path):
    path = export_metrics_csv([_record()], tmp_path / "metrics.csv")
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        row = next(csv.DictReader(stream))
    assert row["search_time_s"] == "0.25"
    assert row["stop_reason"] == "mission_complete"


def test_timing_summary_reports_median_and_iqr():
    summary = summarize_timings([1, 2, 3, 4, 5])
    assert summary["median_s"] == 3
    assert summary["repetitions"] == 5
    assert summary["iqr_s"] == 2


def test_benchmark_discards_warmup_and_requires_five_samples():
    calls = []
    def run(seed):
        calls.append(seed)
        return {"sample": len(calls)}, .1 * len(calls)
    benchmark = benchmark_repetitions(run, repetitions=5, seed=42)
    assert calls == [42] * 6
    assert benchmark["warmup_discarded"] is True
    assert benchmark["repetitions"] == 5
    assert benchmark["median_s"] == .4
    assert set(("cpu", "python", "os")) <= benchmark["machine"].keys()
    with pytest.raises(ValueError, match="five"):
        benchmark_repetitions(run, repetitions=4)


def test_search_timing_uses_planner_event_not_simulated_or_ui_elapsed_time():
    events = [
        {"type": "RunStarted", "t_sim": 0, "seq": 0, "payload": {}},
        {"type": "SearchFinished", "t_sim": 999, "seq": 1,
         "payload": {"planner_execution_time_s": .125, "expanded": 2, "generated": 3,
                     "peak_frontier": 1, "repeated_expansions": 0, "found": True,
                     "path_length_steps": 1, "path_cost": 1}},
        {"type": "RunStopped", "t_sim": 1000, "seq": 2, "payload": {"reason": "mission_complete"}},
    ]
    result = extract_metrics(events=events, mode="coverage", cell_m=.2)
    assert result["search_time_s"] == .125
    assert result["simulated_travel_time_s"] == 1000
