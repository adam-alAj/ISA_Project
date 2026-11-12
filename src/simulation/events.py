"""Versioned, JSON-serializable simulation event and snapshot schemas."""
from dataclasses import dataclass, asdict
from collections import deque
from typing import Any
import json
from pathlib import Path
import threading
import queue

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
        self._lock = threading.RLock()
        self._sink_queue = None
        self._sink_thread = None
        self._sink_error = None
        if self.sink_path is not None:
            self.sink_path.parent.mkdir(parents=True, exist_ok=True)
            self._sink_queue = queue.Queue(maxsize=2048)
            self._sink_thread = threading.Thread(target=self._write_sink, name="simulation-event-writer", daemon=True)
            self._sink_thread.start()

    def _write_sink(self):
        stream = None
        try:
            stream = self.sink_path.open("w", encoding="utf-8", buffering=65536, newline="\n")
        except BaseException as exc:
            self._sink_error = exc
        while True:
            event = self._sink_queue.get()
            try:
                if event is None:
                    break
                if stream is not None and self._sink_error is None:
                    try:
                        stream.write(event.to_json() + "\n")
                    except BaseException as exc:
                        self._sink_error = exc
            finally:
                self._sink_queue.task_done()
        if stream is not None:
            try:
                stream.close()
            except BaseException as exc:
                self._sink_error = self._sink_error or exc
    def emit(self, event_type, t_sim, **payload):
        with self._lock:
            event = SimulationEvent(event_type, float(t_sim), self._seq, payload)
            self._seq += 1
            self.events.append(event)
            if self._sink_queue is not None:
                # The bounded queue caps pending event memory. If disk falls behind,
                # Queue.put yields the GIL while applying backpressure to simulation.
                if self._sink_error is not None:
                    raise RuntimeError("event log sink failed") from self._sink_error
                self._sink_queue.put(event)
        return event

    def snapshot_events(self) -> tuple[SimulationEvent, ...]:
        """Copy retained events atomically for readers running beside emitters."""
        with self._lock:
            return tuple(self.events)

    def close(self):
        """Flush and close the optional durable event stream."""
        with self._lock:
            if self._sink_queue is not None:
                self._sink_queue.put(None)
                self._sink_thread.join()
                self._sink_queue = None
                self._sink_thread = None
                if self._sink_error is not None:
                    raise RuntimeError("event log sink failed") from self._sink_error

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def search_result_metrics(result) -> dict[str, Any]:
    """Return bounded raw planner counters for a SearchFinished event."""
    return {
        "expanded": int(result.expanded),
        "generated": int(result.generated),
        "peak_frontier": int(result.peak_frontier),
        "repeated_expansions": int(result.repeated_expansions),
        "path_length_steps": result.path_length_steps,
        "path_cost": result.path_cost,
        "planner_execution_time_s": float(result.execution_time_s),
        "termination_reason": result.termination_reason.value,
    }

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
