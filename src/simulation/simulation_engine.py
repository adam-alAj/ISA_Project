"""Shared simulation facade for separated mission modes."""
from src.simulation.modes import CoverageMission, PointToPointMission

class SimulationEngine:
    def __init__(self, robot):
        self.robot = robot

    def run_point_to_point(self, mission, planner, options=None):
        if not isinstance(mission, PointToPointMission):
            raise TypeError("run_point_to_point requires PointToPointMission")
        if mission.start != self.robot.state.position:
            raise ValueError("mission start must equal the robot's current position")
        from src.algorithms.problem import SearchProblem
        from src.simulation.events import EventLog
        from src.simulation.executor import RouteExecutor
        from time import perf_counter
        events = EventLog(); events.emit("RunStarted", self.robot.state.elapsed_time_s, mode="point_to_point")
        base = SearchProblem.from_grid_map(self.robot.grid_map, mission.start, mission.goal)
        nav = self.robot.footprint.navigable
        problem = SearchProblem(base.start, base.goal,
            lambda cell: (n for n in base.neighbors(cell) if nav[n]), base.step_cost_fn,
            base.heuristic_fn, lambda c: self.robot.grid_map.is_traversable(c) and bool(nav[c]),
            tuple(c for c in base.all_nodes if nav[c]), base.min_step_cost)
        before = self.robot.snapshot(); events.emit("SearchStarted", self.robot.state.elapsed_time_s)
        start = perf_counter(); result = planner(problem, options); wall = perf_counter()-start
        if self.robot.state != before.state or not (self.robot.cleaning.cleaned == before.cleaned).all():
            raise RuntimeError("planner mutated robot state")
        events.emit("SearchFinished", self.robot.state.elapsed_time_s, found=result.found, wall_time_s=wall)
        if result.found: RouteExecutor(self.robot, events).execute(result.path)
        return result, events

    def run_coverage(self, mission: CoverageMission, controller):
        if not isinstance(mission, CoverageMission):
            raise TypeError("run_coverage requires CoverageMission")
        if mission.policy is not controller.policy:
            raise ValueError("mission policy must be the controller's experiment policy object")
        return controller.run()
