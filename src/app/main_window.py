"""Main Qt desktop shell, pages and worker-driven simulation controls."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton,
    QProgressBar, QScrollArea, QSlider, QSpinBox, QStackedWidget, QTabWidget,
    QVBoxLayout, QWidget,
)

from src.algorithms.registry import REGISTRY
from src.app.app_controller import AppController
from src.app.simulation_worker import SimulationWorker
from src.app import strings as T
from src.map_processing.constants import CellState
from src.robot.config import RobotConfig
from src.visualization.two_d.map_canvas import MapCanvas


class CalibrationImage(QWidget):
    """Image calibration panel with two clicked pixel references."""
    point_clicked = Signal(tuple)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None; self.points = []
        self.setMinimumSize(320, 220); self.setStyleSheet("background:#eef2f6;border:1px solid #cbd5e1")

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
        painter = QPainter(self); painter.fillRect(self.rect(), QColor("#eef2f6"))
        if self.image and not self.image.isNull():
            pix = self.image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            origin = self.rect().center() - pix.rect().center(); painter.drawPixmap(origin, pix)
        else:
            painter.setPen(QColor("#475569")); painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                "Load a floor-plan image, then click the two reference points")
        painter.setPen(QPen(QColor("#D92D20"), 3))
        for point in self.points: painter.drawEllipse(int(point[0])-5, int(point[1])-5, 10, 10)


class MainWindow(QMainWindow):
    """Eight-screen application with controller-mediated domain operations."""
    def __init__(self, app_controller: AppController | None = None):
        super().__init__()
        self.controller = app_controller or AppController()
        self.setWindowTitle(T.APP_TITLE); self.resize(1440, 900)
        self._worker: SimulationWorker | None = None
        self._target = None; self._last_seq = -1; self._close_pending = False
        self._build_shell(); self._build_pages(); self._connect()
        # Snapshot/event presentation is intentionally capped at 10 Hz. The
        # worker still executes every action; this bounds GUI paint work.
        self.timer = QTimer(self); self.timer.setInterval(100); self.timer.timeout.connect(self._poll_run)
        self._shortcuts()
        self.statusBar().showMessage(f"Map: {self.controller.map_version}  |  {T.STATUS_IDLE}")

    def _build_shell(self):
        root = QWidget(); layout = QHBoxLayout(root); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.nav = QListWidget(); self.nav.setFixedWidth(220); self.nav.addItems(T.NAVIGATION); self.nav.setCurrentRow(0)
        self.nav.setStyleSheet("QListWidget{background:#101828;color:#e4e7ec;border:0;padding:10px;font-size:14px} QListWidget::item{padding:13px;border-radius:6px} QListWidget::item:selected{background:#344054;color:white}")
        self.stack = QStackedWidget(); layout.addWidget(self.nav); layout.addWidget(self.stack,1)
        self.setCentralWidget(root); self.setStyleSheet("QMainWindow{background:#f8fafc} QPushButton{padding:7px 12px} QGroupBox{font-weight:600}")

    def _build_pages(self):
        self.home = self._home_page(); self.editor = self._editor_page(); self.robot_page = self._robot_page()
        self.algorithm_page = self._algorithm_page(); self.sim_page = self._simulation_page()
        self.three_d_page = self._three_d_page(); self.results_page = self._results_page(); self.export_page = self._export_page()
        for page in (self.home,self.editor,self.robot_page,self.algorithm_page,self.sim_page,self.three_d_page,self.results_page,self.export_page):
            self.stack.addWidget(page)

    def _heading(self, title, subtitle=""):
        box=QWidget(); lay=QVBoxLayout(box); lay.setContentsMargins(0,0,0,12)
        label=QLabel(title); label.setStyleSheet("font-size:24px;font-weight:700;color:#101828")
        lay.addWidget(label)
        if subtitle:
            sub=QLabel(subtitle); sub.setStyleSheet("color:#667085;font-size:13px"); lay.addWidget(sub)
        return box

    def _page(self, title, subtitle=""):
        page=QWidget(); lay=QVBoxLayout(page); lay.setContentsMargins(24,20,24,20); lay.addWidget(self._heading(title,subtitle)); return page,lay

    def _home_page(self):
        page,lay=self._page("Project Home","Load a map, configure a run, and inspect results.")
        self.home_map_button=QPushButton(T.LOAD_DEPARTMENT); self.home_open_button=QPushButton("Open map folder…")
        self.home_new_button=QPushButton("Create experiment configuration")
        row=QHBoxLayout(); row.addWidget(self.home_map_button); row.addWidget(self.home_open_button); row.addWidget(self.home_new_button); row.addStretch()
        lay.addLayout(row)
        card=QFrame(); card.setStyleSheet("QFrame{background:white;border:1px solid #eaecf0;border-radius:10px;padding:14px}")
        cardlay=QVBoxLayout(card); cardlay.addWidget(QLabel("Project overview")); cardlay.addWidget(QLabel("Smart Vacuum — route planning, resource simulation, and coverage control."))
        self.home_summary=QLabel("No map loaded."); cardlay.addWidget(self.home_summary); lay.addWidget(card); lay.addStretch()
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
        self.cal_open=QPushButton("Load floor-plan image…"); self.cal_result=QLabel("Scale: —\nResidual: —")
        cform.addRow(self.cal_open); cform.addRow("Known distance",self.cal_distance); cform.addRow(self.cal_result)
        cl.addLayout(cform); tabs.addTab(cal,"Import & calibration")
        self.editor_canvas.cell_clicked.connect(self._editor_cell_clicked)
        return page

    def _robot_page(self):
        page,lay=self._page("Robot Configuration","Battery and operational lifetime are independent simulation limits.")
        form=QFormLayout(); self.robot_fields={}
        specs=(('battery_capacity_units','Battery capacity',0,1e9,100,3),('operational_lifetime_s','Operational lifetime',0,1e9,1800,3),
               ('speed_m_per_s','Speed',.001,100,.25,4),('diameter_m','Diameter',.01,10,.35,3),
               ('cleaning_width_m','Cleaning width',.001,1,.30,3),('move_energy_units_per_step','Move energy / step',0,1e6,.05,5),
               ('clean_energy_units_per_cell','Clean energy / cell',0,1e6,.02,5))
        for key,label,minimum,maximum,value,decimals in specs:
            spin=QDoubleSpinBox(); spin.setRange(minimum,maximum); spin.setDecimals(decimals); spin.setValue(value); self.robot_fields[key]=spin; form.addRow(label,spin)
        lay.addLayout(form); presets=QHBoxLayout()
        for text,button_name in (("Default","default"),("Low battery","low"),("Short lifetime","short")):
            b=QPushButton(text); setattr(self,f"preset_{button_name}",b); presets.addWidget(b)
        lay.addLayout(presets); self.robot_save=QPushButton("Apply configuration"); lay.addWidget(self.robot_save); lay.addStretch()
        return page

    def _algorithm_page(self):
        page,lay=self._page("Algorithm Setup","Choose the point-to-point planner and mission mode.")
        form=QFormLayout(); self.algorithm_combo=QComboBox()
        for key in REGISTRY: self.algorithm_combo.addItem(key.upper() if key!="iddfs" else "IDDFS",key)
        self.mode_combo=QComboBox(); self.mode_combo.addItem("Coverage", "coverage"); self.mode_combo.addItem("Point to point", "point_to_point")
        self.heuristic=QLabel("Manhattan distance × minimum step cost (A* / Greedy)")
        self.neighbor_order=QLabel("Up → Right → Down → Left")
        self.policy_label=QLabel("Nearest uncleaned raw-reachable cell (Manhattan; row, column ties)")
        form.addRow("Algorithm",self.algorithm_combo); form.addRow("Mission mode",self.mode_combo); form.addRow("Heuristic",self.heuristic); form.addRow("Neighbor order",self.neighbor_order); form.addRow("Coverage policy",self.policy_label)
        lay.addLayout(form); lay.addWidget(QLabel("Choose start and goal in Map Editor. Coverage mode does not require a goal.")); lay.addStretch()
        return page

    def _simulation_page(self):
        page,lay=self._page("2D Simulation","Exploration, route, cleaning and robot state come from the simulation engine.")
        body=QHBoxLayout(); self.sim_canvas=MapCanvas(); body.addWidget(self.sim_canvas,1)
        panel=QVBoxLayout(); self.hud={}
        for key,label in (("battery","Battery"),("elapsed","Elapsed time"),("lifetime","Lifetime remaining"),("coverage","Coverage"),("target","Current target"),("steps","Steps"),("status","Status")):
            panel.addWidget(QLabel(label)); value=QLabel("—"); value.setStyleSheet("font-size:17px;font-weight:600;color:#344054"); self.hud[key]=value; panel.addWidget(value)
        self.battery_bar=QProgressBar(); panel.addWidget(self.battery_bar); panel.addStretch(); body.addLayout(panel)
        lay.addLayout(body,1); lay.addWidget(QLabel(T.LEGEND))
        controls=QHBoxLayout(); self.run_button=QPushButton(T.RUN); self.pause_button=QPushButton(T.PAUSE); self.resume_button=QPushButton(T.RESUME); self.step_button=QPushButton(T.STEP); self.reset_button=QPushButton(T.RESET); self.stop_button=QPushButton(T.STOP)
        for button in (self.run_button,self.pause_button,self.resume_button,self.step_button,self.reset_button,self.stop_button): controls.addWidget(button)
        controls.addWidget(QLabel("Playback")); self.speed_slider=QSlider(Qt.Orientation.Horizontal); self.speed_slider.setRange(0,6); self.speed_slider.setValue(3); controls.addWidget(self.speed_slider,1)
        lay.addLayout(controls); self.stop_reason=QLabel(""); self.stop_reason.setStyleSheet("color:#B42318;font-weight:700"); lay.addWidget(self.stop_reason)
        return page

    def _three_d_page(self):
        page,lay=self._page("3D Simulation","3D renderer launcher; map and movement state are shared with the simulation engine.")
        lay.addWidget(QLabel("The 3D renderer is maintained as a separate visualization module."))
        self.launch_3d=QPushButton("Open 3D renderer"); lay.addWidget(self.launch_3d); self.three_d_status=QLabel("3D renderer integration is not configured in this build."); lay.addWidget(self.three_d_status); lay.addStretch()
        return page

    def _results_page(self):
        page,lay=self._page("Results Dashboard","Metrics are read from the completed engine run.")
        self.results_text=QLabel("No completed run yet."); self.results_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.results_text.setStyleSheet("background:white;padding:18px;border:1px solid #eaecf0;border-radius:8px"); lay.addWidget(self.results_text); lay.addStretch()
        return page

    def _export_page(self):
        page,lay=self._page("Report Export","Save the current experiment configuration and run metrics locally.")
        self.export_config=QPushButton("Save experiment configuration as JSON…"); self.export_csv=QPushButton("Export current run as CSV…")
        lay.addWidget(self.export_config); lay.addWidget(self.export_csv); lay.addStretch()
        return page

    def _connect(self):
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.home_map_button.clicked.connect(self._load_department); self.home_open_button.clicked.connect(self._open_map)
        self.home_new_button.clicked.connect(lambda: self.nav.setCurrentRow(3))
        self.controller.changed.connect(self._refresh)
        self.controller.message.connect(self.statusBar().showMessage)
        self.pick_start.clicked.connect(lambda:self.editor_canvas.set_pick_mode("start"))
        self.pick_goal.clicked.connect(lambda:self.editor_canvas.set_pick_mode("goal"))
        self.paint_button.clicked.connect(lambda:self.editor_canvas.set_pick_mode("paint"))
        self.undo_button.clicked.connect(self.controller.undo); self.redo_button.clicked.connect(self.controller.redo)
        self.robot_save.clicked.connect(self._apply_robot_config)
        self.preset_default.clicked.connect(self._set_default); self.preset_low.clicked.connect(lambda:self._preset(battery=15))
        self.preset_short.clicked.connect(lambda:self._preset(lifetime=90))
        self.algorithm_combo.currentIndexChanged.connect(lambda _:setattr(self.controller,"algorithm",self.algorithm_combo.currentData()))
        self.mode_combo.currentIndexChanged.connect(lambda _:setattr(self.controller,"mode",self.mode_combo.currentData()))
        self.run_button.clicked.connect(self._start_run); self.pause_button.clicked.connect(self._pause)
        self.resume_button.clicked.connect(self._resume); self.step_button.clicked.connect(self._step)
        self.stop_button.clicked.connect(self._stop); self.reset_button.clicked.connect(self._reset)
        self.export_config.clicked.connect(self._save_config); self.export_csv.clicked.connect(self._save_csv)
        self.cal_open.clicked.connect(self._load_calibration_image); self.cal_image.point_clicked.connect(lambda _:self._update_calibration())
        self.cal_distance.valueChanged.connect(self._update_calibration)

    def _shortcuts(self):
        for sequence, callback in (("Ctrl+R",self._start_run),("Space",self._toggle_pause),("Ctrl+T",self._step),("Ctrl+0",self._reset)):
            shortcut=QShortcut(QKeySequence(sequence),self); shortcut.activated.connect(callback)

    def _refresh(self):
        c=self.controller; self.statusBar().showMessage(f"Map: {c.map_version}  |  {c.run_state.title()}")
        self.home_summary.setText(f"Map: {c.map_version}\nDimensions: {c.map.shape if c.map else '—'}\nStart: {c.start or 'not set'}")
        for canvas in (self.editor_canvas,self.sim_canvas): canvas.set_map(c.map.grid if c.map else None,c.start,c.goal)
        self.validation.clear(); self.validation.addItems(c.validation_messages())

    def _editor_cell_clicked(self, cell):
        mode=self.editor_canvas.pick_mode
        if mode=="start": self.controller.set_start(cell); self.editor_canvas.set_pick_mode("none")
        elif mode=="goal": self.controller.set_goal(cell); self.editor_canvas.set_pick_mode("none")
        elif mode=="paint": self.controller.paint(cell,self.brush.currentData())
        self._refresh()

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
            self._worker.start(); self.timer.start(); self.hud['status'].setText("Running"); self._set_controls(True)
        except Exception as exc: QMessageBox.warning(self,"Cannot start run",str(exc))

    def _poll_run(self):
        c=self.controller; sim=c.coverage_controller
        if sim is None or c.robot is None:return
        # EventLog is a bounded deque. Walk newest-first and stop at the last
        # sequence already rendered instead of rescanning its whole history
        # on every UI tick (which grows increasingly expensive in long runs).
        new_events=[]
        for event in reversed(sim.events.events):
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
        self.sim_canvas.set_overlay(cleaned=cleaned,explored=explored,path=path,robot=c.robot.state.position)
        self.hud['battery'].setText(f"{c.robot.state.battery_remaining:.2f} / {c.robot.config.battery_capacity_units:.2f}")
        self.hud['elapsed'].setText(f"{c.robot.state.elapsed_time_s:.2f} s")
        self.hud['lifetime'].setText(f"{c.robot.state.lifetime_remaining_s:.2f} s")
        self.hud['coverage'].setText(f"{snap.coverage_percent:.1f}%" if snap else "—")
        self.hud['target'].setText(str(target) if target else "—")
        self.hud['steps'].setText(str(c.robot.state.step_count))
        self.battery_bar.setRange(0,100); self.battery_bar.setValue(int(100*c.robot.state.battery_remaining/max(c.robot.config.battery_capacity_units,1e-9)))

    def _run_finished(self,result):
        self.controller.run_result=result; self.controller.run_state="complete"; self.timer.stop()
        self.hud['status'].setText("Complete"); self._set_controls(False); self._poll_run()
        if self.controller.mode=="point_to_point" and self.controller.search_result is not None:
            self.sim_canvas.set_overlay(path=self.controller.search_result.path,explored=self.controller.trace_cells(),
                cleaned=self.controller.robot.cleaning.cleaned,robot=self.controller.robot.state.position)
            if not self.controller.search_result.found:self.stop_reason.setText("No path found")
        self._show_results()
        if self._close_pending:self.close()

    def _run_failed(self,message):
        self.controller.run_state="error"; self.timer.stop(); self.stop_reason.setText(f"Error: {message}"); self.hud['status'].setText("Error"); self._set_controls(False)

    def _pause(self):
        if self.controller.coverage_controller:self.controller.coverage_controller.pause()
        self.controller.run_state="paused"; self.hud['status'].setText("Paused")

    def _resume(self):
        if self.controller.coverage_controller:self.controller.coverage_controller.resume()
        self.controller.run_state="running"; self.hud['status'].setText("Running")

    def _step(self):
        if self.controller.coverage_controller:self.controller.coverage_controller.step_once(); self.controller.run_state="paused"

    def _toggle_pause(self):
        if self.controller.run_state=="paused":self._resume()
        elif self.controller.run_state=="running":self._pause()

    def _stop(self):
        if self.controller.coverage_controller:self.controller.coverage_controller.cancel()
        self.controller.run_state="stopping"; self.hud['status'].setText("Stopping…")

    def _reset(self):
        if self._worker is not None and self._worker.isRunning():
            self._stop(); return
        if self.controller.robot:self.controller.robot.reset()
        if self.controller.coverage_controller:self.controller.coverage_controller.reset()
        self.controller.coverage_controller=None; self.controller.run_state="idle"; self._target=None
        self.sim_canvas.set_map(self.controller.map.grid if self.controller.map else None,self.controller.start,self.controller.goal)
        self.hud['status'].setText("Ready"); self.stop_reason.clear()

    def _set_controls(self,running):
        self.run_button.setEnabled(not running); self.pause_button.setEnabled(running); self.resume_button.setEnabled(running)
        self.step_button.setEnabled(running); self.stop_button.setEnabled(running); self.reset_button.setEnabled(not running)

    def _show_results(self):
        c=self.controller; robot=c.robot
        if robot is None:return
        if c.mode=="coverage" and c.run_result is not None:
            r=c.run_result
            text=(f"Algorithm: {c.algorithm}\nMode: Coverage\nCoverage (achievable): {r.coverage_percent:.2f}%\n"
                  f"Raw coverage: {r.raw_coverage_percent:.2f}%\nSteps: {robot.state.step_count}\n"
                  f"Energy used: {robot.config.battery_capacity_units-robot.state.battery_remaining:.3f}\n"
                  f"Simulated time: {robot.state.elapsed_time_s:.3f} s\nStop reason: {r.stop_reason.value}\n"
                  f"Planner wall time: {r.planner_wall_time_s:.4f} s\nRemaining: {len(r.remaining_cells)} cells")
        else:
            result=c.search_result
            text=f"Algorithm: {c.algorithm}\nMode: Point to point\nFound: {result.found if result else False}\nPath steps: {result.path_length_steps if result else '—'}\nPlanner wall time: {result.execution_time_s:.4f} s" if result else "No completed result."
        self.results_text.setText(text)

    def _save_config(self):
        path,_=QFileDialog.getSaveFileName(self,"Save experiment configuration","experiment.json","JSON (*.json)")
        if path:
            try:self.controller.save_experiment(path); self.statusBar().showMessage(f"Saved {path}")
            except Exception as exc:QMessageBox.warning(self,"Save failed",str(exc))

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

    def _calibration_click(self,event):
        pass

    def _update_calibration(self):
        if len(self.cal_image.points)<2:self.cal_result.setText("Scale: click two points\nResidual: —"); return
        a,b=self.cal_image.points; pixels=((a[0]-b[0])**2+(a[1]-b[1])**2)**.5
        scale=pixels/max(self.cal_distance.value(),1e-9)
        self.cal_result.setText(f"Scale: {scale:.2f} px/m\nResidual: 0.00 px (single reference segment)")

    def closeEvent(self,event):
        if self._worker is not None and self._worker.isRunning():
            self._close_pending=True; self._stop()
            if not self._worker.wait(5000):
                self.statusBar().showMessage("Waiting for the current bounded search call to finish; close again when it stops.")
                event.ignore(); return
        event.accept()

