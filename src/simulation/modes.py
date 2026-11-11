"""Distinct mission types for route planning and floor coverage."""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PointToPointMission:
    start: tuple[int, int]
    goal: tuple[int, int]


@dataclass(frozen=True)
class CoverageMission:
    policy: Any
