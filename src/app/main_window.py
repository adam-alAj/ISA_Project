"""Main Qt desktop shell, pages and worker-driven simulation controls."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QListWidget, QMainWindow, QMessageBox, QPushButton,
    QProgressBar, QSlider, QStackedWidget, QTabWidget, QListWidgetItem,
    QVBoxLayout, QWidget,
)

from src.algorithms.registry import REGISTRY
from src.app.app_controller import AppController
from src.app.config import UiSettings, load_ui_settings, save_ui_settings
from src.app.simulation_worker import SimulationWorker
from src.app.theme import apply_theme
from src.app import strings as T
from src.map_processing.constants import CellState
from src.app.widgets import Banner, Card, MetricTile, PageHeader, StatusChip
from src.robot.config import RobotConfig
from src.visualization.two_d.map_canvas import MapCanvas


class CalibrationImage(QWidget):
    """Image calibration panel with two clicked pixel references."""
    point_clicked = Signal(tuple)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None; self.points = []
        self.setMinimumSize(320, 220)

    def load(self, path):
        from PySide6.QtGui import QPixmap
        self.image = QPixmap(str(path)); self.points.clear(); self.update()

    def mousePressEvent(self, event):
        if self.image and not self.image.isNull():
            self.points.append((event.position().x(), event.position().y()))
            self.points = self.points[-2:]; self.update()
            self.point_clicked.emit(self.points[-1])

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QPen, QColor
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.palette().color(self.backgroundRole()))
        if self.image and not self.image.isNull():
            pix = self.image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            origin = self.rect().center() - pix.rect().center(); painter.drawPixmap(origin, pix)
        else:
            painter.setPen(self.palette().color(self.foregroundRole())); painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                "Load a floor-plan image, then click the two reference points")
        painter.setPen(QPen(self.palette().color(self.palette().ColorRole.Highlight), 3))
        for point in self.points: painter.drawEllipse(int(point[0])-5, int(point[1])-5, 10, 10)


class MainWindow(QMainWindow):
    """Seven-screen application with controller-mediated domain operations."""
    def __init__(self, app_controller: AppController | None = None, theme_mode: str | None = None):
        super().__init__()
        self.controller = app_controller or AppController()
        self.ui_settings = load_ui_settings()
        self.theme_mode = theme_mode or self.ui_settings.theme
        self.setWindowTitle(T.APP_TITLE); self.resize(1440, 900)
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / "brand" / "app_icon.ico")))
        self._worker: SimulationWorker | None = None
        self._target = None; self._last_seq = -1; self._close_pending = False
        self._build_shell(); self._build_pages(); self._connect()
        apply_theme(QApplication.instance(), self.theme_mode, window=self)
        # Snapshot/event presentation is intentionally capped at 10 Hz. The
        # worker still executes every action; this bounds GUI paint work.
        self.timer = QTimer(self); self.timer.setInterval(100); self.timer.timeout.connect(self._poll_run)
        self._shortcuts()
        self.status_chip = StatusChip("idle")
        self.theme_toggle = QPushButton("Theme: Light" if self.theme_mode == "light" else "Theme: Dark")
        self.theme_toggle.clicked.connect(self._toggle_theme)
        self.statusBar().addPermanentWidget(self.status_chip)
        self.statusBar().addPermanentWidget(self.theme_toggle)
        self.statusBar().showMessage(f"Map: {self.controller.map_version}  |  {T.STATUS_IDLE}")

    def _build_shell(self):
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 16, 14, 16)
        side_layout.setSpacing(8)
        brand = QLabel("Smart Vacuum")
        brand.setObjectName("SidebarBrandTitle")
        side_layout.addWidget(brand)
        self.nav = QListWidget()
        nav_icons = (
            "home.svg",
            "grid.svg",
            "robot.svg",
            "route.svg",
            "play.svg",
            "chart.svg",
            "report.svg",
        )
        icon_root = Path(__file__).resolve().parents[2] / "assets" / "icons"
        for label, icon_name in zip(T.NAVIGATION, nav_icons):
            self.nav.addItem(QListWidgetItem(QIcon(str(icon_root / icon_name)), label))
        self.nav.setCurrentRow(0)
        side_layout.addWidget(self.nav, 1)

        self.stack = QStackedWidget()
        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

    def _build_pages(self):
        self.home = self._home_page(); self.editor = self._editor_page(); self.robot_page = self._robot_page()
        self.algorithm_page = self._algorithm_page(); self.sim_page = self._simulation_page()
        self.results_page = self._results_page(); self.export_page = self._export_page()
        for page in (self.home,self.editor,self.robot_page,self.algorithm_page,self.sim_page,self.results_page,self.export_page):
            self.stack.addWidget(page)

    def _heading(self, title, subtitle=""):
        return PageHeader(title, subtitle)

    def _page(self, title, subtitle=""):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)
        lay.addWidget(self._heading(title, subtitle))
        return page, lay

    def _toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        apply_theme(QApplication.instance(), self.theme_mode, window=self)
        self.theme_toggle.setText("Theme: Light" if self.theme_mode == "light" else "Theme: Dark")
        save_ui_settings(UiSettings(theme=self.theme_mode))

    def _home_page(self):
        page, lay = self._page("Project Home", "Load a map, configure a run, and inspect results.")

        action_row = QHBoxLayout()
        self.home_map_button = QPushButton(T.LOAD_DEPARTMENT)
        self.home_map_button.setProperty("variant", "primary")
        self.home_open_button = QPushButton("Open map folderâ€¦")
        self.home_new_button = QPushButton("Create experiment")
        self.home_load_config = QPushButton("Load experiment JSONâ€¦")
        for button in (self.home_map_button, self.home_open_button, self.home_new_button, self.home_load_config):
            action_row.addWidget(button)
        lay.addLayout(action_row)

        card = Card()
        card.layout.addWidget(QLabel("Project overview"))
        card.layout.addWidget(QLabel("Smart Vacuum â€” route planning, resource simulation, and coverage control."))
        self.home_summary = QLabel("No map loaded.")
        card.layout.addWidget(self.home_summary)

        card.layout.addWidget(QLabel("Recent experiments and runs"))
        self.recent_list = QListWidget()
        self.recent_list.setMinimumHeight(160)
        card.layout.addWidget(self.recent_list)

        card.layout.addWidget(QLabel("Recent maps"))
        self.recent_maps_list = QListWidget()
        self.recent_maps_list.setMinimumHeight(110)
        card.layout.addWidget(self.recent_maps_list)
        lay.addWidget(card)
        lay.addStretch(1)
        return page

    def _editor_page(self):
        page,lay=self._page("Map Editor","Import/calibrate plans, paint occupancy states, and validate start/goal cells.")
        tabs=QTabWidget(); lay.addWidget(tabs,1)
        edit=QWidget(); editlay=QHBoxLayout(edit); side=QVBoxLayout()
        self.brush=QComboBox(); self.brush.addItem("FREE",int(CellState.FREE)); self.brush.addItem("OCCUPIED",int(CellState.OCCUPIED)); self.brush.addItem("DOOR",int(CellState.DOOR)); self.brush.addItem("UNKNOWN",int(CellState.UNKNOWN))
        side.addWidget(QLabel("Paint state")); side.addWidget(self.brush)
        self.pick_start=QPushButton("Pick start"); self.pick_goal=QPushButton("Pick goal"); self.paint_button=QPushButton("Paint cells")
        self.undo_button=QPushButton("Undo"); self.redo_button=QPushButton("Redo")
        for w in (self.pick_start,self.pick_goal,self.paint_button,self.undo_button,self.redo_button): side.addWidget(w)
        side.addWidget(QLabel("Validation")); self.validation=QListWidget(); side.addWidget(self.validation,1)
        editlay.addLayout(side); self.editor_canvas=MapCanvas(); editlay.addWidget(self.editor_canvas,1)
        tabs.addTab(edit,"Grid editor")
        cal=QWidget(); cl=QHBoxLayout(cal); self.cal_image=CalibrationImage(); cl.addWidget(self.cal_image,1)
        cform=QFormLayout(); self.cal_distance=QDoubleSpinBox(); self.cal_distance.setRange(.001,10000); self.cal_distance.setValue(1.0); self.cal_distance.setSuffix(" m")
        self.cal_open=QPushButton("Load floor-plan imageâ€¦"); self.cal_result=QLabel("Scale: â€”\nResidual: â€”")
        cform.addRow(self.cal_open); cform.addRow("Known distance",self.cal_distance); cform.addRow(self.cal_result)
        cl.addLayout(cform); tabs.addTab(cal,"Import & calibration")
        self.editor_canvas.cell_clicked.connect(self._editor_cell_clicked)
        return page

    def _robot_page(self):
        page, lay = self._page("Robot Configuration", "Battery and operational lifetime are independent simulation limits.")
        body = QHBoxLayout()
        limits_card = Card()
        limits_card.layout.addWidget(QLabel("Limits"))
        form = QFormLayout()
        self.robot_fields = {}
        specs=(('battery_capacity_units','Battery capacity',0,1e9,100,3),('operational_lifetime_s','Operational lifetime',0,1e9,1800,3),
               ('speed_m_per_s','Speed',.001,100,.25,4),('diameter_m','Diameter',.01,10,.35,3),
               ('cleaning_width_m','Cleaning width',.001,1,.30,3),('move_energy_units_per_step','Move energy / step',0,1e6,.05,5),
               ('clean_energy_units_per_cell','Clean energy / cell',0,1e6,.02,5))
        for key,label,minimum,maximum,value,decimals in specs:
            spin = QDoubleSpinBox()
            spin.setRange(minimum, maximum)
            spin.setDecimals(decimals)
            spin.setValue(value)
            self.robot_fields[key] = spin
            form.addRow(label, spin)
        limits_card.layout.addLayout(form)

        presets = QHBoxLayout()
        for text,button_name in (("Default","default"),("Low battery","low"),("Short lifetime","short")):
            b = QPushButton(text)
            setattr(self, f"preset_{button_name}", b)
            presets.addWidget(b)
        limits_card.layout.addLayout(presets)
        self.robot_save = QPushButton("Apply configuration")
        self.robot_save.setProperty("variant", "primary")
        limits_card.layout.addWidget(self.robot_save)

        summary = Card()
        summary.layout.addWidget(QLabel("Summary"))
        self.robot_summary = QLabel("Apply a configuration to compute derived values.")
        self.robot_summary.setWordWrap(True)
        summary.layout.addWidget(self.robot_summary)

        body.addWidget(limits_card, 2)
        body.addWidget(summary, 1)
        lay.addLayout(body)
        lay.addStretch(1)
        return page

    def _algorithm_page(self):
        page,lay=self._page("Algorithm Setup","Choose the point-to-point planner and mission mode.")
        form=QFormLayout(); self.algorithm_combo=QComboBox()
        for key in REGISTRY: self.algorithm_combo.addItem(key.upper() if key!="iddfs" else "IDDFS",key)
        self.mode_combo=QComboBox(); self.mode_combo.addItem("Coverage", "coverage"); self.mode_combo.addItem("Point to point", "point_to_point")
        self.heuristic=QLabel("Manhattan distance Ã— minimum step cost (A* / Greedy)")
        self.neighbor_order=QLabel("Up â†’ Right â†’ Down â†’ Left")
        self.policy_label=QLabel("Nearest uncleaned raw-reachable cell (Manhattan; row, column ties)")
        self.quick_goal=QComboBox(); self.quick_goal.addItem("Choose a demo goalâ€¦",None)
        goals_path=Path(__file__).resolve().parents[2]/"docs"/"map_spec"/"demo_goals.csv"
        try:
            with goals_path.open(encoding="utf-8",newline="") as stream:
                for row in csv.DictReader(stream):
                    if row.get("synthetic_only") == "true" or row.get("scenario") == "unreachable_synthetic": continue
                    self.quick_goal.addItem(row["scenario"].replace("_"," ").title(),
                        {"start":(int(row["start_row"]),int(row["start_col"])),"goal":(int(row["goal_row"]),int(row["goal_col"]))})
        except (OSError,KeyError,ValueError): pass
        form.addRow("Algorithm",self.algorithm_combo); form.addRow("Mission mode",self.mode_combo); form.addRow("Heuristic",self.heuristic); form.addRow("Neighbor order",self.neighbor_order); form.addRow("Coverage policy",self.policy_label); form.addRow("Demo goal",self.quick_goal)
        lay.addLayout(form); lay.addWidget(QLabel("Choose start and goal in Map Editor. Coverage mode does not require a goal.")); lay.addStretch()
        return page

    def _simulation_page(self):
        page, lay = self._page("2D Simulation", "Exploration, route, cleaning and robot state come from the simulation engine.")
        body = QHBoxLayout()
        self.sim_canvas = MapCanvas()
        body.addWidget(self.sim_canvas, 4)
        panel_card = Card()
        panel = QVBoxLayout()
        self.hud = {}
        for key, label in (("battery", "Battery"), ("elapsed", "Elapsed time"), ("lifetime", "Lifetime remaining"), ("coverage", "Coverage"), ("target", "Current target"), ("steps", "Steps"), ("status", "Status")):
            tile = MetricTile(label)
            self.hud[key] = tile.value
            panel.addWidget(tile)
        self.battery_bar = QProgressBar()
        panel.addWidget(self.battery_bar)
        panel_card.layout.addLayout(panel)
        body.addWidget(panel_card, 2)
        lay.addLayout(body, 1)
        legend = QLabel(T.LEGEND)
        legend.setProperty("variant", "muted")
        legend.setWordWrap(True)
        lay.addWidget(legend)
        controls=QHBoxLayout(); self.run_button=QPushButton(T.RUN); self.pause_button=QPushButton(T.PAUSE); self.resume_button=QPushButton(T.RESUME); self.step_button=QPushButton(T.STEP); self.reset_button=QPushButton(T.RESET); self.stop_button=QPushButton(T.STOP)
        for button in (self.run_button,self.pause_button,self.resume_button,self.step_button,self.reset_button,self.stop_button): controls.addWidget(button)
        self.run_button.setProperty("variant", "primary")
        self.stop_button.setProperty("variant", "danger")
        controls.addWidget(QLabel("Playback")); self.speed_slider=QSlider(Qt.Orientation.Horizontal); self.speed_slider.setRange(0,6); self.speed_slider.setValue(2); controls.addWidget(self.speed_slider,1)
        self.speed_label=QLabel("1Ã—"); controls.addWidget(self.speed_label)
        self.skip_to_end=QPushButton("Show latest state"); controls.addWidget(self.skip_to_end)
        lay.addLayout(controls)
        self.stop_banner = Banner("warning", "")
        self.stop_banner.hide()
        lay.addWidget(self.stop_banner)
        self.stop_reason=QLabel("")
        self.stop_reason.setProperty("variant", "muted")
        lay.addWidget(self.stop_reason)
        return page

    def _results_page(self):
        page,lay=self._page("Results Dashboard","Metrics are read from the completed engine run.")
        card = Card()
        self.results_text=QLabel("No completed run yet.")
        self.results_text.setWordWrap(True)
        self.results_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        card.layout.addWidget(self.results_text)
        lay.addWidget(card)
        lay.addStretch()
        return page

    def _export_page(self):
        page,lay=self._page("Report Export","Save the current experiment configuration and run metrics locally.")
        self.export_config=QPushButton("Save experiment configuration as JSONâ€¦"); self.export_csv=QPushButton("Export current run as CSVâ€¦")
        lay.addWidget(self.export_config); lay.addWidget(self.export_csv); lay.addStretch()
        return page

    def _connect(self):
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.home_map_button.clicked.connect(self._load_department); self.home_open_button.clicked.connect(self._open_map)
        self.home_new_button.clicked.connect(lambda: self.nav.setCurrentRow(3))
        self.home_load_config.clicked.connect(self._load_config)
        self.recent_list.itemDoubleClicked.connect(self._open_recent)
        self.recent_maps_list.itemDoubleClicked.connect(self._open_recent_map)
        self.controller.changed.connect(self._refresh)
        self.controller.message.connect(self.statusBar().showMessage)
        self.pick_start.clicked.connect(lambda:self.editor_canvas.set_pick_mode("start"))
        self.pick_goal.clicked.connect(lambda:self.editor_canvas.set_pick_mode("goal"))
        self.paint_button.clicked.connect(lambda:self.editor_canvas.set_pick_mode("paint"))
        self.validation.itemClicked.connect(self._jump_to_validation_cell)
        self.undo_button.clicked.connect(self.controller.undo); self.redo_button.clicked.connect(self.controller.redo)
        self.robot_save.clicked.connect(self._apply_robot_config)
        self.preset_default.clicked.connect(self._set_default); self.preset_low.clicked.connect(lambda:self._preset(battery=15))
        self.preset_short.clicked.connect(lambda:self._preset(lifetime=90))
        self.algorithm_combo.currentIndexChanged.connect(lambda _:setattr(self.controller,"algorithm",self.algorithm_combo.currentData()))
        self.mode_combo.currentIndexChanged.connect(lambda _:setattr(self.controller,"mode",self.mode_combo.currentData()))
        self.quick_goal.currentIndexChanged.connect(self._select_quick_goal)
        self.run_button.clicked.connect(self._start_run); self.pause_button.clicked.connect(self._pause)
        self.resume_button.clicked.connect(self._resume); self.step_button.clicked.connect(self._step)
        self.stop_button.clicked.connect(self._stop); self.reset_button.clicked.connect(self._reset)
        self.speed_slider.valueChanged.connect(self._apply_playback_speed)
        self.skip_to_end.clicked.connect(self._skip_to_end)
        self.export_config.clicked.connect(self._save_config); self.export_csv.clicked.connect(self._save_csv)
        self.cal_open.clicked.connect(self._load_calibration_image); self.cal_image.point_clicked.connect(lambda _:self._update_calibration())
        self.cal_distance.valueChanged.connect(self._update_calibration)

    def _shortcuts(self):
        for sequence, callback in (("Ctrl+R",self._start_run),("Space",self._toggle_pause),("Ctrl+T",self._step),("Ctrl+0",self._reset)):
            shortcut=QShortcut(QKeySequence(sequence),self); shortcut.activated.connect(callback)

    def _refresh(self):
        c=self.controller; self.statusBar().showMessage(f"Map: {c.map_version}  |  {c.run_state.title()}")
        self.status_chip.set_state(c.run_state)
        self.home_summary.setText(f"Map: {c.map_version}\nDimensions: {c.map.shape if c.map else 'â€”'}\nStart: {c.start or 'not set'}")
        if c.robot is not None:
            cfg = c.robot.config
            steps_est = int(cfg.battery_capacity_units / max(cfg.move_energy_units_per_step, 1e-9))
            mins = cfg.operational_lifetime_s / 60.0
            self.robot_summary.setText(
                f"Estimated max move steps: {steps_est}\n"
                f"Operational lifetime: {mins:.1f} min\n"
                f"Cleaning width: {cfg.cleaning_width_m:.3f} m"
            )
        for canvas in (self.editor_canvas,self.sim_canvas): canvas.set_map(c.map.grid if c.map else None,c.start,c.goal)
        self.validation.clear()
        issues=c.validation_issues()
        if issues:
            for issue in issues:
                item=QListWidgetItem(issue.message)
                item.setData(Qt.ItemDataRole.UserRole,issue.cells[0] if issue.cells else None)
                self.validation.addItem(item)
        else:self.validation.addItems(c.validation_messages())
        self._refresh_recent_list()

    def _refresh_recent_list(self):
        self.recent_list.clear()
        for record in self.controller.recent_experiments()[:12]:
            kind = "Run" if record.get("kind") == "run_record" else "Config"
            experiment = record.get("experiment", {})
            label = (f"{kind}: {record.get('algorithm', experiment.get('algorithm', 'â€”'))} Â· "
                     f"{record.get('mode', experiment.get('mode', 'â€”'))} Â· "
                     f"{record.get('map_version', record.get('map', {}).get('version', 'â€”'))}")
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, record["_path"])
            self.recent_list.addItem(item)
        self.recent_maps_list.clear()
        for record in self.controller.recent_map_records()[:8]:
            item=QListWidgetItem(f"{record.get('version','Map')} Â· {Path(record['path']).name}")
            item.setData(Qt.ItemDataRole.UserRole,record["path"])
            self.recent_maps_list.addItem(item)

    def _editor_cell_clicked(self, cell):
        mode=self.editor_canvas.pick_mode
        if mode=="start": self.controller.set_start(cell); self.editor_canvas.set_pick_mode("none")
        elif mode=="goal": self.controller.set_goal(cell); self.editor_canvas.set_pick_mode("none")
        elif mode=="paint": self.controller.paint(cell,self.brush.currentData())
        self._refresh()

    def _jump_to_validation_cell(self,item):
        cell=item.data(Qt.ItemDataRole.UserRole)
        if cell:
            r,c=cell; self.editor_canvas.centerOn(c+.5,r+.5); self.nav.setCurrentRow(1)

    def _select_quick_goal(self, index):
        spec=self.quick_goal.itemData(index)
        if not spec or self.controller.map is None:return
        start,goal=spec["start"],spec["goal"]
        if start!=self.controller.start and not self.controller.set_start(start):return
        if self.controller.set_goal(goal):self.nav.setCurrentRow(4)

    def _load_department(self):
        try: self.controller.load_department_map()
        except Exception as exc: QMessageBox.critical(self,"Map load failed",str(exc))

    def _open_map(self):
        path=QFileDialog.getExistingDirectory(self,"Open map bundle",str(Path.cwd()/"data"/"maps"))
        if path:
            try:self.controller.load_map(path)
            except Exception as exc:QMessageBox.critical(self,"Map load failed",str(exc))

    def _apply_robot_config(self):
        values={key:widget.value() for key,widget in self.robot_fields.items()}
        try:
            old=self.controller.robot_config
            self.controller.set_robot_config(**{**old.__dict__,**values})
        except Exception as exc: QMessageBox.warning(self,"Invalid robot configuration",str(exc))

    def _preset(self,battery=None,lifetime=None):
        if battery is not None:self.robot_fields['battery_capacity_units'].setValue(battery)
        if lifetime is not None:self.robot_fields['operational_lifetime_s'].setValue(lifetime)
        self._apply_robot_config()

    def _set_default(self):
        cfg=RobotConfig()
        for key,widget in self.robot_fields.items():widget.setValue(getattr(cfg,key))
        self._apply_robot_config()

    def _start_run(self):
        if self._worker is not None and self._worker.isRunning():return
        try:
            self.controller.algorithm=self.algorithm_combo.currentData(); self.controller.mode=self.mode_combo.currentData()
            self.controller.run_state="running"; self.controller.search_result=None; self.controller.run_result=None
            self.stop_reason.setText(""); self._last_seq=-1
            self._worker=SimulationWorker(self.controller); self._worker.finished_result.connect(self._run_finished); self._worker.failed.connect(self._run_failed)
            self._worker.record_failed.connect(lambda message: self.statusBar().showMessage(f"Run finished; record save failed: {message}"))
            self._worker.start(); self.timer.start(); self.hud['status'].setText("Running"); self._set_controls(True)
        except Exception as exc: QMessageBox.warning(self,"Cannot start run",str(exc))

    def _poll_run(self):
        c=self.controller; sim=c.coverage_controller
        if sim is None or c.robot is None:return
        # EventLog is a bounded deque. Walk newest-first and stop at the last
        # sequence already rendered instead of rescanning its whole history
        # on every UI tick (which grows increasingly expensive in long runs).
        new_events=[]
        for event in reversed(sim.events.snapshot_events()):
            if event.seq <= self._last_seq:
                break
            new_events.append(event)
        new_events.reverse()
        if new_events:self._last_seq=new_events[-1].seq
        target=self._target
        for event in new_events:
            if event.type=="TargetSelected":target=tuple(event.payload["target"])
            elif event.type=="RunStopped":self.stop_reason.setText(f"Stopped: {event.payload['reason']}")
        self._target=target
        snap=sim.snapshots[-1] if sim.snapshots else None
        cleaned=snap.cleaned if snap else c.robot.cleaning.cleaned
        path=snap.current_path if snap else ()
        explored=c.trace_cells()
        self.sim_canvas.set_overlay(cleaned=cleaned,explored=explored,frontier=c.frontier_cells(),path=path,robot=c.robot.state.position)
        self.hud['battery'].setText(f"{c.robot.state.battery_remaining:.2f} / {c.robot.config.battery_capacity_units:.2f}")
        self.hud['elapsed'].setText(f"{c.robot.state.elapsed_time_s:.2f} s")
        self.hud['lifetime'].setText(f"{c.robot.state.lifetime_remaining_s:.2f} s")
        self.hud['coverage'].setText(f"{snap.coverage_percent:.1f}%" if snap else "â€”")
        self.hud['target'].setText(str(target) if target else "â€”")
        self.hud['steps'].setText(str(c.robot.state.step_count))
        self.battery_bar.setRange(0,100); self.battery_bar.setValue(int(100*c.robot.state.battery_remaining/max(c.robot.config.battery_capacity_units,1e-9)))

    def _run_finished(self,result):
        self.controller.run_result=result; self.controller.run_state="complete"; self.timer.stop()
        self._refresh_recent_list()
        self.hud['status'].setText("Complete"); self._set_controls(False); self._poll_run(); self.status_chip.set_state("complete")
        if self.controller.mode=="point_to_point" and self.controller.search_result is not None:
            self.sim_canvas.set_overlay(path=self.controller.search_result.path,explored=self.controller.trace_cells(),
                frontier=self.controller.frontier_cells(),
                cleaned=self.controller.robot.cleaning.cleaned,robot=self.controller.robot.state.position)
            if not self.controller.search_result.found:self.stop_reason.setText("No path found")
        self._show_results()
        if self._close_pending:self.close()

    def _run_failed(self,message):
        self.controller.run_state="error"; self.timer.stop(); self.stop_reason.setText(f"Error: {message}"); self.hud['status'].setText("Error"); self._set_controls(False)
        self.status_chip.set_state("error")
        self.stop_banner.set_kind("error")
        self.stop_banner.set_text(f"Simulation error: {message}")
        self.stop_banner.show()

    def _pause(self):
        if self.controller.coverage_controller:self.controller.coverage_controller.pause()
        self.controller.run_state="paused"; self.hud['status'].setText("Paused"); self.status_chip.set_state("paused")

    def _resume(self):
        if self.controller.coverage_controller:self.controller.coverage_controller.resume()
        self.controller.run_state="running"; self.hud['status'].setText("Running"); self.status_chip.set_state("running")

    def _step(self):
        if self.controller.coverage_controller:self.controller.coverage_controller.step_once(); self.controller.run_state="paused"

    def _toggle_pause(self):
        if self.controller.run_state=="paused":self._resume()
        elif self.controller.run_state=="running":self._pause()

    def _stop(self):
        if self.controller.coverage_controller:self.controller.coverage_controller.cancel()
        self.controller.run_state="stopping"; self.hud['status'].setText("Stoppingâ€¦"); self.status_chip.set_state("stopped")

    def _reset(self):
        if self._worker is not None and self._worker.isRunning():
            self._stop(); return
        if self.controller.robot:self.controller.robot.reset()
        if self.controller.coverage_controller:self.controller.coverage_controller.reset()
        self.controller.coverage_controller=None; self.controller.run_state="idle"; self._target=None
        self.sim_canvas.set_map(self.controller.map.grid if self.controller.map else None,self.controller.start,self.controller.goal)
        self.hud['status'].setText("Ready"); self.stop_reason.clear(); self.status_chip.set_state("idle")
        self.stop_banner.hide()

    def _set_controls(self,running):
        self.run_button.setEnabled(not running); self.pause_button.setEnabled(running); self.resume_button.setEnabled(running)
        self.step_button.setEnabled(running); self.stop_button.setEnabled(running); self.reset_button.setEnabled(not running)

    def _show_results(self):
        c=self.controller; robot=c.robot
        if robot is None:return
        if c.mode=="coverage" and c.run_result is not None:
            r=c.run_result
            self.stop_reason.setText(f"Stopped: {r.stop_reason.value}")
            text=(f"Algorithm: {c.algorithm}\nMode: Coverage\nCoverage (achievable): {r.coverage_percent:.2f}%\n"
                  f"Raw coverage: {r.raw_coverage_percent:.2f}%\nSteps: {robot.state.step_count}\n"
                  f"Energy used: {robot.config.battery_capacity_units-robot.state.battery_remaining:.3f}\n"
                  f"Battery remaining: {robot.state.battery_remaining:.3f} / {robot.config.battery_capacity_units:.3f}\n"
                  f"Simulated time: {robot.state.elapsed_time_s:.3f} s\nLifetime remaining: {robot.state.lifetime_remaining_s:.3f} s\nStop reason: {r.stop_reason.value}\n"
                  f"Planner wall time: {r.planner_wall_time_s:.4f} s\nRemaining: {len(r.remaining_cells)} cells")
        else:
            result=c.search_result
            text=f"Algorithm: {c.algorithm}\nMode: Point to point\nFound: {result.found if result else False}\nPath steps: {result.path_length_steps if result else 'â€”'}\nPlanner wall time: {result.execution_time_s:.4f} s" if result else "No completed result."
        if c.mode != "coverage" and c.search_result is not None:
            result=c.search_result
            reason=(robot.termination_reason.value if robot.termination_reason else
                    "mission_complete" if result.found and robot.state.position==c.goal else
                    "no_path" if not result.found else "in_progress")
            self.stop_reason.setText(f"Stopped: {reason}")
            text += (f"\nSteps: {robot.state.step_count}\nBattery remaining: {robot.state.battery_remaining:.3f} / "
                     f"{robot.config.battery_capacity_units:.3f}\nSimulated time: {robot.state.elapsed_time_s:.3f} s\n"
                     f"Lifetime remaining: {robot.state.lifetime_remaining_s:.3f} s\nStop reason: {reason}")
        self.hud["battery"].setText(f"{robot.state.battery_remaining:.2f} / {robot.config.battery_capacity_units:.2f}")
        self.hud["elapsed"].setText(f"{robot.state.elapsed_time_s:.2f} s")
        self.hud["lifetime"].setText(f"{robot.state.lifetime_remaining_s:.2f} s")
        if c.mode == "coverage" and c.run_result is not None:
            self.hud["coverage"].setText(f"{c.run_result.raw_coverage_percent:.2f}% raw")
        self.hud["steps"].setText(str(robot.state.step_count))
        self.hud["status"].setText("Complete")
        self.battery_bar.setRange(0,100)
        self.battery_bar.setValue(int(100*robot.state.battery_remaining/max(robot.config.battery_capacity_units,1e-9)))
        self.results_text.setText(text)

    def _save_config(self):
        self.controller.experiments_dir.mkdir(parents=True, exist_ok=True)
        path,_=QFileDialog.getSaveFileName(self,"Save experiment configuration",str(self.controller.experiments_dir/"experiment.json"),"JSON (*.json)")
        if path:
            try:self.controller.save_experiment(path); self._refresh(); self.statusBar().showMessage(f"Saved {path}")
            except Exception as exc:QMessageBox.warning(self,"Save failed",str(exc))

    def _load_config(self):
        path,_=QFileDialog.getOpenFileName(self,"Load experiment configuration",str(self.controller.experiments_dir),"JSON (*.json)")
        if not path:return
        try:
            self.controller.load_experiment(path)
            self._sync_configuration_widgets()
            self.statusBar().showMessage(f"Loaded {path}")
        except Exception as exc:QMessageBox.warning(self,"Load failed",str(exc))

    def _open_recent(self, item):
        path=Path(item.data(Qt.ItemDataRole.UserRole))
        try:
            document=json.loads(path.read_text(encoding="utf-8"))
            if document.get("kind")=="experiment_config":
                self.controller.load_experiment(path)
                self._sync_configuration_widgets()
            else:
                fields=("map_version","algorithm","mode","coverage_percent","raw_coverage_percent","steps",
                        "energy_used","simulated_time_s","stop_reason","planner_wall_time_s")
                self.results_text.setText("\n".join(f"{key.replace('_',' ').title()}: {document.get(key, 'â€”')}" for key in fields))
                self.nav.setCurrentRow(6)
        except Exception as exc:QMessageBox.warning(self,"Open recent item failed",str(exc))

    def _open_recent_map(self,item):
        try:self.controller.load_map(Path(item.data(Qt.ItemDataRole.UserRole)))
        except Exception as exc:QMessageBox.warning(self,"Open recent map failed",str(exc))

    def _sync_configuration_widgets(self):
        self.algorithm_combo.setCurrentIndex(self.algorithm_combo.findData(self.controller.algorithm))
        self.mode_combo.setCurrentIndex(self.mode_combo.findData(self.controller.mode))
        for key,widget in self.robot_fields.items():widget.setValue(getattr(self.controller.robot_config,key))
        self._refresh()

    def _apply_playback_speed(self, value):
        speeds=(.25,.5,1,2,4,8,16); speed=speeds[value]
        self.speed_label.setText(f"{speed:g}Ã—")
        # Presentation cadence only; simulation time and planner time do not change.
        self.timer.setInterval(max(34,int(100/speed)))  # capped at 30 UI updates/second

    def _skip_to_end(self):
        self._poll_run()
        if self.controller.run_state in ("complete","idle","error") and self.controller.robot:
            snapshots=(self.controller.coverage_controller.snapshots
                       if self.controller.coverage_controller else ())
            snapshot=snapshots[-1] if snapshots else None
            self.sim_canvas.set_overlay(explored=self.controller.trace_cells(),
                frontier=self.controller.frontier_cells(),
                path=getattr(self.controller.search_result,"path",()) or (snapshot.current_path if snapshot else ()),
                cleaned=self.controller.robot.cleaning.cleaned,
                robot=self.controller.robot.state.position)

    def _save_csv(self):
        path,_=QFileDialog.getSaveFileName(self,"Export run metrics","run.csv","CSV (*.csv)")
        if not path:return
        c=self.controller; robot=c.robot
        if robot is None or c.run_result is None:QMessageBox.information(self,"No run","Run a simulation before exporting."); return
        result=c.run_result
        with open(path,"w",newline="",encoding="utf-8") as stream:
            writer=csv.writer(stream); writer.writerow(("algorithm","mode","coverage_pct","steps","energy_used","sim_time_s","stop_reason","planner_wall_time_s"))
            writer.writerow((c.algorithm,c.mode,getattr(result,"coverage_percent",""),robot.state.step_count,
                robot.config.battery_capacity_units-robot.state.battery_remaining,robot.state.elapsed_time_s,
                getattr(getattr(result,"stop_reason",None),"value",""),getattr(result,"planner_wall_time_s",getattr(result,"execution_time_s",""))))

    def _load_calibration_image(self):
        path,_=QFileDialog.getOpenFileName(self,"Load floor plan image",str(Path.cwd()),"Images (*.png *.jpg *.jpeg *.bmp)")
        if path:self.cal_image.load(path); self._update_calibration()

    def _update_calibration(self):
        if len(self.cal_image.points)<2:self.cal_result.setText("Scale: click two points\nResidual: â€”"); return
        a,b=self.cal_image.points; pixels=((a[0]-b[0])**2+(a[1]-b[1])**2)**.5
        scale=pixels/max(self.cal_distance.value(),1e-9)
        self.cal_result.setText(f"Scale: {scale:.2f} px/m\nResidual: n/a (one reference segment; no independent check)")

    def closeEvent(self,event):
        if self._worker is not None and self._worker.isRunning():
            self._close_pending=True; self._stop()
            if not self._worker.wait(5000):
                self.statusBar().showMessage("Waiting for the current bounded search call to finish; close again when it stops.")
                event.ignore(); return
        event.accept()


