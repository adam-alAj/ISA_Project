"""Reproducible repeated timing protocol for planner-only measurements."""
from __future__ import annotations

from typing import Callable

from .metrics import summarize_timings
from .records import machine_info


def benchmark_repetitions(run_once: Callable[[int | None], tuple[object, float]], *,
                          repetitions: int = 5, seed: int | None = 0) -> dict:
    """Run one discarded warm-up and N fixed-seed measured calls.

    `run_once(seed)` must return `(raw_result, planner_wall_seconds)`, measured
    strictly around the planner invocation (not UI, event, or animation work).
    """
    if repetitions < 5:
        raise ValueError("P8 timing protocol requires at least five measured repetitions")
    warmup_result, warmup_seconds = run_once(seed)
    measured = [run_once(seed) for _ in range(repetitions)]
    durations = [float(seconds) for _, seconds in measured]
    summary = summarize_timings(durations)
    return {"seed": seed, "warmup_discarded": True, "warmup_seconds_discarded": float(warmup_seconds),
            "repetitions": repetitions, "samples_s": durations, **summary,
            "machine": machine_info(), "raw_results": [result for result, _ in measured]}
