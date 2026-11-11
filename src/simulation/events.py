"""Versioned, JSON-serializable simulation event and snapshot schemas."""
from dataclasses import dataclass, asdict
from typing import Any
import json

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
    """Append-only canonical event stream with deterministic sequence numbers."""
    def __init__(self): self.events = []
    def emit(self, event_type, t_sim, **payload):
        event = SimulationEvent(event_type, float(t_sim), len(self.events), payload)
        self.events.append(event)
        return event

def replay_actions(robot, events):
    """Replay successful movement events through the same validated robot API."""
    for event in events:
        if event.type == "MoveExecuted":
            outcome = robot.step(tuple(event.payload["position"]))
            if not outcome.executed:
                raise ValueError("event replay encountered a rejected movement")
    return robot.snapshot()
