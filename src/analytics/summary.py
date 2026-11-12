"""Mode-aware run summaries and their plain-text renderer."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    mode: str
    algorithm: str
    path_length_steps: int | None
    path_length_m: float | None
    path_cost: float | None
    expanded: int
    search_time_s: float
    simulated_travel_time_s: float | None
    energy_units: float | None
    lifetime_remaining_s: float | None
    coverage_percent: float | None
    raw_coverage_percent: float | None
    stop_reason: str | None

    @classmethod
    def from_record(cls, record: dict) -> "RunSummary":
        metrics = record.get("metrics", {})
        return cls(record["run_id"], record["experiment"]["mode"], record["experiment"]["algorithm"],
                   metrics.get("path_length_steps"), metrics.get("path_length_m"), metrics.get("path_cost"),
                   int(metrics.get("expanded", 0)), float(metrics.get("search_time_s", 0.0)),
                   metrics.get("simulated_travel_time_s"), metrics.get("battery_consumed_units"),
                   metrics.get("lifetime_remaining_s"), metrics.get("achievable_coverage_percent"),
                   metrics.get("raw_coverage_percent"), metrics.get("stop_reason"))

    def render_text(self) -> str:
        route = "no route" if self.path_length_steps is None else f"{self.path_length_steps} steps ({self.path_length_m} m)"
        details = (f"achievable coverage {self.coverage_percent}% (raw {self.raw_coverage_percent}%)"
                   if self.mode == "coverage" else f"route {route}, path cost {self.path_cost}")
        return (f"{self.mode.replace('_', ' ').title()} · {self.algorithm.upper()}: {details}; "
                f"expanded {self.expanded}; planner time {self.search_time_s:.6f} s; "
                f"travel time {self.simulated_travel_time_s} s; energy {self.energy_units}; "
                f"lifetime remaining {self.lifetime_remaining_s} s; stop reason {self.stop_reason}. "
                "DFS depends on neighbor order. "
                "Greedy search is not guaranteed to return an optimal path. "
                "IDDFS may repeat expansions across depth limits. "
                "Simulated battery values are abstract model outputs, not real appliance measurements.")
