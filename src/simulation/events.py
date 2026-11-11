"""Versioned, JSON-serializable simulation event and snapshot schemas."""
from dataclasses import dataclass, asdict
from collections import deque
from typing import Any
import json
from pathlib import Path

SCHEMA_VERSION = 1

@dataclass(frozen=True)
class SimulationEvent:
    type: str
    t_sim: float
    seq: int
    payload: dict[str, Any]
    schema_version: int = SCHEMA_VERSION

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, default=str)

@dataclass(frozen=True)
class SimulationSnapshot:
    robot_state: Any
    cleaned: Any
    current_path: tuple = ()
    explored: tuple = ()
    coverage_percent: float = 0.0

class EventLog:
    """Bounded in-memory canonical event stream with deterministic sequence numbers."""
    def __init__(self, capacity=10000, sink_path: str | Path | None = None):
        if capacity <= 0:
            raise ValueError("event capacity must be positive")
        self.events = deque(maxlen=capacity)
        self._seq = 0
        self.sink_path = Path(sink_path) if sink_path is not None else None
    def emit(self, event_type, t_sim, **payload):
        event = SimulationEvent(event_type, float(t_sim), self._seq, payload)
        self._seq += 1
        self.events.append(event)
        if self.sink_path is not None:
            self.sink_path.parent.mkdir(parents=True, exist_ok=True)
            with self.sink_path.open("a", encoding="utf-8") as stream:
                stream.write(event.to_json() + "\n")
        return event

def replay_actions(robot, events):
    """Replay movement and mission-stop events through the same robot API."""
    from src.robot.state import StopReason
    initialized_clean = False
    for event in events:
        if event.type == "CellsCleaned" and not initialized_clean and robot.state.step_count == 0:
            robot.clean()
            initialized_clean = True
        if event.type == "MoveExecuted":
            outcome = robot.step(tuple(event.payload["position"]))
            if not outcome.executed:
                raise ValueError("event replay encountered a rejected movement")
        elif event.type == "RunStopped" and robot.termination_reason is None:
            robot.stop(StopReason(event.payload["reason"]))
    return robot.snapshot()
