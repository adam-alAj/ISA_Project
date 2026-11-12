"""Regression: UI snapshots must be safe while the simulation emits events."""

import threading

from src.simulation.events import EventLog


def test_event_log_snapshot_is_consistent_during_concurrent_emission():
    log = EventLog(capacity=64)
    finished = threading.Event()

    def emit_events():
        for index in range(20_000):
            log.emit("MoveExecuted", index / 10, position=(index, 0))
        finished.set()

    writer = threading.Thread(target=emit_events)
    writer.start()
    snapshots = 0
    while not finished.is_set():
        events = log.snapshot_events()
        sequences = [event.seq for event in events]
        assert sequences == sorted(sequences)
        assert len(events) <= 64
        snapshots += 1
    writer.join(timeout=2)
    assert not writer.is_alive()
    assert snapshots > 0
    assert [event.seq for event in log.snapshot_events()] == list(range(19_936, 20_000))
