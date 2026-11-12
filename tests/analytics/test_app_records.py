import numpy as np

from src.app.app_controller import AppController
from src.analytics.records import load_run_record


def test_completed_app_run_writes_schema_valid_replay_bundle(tmp_path):
    controller = AppController(data_root=tmp_path / "data")
    controller.import_grid(np.zeros((4, 4), dtype=np.uint8), cell_m=1, version="test-map")
    assert controller.set_start((0, 0))
    controller.algorithm = "bfs"
    controller.mode = "point_to_point"
    assert controller.set_goal((0, 2))
    result = controller.run()
    record_path = controller.record_completed_run(result)
    record = load_run_record(record_path)
    assert record["experiment"]["mode"] == "point_to_point"
    assert record["metrics"]["path_length_steps"] == 2
    assert record["raw_results"]["map"] if "map" in record["raw_results"] else record["map"]["grid"]

    controller._make_robot()
    controller.mode = "coverage"
    coverage = controller.run()
    coverage_path = controller.record_completed_run(coverage)
    coverage_record = load_run_record(coverage_path)
    assert coverage_record["metrics"]["coverage_denominator_cells"] == 16
    assert coverage_record["metrics"]["achievable_coverage_percent"] == 100
