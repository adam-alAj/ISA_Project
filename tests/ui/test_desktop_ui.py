from pathlib import Path
import os
import time

import numpy as np
import pytest
from PySide6.QtGui import QImage
from PySide6.QtCore import QTimer

from src.algorithms.registry import REGISTRY
from src.app.app_controller import AppController
from src.app.main_window import MainWindow
from src.app.simulation_worker import SimulationWorker
from src.coverage.cleanable import build_cleanable_cells
from src.coverage.controller import CoverageController
from src.coverage.target_policy import NearestUncleanedPolicy
from src.environment.grid_map import GridMap
from src.robot.config import RobotConfig
from src.robot.vacuum_robot import Robot
from src.visualization.two_d.map_canvas import MapCanvas

ROOT = Path(__file__).resolve().parents[2]


def test_eight_screens_and_department_map_load(qtbot,tmp_path):
    window = MainWindow(AppController(data_root=tmp_path/"data"))
    qtbot.addWidget(window); window.show()
    assert window.stack.count() == 8
    assert window.nav.count() == 8
    window.controller.load_map(ROOT/"data"/"maps"/"department_v1")
    assert window.controller.map.shape == (127, 120)
    assert window.controller.start == (118, 54)
    assert "1.0-draft" in window.statusBar().currentMessage()


def _golden_canvas(qtbot):
    grid = np.array([[0, 0, 3, 1, 2, 0], [0, 1, 0, 0, 2, 0], [0, 0, 0, 3, 0, 0],
                     [2, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0]], dtype=np.uint8)
    canvas = MapCanvas(); canvas.setFixedSize(640, 480); canvas.set_map(grid, (4,0), (0,5))
    cleaned = np.zeros(grid.shape, dtype=bool); cleaned[3,1]=True; cleaned[2,2]=True
    canvas.set_overlay(cleaned=cleaned, explored={(1,0),(1,1),(2,1)}, path=((4,0),(3,0),(2,0),(1,0)), robot=(2,0))
    qtbot.addWidget(canvas); canvas.show(); qtbot.wait(80)
    # Ignore platform-dependent frame, focus and device-scale pixels.
    # Integer scene scaling avoids fractional-pixel raster differences across
    # Windows Qt paint devices while still exercising the complete map layer.
    return canvas.render_content(480, 400, include_marker_labels=False)


def test_map_canvas_matches_fixed_golden_image(qtbot):
    actual = _golden_canvas(qtbot)
    golden_path = ROOT / "docs/img/map_canvas_golden.png"
    if os.environ.get("UPDATE_MAP_GOLDEN") == "1":
        assert actual.save(str(golden_path)), "could not update map golden image"
    golden = QImage(str(golden_path)).convertToFormat(QImage.Format.Format_RGBA8888)
    assert not golden.isNull(), "golden image asset is missing"
    assert (actual.width(), actual.height()) == (golden.width(), golden.height())
    size=actual.sizeInBytes()
    assert actual.constBits().tobytes()[:size] == golden.constBits().tobytes()[:size]


def test_displayed_point_to_point_metrics_match_engine(qtbot, tmp_path):
    controller=AppController(data_root=tmp_path/"data"); controller.import_grid(np.zeros((7,7),dtype=np.uint8),.1)
    assert controller.set_start((3,3)); assert controller.set_goal((3,5))
    controller.mode="point_to_point"; controller.algorithm="bfs"
    window=MainWindow(controller); qtbot.addWidget(window)
    worker=SimulationWorker(controller)
    with qtbot.waitSignal(worker.finished_result,timeout=5000) as result:
        worker.start()
    assert worker.wait(1000)
    window._run_finished(result.args[0])
    assert controller.search_result.path_length_steps == controller.robot.state.step_count == 2
    assert f"Path steps: {controller.search_result.path_length_steps}" in window.results_text.text()
    assert f"{controller.search_result.execution_time_s:.4f} s" in window.results_text.text()
    assert list((tmp_path/"data"/"experiments").glob("run_*.json"))


def test_experiment_config_round_trip_and_recent_run_list(tmp_path):
    data_root=tmp_path/"data"; controller=AppController(data_root=data_root)
    controller.load_map(ROOT/"data"/"maps"/"department_v1"); controller.algorithm="astar"; controller.mode="point_to_point"
    assert controller.recent_map_records()[0]["version"]==controller.map_version
    controller.paint((0,0),int(0))  # Edited map is embedded, not silently reloaded from the original bundle.
    config=data_root/"experiments"/"saved.json"; controller.save_experiment(config)
    restored=AppController(data_root=data_root); restored.load_experiment(config)
    assert restored.algorithm=="astar" and restored.mode=="point_to_point"
    assert restored.start==controller.start and restored.map_version==controller.map_version
    assert np.array_equal(restored.map.grid,controller.map.grid)
    run_path=restored.record_completed_run(type("Result",(),{"coverage_percent":12.5,"raw_coverage_percent":10.0,"stop_reason":type("Stop",(),{"value":"user_stop"})(),"planner_wall_time_s":.02})())
    recent=restored.recent_experiments()
    assert {Path(row["_path"]).name for row in recent}=={"saved.json",run_path.name}


def test_cancelled_worker_exits_at_safe_boundary(qtbot):
    grid=GridMap(np.zeros((9,9),dtype=np.uint8),.1)
    robot=Robot(grid,(4,4),RobotConfig(diameter_m=.1,cleaning_width_m=.1,
               battery_capacity_units=1e6,operational_lifetime_s=1e6))
    cleanable=build_cleanable_cells(grid,(4,4),robot); policy=NearestUncleanedPolicy(cleanable.cells)
    coverage=CoverageController(robot,cleanable,policy,REGISTRY["bfs"],"bfs")
    coverage.pause(); worker=SimulationWorker(coverage); worker.start(); qtbot.wait(80)
    assert worker.isRunning(); coverage.cancel(); assert worker.wait(2000)
    assert coverage.events.events[-1].payload["reason"] == "user_stop"


def test_window_stop_tears_down_coverage_worker(qtbot,tmp_path):
    controller=AppController(data_root=tmp_path/"data"); controller.load_map(ROOT/"data"/"maps"/"department_v1")
    window=MainWindow(controller); qtbot.addWidget(window); window.show()
    window._start_run()
    qtbot.waitUntil(lambda: controller.coverage_controller is not None,timeout=3000)
    window._stop()
    qtbot.waitUntil(lambda: window._worker is not None and not window._worker.isRunning(),timeout=5000)
    window.close()
    assert not window._worker.isRunning()


def test_gui_timer_latency_stays_under_100ms_during_coverage(qtbot,tmp_path):
    controller=AppController(data_root=tmp_path/"data"); controller.load_map(ROOT/"data"/"maps"/"department_v1")
    controller.mode="coverage"; controller.algorithm="bfs"
    window=MainWindow(controller); qtbot.addWidget(window); window.show()
    qtbot.wait(100)  # Let the initial full-map paint complete before measuring run-time latency.
    times=[]; timer=QTimer(window); timer.setInterval(30)
    timer.timeout.connect(lambda:times.append(time.perf_counter()))
    timer.start(); window._start_run()
    def cancel_run():
        if controller.coverage_controller is None:
            QTimer.singleShot(30,cancel_run)
        else:
            controller.coverage_controller.cancel()
    QTimer.singleShot(500,cancel_run)
    qtbot.waitUntil(lambda: window._worker is not None and not window._worker.isRunning(),timeout=10000)
    timer.stop()
    delays=[(b-a)*1000 for a,b in zip(times,times[1:])]
    print(f"ui_timer_samples={len(times)}; max_event_interval_ms={max(delays,default=0):.2f}")
    assert times and (not delays or max(delays)<100), f"max timer delay was {max(delays,default=0):.1f} ms"
