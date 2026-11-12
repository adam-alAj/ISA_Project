"""Shared semantic map and algorithm colors with non-color cues metadata."""

from __future__ import annotations

MAP_STATES = {
    "wall": {"color": "#2F3640", "cue": "cross_hatch"},
    "free": {"color": "#EAE3D0", "cue": "center_dot"},
    "unknown": {"color": "#7B8794", "cue": "diagonal_hatch"},
    "door": {"color": "#F59E0B", "cue": "stripe"},
    "explored": {"color": "#0EA5E9", "cue": "small_dot"},
    "frontier": {"color": "#A855F7", "cue": "diamond"},
    "route": {"color": "#DC2626", "cue": "polyline"},
    "cleaned": {"color": "#16A34A", "cue": "circle"},
    "robot": {"color": "#EF4444", "cue": "label_R"},
    "start": {"color": "#2563EB", "cue": "label_S"},
}

OCCUPANCY_TO_STATE = {
    0: "free",
    1: "wall",
    2: "door",
    3: "unknown",
}

CANVAS_COLORS = {
    "background": "#F4F6FA",
    "empty_text": "#475569",
    "wall_hatch": "#62676F",
    "free_dot": "#AAA493",
    "door_stripe": "#8A6814",
    "unknown_stripe": "#063F46",
    "route": "#DC2626",
    "marker_text": "#FFFFFF",
}

ALGORITHM_COLORS = {
    "bfs": "#0EA5E9",
    "dfs": "#F97316",
    "ucs": "#22C55E",
    "greedy": "#A855F7",
    "astar": "#E11D48",
    "iddfs": "#14B8A6",
}
