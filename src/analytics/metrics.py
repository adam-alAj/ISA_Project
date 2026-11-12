"""Canonical metric formulas; semantics are frozen in ``docs/metrics.md``."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Iterable


def _event_value(event: Any) -> dict[str, Any]:
    if isinstance(event, dict):
        return event
    if is_dataclass(event):
        return asdict(event)
    raise TypeError(f"unsupported event value: {type(event).__name__}")


def _value(value: Any, name: str, default=None):
    return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)


def _percent(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return 100.0 * numerator / denominator


def extract_metrics(
    search_result=None,
    events: Iterable[Any] = (),
    *,
    mode: str,
    cell_m: float,
    robot_config=None,
    coverage_result=None,
) -> dict[str, Any]:
    """Extract one mode-specific metric record from raw planner/event data.

    This is a pure function: it does not inspect UI state, rerun planners, or
    mutate the supplied result/event objects. See ``docs/metrics.md``.
    """
    if mode not in {"point_to_point", "coverage"}:
        raise ValueError("mode must be point_to_point or coverage")
    if cell_m <= 0:
        raise ValueError("cell_m must be positive")
    normalized_events = [_event_value(event) for event in events]
    summaries = [e.get("payload", {}) for e in normalized_events if e.get("type") == "SearchFinished"]
    movements = [e for e in normalized_events if e.get("type") == "MoveExecuted"]
    cleaned_cells: set[tuple[int, int]] = set()
    for event in normalized_events:
        if event.get("type") == "CellsCleaned":
            cleaned_cells.update(tuple(map(int, cell)) for cell in event.get("payload", {}).get("cells", ()))

    if mode == "point_to_point" and search_result is not None:
        expanded = int(_value(search_result, "expanded", 0))
        generated = int(_value(search_result, "generated", 0))
        repeated = int(_value(search_result, "repeated_expansions", 0))
        peak = int(_value(search_result, "peak_frontier", 0))
        path_steps = _value(search_result, "path_length_steps")
        path_cost = _value(search_result, "path_cost")
        search_time = float(_value(search_result, "execution_time_s", 0.0))
    elif summaries:
        expanded = sum(int(s.get("expanded", 0)) for s in summaries)
        generated = sum(int(s.get("generated", 0)) for s in summaries)
        repeated = sum(int(s.get("repeated_expansions", 0)) for s in summaries)
        peak = max((int(s.get("peak_frontier", 0)) for s in summaries), default=0)
        search_time = sum(float(s.get("planner_execution_time_s", s.get("wall_time_s", 0.0))) for s in summaries)
        costs = [float(s["path_cost"]) for s in summaries if s.get("found") and s.get("path_cost") is not None]
        path_cost = sum(costs) if costs else None
        path_steps = len(movements) if mode == "coverage" else next(
            (s.get("path_length_steps") for s in summaries if s.get("found")), None)
    else:
        expanded = generated = repeated = peak = 0
        search_time = 0.0
        path_steps = None
        path_cost = None

    executed_steps = len(movements)
    executed_distance = executed_steps * float(cell_m)
    if mode == "point_to_point" and search_result is not None and _value(search_result, "path_length_steps") is not None:
        path_m = int(_value(search_result, "path_length_steps")) * float(cell_m)
    else:
        path_m = int(path_steps) * float(cell_m) if path_steps is not None else None

    starts = [e for e in normalized_events if e.get("type") == "RunStarted"]
    stops = [e for e in normalized_events if e.get("type") == "RunStopped"]
    start_t = float(starts[0].get("t_sim", 0.0)) if starts else None
    last_t = float(normalized_events[-1].get("t_sim", 0.0)) if normalized_events else None
    end_t = float(stops[-1].get("t_sim", 0.0)) if stops else last_t
    simulated_time = max(0.0, end_t - start_t) if start_t is not None and end_t is not None else None
    stop_reason = stops[-1].get("payload", {}).get("reason") if stops else None

    resources = [e.get("payload", {}) for e in normalized_events
                 if e.get("type") in {"ResourceUpdated", "MoveExecuted"}]
    final_resources = resources[-1] if resources else {}
    initial_battery = _value(robot_config, "battery_capacity_units") if robot_config is not None else None
    initial_lifetime = _value(robot_config, "operational_lifetime_s") if robot_config is not None else None
    battery_remaining = final_resources.get("battery")
    lifetime_remaining = final_resources.get("lifetime")
    # Some event streams omit the final ResourceUpdated after a zero-step run.
    battery_remaining = initial_battery if battery_remaining is None else float(battery_remaining)
    lifetime_remaining = initial_lifetime if lifetime_remaining is None else float(lifetime_remaining)
    battery_consumed = (max(0.0, float(initial_battery) - battery_remaining)
                        if initial_battery is not None and battery_remaining is not None else None)
    lifetime_consumed = (max(0.0, float(initial_lifetime) - lifetime_remaining)
                         if initial_lifetime is not None and lifetime_remaining is not None else None)
    battery_capacity = float(initial_battery) if initial_battery is not None else None
    lifetime_capacity = float(initial_lifetime) if initial_lifetime is not None else None
    if stop_reason is None and mode == "point_to_point" and search_result is not None:
        if not bool(_value(search_result, "found", False)):
            stop_reason = str(getattr(_value(search_result, "termination_reason", "no_path"), "value",
                                         _value(search_result, "termination_reason", "no_path")))
        elif battery_remaining is not None and float(battery_remaining) <= 1e-12:
            stop_reason = "battery_depleted"
        elif lifetime_remaining is not None and float(lifetime_remaining) <= 1e-12:
            stop_reason = "lifetime_expired"
        else:
            stop_reason = "mission_complete"

    result: dict[str, Any] = {
        "expanded": expanded, "generated": generated,
        "repeated_expansions": repeated, "peak_frontier": peak,
        "path_length_steps": path_steps, "path_length_m": path_m,
        "path_cost": path_cost, "executed_steps": executed_steps,
        "executed_distance_m": executed_distance, "search_time_s": search_time,
        "simulated_travel_time_s": simulated_time,
        "battery_consumed_units": battery_consumed,
        "battery_remaining_units": battery_remaining,
        "battery_consumed_percent": _percent(battery_consumed, battery_capacity)
        if battery_consumed is not None and battery_capacity else None,
        "battery_remaining_percent": _percent(battery_remaining, battery_capacity)
        if battery_remaining is not None and battery_capacity else None,
        "lifetime_consumed_s": lifetime_consumed,
        "lifetime_remaining_s": lifetime_remaining,
        "lifetime_consumed_min": lifetime_consumed / 60 if lifetime_consumed is not None else None,
        "lifetime_remaining_min": lifetime_remaining / 60 if lifetime_remaining is not None else None,
        "lifetime_consumed_percent": _percent(lifetime_consumed, lifetime_capacity)
        if lifetime_consumed is not None and lifetime_capacity else None,
        "stop_reason": stop_reason,
        "cleaned_cells": len(cleaned_cells),
        "coverage_numerator_cells": None, "coverage_denominator_cells": None,
        "raw_coverage_percent": None, "achievable_numerator_cells": None,
        "achievable_denominator_cells": None, "achievable_coverage_percent": None,
        "remaining_cells": None, "unreachable_cells": None,
        "structurally_uncoverable_cells": None,
    }
    if mode == "coverage" and coverage_result is not None:
        remaining = {tuple(map(int, c)) for c in _value(coverage_result, "remaining_cells", ())}
        structural = {tuple(map(int, c)) for c in _value(coverage_result, "structurally_uncoverable", ())}
        explicit_cleanable = _value(coverage_result, "cleanable_cells")
        denominator_cells = ({tuple(map(int, c)) for c in explicit_cleanable}
                             if explicit_cleanable is not None else remaining | cleaned_cells)
        cleaned_denominator = denominator_cells & cleaned_cells
        raw_denominator = len(denominator_cells)
        raw_percent = _percent(len(cleaned_denominator), raw_denominator)
        structural = structural & denominator_cells
        achievable_denominator = raw_denominator - len(structural)
        achievable_cleaned = len(cleaned_denominator - structural)
        result.update({
            "coverage_numerator_cells": len(cleaned_denominator),
            "coverage_denominator_cells": raw_denominator,
            "raw_coverage_percent": 100.0 if raw_percent is None else raw_percent,
            "achievable_numerator_cells": achievable_cleaned,
            "achievable_denominator_cells": achievable_denominator,
            "achievable_coverage_percent": 100.0 if achievable_denominator == 0
            else 100.0 * achievable_cleaned / achievable_denominator,
            "remaining_cells": len(remaining),
            "unreachable_cells": len(_value(coverage_result, "unreachable_cells", ())),
            "structurally_uncoverable_cells": len(structural),
        })
    return result


def summarize_timings(values: Iterable[float]) -> dict[str, float | int]:
    """Return median and inclusive quartile IQR for a nonempty timing sample."""
    import statistics

    data = sorted(float(value) for value in values)
    if not data:
        raise ValueError("at least one timing value is required")
    if any(value < 0 for value in data):
        raise ValueError("timings cannot be negative")
    if len(data) == 1:
        q1 = q3 = data[0]
    else:
        quartiles = statistics.quantiles(data, n=4, method="inclusive")
        q1, q3 = quartiles[0], quartiles[2]
    return {"repetitions": len(data), "median_s": statistics.median(data),
            "q1_s": q1, "q3_s": q3, "iqr_s": q3 - q1}
