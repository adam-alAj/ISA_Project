"""Algorithm-independent coverage loop."""
from dataclasses import dataclass
from dataclasses import asdict
from hashlib import sha256
import json
import time
import threading

from src.algorithms.problem import SearchProblem
from src.robot.state import StopReason
from src.simulation.events import EventLog, SimulationSnapshot
from src.simulation.executor import RouteExecutor


@dataclass(frozen=True)
class CoverageResult:
    coverage_percent: float
    raw_coverage_percent: float
    remaining_cells: tuple
    unreachable_cells: tuple
    structurally_uncoverable: tuple
    stop_reason: StopReason
    planner_wall_time_s: float
    iterations: int
    run_id: str


class CoverageController:
    def __init__(self, robot, cleanable, policy, planner, algorithm_id, *, options=None, max_iterations=100000,
                 snapshot_cadence=1, snapshot_capacity=256):
        self.robot, self.cleanable, self.policy, self.planner = robot, cleanable, policy, planner
        self.algorithm_id, self.options = algorithm_id, options
        self.max_iterations, self.snapshot_cadence = max_iterations, max(1, snapshot_cadence)
        self.snapshots = __import__('collections').deque(maxlen=snapshot_capacity)
        self.events = EventLog(); self._cancel = threading.Event(); self.paused = False
        config = {"algorithm": algorithm_id, "policy": policy.policy_id,
                  "cleanable_cells": sorted(cleanable.cells),
                  "robot": asdict(robot.config), "cell_m": robot.grid_map.cell_m}
        self.run_id = sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()

    def cancel(self): self._cancel.set()
    def pause(self): self.paused = True
    def resume(self): self.paused = False
    def reset(self):
        self.robot.reset(); self.events = EventLog(); self.snapshots.clear(); self._cancel.clear()

    def run(self):
        self.events.emit("RunStarted", self.robot.state.elapsed_time_s, run_id=self.run_id, algorithm=self.algorithm_id)
        executor = RouteExecutor(self.robot, self.events)
        initial_clean = self.robot.clean()
        if initial_clean.newly_cleaned:
            self.events.emit("CellsCleaned", self.robot.state.elapsed_time_s, cells=initial_clean.newly_cleaned)
            self.events.emit("ResourceUpdated", self.robot.state.elapsed_time_s,
                             battery=self.robot.state.battery_remaining, lifetime=self.robot.state.lifetime_remaining_s)
        cleaned = self.robot.cleaning.cleaned
        excluded, unreachable = set(self.cleanable.structurally_uncoverable), set()
        stop = self.robot.check_limits()
        iterations, planner_time = 0, 0.0
        while stop is None and iterations < self.max_iterations:
            if self._cancel.is_set():
                stop = StopReason.USER_STOP; break
            while self.paused and not self._cancel.is_set():
                time.sleep(.01)
            if self._cancel.is_set():
                stop = StopReason.USER_STOP; break
            cleaned_cells = set(map(tuple, __import__('numpy').argwhere(cleaned))) | excluded
            target = self.policy.next_target(self.robot.state, cleaned_cells)
            if target is None:
                remaining_achievable = self.cleanable.achievable_cells - set(map(tuple, __import__('numpy').argwhere(cleaned)))
                stop = StopReason.MISSION_COMPLETE if not remaining_achievable else StopReason.NO_REACHABLE_TARGET
                break
            self.events.emit("TargetSelected", self.robot.state.elapsed_time_s, target=target)
            navigable = self.robot.footprint.navigable
            problem = SearchProblem.from_grid_map(self.robot.grid_map, self.robot.state.position, target,
                       heuristic_fn=None)
            original_neighbors = problem.neighbors_fn
            problem = SearchProblem(problem.start, problem.goal,
                lambda cell: (n for n in original_neighbors(cell) if navigable[n]), problem.step_cost_fn,
                problem.heuristic_fn, lambda c: self.robot.grid_map.is_traversable(c) and bool(navigable[c]),
                tuple(c for c in problem.all_nodes if navigable[c]), problem.min_step_cost)
            before = self.robot.snapshot()
            self.events.emit("SearchStarted", self.robot.state.elapsed_time_s, target=target)
            started = time.perf_counter(); result = self.planner(problem, self.options); duration = time.perf_counter()-started
            planner_time += duration
            if self.robot.state != before.state or not (self.robot.cleaning.cleaned == before.cleaned).all():
                raise RuntimeError("planner mutated robot state or cleaning layer")
            self.events.emit("SearchFinished", self.robot.state.elapsed_time_s, found=result.found,
                             wall_time_s=duration, explored=result.trace or ())
            if not result.found:
                excluded.add(target); unreachable.add(target)
                self.events.emit("TargetUnreachable", self.robot.state.elapsed_time_s, target=target,
                                 reason="unreachable_for_planner")
            else:
                executor.execute(result.path)
            iterations += 1
            if iterations % self.snapshot_cadence == 0:
                raw = len(set(map(tuple, __import__('numpy').argwhere(cleaned))) & self.cleanable.cells)
                pct = 100.0*raw/self.cleanable.denominator if self.cleanable.denominator else 100.0
                arr = self.robot.cleaning.cleaned.copy(); arr.setflags(write=False)
                self.snapshots.append(SimulationSnapshot(self.robot.state, arr, result.path if result.found else (), (), pct))
            stop = self.robot.check_limits()
        if stop is None:
            stop = StopReason.ERROR if iterations >= self.max_iterations else StopReason.MISSION_COMPLETE
        self.robot.stop(stop) if self.robot.termination_reason is None else None
        clean_cells = set(map(tuple, __import__('numpy').argwhere(self.robot.cleaning.cleaned))) & self.cleanable.cells
        remaining = sorted(self.cleanable.cells - clean_cells)
        denom = self.cleanable.denominator
        rawpct = 100*len(clean_cells)/denom if denom else 100.0
        ach = self.cleanable.achievable_cells
        achpct = 100*len(clean_cells & ach)/len(ach) if ach else 100.0
        self.events.emit("RunStopped", self.robot.state.elapsed_time_s, reason=stop.value)
        return CoverageResult(achpct, rawpct, tuple(remaining), tuple(sorted(unreachable)),
                              tuple(sorted(self.cleanable.structurally_uncoverable)), stop, planner_time, iterations, self.run_id)
