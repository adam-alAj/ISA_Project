"""Comparability checks and separate-mode comparison summaries."""
from __future__ import annotations

COMPARABILITY_FIELDS = (
    ("map.sha256", "map"), ("experiment.robot", "experiment"),
    ("experiment.policy", "experiment"), ("experiment.neighbor_order", "experiment"),
    ("experiment.cost_model", "experiment"), ("experiment.heuristic", "experiment"),
    ("experiment.start", "experiment"), ("experiment.goal", "experiment"),
    ("experiment.seed", "experiment"), ("experiment.movement_model", "experiment"),
    ("experiment.search_budgets", "experiment"),
)


class IncomparableRuns(ValueError):
    """Raised when records do not describe controlled, comparable runs."""


def _path(record, dotted):
    value = record
    for part in dotted.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    return value


def comparability_issues(records: list[dict]) -> list[str]:
    if not records:
        return ["no run records supplied"]
    issues = []
    modes = {_path(record, "experiment.mode") for record in records}
    if len(modes) > 1:
        issues.append("mission modes differ; point-to-point and coverage cannot be mixed")
    for field, _ in COMPARABILITY_FIELDS:
        values = {_freeze(_path(record, field)) for record in records}
        if len(values) > 1:
            issues.append(f"{field} differs across runs")
    return issues


def _freeze(value):
    if isinstance(value, dict):
        return tuple(sorted((k, _freeze(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    return value


def require_comparable(records: list[dict]) -> str:
    issues = comparability_issues(records)
    if issues:
        raise IncomparableRuns("Runs cannot be compared: " + "; ".join(issues))
    return _path(records[0], "experiment.mode")


def comparison_rows(records: list[dict]) -> dict:
    """Return rows by mode so two mission types can never share a table."""
    import statistics
    mode = require_comparable(records)
    grouped = {}
    for record in records:
        grouped.setdefault(record["experiment"]["algorithm"], []).append(record.get("metrics", {}))
    rows = []
    keys = {"expanded": "expanded", "search_time_s": "search_time_s", "path_length_steps": "path_length_steps",
            "path_cost": "path_cost", "energy_units": "battery_consumed_units",
            "coverage_percent": "achievable_coverage_percent"}
    for algorithm, samples in grouped.items():
        row = {"algorithm": algorithm, "repetitions": len(samples)}
        for label, key in keys.items():
            values = [float(sample[key]) for sample in samples if sample.get(key) is not None]
            row[label] = statistics.median(values) if values else None
            if label == "search_time_s" and values:
                ordered = sorted(values)
                if len(ordered) == 1:
                    q1 = q3 = ordered[0]
                else:
                    quartiles = statistics.quantiles(ordered, n=4, method="inclusive")
                    q1, q3 = quartiles[0], quartiles[2]
                row["search_time_q1_s"], row["search_time_q3_s"] = q1, q3
                row["search_time_iqr_s"] = q3 - q1
        reasons = {sample.get("stop_reason") for sample in samples}
        row["stop_reason"] = next(iter(reasons)) if len(reasons) == 1 else "varied"
        rows.append(row)
    return {"mode": mode, "rows": sorted(rows, key=lambda row: row["algorithm"])}
