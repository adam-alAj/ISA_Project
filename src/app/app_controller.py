"""Application-level state and actions; views delegate here instead of to domain code."""
from __future__ import annotations

import json
import threading
import time
from collections import deque
from pathlib import Path

import numpy as np
from PySide6.QtCore import QObject, Signal

from src.algorithms.registry import REGISTRY
from src.algorithms.result import SearchOptions
from src.coverage.cleanable import build_cleanable_cells
from src.coverage.controller import CoverageController
from src.coverage.target_policy import NearestUncleanedPolicy
from src.environment.grid_map import GridMap
from src.environment.validation import validate_map
from src.map_processing.constants import CellState
from src.map_processing.map_io import load_map
from src.robot.config import RobotConfig
from src.robot.vacuum_robot import Robot
from src.simulation.modes import CoverageMission, PointToPointMission
from src.simulation.simulation_engine import SimulationEngine


class AppController(QObject):
    """Own application configuration and construct UI-free domain runs."""
    changed = Signal()
    message = Signal(str)

    def __init__(self, data_root: Path | None = None):
        super().__init__()
        self.data_root = data_root or Path.cwd() / "data"
        self.map: GridMap | None = None
        self.map_path: Path | None = None
        self.metadata: dict = {}
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None
        self.algorithm = "bfs"
        self.mode = "coverage"
        self.robot_config = RobotConfig()
        self.robot: Robot | None = None
        self.engine: SimulationEngine | None = None
        self.coverage_controller: CoverageController | None = None
        self.search_result = None
        self.run_result = None
        self.run_state = "idle"
        self._undo: list[tuple[tuple[int, int], int]] = []
        self._redo: list[tuple[tuple[int, int], int]] = []
        self.recent_runs: list[dict] = []
        self._trace_lock = threading.Lock()
        self._trace_cells: deque[tuple[int, int]] = deque(maxlen=2500)
        self._trace_event_count = 0

    @property
    def map_version(self) -> str:
        return str(self.metadata.get("version", "unloaded"))

    def load_department_map(self) -> None:
        self.load_map(self.data_root / "maps" / "department_v1")

    def load_map(self, directory: str | Path) -> None:
        path = Path(directory)
        grid, metadata = load_map(path)
        self.map_path, self.metadata = path, metadata
        self.start = tuple(metadata["start_cell"]) if metadata.get("start_cell") else None
        self.goal = None
        self.map = GridMap(grid, float(metadata["cell_m"]), tuple(metadata.get("origin_px", (0, 0))), metadata)
        self._undo.clear(); self._redo.clear()
        self._make_robot()
        self.message.emit(f"Loaded map {metadata.get('version', path.name)} ({grid.shape[0]} × {grid.shape[1]})")
        self.changed.emit()

    def import_grid(self, grid: np.ndarray, cell_m: float = 0.1, version: str = "imported") -> None:
        self.metadata = {"version": version, "cell_m": cell_m, "start_cell": None}
        self.map = GridMap(grid, cell_m, metadata=self.metadata)
        self.map_path = None; self.start = None; self.goal = None
        self._make_robot(); self.changed.emit()

    def set_robot_config(self, **values) -> None:
        self.robot_config = RobotConfig(**values)
        if self.map is not None:
            self._make_robot()
        self.changed.emit()

    def _make_robot(self) -> None:
        if self.map is not None and self.start is not None:
            try:
                self.robot = Robot(self.map, self.start, self.robot_config)
                self.engine = SimulationEngine(self.robot)
            except ValueError as exc:
                self.robot = None; self.engine = None
                self.message.emit(str(exc))

    def set_start(self, cell: tuple[int, int]) -> bool:
        if self.map is None or not self.map.is_traversable(cell):
            self.message.emit("Start must be on a FREE or DOOR cell.")
            return False
        previous = self.start; self.start = cell
        self._make_robot()
        if self.robot is None:
            self.start = previous; self._make_robot()
            self.message.emit("Start has insufficient robot-footprint clearance.")
            return False
        self.changed.emit(); return True

    def set_goal(self, cell: tuple[int, int]) -> bool:
        if self.map is None or not self.map.is_traversable(cell):
            self.message.emit("Goal must be on a FREE or DOOR cell.")
            return False
        self.goal = cell; self.changed.emit(); return True

    def paint(self, cell: tuple[int, int], state: int) -> bool:
        if self.map is None or not self.map.in_bounds(cell):
            return False
        grid = np.array(self.map.grid, copy=True)
        self._undo.append((cell, int(grid[cell]))); self._redo.clear()
        grid[cell] = state
        self.map = GridMap(grid, self.map.cell_m, self.map.origin_px, self.metadata)
        if cell == self.start and state not in (CellState.FREE, CellState.DOOR):
            self.start = None; self.robot = None; self.engine = None
        else:
            self._make_robot()
        self.changed.emit(); return True

    def undo(self) -> None:
        if not self._undo or self.map is None: return
        cell, old = self._undo.pop(); self._redo.append((cell, int(self.map.grid[cell])))
        grid = np.array(self.map.grid, copy=True); grid[cell] = old
        self.map = GridMap(grid, self.map.cell_m, self.map.origin_px, self.metadata); self._make_robot(); self.changed.emit()

    def redo(self) -> None:
        if not self._redo or self.map is None: return
        cell, state = self._redo.pop(); self._undo.append((cell, int(self.map.grid[cell])))
        grid = np.array(self.map.grid, copy=True); grid[cell] = state
        self.map = GridMap(grid, self.map.cell_m, self.map.origin_px, self.metadata); self._make_robot(); self.changed.emit()

    def validation_messages(self) -> list[str]:
        if self.map is None: return ["Load a map first."]
        if self.start is None: return ["Choose a start cell."]
        return [issue.message for issue in validate_map(self.map, self.start)]

    def make_coverage_controller(self) -> CoverageController:
        if self.map is None or self.start is None or self.robot is None:
            raise ValueError("Load a map and choose a valid start position first.")
        cleanable = build_cleanable_cells(self.map, self.start, self.robot)
        policy = NearestUncleanedPolicy(cleanable.cells)
        options = SearchOptions(max_expansions=20000, time_budget_s=2.0,
                                trace_callback=self._trace_event, frontier_sample_every=100)
        with self._trace_lock: self._trace_cells.clear()
        self._trace_event_count = 0
        return CoverageController(self.robot, cleanable, policy, REGISTRY[self.algorithm], self.algorithm, options=options)

    def _trace_event(self, event: dict) -> None:
        if event.get("event") == "NodeExpanded":
            self._trace_event_count += 1
            # Windows does not always preempt a CPU-bound Python search as
            # promptly as Qt's event loop needs. Cooperatively yield without
            # imposing a timed sleep on the simulation.
            if self._trace_event_count % 32 == 0:
                time.sleep(0)
            if self._trace_event_count % 8:
                return
            node = event.get("node")
            if isinstance(node, list) and len(node) == 2:
                with self._trace_lock: self._trace_cells.append((int(node[0]), int(node[1])))

    def trace_cells(self) -> tuple[tuple[int, int], ...]:
        with self._trace_lock: return tuple(self._trace_cells)

    def run(self):
        if self.engine is None or self.robot is None:
            raise ValueError("Load a map and choose a valid start position first.")
        if self.mode == "coverage":
            self.coverage_controller = self.make_coverage_controller()
            return self.engine.run_coverage(CoverageMission(self.coverage_controller.policy), self.coverage_controller)
        if self.goal is None:
            raise ValueError("Choose a point-to-point goal first.")
        with self._trace_lock: self._trace_cells.clear()
        self._trace_event_count = 0
        options = SearchOptions(max_expansions=20000, time_budget_s=2.0,
                                trace_callback=self._trace_event, frontier_sample_every=100)
        self.search_result, _events = self.engine.run_point_to_point(
            PointToPointMission(self.robot.state.position, self.goal), REGISTRY[self.algorithm], options)
        return self.search_result

    def save_experiment(self, path: str | Path) -> None:
        document = {"map_path": str(self.map_path) if self.map_path else None, "algorithm": self.algorithm,
                    "mode": self.mode, "start": self.start, "goal": self.goal,
                    "robot": self.robot_config.__dict__}
        Path(path).write_text(json.dumps(document, indent=2), encoding="utf-8")

