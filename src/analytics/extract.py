"""Public pure extraction API from frozen search results and event logs."""

from __future__ import annotations

from typing import Any, Iterable

from .metrics import extract_metrics


def extract_run_metrics(
    search_result=None,
    event_log: Iterable[Any] = (),
    *,
    mode: str,
    cell_m: float,
    robot_config=None,
    coverage_result=None,
) -> dict[str, Any]:
    """Compute canonical metrics without consulting UI or rerunning search."""
    events = event_log.snapshot_events() if hasattr(event_log, "snapshot_events") else event_log
    return extract_metrics(search_result, events, mode=mode, cell_m=cell_m,
                           robot_config=robot_config, coverage_result=coverage_result)
