"""Automated P6 gate evidence on the real MainWindow and department map."""

from pathlib import Path
import time

import numpy as np
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage

from src.app.app_controller import AppController
from src.app.main_window import MainWindow
from src.map_processing.constants import CellState
from src.visualization.two_d.map_canvas import MapCanvas
from src.app import strings as T


ROOT = Path(__file__).resolve().parents[2]


def _capture(window, folder: Path, name: str):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.png"
    assert window.grab().save(str(path)), f"failed to save screenshot: {path}"
    assert path.stat().st_size > 1_000
    return path


def _wait_finished(qtbot, window, timeout=30_000):
    qtbot.waitUntil(lambda: window._worker is not None and not window._worker.isRunning(), timeout=timeout)
    assert window._worker.wait(1000)
    qtbot.wait(30)


def test_scripted_p6_end_to_end_workflow_and_screenshots(qtbot, tmp_path):
    """Exercise load/start/config/algorithm/point/coverage/render/stop/results."""
    shots = ROOT / "docs" / "img" / "p6_e2e"
    controller = AppController(data_root=ROOT / "data")
    window = MainWindow(controller)
    qtbot.addWidget(window)
    window.show()
    _capture(window, shots, "01_project_home")

    qtbot.mouseClick(window.home_map_button, Qt.MouseButton.LeftButton)
    assert controller.map.shape == (127, 120)
    assert controller.start == (118, 54)
    _capture(window, shots, "02_department_map_loaded")

    window.nav.setCurrentRow(1)
    window.editor_canvas.set_pick_mode("start")
    window.editor_canvas.cell_clicked.emit(controller.start)
    assert controller.robot is not None
    _capture(window, shots, "03_start_selected")

    window.nav.setCurrentRow(2)
    window.robot_fields["battery_capacity_units"].setValue(10.0)
    window.robot_save.click()
    assert controller.robot_config.battery_capacity_units == 10.0
    _capture(window, shots, "04_robot_configured")

    window.nav.setCurrentRow(3)
    window.algorithm_combo.setCurrentIndex(window.algorithm_combo.findData("bfs"))
    window.mode_combo.setCurrentIndex(window.mode_combo.findData("point_to_point"))
    assert controller.algorithm == "bfs" and controller.mode == "point_to_point"
    assert controller.set_goal((118, 68))
    _capture(window, shots, "05_algorithm_and_goal_selected")

    window.nav.setCurrentRow(4)
    window.run_button.click()
    _wait_finished(qtbot, window)
    assert controller.search_result.found
    assert window.sim_canvas.path == controller.search_result.path
    assert "mission_complete" in window.stop_reason.text()
    assert controller.search_result.path_length_steps == controller.robot.state.step_count
    _capture(window, shots, "06_point_to_point_complete")

    # Reapply the limited but nonzero budget so the department coverage run
    # reaches a real resource stop and completes its normal run/stop workflow.
    window.nav.setCurrentRow(2)
    window.robot_fields["battery_capacity_units"].setValue(10.0)
    window.robot_save.click()
    window.nav.setCurrentRow(3)
    window.mode_combo.setCurrentIndex(window.mode_combo.findData("coverage"))
    assert controller.mode == "coverage"
    _capture(window, shots, "07_coverage_selected")

    window.nav.setCurrentRow(4)
    window.run_button.click()
    qtbot.waitUntil(lambda: controller.coverage_controller is not None, timeout=5000)
    _capture(window, shots, "08_coverage_running")
    _wait_finished(qtbot, window, timeout=60_000)
    result = controller.run_result
    assert result is not None and result.stop_reason.value in {"battery_depleted", "lifetime_expired", "mission_complete"}
    assert window.sim_canvas.explored, "explored overlay was not rendered"
    assert window.sim_canvas.path, "route overlay was not rendered"
    assert window.sim_canvas.cleaned.any(), "cleaned overlay was not rendered"
    assert "Stopped:" in window.stop_reason.text()
    _capture(window, shots, "09_coverage_layers_and_stop_reason")

    window.nav.setCurrentRow(6)
    assert f"{result.coverage_percent:.2f}%" in window.results_text.text()
    assert str(controller.robot.state.step_count) in window.results_text.text()
    assert result.stop_reason.value in window.results_text.text()
    _capture(window, shots, "10_results_dashboard")


def test_p6_dashboard_numbers_match_engine_state(qtbot, tmp_path):
    controller = AppController(data_root=ROOT / "data")
    controller.load_department_map()
    assert controller.set_goal((118, 68))
    controller.mode = "point_to_point"
    controller.algorithm = "bfs"
    window = MainWindow(controller)
    qtbot.addWidget(window)
    window.mode_combo.setCurrentIndex(window.mode_combo.findData("point_to_point"))
    window.algorithm_combo.setCurrentIndex(window.algorithm_combo.findData("bfs"))
    window._start_run()
    _wait_finished(qtbot, window)
    robot = controller.robot
    text = window.results_text.text()
    assert f"{robot.state.battery_remaining:.3f} / {robot.config.battery_capacity_units:.3f}" in text
    assert f"{robot.state.elapsed_time_s:.3f} s" in text
    assert f"{robot.state.lifetime_remaining_s:.3f} s" in text
    assert f"Steps: {robot.state.step_count}" in text
    assert "Stop reason: mission_complete" in text
    assert "Path steps: 14" in text


def test_p6_legend_covers_every_state_and_map_states_have_texture(qtbot):
    lowered = T.LEGEND.lower()
    for state in ("wall", "free", "unknown", "door", "explored", "frontier", "route", "cleaned", "robot", "start"):
        assert state in lowered
    grid = np.array([[CellState.FREE, CellState.OCCUPIED, CellState.UNKNOWN, CellState.DOOR]], dtype=np.uint8)
    canvas = MapCanvas()
    canvas.set_map(grid)
    qtbot.addWidget(canvas)
    # Every occupancy state has a fill plus a pattern/marker in its cached tile.
    image = canvas._base_image.convertToFormat(QImage.Format.Format_RGB32)
    for col in range(4):
        colors = {image.pixel(col * 8 + dx, dy) for dx in range(8) for dy in range(8)}
        assert len(colors) > 1, f"cell state {int(grid[0,col])} is color-only"


def test_p6_cancel_and_close_leaves_no_worker_thread(qtbot):
    controller = AppController(data_root=ROOT / "data")
    controller.load_department_map()
    window = MainWindow(controller)
    qtbot.addWidget(window)
    window.show()
    window._start_run()
    qtbot.waitUntil(lambda: controller.coverage_controller is not None, timeout=5000)
    controller.coverage_controller.cancel()
    window.close()
    qtbot.waitUntil(lambda: window._worker is not None and not window._worker.isRunning(), timeout=10000)
    assert not window._worker.isRunning()
    assert window.stack.count() == window.nav.count()
    assert all("3D" not in window.nav.item(i).text() for i in range(window.nav.count()))


def test_p6_department_coverage_responsiveness_through_terminal_stop(qtbot):
    """Measure GUI stalls/update rate through a complete, resource-limited run."""
    controller = AppController(data_root=ROOT / "data")
    controller.load_department_map()
    window = MainWindow(controller)
    qtbot.addWidget(window)
    window.show()
    window.speed_slider.setValue(6)  # fastest presentation setting; capped at ~29.4 Hz
    callback_times = []
    original_poll = window._poll_run

    def measured_poll():
        callback_times.append(time.perf_counter())
        original_poll()

    window._poll_run = measured_poll
    timer_times = []
    timer = QTimer(window)
    timer.setInterval(10)
    timer.timeout.connect(lambda: timer_times.append(time.perf_counter()))
    timer.start()
    started = time.perf_counter()
    window._start_run()
    _wait_finished(qtbot, window, timeout=60_000)
    elapsed = time.perf_counter() - started
    timer.stop()
    timer_gaps_ms = [(b-a)*1000 for a,b in zip(timer_times,timer_times[1:])]
    update_rate_hz = len(callback_times) / elapsed
    max_stall_ms = max(timer_gaps_ms, default=0.0)
    print(f"department_coverage_elapsed_s={elapsed:.3f}; ui_updates={len(callback_times)}; "
          f"ui_update_rate_hz={update_rate_hz:.2f}; max_gui_timer_gap_ms={max_stall_ms:.2f}; "
          f"stop_reason={controller.run_result.stop_reason.value}")
    assert controller.run_result is not None
    assert max_stall_ms < 100.0
    assert update_rate_hz <= 30.0

