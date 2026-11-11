"""Route executor; all movement goes through Robot.step."""
from src.robot.state import StopReason

class RouteExecutor:
    def __init__(self, robot, event_log):
        self.robot, self.events = robot, event_log

    def execute(self, path):
        executed = []
        for target in tuple(path)[1:]:
            result = self.robot.step(target)
            if not result.executed:
                if result.stop_reason:
                    self.events.emit("RunStopped", self.robot.state.elapsed_time_s, reason=result.stop_reason.value)
                break
            executed.append(self.robot.state.position)
            self.events.emit("MoveExecuted", self.robot.state.elapsed_time_s, position=self.robot.state.position,
                             battery=self.robot.state.battery_remaining, lifetime=self.robot.state.lifetime_remaining_s)
            self.events.emit("ResourceUpdated", self.robot.state.elapsed_time_s,
                             battery=self.robot.state.battery_remaining, lifetime=self.robot.state.lifetime_remaining_s)
            if result.newly_cleaned:
                self.events.emit("CellsCleaned", self.robot.state.elapsed_time_s, cells=result.newly_cleaned)
            reason = result.stop_reason or self.robot.check_limits()
            if reason:
                self.events.emit("RunStopped", self.robot.state.elapsed_time_s, reason=reason.value)
                break
        return tuple(executed)
