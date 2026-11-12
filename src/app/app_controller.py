"""Application-level state and actions; views delegate here instead of to domain code."""
from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
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
from src.analytics.metrics import extract_metrics
from src.analytics.records import machine_info, map_sha256, save_run_record, software_versions, stable_run_id


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
        self.experiment_seed: int | None = None
        self.mode = "coverage"
        self.robot_config = RobotConfig()
        self.robot: Robot | None = None
        self.engine: SimulationEngine | None = None
        self.coverage_controller: CoverageController | None = None
        self.search_result = None
        self.search_events = None
        self.run_result = None
        self.run_state = "idle"
        self._undo: list[tuple[tuple[int, int], int]] = []
        self._redo: list[tuple[tuple[int, int], int]] = []
        self.recent_runs: list[dict] = []
        self.experiments_dir = self.data_root / "experiments"
        self._trace_lock = threading.Lock()
        self._trace_cells: deque[tuple[int, int]] = deque(maxlen=2500)
        self._frontier_cells: set[tuple[int, int]] = set()
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
        self._remember_map(path)
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

    def validation_issues(self):
        if self.map is None or self.start is None:return ()
        return tuple(validate_map(self.map,self.start))

    def make_coverage_controller(self) -> CoverageController:
        if self.map is None or self.start is None or self.robot is None:
            raise ValueError("Load a map and choose a valid start position first.")
        cleanable = build_cleanable_cells(self.map, self.start, self.robot)
        policy = NearestUncleanedPolicy(cleanable.cells)
        options = SearchOptions(max_expansions=20000, time_budget_s=2.0,
                                trace_callback=self._trace_event, frontier_sample_every=100)
        with self._trace_lock: self._trace_cells.clear()
        with self._trace_lock: self._frontier_cells.clear()
        self._trace_event_count = 0
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        event_path = self.experiments_dir / f".pending_{uuid.uuid4().hex}.jsonl"
        return CoverageController(self.robot, cleanable, policy, REGISTRY[self.algorithm], self.algorithm,
                                  options=options, event_sink_path=event_path)

    def _trace_event(self, event: dict) -> None:
        node = event.get("node")
        if event.get("event") == "NodeGenerated" and isinstance(node,list) and len(node)==2:
            with self._trace_lock:self._frontier_cells.add((int(node[0]),int(node[1])))
        elif event.get("event") == "NodeExpanded":
            self._trace_event_count += 1
            if event.get("expanded") == 1:
                with self._trace_lock:self._frontier_cells.clear()
            # Windows does not always preempt a CPU-bound Python search as
            # promptly as Qt's event loop needs. Cooperatively yield without
            # imposing a timed sleep on the simulation.
            if self._trace_event_count % 32 == 0:
                time.sleep(0)
            if self._trace_event_count % 8:
                return
            if isinstance(node, list) and len(node) == 2:
                cell=(int(node[0]),int(node[1]))
                with self._trace_lock:
                    self._trace_cells.append(cell); self._frontier_cells.discard(cell)

    def trace_cells(self) -> tuple[tuple[int, int], ...]:
        with self._trace_lock: return tuple(self._trace_cells)

    def frontier_cells(self) -> tuple[tuple[int,int], ...]:
        with self._trace_lock:return tuple(self._frontier_cells)

    def run(self):
        if self.engine is None or self.robot is None:
            raise ValueError("Load a map and choose a valid start position first.")
        if self.mode == "coverage":
            self.coverage_controller = self.make_coverage_controller()
            return self.engine.run_coverage(CoverageMission(self.coverage_controller.policy), self.coverage_controller)
        if self.goal is None:
            raise ValueError("Choose a point-to-point goal first.")
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        self.engine.event_sink_path = self.experiments_dir / f".pending_{uuid.uuid4().hex}.jsonl"
        with self._trace_lock: self._trace_cells.clear()
        with self._trace_lock: self._frontier_cells.clear()
        self._trace_event_count = 0
        options = SearchOptions(max_expansions=20000, time_budget_s=2.0,
                                trace_callback=self._trace_event, frontier_sample_every=100)
        self.search_result, self.search_events = self.engine.run_point_to_point(
            PointToPointMission(self.robot.state.position, self.goal), REGISTRY[self.algorithm], options)
        return self.search_result

    def save_experiment(self, path: str | Path) -> None:
        document = {"schema_version": 1, "kind": "experiment_config",
                    "map_path": str(self.map_path) if self.map_path else None,
                    "map_version": self.map_version, "algorithm": self.algorithm,
                    "mode": self.mode, "start": self.start, "goal": self.goal,
                    "robot": asdict(self.robot_config),
                    "map_data": ({"grid": self.map.grid.tolist(), "cell_m": self.map.cell_m,
                                  "origin_px": self.map.origin_px, "metadata": self.metadata}
                                 if self.map is not None else None)}
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(document, indent=2), encoding="utf-8")

    def load_experiment(self, path: str | Path) -> None:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        if document.get("schema_version") != 1 or document.get("kind") != "experiment_config":
            raise ValueError("Unsupported experiment configuration schema.")
        algorithm, mode = document.get("algorithm"), document.get("mode")
        if algorithm not in REGISTRY:
            raise ValueError(f"Unknown algorithm in configuration: {algorithm}")
        if mode not in ("coverage", "point_to_point"):
            raise ValueError(f"Unknown mission mode in configuration: {mode}")
        map_path = document.get("map_path")
        candidate = Path(map_path) if map_path else None
        if candidate is not None and not candidate.is_absolute():
            candidate = (Path(path).parent / candidate).resolve()
        if candidate is not None and candidate.exists():
            self.load_map(candidate)
        map_data=document.get("map_data")
        if map_data:
            metadata=dict(map_data.get("metadata",{})); metadata.setdefault("version",document.get("map_version","imported"))
            self.map=GridMap(np.asarray(map_data["grid"],dtype=np.uint8),float(map_data["cell_m"]),
                             tuple(map_data.get("origin_px",(0,0))),metadata)
            self.metadata=metadata; self.map_path=candidate if candidate is not None and candidate.exists() else None
        elif self.map is None:
            raise ValueError("Configuration has no embedded map and its map bundle is unavailable.")
        self.robot_config = RobotConfig(**document["robot"])
        self.algorithm, self.mode = algorithm, mode
        self.start = tuple(document["start"]) if document.get("start") is not None else self.start
        self.goal = tuple(document["goal"]) if document.get("goal") is not None else None
        self._make_robot()
        if self.start is not None and self.robot is None:
            raise ValueError("Saved start position is not valid for the saved robot configuration.")
        self.changed.emit()

    def recent_experiments(self) -> list[dict]:
        """Read saved configurations and run summaries from data/experiments."""
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        records = []
        # The directory can contain many large versioned records with embedded
        # canonical grids. The home screen needs only the newest dozen entries;
        # parsing the entire history here stalls Qt's GUI thread.
        newest_files = sorted(self.experiments_dir.glob("*.json"),
                              key=lambda item: item.stat().st_mtime, reverse=True)[:12]
        for file in newest_files:
            try:
                record = json.loads(file.read_text(encoding="utf-8"))
                if isinstance(record,dict) and record.get("kind") in ("experiment_config", "run_record"):
                    record["_path"] = str(file)
                    records.append(record)
            except (OSError, json.JSONDecodeError):
                continue
        self.recent_runs = records
        return records

    @property
    def recent_maps_path(self) -> Path:
        return self.experiments_dir / "recent_maps.json"

    def _remember_map(self, path: Path) -> None:
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        try: records=json.loads(self.recent_maps_path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError): records=[]
        normalized=str(path.resolve()).casefold()
        records=[row for row in records if str(row.get("path","")).casefold()!=normalized]
        records.insert(0,{"path":str(path.resolve()),"version":self.map_version,
                          "opened_utc":datetime.now(timezone.utc).isoformat()})
        self.recent_maps_path.write_text(json.dumps(records[:10],indent=2),encoding="utf-8")

    def recent_map_records(self) -> list[dict]:
        try:records=json.loads(self.recent_maps_path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):return []
        return [row for row in records if Path(row.get("path","" )).exists()]

    def record_completed_run(self, result) -> Path:
        """Persist a versioned P8 record and its immutable event stream sidecar."""
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        robot = self.robot
        if self.map is None or robot is None or self.start is None:
            raise ValueError("A completed run requires a loaded map, valid start, and robot.")
        coverage_result = result if self.mode == "coverage" else None
        search_result = self.search_result if self.mode == "point_to_point" else None
        event_log = (self.coverage_controller.events if self.mode == "coverage" and self.coverage_controller
                     else self.search_events)
        events = event_log.snapshot_events() if event_log is not None else ()
        policy = ({"id": self.coverage_controller.policy.policy_id,
                   "configuration": getattr(self.coverage_controller.policy, "config", {})}
                  if self.mode == "coverage" and self.coverage_controller else None)
        result_rows = []
        if search_result is not None:
            result_rows.append({"found": search_result.found, "path": [list(cell) for cell in search_result.path],
                "path_length_steps": search_result.path_length_steps, "path_cost": search_result.path_cost,
                "expanded": search_result.expanded, "generated": search_result.generated,
                "peak_frontier": search_result.peak_frontier,
                "repeated_expansions": search_result.repeated_expansions,
                "execution_time_s": search_result.execution_time_s,
                "termination_reason": search_result.termination_reason.value})
        else:
            result_rows = [{k: event.payload.get(k) for k in ("found", "path_length_steps", "path_cost", "expanded",
                "generated", "peak_frontier", "repeated_expansions", "planner_execution_time_s", "termination_reason")}
                for event in events if event.type == "SearchFinished"]
            for row in result_rows:
                row.update({"found": bool(row.get("found")), "path": [],
                    "execution_time_s": float(row.pop("planner_execution_time_s", 0.0) or 0.0),
                    "path_length_steps": row.get("path_length_steps"), "path_cost": row.get("path_cost"),
                    "expanded": int(row.get("expanded") or 0), "generated": int(row.get("generated") or 0),
                    "peak_frontier": int(row.get("peak_frontier") or 0),
                    "repeated_expansions": int(row.get("repeated_expansions") or 0),
                    "termination_reason": row.get("termination_reason") or "unknown"})
        coverage_metrics_input = ({"remaining_cells": coverage_result.remaining_cells,
            "unreachable_cells": coverage_result.unreachable_cells,
            "structurally_uncoverable": coverage_result.structurally_uncoverable,
            "cleanable_cells": self.coverage_controller.cleanable.cells}
            if coverage_result is not None and self.coverage_controller else coverage_result)
        metrics = extract_metrics(search_result, events, mode=self.mode, cell_m=self.map.cell_m,
                                  robot_config=self.robot_config, coverage_result=coverage_metrics_input)
        grid_hash = map_sha256(self.map.grid, self.map.cell_m, self.map.origin_px)
        algorithm_settings = {"max_expansions": 20000, "time_budget_s": 2.0}
        experiment = {"mode": self.mode, "algorithm": self.algorithm, "algorithm_settings": algorithm_settings,
                      "start": list(self.start), "goal": list(self.goal) if self.goal else None, "seed": self.experiment_seed,
                      "robot": asdict(self.robot_config), "policy": policy,
                      "neighbor_order": ["up", "right", "down", "left"], "movement_model": "four-neighbor-cardinal",
                      "cost_model": {"transition": "unit"}, "heuristic": "manhattan",
                      "search_budgets": algorithm_settings}
        record = {"schema_version": 1, "kind": "run_record",
            "run_id": stable_run_id(grid_hash, experiment, self.algorithm, policy, self.experiment_seed),
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "project": {"name": "Smart Vacuum", "version": "0.1.0", **machine_info(),
                        "software": software_versions()},
            "map": {"id": self.map_path.name if self.map_path else "imported", "version": self.map_version,
                    "sha256": grid_hash, "rows": int(self.map.grid.shape[0]), "cols": int(self.map.grid.shape[1]),
                    "cell_m": float(self.map.cell_m), "origin_px": list(self.map.origin_px),
                    "grid": self.map.grid.tolist()},
            "experiment": experiment,
            "raw_results": {"search_results": result_rows,
                "coverage_result": ({"coverage_percent": coverage_result.coverage_percent,
                    "raw_coverage_percent": coverage_result.raw_coverage_percent,
                    "remaining_cells": coverage_result.remaining_cells,
                    "unreachable_cells": coverage_result.unreachable_cells,
                    "structurally_uncoverable": coverage_result.structurally_uncoverable,
                    "cleanable_cells": sorted(self.coverage_controller.cleanable.cells),
                    "stop_reason": coverage_result.stop_reason.value} if coverage_result else None),
                "final_robot_state": asdict(robot.state),
                "cleaned_cells": [list(map(int, cell)) for cell in np.argwhere(robot.cleaning.cleaned)],
                "visualization": {"explored_cells": [list(c) for c in self.trace_cells()],
                    "route_cells": ([list(c) for c in search_result.path] if search_result is not None else
                        [list(event.payload["position"]) for event in events if event.type == "MoveExecuted"]),
                    "cleaned_cells": [list(map(int, cell)) for cell in np.argwhere(robot.cleaning.cleaned)]}},
            "metrics": metrics}
        source_path = getattr(event_log, "sink_path", None) if event_log is not None else None
        path = save_run_record(record, self.experiments_dir, events, event_source_path=source_path)
        self.recent_experiments()
        return path

